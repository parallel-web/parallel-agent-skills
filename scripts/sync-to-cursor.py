#!/usr/bin/env python3
"""Sync skills from agent-skills (source of truth) to parallel-cursor-plugin.

Differences between the two repos:
- Cursor SKILL.md frontmatter omits Claude Code-specific fields:
  user-invocable, argument-hint, context, agent
- Cursor skills replace the trailing "## Setup" section (which has full
  install commands inline) with a brief "## If `parallel-cli` is not
  found" stanza that delegates to the cursor /parallel-setup command
- Cursor has 4 skills (search/extract/research/enrichment); setup/status/
  result are slash commands in cursor, not skills, so they are skipped
  by this sync. Skills new to agent-skills (findall, monitor) get both a
  synced SKILL.md AND a freshly-generated command wrapper

Usage:
    python3 scripts/sync-to-cursor.py [--dry-run] [--cursor-repo PATH]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CURSOR_REPO = REPO_ROOT.parent / "parallel-cursor-plugin"

# Skills synced as cursor skills. setup/result/status exist in agent-skills as
# user-invocable skills, but cursor exposes those as commands — skip them.
SKILLS_TO_SYNC = [
    "parallel-web-search",
    "parallel-web-extract",
    "parallel-deep-research",
    "parallel-data-enrichment",
    "parallel-findall",
    "parallel-monitor",
]

# Frontmatter fields that only make sense in Claude Code agent-skills.
CC_ONLY_FIELDS = {"user-invocable", "argument-hint", "context", "agent"}

# Replacement for the agent-skills "## Setup" trailing section.
CURSOR_SETUP_SECTION = """## If `parallel-cli` is not found

If the command fails with "command not found", **stop immediately**. Do NOT search the web yourself, do NOT use any built-in search tools, and do NOT try to answer the query from your own knowledge. Instead, tell the user:

1. `parallel-cli` is not installed
2. Run `/parallel-setup` to install it
3. Then retry their request
"""

# Skill → cursor command wrapper config. Heading-label is the noun the
# command's body uses for $ARGUMENTS ("Query: ...", "URLs: ...", etc.).
COMMAND_WRAPPERS = {
    "parallel-web-search": {
        "command": "parallel-search",
        "title": "Web Search",
        "description": "Web search for a given query (default for most research queries). Usage: /parallel-search <query>",
        "label": "Query",
    },
    "parallel-web-extract": {
        "command": "parallel-extract",
        "title": "URL Content Extraction",
        "description": "URL content extraction for webpages, articles, PDFs. Usage: /parallel-extract <url> [url2] [url3]",
        "label": "URLs",
    },
    "parallel-deep-research": {
        "command": "parallel-research",
        "title": "Deep Research",
        "description": "Exhaustive multi-source research on a topic (slower, use only when explicitly requested). Usage: /parallel-research <topic>",
        "label": "Topic",
    },
    "parallel-data-enrichment": {
        "command": "parallel-enrich",
        "title": "Data Enrichment",
        "description": "Bulk data enrichment with web-sourced fields. Usage: /parallel-enrich <file or entities> with <fields to add>",
        "label": "Request",
    },
    "parallel-findall": {
        "command": "parallel-findall",
        "title": "FindAll: Entity Discovery",
        "description": "Discover entities (companies, people, products) matching a natural-language description. Usage: /parallel-findall <objective>",
        "label": "Objective",
    },
    "parallel-monitor": {
        "command": "parallel-monitor",
        "title": "Web Monitor",
        "description": "Continuously track the web for changes on a recurring cadence. Usage: /parallel-monitor <action>",
        "label": "Request",
    },
}


def transform_frontmatter(fm: str) -> str:
    """Drop CC-only fields. fm is the inner frontmatter, no leading/trailing ---."""
    out: list[str] = []
    skip_continuation = False
    for line in fm.splitlines():
        m = re.match(r"^([a-zA-Z_-]+):", line)
        if m:
            skip_continuation = m.group(1) in CC_ONLY_FIELDS
            if skip_continuation:
                continue
        elif skip_continuation and (line.startswith((" ", "\t")) or line.strip() == ""):
            # multi-line value continuation of a skipped field
            continue
        else:
            skip_continuation = False
        out.append(line)
    return "\n".join(out).rstrip()


def transform_body(body: str) -> str:
    """Replace trailing '## Setup' section with cursor's variant."""
    m = re.search(r"\n## Setup\b", body)
    if m is None:
        return body.rstrip() + "\n"
    return body[: m.start()].rstrip() + "\n\n" + CURSOR_SETUP_SECTION


def transform_skill(content: str) -> str:
    fm_match = re.match(r"^---\n(.*?)\n---\n(.*)", content, re.DOTALL)
    if fm_match is None:
        raise ValueError("no frontmatter found")
    fm, body = fm_match.group(1), fm_match.group(2)
    return f"---\n{transform_frontmatter(fm)}\n---\n\n{transform_body(body).lstrip()}"


def make_command_wrapper(skill: str) -> str:
    cfg = COMMAND_WRAPPERS[skill]
    return (
        f"---\n"
        f"name: {cfg['command']}\n"
        f"description: \"{cfg['description']}\"\n"
        f"---\n"
        f"\n"
        f"# {cfg['title']}\n"
        f"\n"
        f"## {cfg['label']}: $ARGUMENTS\n"
        f"\n"
        f"Use the **{skill}** skill. Follow the skill instructions exactly.\n"
    )


def sync(cursor_repo: Path, dry_run: bool) -> int:
    if not cursor_repo.exists():
        print(f"error: cursor repo not found at {cursor_repo}", file=sys.stderr)
        return 1

    src_skills = REPO_ROOT / "skills"
    dst_skills = cursor_repo / "skills"
    dst_commands = cursor_repo / "commands"
    plugin_json_path = cursor_repo / ".cursor-plugin" / "plugin.json"

    plugin_json = json.loads(plugin_json_path.read_text())
    existing_commands = list(plugin_json.get("commands", []))

    changed: list[str] = []

    for skill in SKILLS_TO_SYNC:
        src = src_skills / skill / "SKILL.md"
        if not src.exists():
            print(f"warn: source missing: {src}", file=sys.stderr)
            continue

        dst = dst_skills / skill / "SKILL.md"
        new_content = transform_skill(src.read_text())
        old_content = dst.read_text() if dst.exists() else None

        if old_content != new_content:
            changed.append(str(dst.relative_to(cursor_repo)))
            if not dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text(new_content)

        # Ensure a command wrapper exists for this skill.
        cmd_cfg = COMMAND_WRAPPERS.get(skill)
        if cmd_cfg is None:
            continue
        cmd_path = dst_commands / f"{cmd_cfg['command']}.md"
        if not cmd_path.exists():
            wrapper = make_command_wrapper(skill)
            changed.append(str(cmd_path.relative_to(cursor_repo)))
            if not dry_run:
                cmd_path.parent.mkdir(parents=True, exist_ok=True)
                cmd_path.write_text(wrapper)

            cmd_rel = f"commands/{cmd_cfg['command']}.md"
            if cmd_rel not in existing_commands:
                existing_commands.append(cmd_rel)

    if existing_commands != plugin_json.get("commands", []):
        plugin_json["commands"] = existing_commands
        changed.append(str(plugin_json_path.relative_to(cursor_repo)))
        if not dry_run:
            plugin_json_path.write_text(json.dumps(plugin_json, indent=2) + "\n")

    if changed:
        verb = "Would update" if dry_run else "Updated"
        print(f"{verb} {len(changed)} file(s) in {cursor_repo.name}:")
        for f in changed:
            print(f"  {f}")
    else:
        print(f"No changes — {cursor_repo.name} is already in sync.")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cursor-repo", type=Path, default=DEFAULT_CURSOR_REPO)
    p.add_argument("--dry-run", action="store_true", help="show what would change without writing")
    args = p.parse_args()
    return sync(args.cursor_repo, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
