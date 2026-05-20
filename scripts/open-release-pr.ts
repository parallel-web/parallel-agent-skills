#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { bumpVersion, REPO_ROOT, SEMVER_RE } from "./site-lib.ts";

const VERSION_FILE = resolve(REPO_ROOT, "VERSION");
const FILES_TO_COMMIT = [
  "VERSION",
  ".claude-plugin/plugin.json",
  ".claude-plugin/marketplace.json",
  ".codex-plugin/plugin.json",
];
const PR_BODY = `## Release checklist
- [ ] Review version bumps and changelog-relevant changes
- [ ] Merge this PR to \`main\`

Any merged \`release/v*\` PR triggers the automatic tag + GitHub Release workflow.
`;

class ScriptError extends Error {}

function run(command: string, args: string[], options: { inherit?: boolean; check?: boolean } = {}) {
  const result = spawnSync(command, args, {
    cwd: REPO_ROOT,
    encoding: "utf8",
    stdio: options.inherit ? "inherit" : "pipe",
  });

  if ((options.check ?? true) && result.status !== 0) {
    const output = [result.stdout, result.stderr].filter(Boolean).join("");
    throw new ScriptError(output || `${command} ${args.join(" ")} failed`);
  }

  return result;
}

function gitOutput(...args: string[]): string {
  return (run("git", args).stdout ?? "").trim();
}

function requireCommand(name: string): void {
  const result = run("which", [name], { check: false });
  if (result.status !== 0) {
    throw new ScriptError(`Missing required command: ${name}`);
  }
}

function requireCleanWorktree(): void {
  if (gitOutput("status", "--porcelain")) {
    throw new ScriptError("Git working tree is not clean. Commit or stash changes first.");
  }
}

function requireBranch(expectedBranch: string): void {
  const currentBranch = gitOutput("branch", "--show-current");
  if (currentBranch !== expectedBranch) {
    throw new ScriptError(`Current branch is ${JSON.stringify(currentBranch)}; switch to ${JSON.stringify(expectedBranch)} first.`);
  }
}

function requireUpToDateWithOrigin(baseBranch: string): void {
  run("git", ["fetch", "origin", baseBranch], { inherit: true });
  const localHead = gitOutput("rev-parse", "HEAD");
  const remoteHead = gitOutput("rev-parse", `origin/${baseBranch}`);
  if (localHead !== remoteHead) {
    throw new ScriptError(`Local ${JSON.stringify(baseBranch)} is not at origin/${baseBranch}. Run \`git pull --ff-only\` first.`);
  }
}

function requireGhAuth(): void {
  const result = run("gh", ["auth", "status"], { check: false });
  if (result.status !== 0) {
    throw new ScriptError("GitHub CLI is not authenticated. Run `gh auth login` first.");
  }
}

function readVersion(): string {
  const version = readFileSync(VERSION_FILE, "utf8").trim();
  if (!SEMVER_RE.test(version)) {
    throw new ScriptError(`Invalid VERSION contents: ${JSON.stringify(version)}`);
  }
  return version;
}

function nextVersion(current: string, part: "patch" | "minor" | "major"): string {
  const match = SEMVER_RE.exec(current);
  if (!match) {
    throw new ScriptError(`Invalid semver: ${JSON.stringify(current)}`);
  }

  const major = Number(match[1]);
  const minor = Number(match[2]);
  const patch = Number(match[3]);

  if (part === "major") return `${major + 1}.0.0`;
  if (part === "minor") return `${major}.${minor + 1}.0`;
  return `${major}.${minor}.${patch + 1}`;
}

function ensureBranchDoesNotExist(branch: string): void {
  const local = run("git", ["show-ref", "--verify", "--quiet", `refs/heads/${branch}`], { check: false });
  if (local.status === 0) {
    throw new ScriptError(`Local branch already exists: ${branch}`);
  }

  const remote = run("git", ["ls-remote", "--exit-code", "--heads", "origin", branch], { check: false });
  if (remote.status === 0) {
    throw new ScriptError(`Remote branch already exists on origin: ${branch}`);
  }
}

function commitRelease(branch: string, version: string): void {
  run("git", ["switch", "-c", branch], { inherit: true });
  run("git", ["add", ...FILES_TO_COMMIT], { inherit: true });
  run("git", ["commit", "-m", `Release v${version}`], { inherit: true });
  run("git", ["push", "--set-upstream", "origin", branch], { inherit: true });
}

function openPullRequest(baseBranch: string, branch: string, version: string): string {
  const result = run("gh", [
    "pr",
    "create",
    "--base",
    baseBranch,
    "--head",
    branch,
    "--title",
    `Release v${version}`,
    "--body",
    PR_BODY,
  ]);
  return (result.stdout ?? "").trim();
}

function parseArgs(): { part: "patch" | "minor" | "major"; base: string } {
  const args = process.argv.slice(2);
  const partIndex = args.indexOf("--part");
  const baseIndex = args.indexOf("--base");
  const part = partIndex >= 0 ? args[partIndex + 1] : undefined;
  const base = baseIndex >= 0 && args[baseIndex + 1] ? args[baseIndex + 1]! : "main";

  if (part !== "patch" && part !== "minor" && part !== "major") {
    throw new ScriptError("Usage: tsx scripts/open-release-pr.ts --part <patch|minor|major> [--base main]");
  }

  return { part, base };
}

function main(): void {
  try {
    const { part, base } = parseArgs();

    requireCommand("git");
    requireCommand("gh");
    requireCleanWorktree();
    requireBranch(base);
    requireUpToDateWithOrigin(base);
    requireGhAuth();

    const targetVersion = nextVersion(readVersion(), part);
    const branch = `release/v${targetVersion}`;
    ensureBranchDoesNotExist(branch);

    const version = bumpVersion(part);
    if (version !== targetVersion) {
      throw new ScriptError(`Expected bumped version ${targetVersion}, got ${version}`);
    }

    commitRelease(branch, version);
    const prUrl = openPullRequest(base, branch, version);
    console.log(`Opened release PR for v${version}: ${prUrl}`);
  } catch (error) {
    console.error(error instanceof Error ? `error: ${error.message}` : error);
    process.exit(1);
  }
}

main();
