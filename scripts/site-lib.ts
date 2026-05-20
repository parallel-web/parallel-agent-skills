import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { createWriteStream, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync, cpSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import archiver from "archiver";

import { renderIndexPage } from "./site-templates.ts";

const __dirname = dirname(fileURLToPath(import.meta.url));

export const REPO_ROOT = resolve(__dirname, "..");
export const SKILLS_DIR = join(REPO_ROOT, "skills");
export const VERSION_FILE = join(REPO_ROOT, "VERSION");
export const SITE_URL = "https://skills.parallel.ai";
export const REPOSITORY = "https://github.com/parallel-web/parallel-agent-skills";
export const OWNER = "parallel-web";
export const REPO_NAME = "parallel-agent-skills";
export const REPO_SLUG = `${OWNER}/${REPO_NAME}`;
export const SCHEMA_VERSION = 1;
export const SEMVER_RE = /^v?(\d+)\.(\d+)\.(\d+)$/;

type Scalar = string | number | boolean | null;
export interface FrontmatterMap {
  [key: string]: FrontmatterValue;
}
export type FrontmatterValue = Scalar | FrontmatterMap;

export type SkillFileInfo = {
  path: string;
  sha256: string;
  size: number;
};

export type SkillData = {
  name: string;
  directory: string;
  description: string;
  metadata: FrontmatterMap;
  body: string;
  files: SkillFileInfo[];
};

export type ReleaseInfo = {
  tag: string;
  version: string;
  published_at: string | null;
};

export class SkillError extends Error {}

function runGit(args: string[], check = true): string {
  try {
    return execFileSync("git", args, { cwd: REPO_ROOT, encoding: "utf8" }).trim();
  } catch (error) {
    if (!check) {
      return "";
    }
    throw error;
  }
}

export function currentCommitSha(): string {
  return runGit(["rev-parse", "HEAD"]);
}

export function readRepositoryVersion(): string {
  return readFileSync(VERSION_FILE, "utf8").trim();
}

function parseScalar(value: string): FrontmatterValue {
  const lowered = value.toLowerCase();
  if (lowered === "true") return true;
  if (lowered === "false") return false;
  if (lowered === "null" || lowered === "~") return null;
  if (/^-?\d+$/.test(value)) return Number.parseInt(value, 10);
  if (/^-?\d+\.\d+$/.test(value)) return Number.parseFloat(value);
  if (
    (value.startsWith('"') && value.endsWith('"')) ||
    (value.startsWith("'") && value.endsWith("'"))
  ) {
    return value.slice(1, -1);
  }
  return value;
}

export function parseFrontmatter(text: string): { metadata: FrontmatterMap; body: string } {
  if (!text.startsWith("---\n")) {
    throw new SkillError("SKILL.md is missing YAML frontmatter");
  }

  const secondFenceIndex = text.indexOf("\n---\n", 4);
  if (secondFenceIndex === -1) {
    throw new SkillError("SKILL.md frontmatter is malformed");
  }

  const frontmatterText = text.slice(4, secondFenceIndex);
  const body = text.slice(secondFenceIndex + 5).replace(/^\n+/, "");

  const data: FrontmatterMap = {};
  const stack: Array<{ indent: number; target: FrontmatterMap }> = [{ indent: -1, target: data }];

  for (const rawLine of frontmatterText.split(/\r?\n/)) {
    if (!rawLine.trim() || rawLine.trimStart().startsWith("#")) {
      continue;
    }

    const indent = rawLine.length - rawLine.trimStart().length;
    const line = rawLine.trim();
    const separatorIndex = line.indexOf(":");
    if (separatorIndex === -1) {
      throw new SkillError(`Unsupported frontmatter line: ${rawLine}`);
    }

    while (stack.length > 1 && indent <= stack.at(-1)!.indent) {
      stack.pop();
    }

    const key = line.slice(0, separatorIndex).trim();
    const rawValue = line.slice(separatorIndex + 1).trim();
    const parent = stack.at(-1)!.target;

    if (rawValue === "") {
      const child: FrontmatterMap = {};
      parent[key] = child;
      stack.push({ indent, target: child });
    } else {
      parent[key] = parseScalar(rawValue);
    }
  }

  return { metadata: data, body };
}

function sha256File(path: string): string {
  const digest = createHash("sha256");
  digest.update(readFileSync(path));
  return digest.digest("hex");
}

function walkFiles(directory: string): string[] {
  const entries = readdirSync(directory, { withFileTypes: true });
  const files: string[] = [];

  for (const entry of entries) {
    const fullPath = join(directory, entry.name);
    if (entry.isDirectory()) {
      files.push(...walkFiles(fullPath));
    } else if (entry.isFile()) {
      files.push(fullPath);
    }
  }

  return files.sort();
}

function skillDirectories(): string[] {
  return readdirSync(SKILLS_DIR)
    .map((entry) => join(SKILLS_DIR, entry))
    .filter((path) => statSync(path).isDirectory() && existsSync(join(path, "SKILL.md")))
    .sort();
}

export function semverKey(version: string): [number, number, number] {
  const match = SEMVER_RE.exec(version);
  if (!match) {
    throw new Error(`Invalid semver: ${version}`);
  }
  return [Number(match[1]), Number(match[2]), Number(match[3])];
}

export function discoverReleases(): ReleaseInfo[] {
  const raw = runGit(
    [
      "for-each-ref",
      "--sort=version:refname",
      "--format=%(refname:strip=2)\t%(creatordate:iso8601-strict)",
      "refs/tags/v*",
    ],
    false,
  );

  const releases: ReleaseInfo[] = [];
  for (const line of raw.split(/\r?\n/)) {
    if (!line.trim()) continue;
    const [tag, createdAt = ""] = line.split("\t");
    const version = tag.startsWith("v") ? tag.slice(1) : tag;
    if (!SEMVER_RE.test(version)) continue;
    releases.push({
      tag: `v${version}`,
      version,
      published_at: createdAt || null,
    });
  }

  releases.sort((a, b) => {
    const left = semverKey(a.version);
    const right = semverKey(b.version);
    return right[0] - left[0] || right[1] - left[1] || right[2] - left[2];
  });

  return releases;
}

export function collectSkills(): SkillData[] {
  const skills: SkillData[] = [];

  for (const skillDir of skillDirectories()) {
    const skillText = readFileSync(join(skillDir, "SKILL.md"), "utf8");
    const { metadata, body } = parseFrontmatter(skillText);

    const directory = relative(SKILLS_DIR, skillDir);
    const name = typeof metadata.name === "string" ? metadata.name : directory;
    const description = metadata.description;
    if (typeof description !== "string" || !description) {
      throw new SkillError(`${join(skillDir, "SKILL.md")} is missing description`);
    }

    const files: SkillFileInfo[] = walkFiles(skillDir).map((filePath) => ({
      path: relative(skillDir, filePath).replaceAll("\\", "/"),
      sha256: sha256File(filePath),
      size: statSync(filePath).size,
    }));

    skills.push({
      name,
      directory,
      description,
      metadata,
      body,
      files,
    });
  }

  return skills;
}

function jsonDump(path: string, payload: unknown): void {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
}

function buildHeadersFile(outputDir: string): void {
  const headers = `/*.md
  Content-Type: text/markdown; charset=utf-8
/*.txt
  Content-Type: text/plain; charset=utf-8
/*.json
  Content-Type: application/json; charset=utf-8
/*
  Access-Control-Allow-Origin: *
`;
  writeFileSync(join(outputDir, "_headers"), headers, "utf8");
}

function absoluteUrl(path: string): string {
  return `${SITE_URL}${path}`;
}

export function installCommandForSkill(skillName: string): string {
  return `npx skills add ${REPO_SLUG} --skill ${skillName}`;
}

function buildVersionsPayload(skillName: string, releases: ReleaseInfo[]) {
  const latestReleaseVersion = releases[0]?.version ?? null;
  return {
    schema_version: SCHEMA_VERSION,
    name: skillName,
    latest_release_version: latestReleaseVersion,
    versions: releases.map((release) => {
      const assetName = `${skillName}-${release.version}.zip`;
      return {
        version: release.version,
        archive_url: absoluteUrl(`/archives/${skillName}/${release.version}.zip`),
        asset_name: assetName,
        release_url: `${REPOSITORY}/releases/tag/v${release.version}`,
        github_asset_url: `${REPOSITORY}/releases/download/v${release.version}/${assetName}`,
        published_at: release.published_at,
      };
    }),
  };
}

function buildManifestPayload(
  skill: SkillData,
  repositoryVersion: string,
  latestReleaseVersion: string | null,
  commitSha: string,
) {
  return {
    schema_version: SCHEMA_VERSION,
    name: skill.name,
    description: skill.description,
    repository_version: repositoryVersion,
    latest_release_version: latestReleaseVersion,
    channel: "main",
    commit_sha: commitSha,
    repository: REPOSITORY,
    files: skill.files.map((fileInfo) => ({
      path: fileInfo.path,
      url: absoluteUrl(`/${skill.name}/${fileInfo.path}`),
      sha256: fileInfo.sha256,
      size: fileInfo.size,
    })),
  };
}

function buildIndexPayload(
  skills: SkillData[],
  repositoryVersion: string,
  latestReleaseVersion: string | null,
  commitSha: string,
) {
  return {
    schema_version: SCHEMA_VERSION,
    generated_at: new Date().toISOString(),
    site_url: SITE_URL,
    repository: REPOSITORY,
    repository_version: repositoryVersion,
    latest_release_version: latestReleaseVersion,
    channel: "main",
    commit_sha: commitSha,
    install: {
      agent_skills: {
        command: `npx skills add ${REPO_SLUG} --all --global`,
        description: "Install all Parallel skills globally using the Agent Skills CLI.",
      },
      claude_code: {
        commands: [
          "/plugin marketplace add parallel-web/parallel-agent-skills",
          "/plugin install parallel",
        ],
        description: "Install the Parallel Claude Code plugin from its marketplace.",
      },
      codex: {
        command: "$skill-installer parallel-web/parallel-agent-skills",
        description: "Install the Parallel skills package in OpenAI Codex.",
      },
    },
    skills: skills.map((skill) => ({
      name: skill.name,
      description: skill.description,
      skill_url: absoluteUrl(`/${skill.name}/SKILL.md`),
      manifest_url: absoluteUrl(`/${skill.name}/manifest.json`),
      versions_url: absoluteUrl(`/${skill.name}/versions.json`),
      install_command: installCommandForSkill(skill.name),
    })),
  };
}

function buildLlmsTxt(
  skills: SkillData[],
  repositoryVersion: string,
  latestReleaseVersion: string | null,
): string {
  const lines = [
    "# Parallel Agent Skills",
    "",
    "> CDN-hosted Parallel Agent Skills catalog with install instructions and direct links to each skill.",
    "",
    `Repository version: ${repositoryVersion}`,
    `Latest release version: ${latestReleaseVersion ?? "none"}`,
    "",
    "Install all skills with:",
    "",
    "```bash",
    `npx skills add ${REPO_SLUG} --all --global`,
    "```",
    "",
    "## Catalog",
  ];

  for (const skill of skills) {
    lines.push(`- [${skill.name}](${absoluteUrl(`/${skill.name}/SKILL.md`)}): ${skill.description}`);
  }

  lines.push(
    "",
    "## Metadata",
    `- [index.json](${absoluteUrl("/index.json")}): machine-readable catalog for all available skills.`,
    `- [GitHub repository](${REPOSITORY}): source for the skill definitions and release workflow.`,
  );

  return `${lines.join("\n")}\n`;
}

function ensureCleanDirectory(path: string): void {
  if (existsSync(path)) {
    rmSync(path, { recursive: true, force: true });
  }
  mkdirSync(path, { recursive: true });
}

export function buildSite(outputDirInput: string): void {
  const outputDir = resolve(outputDirInput);
  const repositoryVersion = readRepositoryVersion();
  const commitSha = currentCommitSha();
  const releases = discoverReleases();
  const latestReleaseVersion = releases[0]?.version ?? null;
  const skills = collectSkills();

  ensureCleanDirectory(outputDir);
  buildHeadersFile(outputDir);

  for (const skill of skills) {
    const destination = join(outputDir, skill.name);
    cpSync(join(SKILLS_DIR, skill.directory), destination, { recursive: true });
    jsonDump(
      join(destination, "manifest.json"),
      buildManifestPayload(skill, repositoryVersion, latestReleaseVersion, commitSha),
    );
    jsonDump(join(destination, "versions.json"), buildVersionsPayload(skill.name, releases));
  }

  jsonDump(join(outputDir, "index.json"), buildIndexPayload(skills, repositoryVersion, latestReleaseVersion, commitSha));
  writeFileSync(
    join(outputDir, "index.html"),
    renderIndexPage(skills, repositoryVersion, latestReleaseVersion, REPOSITORY, REPO_SLUG),
    "utf8",
  );
  writeFileSync(join(outputDir, "llms.txt"), buildLlmsTxt(skills, repositoryVersion, latestReleaseVersion), "utf8");
}

export async function buildArchives(outputDirInput: string, version: string): Promise<void> {
  if (!SEMVER_RE.test(version)) {
    throw new Error(`Version must be semver, got: ${version}`);
  }

  const outputDir = resolve(outputDirInput);
  ensureCleanDirectory(outputDir);

  for (const skill of collectSkills()) {
    const skillDir = join(SKILLS_DIR, skill.directory);
    const archivePath = join(outputDir, `${skill.name}-${version}.zip`);

    await new Promise<void>((resolvePromise, rejectPromise) => {
      const output = createWriteStream(archivePath);
      const archive = archiver("zip", { zlib: { level: 9 } });

      output.on("close", () => resolvePromise());
      output.on("error", rejectPromise);
      archive.on("error", rejectPromise);

      archive.pipe(output);
      for (const filePath of walkFiles(skillDir)) {
        const arcname = `${skill.name}/${relative(skillDir, filePath).replaceAll("\\", "/")}`;
        archive.file(filePath, { name: arcname });
      }
      void archive.finalize();
    });
  }
}

function writeJsonFile(path: string, data: unknown): void {
  writeFileSync(path, `${JSON.stringify(data, null, 2)}\n`, "utf8");
}

export function bumpVersion(part: "major" | "minor" | "patch"): string {
  const current = readRepositoryVersion();
  const [major, minor, patch] = semverKey(current);

  let newVersion: string;
  if (part === "major") {
    newVersion = `${major + 1}.0.0`;
  } else if (part === "minor") {
    newVersion = `${major}.${minor + 1}.0`;
  } else {
    newVersion = `${major}.${minor}.${patch + 1}`;
  }

  writeFileSync(VERSION_FILE, `${newVersion}\n`, "utf8");

  const claudePluginPath = join(REPO_ROOT, ".claude-plugin", "plugin.json");
  const claudePlugin = JSON.parse(readFileSync(claudePluginPath, "utf8")) as Record<string, unknown>;
  claudePlugin.version = newVersion;
  writeJsonFile(claudePluginPath, claudePlugin);

  const marketplacePath = join(REPO_ROOT, ".claude-plugin", "marketplace.json");
  const marketplace = JSON.parse(readFileSync(marketplacePath, "utf8")) as Record<string, unknown> & {
    metadata?: Record<string, unknown>;
    plugins?: Array<Record<string, unknown>>;
  };
  marketplace.metadata ??= {};
  marketplace.metadata.version = newVersion;
  if (marketplace.plugins?.[0]) {
    marketplace.plugins[0].version = newVersion;
  }
  writeJsonFile(marketplacePath, marketplace);

  const codexPluginPath = join(REPO_ROOT, ".codex-plugin", "plugin.json");
  const codexPlugin = JSON.parse(readFileSync(codexPluginPath, "utf8")) as Record<string, unknown>;
  codexPlugin.version = newVersion;
  writeJsonFile(codexPluginPath, codexPlugin);

  return newVersion;
}
