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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def validate_source() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("name") != PLUGIN_ROOT.name:
        raise SystemExit("plugin folder and manifest name must match")
    if not (PLUGIN_ROOT / "skills" / "parallel-web-research" / "SKILL.md").is_file():
        raise SystemExit("parallel-web-research skill is missing")
    if (PLUGIN_ROOT / ".mcp.json").exists() or "mcpServers" in manifest:
        raise SystemExit("portal package must not rely on bundled MCP configuration")


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
