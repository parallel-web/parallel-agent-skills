#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
VERSION_FILE = REPO_ROOT / "VERSION"
SITE_URL = "https://skills.parallel.ai"
REPOSITORY = "https://github.com/parallel-web/parallel-agent-skills"
OWNER = "parallel-web"
REPO_NAME = "parallel-agent-skills"
SCHEMA_VERSION = 1
SEMVER_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


class SkillError(RuntimeError):
    pass


def run_git(*args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=check,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def current_commit_sha() -> str:
    return run_git("rev-parse", "HEAD")


def read_repository_version() -> str:
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def parse_scalar(value: str) -> Any:
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "~"}:
        return None
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return ast.literal_eval(value)
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        raise SkillError("SKILL.md is missing YAML frontmatter")

    try:
        _, remainder = text.split("---\n", 1)
        frontmatter_text, body = remainder.split("\n---\n", 1)
    except ValueError as exc:
        raise SkillError("SKILL.md frontmatter is malformed") from exc

    data: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, data)]

    for raw_line in frontmatter_text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if ":" not in line:
            raise SkillError(f"Unsupported frontmatter line: {raw_line}")

        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()

        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        parent = stack[-1][1]

        if raw_value == "":
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = parse_scalar(raw_value)

    return data, body.lstrip("\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def skill_directories() -> list[Path]:
    return sorted(
        path for path in SKILLS_DIR.iterdir() if path.is_dir() and (path / "SKILL.md").exists()
    )


def semver_key(version: str) -> tuple[int, int, int]:
    match = SEMVER_RE.match(version)
    if not match:
        raise ValueError(f"Invalid semver: {version}")
    return tuple(int(part) for part in match.groups())


def discover_releases() -> list[dict[str, Any]]:
    try:
        raw = run_git(
            "for-each-ref",
            "--sort=version:refname",
            "--format=%(refname:strip=2)\t%(creatordate:iso8601-strict)",
            "refs/tags/v*",
        )
    except subprocess.CalledProcessError:
        return []

    releases: list[dict[str, Any]] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        tag, _, created_at = line.partition("\t")
        version = tag[1:] if tag.startswith("v") else tag
        if not SEMVER_RE.match(version):
            continue
        releases.append(
            {
                "tag": f"v{version}",
                "version": version,
                "published_at": created_at or None,
            }
        )

    releases.sort(key=lambda item: semver_key(item["version"]), reverse=True)
    return releases


def collect_skills() -> list[dict[str, Any]]:
    skills: list[dict[str, Any]] = []
    for skill_dir in skill_directories():
        skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        metadata, body = parse_frontmatter(skill_text)

        name = metadata.get("name") or skill_dir.name
        description = metadata.get("description")
        if not description:
            raise SkillError(f"{skill_dir / 'SKILL.md'} is missing description")

        raw_files: list[dict[str, Any]] = []
        for file_path in sorted(path for path in skill_dir.rglob("*") if path.is_file()):
            relative_path = file_path.relative_to(skill_dir).as_posix()
            raw_files.append(
                {
                    "path": relative_path,
                    "sha256": sha256_file(file_path),
                    "size": file_path.stat().st_size,
                }
            )

        skills.append(
            {
                "name": name,
                "directory": skill_dir.name,
                "description": description,
                "metadata": metadata,
                "body": body,
                "files": raw_files,
            }
        )

    return skills


def json_dump(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_headers_file(output_dir: Path) -> None:
    headers = """/*.md
  Content-Type: text/markdown; charset=utf-8
/*.txt
  Content-Type: text/plain; charset=utf-8
/*.json
  Content-Type: application/json; charset=utf-8
/*
  Access-Control-Allow-Origin: *
"""
    (output_dir / "_headers").write_text(headers, encoding="utf-8")


def absolute_url(path: str) -> str:
    return f"{SITE_URL}{path}"


def build_versions_payload(skill_name: str, releases: list[dict[str, Any]]) -> dict[str, Any]:
    latest_release_version = releases[0]["version"] if releases else None
    versions = []
    for release in releases:
        version = release["version"]
        asset_name = f"{skill_name}-{version}.zip"
        versions.append(
            {
                "version": version,
                "archive_url": absolute_url(f"/archives/{skill_name}/{version}.zip"),
                "asset_name": asset_name,
                "release_url": f"{REPOSITORY}/releases/tag/v{version}",
                "github_asset_url": f"{REPOSITORY}/releases/download/v{version}/{asset_name}",
                "published_at": release["published_at"],
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "name": skill_name,
        "latest_release_version": latest_release_version,
        "versions": versions,
    }


def build_manifest_payload(
    skill: dict[str, Any],
    repository_version: str,
    latest_release_version: str | None,
    commit_sha: str,
) -> dict[str, Any]:
    files = []
    for file_info in skill["files"]:
        path = file_info["path"]
        files.append(
            {
                "path": path,
                "url": absolute_url(f"/skills/{skill['name']}/{path}"),
                "sha256": file_info["sha256"],
                "size": file_info["size"],
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "name": skill["name"],
        "description": skill["description"],
        "repository_version": repository_version,
        "latest_release_version": latest_release_version,
        "channel": "main",
        "commit_sha": commit_sha,
        "repository": REPOSITORY,
        "files": files,
    }


def build_index_payload(
    skills: list[dict[str, Any]],
    repository_version: str,
    latest_release_version: str | None,
    commit_sha: str,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "site_url": SITE_URL,
        "repository": REPOSITORY,
        "repository_version": repository_version,
        "latest_release_version": latest_release_version,
        "channel": "main",
        "commit_sha": commit_sha,
        "install": {
            "agent_skills": {
                "command": "npx skills add parallel-web/parallel-agent-skills --all --global",
                "description": "Install all Parallel skills globally using the Agent Skills CLI.",
            },
            "claude_code": {
                "commands": [
                    "/plugin marketplace add parallel-web/parallel-agent-skills",
                    "/plugin install parallel",
                ],
                "description": "Install the Parallel Claude Code plugin from its marketplace.",
            },
            "codex": {
                "command": "$skill-installer parallel-web/parallel-agent-skills",
                "description": "Install the Parallel skills package in OpenAI Codex.",
            },
        },
        "skills": [
            {
                "name": skill["name"],
                "description": skill["description"],
                "skill_url": absolute_url(f"/skills/{skill['name']}/SKILL.md"),
                "manifest_url": absolute_url(f"/skills/{skill['name']}/manifest.json"),
                "versions_url": absolute_url(f"/skills/{skill['name']}/versions.json"),
            }
            for skill in skills
        ],
    }


def render_index_html(
    skills: list[dict[str, Any]],
    repository_version: str,
    latest_release_version: str | None,
) -> str:
    release_line = (
        f"Latest release: <strong>{html.escape(latest_release_version)}</strong>."
        if latest_release_version
        else "No GitHub release has been published yet."
    )

    skill_items = []
    for skill in skills:
        name = html.escape(skill["name"])
        description = html.escape(skill["description"])
        archive_link = ""
        if latest_release_version:
            archive_link = (
                f'<a href="/archives/{name}/{html.escape(latest_release_version)}.zip">'
                f'latest archive ({html.escape(latest_release_version)})</a>'
            )
        skill_items.append(
            f"""
            <li>
              <h2><a href="/skills/{name}/SKILL.md">{name}</a></h2>
              <p>{description}</p>
              <p class=\"links\">
                <a href=\"/skills/{name}/manifest.json\">manifest.json</a>
                <a href=\"/skills/{name}/versions.json\">versions.json</a>
                {archive_link}
              </p>
            </li>
            """.strip()
        )

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Parallel Agent Skills</title>
    <style>
      :root {{
        color-scheme: light dark;
        --bg: #0d0d0d;
        --panel: #171717;
        --text: #f4f4ef;
        --muted: #b8b4aa;
        --accent: #fb631b;
        --border: #2b2b2b;
      }}
      @media (prefers-color-scheme: light) {{
        :root {{
          --bg: #fcfcfa;
          --panel: #ffffff;
          --text: #1d1b16;
          --muted: #6e675b;
          --accent: #fb631b;
          --border: #e7e0d1;
        }}
      }}
      body {{
        margin: 0;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: var(--bg);
        color: var(--text);
        line-height: 1.6;
      }}
      main {{
        max-width: 960px;
        margin: 0 auto;
        padding: 48px 20px 80px;
      }}
      h1, h2, h3 {{
        line-height: 1.2;
      }}
      a {{
        color: var(--accent);
        text-decoration: none;
      }}
      a:hover {{
        text-decoration: underline;
      }}
      .hero, .panel {{
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 24px;
      }}
      .hero {{
        margin-bottom: 20px;
      }}
      .meta {{
        color: var(--muted);
      }}
      code, pre {{
        font-family: "SFMono-Regular", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      }}
      pre {{
        background: rgba(127, 127, 127, 0.12);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 16px;
        overflow-x: auto;
      }}
      ul.skills {{
        list-style: none;
        padding: 0;
        margin: 24px 0 0;
        display: grid;
        gap: 16px;
      }}
      ul.skills li {{
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 20px;
      }}
      .links {{
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
      }}
      .section {{
        margin-top: 20px;
      }}
    </style>
  </head>
  <body>
    <main>
      <section class="hero">
        <h1>Parallel Agent Skills</h1>
        <p>
          Discoverable, CDN-hosted Parallel skills for Claude Code, Codex, and other
          <a href="https://agentskills.io/specification">Agent Skills</a>-compatible clients.
        </p>
        <p class="meta">
          Repository version: <strong>{html.escape(repository_version)}</strong>.<br />
          {release_line}
        </p>
        <p class="links">
          <a href="/index.json">index.json</a>
          <a href="/llms.txt">llms.txt</a>
          <a href="{REPOSITORY}">GitHub repository</a>
        </p>
      </section>

      <section class="panel section">
        <h2>Install</h2>
        <p>Install all Parallel skills globally with the Agent Skills CLI:</p>
        <pre><code>npx skills add parallel-web/parallel-agent-skills --all --global</code></pre>
        <p>Other install options:</p>
        <ul>
          <li><strong>Claude Code</strong>: <code>/plugin marketplace add parallel-web/parallel-agent-skills</code> then <code>/plugin install parallel</code></li>
          <li><strong>OpenAI Codex</strong>: <code>$skill-installer parallel-web/parallel-agent-skills</code></li>
        </ul>
      </section>

      <section class="section">
        <h2>Available skills</h2>
        <ul class="skills">
          {''.join(skill_items)}
        </ul>
      </section>
    </main>
  </body>
</html>
"""


def build_llms_txt(
    skills: list[dict[str, Any]],
    repository_version: str,
    latest_release_version: str | None,
) -> str:
    lines = [
        "# Parallel Agent Skills",
        "",
        "> CDN-hosted Parallel Agent Skills catalog with install instructions and direct links to each skill.",
        "",
        f"Repository version: {repository_version}",
        f"Latest release version: {latest_release_version or 'none'}",
        "",
        "Install all skills with:",
        "",
        "```bash",
        "npx skills add parallel-web/parallel-agent-skills --all --global",
        "```",
        "",
        "## Catalog",
    ]

    for skill in skills:
        lines.append(
            f"- [{skill['name']}]({absolute_url(f'/skills/{skill['name']}/SKILL.md')}): {skill['description']}"
        )

    lines.extend(
        [
            "",
            "## Metadata",
            f"- [index.json]({absolute_url('/index.json')}): machine-readable catalog for all available skills.",
            f"- [GitHub repository]({REPOSITORY}): source for the skill definitions and release workflow.",
        ]
    )

    return "\n".join(lines) + "\n"


def build_site(output_dir: Path) -> None:
    repository_version = read_repository_version()
    commit_sha = current_commit_sha()
    releases = discover_releases()
    latest_release_version = releases[0]["version"] if releases else None
    skills = collect_skills()

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    build_headers_file(output_dir)

    for skill in skills:
        destination = output_dir / "skills" / skill["name"]
        shutil.copytree(SKILLS_DIR / skill["directory"], destination)
        json_dump(
            destination / "manifest.json",
            build_manifest_payload(skill, repository_version, latest_release_version, commit_sha),
        )
        json_dump(destination / "versions.json", build_versions_payload(skill["name"], releases))

    json_dump(
        output_dir / "index.json",
        build_index_payload(skills, repository_version, latest_release_version, commit_sha),
    )
    (output_dir / "index.html").write_text(
        render_index_html(skills, repository_version, latest_release_version),
        encoding="utf-8",
    )
    (output_dir / "llms.txt").write_text(
        build_llms_txt(skills, repository_version, latest_release_version),
        encoding="utf-8",
    )


def build_archives(output_dir: Path, version: str) -> None:
    if not SEMVER_RE.match(version):
        raise ValueError(f"Version must be semver, got: {version}")

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for skill in collect_skills():
        skill_dir = SKILLS_DIR / skill["directory"]
        skill_name = skill["name"]
        archive_name = f"{skill_name}-{version}.zip"
        archive_path = output_dir / archive_name
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for file_path in sorted(path for path in skill_dir.rglob("*") if path.is_file()):
                arcname = f"{skill_name}/{file_path.relative_to(skill_dir).as_posix()}"
                archive.write(file_path, arcname)


def write_json_file(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def bump_version(part: str) -> str:
    current = read_repository_version()
    major, minor, patch = semver_key(current)
    if part == "major":
        new_version = f"{major + 1}.0.0"
    elif part == "minor":
        new_version = f"{major}.{minor + 1}.0"
    elif part == "patch":
        new_version = f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Unsupported bump part: {part}")

    VERSION_FILE.write_text(new_version + "\n", encoding="utf-8")

    claude_plugin_path = REPO_ROOT / ".claude-plugin" / "plugin.json"
    claude_plugin = json.loads(claude_plugin_path.read_text(encoding="utf-8"))
    claude_plugin["version"] = new_version
    write_json_file(claude_plugin_path, claude_plugin)

    marketplace_path = REPO_ROOT / ".claude-plugin" / "marketplace.json"
    marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    marketplace.setdefault("metadata", {})["version"] = new_version
    if marketplace.get("plugins"):
        marketplace["plugins"][0]["version"] = new_version
    write_json_file(marketplace_path, marketplace)

    codex_plugin_path = REPO_ROOT / ".codex-plugin" / "plugin.json"
    codex_plugin = json.loads(codex_plugin_path.read_text(encoding="utf-8"))
    codex_plugin["version"] = new_version
    write_json_file(codex_plugin_path, codex_plugin)

    return new_version


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build and release helpers for skills.parallel.ai")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_site_parser = subparsers.add_parser("build-site", help="Generate the static CDN site")
    build_site_parser.add_argument("--output", default="dist", help="Output directory (default: dist)")

    build_archives_parser = subparsers.add_parser("build-archives", help="Build per-skill zip archives")
    build_archives_parser.add_argument("--output", default="release-assets", help="Output directory")
    build_archives_parser.add_argument("--version", required=True, help="Release version (without leading v)")

    bump_parser = subparsers.add_parser("bump-version", help="Bump the repository version")
    bump_parser.add_argument("--part", choices=["major", "minor", "patch"], required=True)

    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    if args.command == "build-site":
        build_site(REPO_ROOT / args.output)
        return 0

    if args.command == "build-archives":
        build_archives(REPO_ROOT / args.output, args.version)
        return 0

    if args.command == "bump-version":
        print(bump_version(args.part))
        return 0

    raise AssertionError("Unhandled command")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
