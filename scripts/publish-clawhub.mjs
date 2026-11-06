#!/usr/bin/env node
import { execFile } from "node:child_process";
import { mkdtemp, readFile, readdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { setTimeout as sleep } from "node:timers/promises";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";

// Reuse the pinned CLI's file selection and hashing, including its ignore rules.
import { prepareSkillFilesForPublish } from "clawhub/dist/cli/commands/publish.js";
import { apiRequest, getHttpErrorStatus, registryUrl } from "clawhub/dist/http.js";
import { ApiV1SkillVersionResponseSchema, ApiV1SkillPublicationResponseSchema } from "clawhub/dist/schema/index.js";
import { buildSkillFingerprint, hashSkillFiles } from "clawhub/dist/skills.js";

const exec = promisify(execFile);
const cli = fileURLToPath(import.meta.resolve("clawhub/bin/clawdhub.js"));

export async function publishRelease({
  root,
  owner,
  token,
  registry = "https://clawhub.ai",
  timeoutMs = 20 * 60 * 1000,
  pollMs = 30 * 1000,
}) {
  owner = (owner ?? "").trim().replace(/^@/, "").toLowerCase();
  if (!/^[a-z0-9](?:[a-z0-9._-]*[a-z0-9])?$/.test(owner)) {
    throw new Error("Set CLAWHUB_OWNER to your ClawHub organization publisher handle.");
  }
  if (!token?.trim()) {
    throw new Error("Set the CLAWHUB_TOKEN Actions secret to a token with access to that publisher.");
  }
  root = resolve(root);
  const git = async (...args) => (await exec("git", args, { cwd: root })).stdout.trim();
  const version = (await readFile(join(root, "VERSION"), "utf8")).trim();
  if (!/^\d+\.\d+\.\d+$/.test(version)) throw new Error("VERSION must contain X.Y.Z.");
  const ref = `refs/tags/v${version}`;
  const commit = await git("rev-parse", "HEAD");
  if (commit !== await git("rev-parse", `${ref}^{commit}`)) {
    throw new Error(`Check out v${version} before publishing; HEAD does not match the release tag.`);
  }
  if (await git("status", "--porcelain", "--untracked-files=all", "--", "VERSION", "skills")) {
    throw new Error("VERSION and skills/ must match the clean release checkout.");
  }
  const deadline = Date.now() + timeoutMs;
  const configDir = await mkdtemp(join(tmpdir(), "clawhub-release-"));
  const configPath = join(configDir, "config.json");
  async function get(path, schema) {
    const url = registryUrl(path, registry);
    url.searchParams.set("ownerHandle", owner);
    try {
      return { status: 200, data: await apiRequest(registry, { method: "GET", url: url.toString(), token }, schema) };
    } catch (error) {
      const status = getHttpErrorStatus(error);
      if ([403, 404, 423].includes(status)) return { status };
      throw error;
    }
  }

  async function state(skill) {
    const path = `/api/v1/skills/${encodeURIComponent(skill.name)}/versions/${version}`;
    const result = await get(path, ApiV1SkillVersionResponseSchema);
    if (result.data?.version) {
      const published = result.data.version;
      if (published.version !== version || !Array.isArray(published.files)) {
        throw new Error(`Invalid version response for @${owner}/${skill.name}@${version}.`);
      }
      // ClawHub can generate this file after upload; it is not part of the source bundle.
      const files = published.files.filter((file) => file.path.toLowerCase() !== "skill-card.md");
      if (buildSkillFingerprint(files) !== skill.fingerprint) {
        throw new Error(`@${owner}/${skill.name}@${version} already contains different files. Release a new repository version.`);
      }
      return "published";
    }
    const held = await get(`${path}/publication`, ApiV1SkillPublicationResponseSchema);
    if (held.data?.publication) {
      const { stage, retrying } = held.data.publication;
      if (retrying || ["pending_checks", "ready_to_finalize", "finalizing"].includes(stage)) return "pending";
      throw new Error(`@${owner}/${skill.name}@${version}: publication ${stage}. Inspect this version in ClawHub before retrying.`);
    }
    if (result.status === 404 && held.status === 404) return "missing";
    throw new Error(`Cannot read @${owner}/${skill.name}@${version}; check publisher access and moderation status.`);
  }

  try {
    await writeFile(configPath, JSON.stringify({ registry, token }), { mode: 0o600 });
    const skills = [];
    for (const directory of (await readdir(join(root, "skills"), { withFileTypes: true })).sort((a, b) => a.name.localeCompare(b.name))) {
      if (!directory.isDirectory()) continue;
      const folder = join(root, "skills", directory.name);
      if (!(await readdir(folder)).includes("SKILL.md")) continue;
      const { fingerprint } = hashSkillFiles(await prepareSkillFilesForPublish(folder));
      skills.push({ name: directory.name, folder, fingerprint });
    }
    if (skills.length === 0) throw new Error("No skills found in the release checkout.");

    // Check every existing version before creating any new ones.
    const states = new Map();
    for (const skill of skills) states.set(skill.name, await state(skill));
    for (const skill of skills) {
      if (states.get(skill.name) !== "missing") continue;
      console.log(`Submitting @${owner}/${skill.name}@${version}`);
      const { stdout } = await exec(process.execPath, [
        cli, "--registry", registry, "--no-input", "skill", "publish", skill.folder,
        "--owner", owner, "--version", version,
        "--source-repo", process.env.GITHUB_REPOSITORY || "parallel-web/parallel-agent-skills",
        "--source-commit", commit, "--source-ref", ref, "--source-path", `skills/${skill.name}`,
        "--changelog", `Repository release v${version}`, "--json",
      ], {
        cwd: root,
        env: { ...process.env, CLAWHUB_CONFIG_PATH: configPath, CLAWHUB_DISABLE_TELEMETRY: "1" },
        timeout: Math.max(1, deadline - Date.now()),
      });
      console.log(stdout.trim());
    }

    let remaining = [...skills];
    while (remaining.length) {
      const pending = [];
      for (const skill of remaining) {
        if (await state(skill) === "published") {
          console.log(`Verified @${owner}/${skill.name}@${version}`);
        } else {
          pending.push(skill);
        }
      }
      remaining = pending;
      if (!remaining.length) break;
      if (Date.now() >= deadline) {
        throw new Error(`Timed out waiting for ClawHub publication: ${remaining.map((skill) => skill.name).join(", ")}. Rerun the job to resume checks.`);
      }
      console.log(`Waiting for security checks on ${remaining.length} skill(s).`);
      await sleep(Math.min(pollMs, Math.max(0, deadline - Date.now())));
    }
    console.log(`All ${skills.length} skills are published and verified at ${version}.`);
  } finally {
    await rm(configDir, { recursive: true, force: true });
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2).filter((arg) => arg !== "--");
  if (args.length !== 0 && (args.length !== 2 || args[0] !== "--root")) {
    console.error("Usage: pnpm run release:clawhub -- --root <release-checkout>");
    process.exitCode = 1;
  } else {
    await publishRelease({
      root: args[1] || ".",
      owner: process.env.CLAWHUB_OWNER,
      token: process.env.CLAWHUB_TOKEN,
    }).catch((error) => {
      console.error(error.message);
      process.exitCode = 1;
    });
  }
}
