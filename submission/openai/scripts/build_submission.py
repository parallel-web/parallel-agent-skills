#!/usr/bin/env python3
"""Build the OpenAI plugin submission ZIP deterministically."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


SUBMISSION_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = SUBMISSION_ROOT / "parallel"
MANIFEST = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
EXPECTED_SKILLS = {"parallel-web-research"}
FORBIDDEN_CREDENTIAL_PATTERNS = (
    "${user_config.",
    "PARALLEL_API_KEY",
    "PERPLEXITY_API_KEY",
    "FIRECRAWL_API_KEY",
    "EXA_API_KEY",
    "TAVILY_API_KEY",
    "os.environ",
    "process.env",
    "credential-store",
    "keyring",
    "parallel-cli",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def validate_source() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("name") != PLUGIN_ROOT.name:
        raise SystemExit("plugin folder and manifest name must match")
    skills_root = PLUGIN_ROOT / "skills"
    packaged_skills = {
        path.name for path in skills_root.iterdir() if path.is_dir()
    }
    if packaged_skills != EXPECTED_SKILLS:
        raise SystemExit(
            f"unexpected packaged skills: {sorted(packaged_skills)}; "
            f"expected {sorted(EXPECTED_SKILLS)}"
        )
    if not (skills_root / "parallel-web-research" / "SKILL.md").is_file():
        raise SystemExit("parallel-web-research skill is missing")
    if (PLUGIN_ROOT / ".mcp.json").exists() or "mcpServers" in manifest:
        raise SystemExit("portal package must not rely on bundled MCP configuration")

    for path in sorted(PLUGIN_ROOT.rglob("*")):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_CREDENTIAL_PATTERNS:
            if pattern in text:
                relative = path.relative_to(PLUGIN_ROOT)
                raise SystemExit(
                    f"credential access pattern {pattern!r} found in {relative}"
                )


def build(output: Path) -> None:
    validate_source()
    output.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(path for path in PLUGIN_ROOT.rglob("*") if path.is_file())
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            relative = Path(PLUGIN_ROOT.name) / path.relative_to(PLUGIN_ROOT)
            info = ZipInfo(relative.as_posix(), date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


def main() -> None:
    args = parse_args()
    build(args.output.resolve())
    print(args.output.resolve())


if __name__ == "__main__":
    main()
