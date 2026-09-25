from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("cursor_sync", REPO_ROOT / "scripts/sync-to-cursor.py")
assert SPEC is not None and SPEC.loader is not None
SYNC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNC)


class CursorSyncTestCase(unittest.TestCase):
    def test_cursor_routing_does_not_assume_a_bundled_mcp(self):
        for name in ("parallel-web-search", "parallel-web-extract"):
            source = (REPO_ROOT / "skills" / name / "SKILL.md").read_text()
            generated = SYNC.transform_skill(source)
            description = next(line for line in generated.splitlines() if line.startswith("description:"))
            with self.subTest(skill=name):
                self.assertNotIn("MCP", description)
                self.assertIn("CLI", description)
                if name == "parallel-web-search":
                    self.assertIn("default", description.lower())
                    self.assertIn("explicitly", description)
            self.assertIn("bundled Parallel Search MCP", source)

    def test_setup_replacement_retains_distinct_failure_paths(self):
        source = "---\nname: example\ndescription: Example\n---\n\n# Example\n\nKeep workflow.\n\n## Setup\n\nSource-client install instructions.\n"
        generated = SYNC.transform_skill(source)
        self.assertIn("Keep workflow.", generated)
        self.assertNotIn("Source-client install instructions", generated)
        self.assertIn("command not found", generated)
        self.assertIn("/parallel-setup", generated)
        self.assertIn("No such command", generated)
        self.assertIn("installation method", generated)
        self.assertIn("authentication", generated.lower())
        self.assertIn("authenticated", generated)
        self.assertIn("403", generated)

    def test_platform_fields_are_stripped_without_dropping_other_metadata(self):
        source = "---\nname: example\ndescription: Example\ncontext:\n  mode: fork\nagent: parallel:parallel-subagent\nargument-hint: <query>\nuser-invocable: true\ncompatibility: Requires CLI\nallowed-tools: Bash(parallel-cli:*)\nmetadata:\n  author: parallel\n---\n\n# Example\n"
        generated = SYNC.transform_skill(source)
        self.assertNotIn("mode: fork", generated)
        for key in SYNC.CC_ONLY_FIELDS:
            self.assertNotIn(f"\n{key}:", generated)
        self.assertIn("compatibility: Requires CLI", generated)
        self.assertIn("allowed-tools: Bash(parallel-cli:*)", generated)
        self.assertIn("metadata:\n  author: parallel", generated)

    def test_sync_is_repeatable_and_preserves_existing_wrappers_and_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / ".cursor-plugin").mkdir()
            (target / "commands").mkdir()
            wrapper = target / "commands/parallel-search.md"
            wrapper.write_text("Keep the existing reviewed command.\n")
            manifest = {"name": "parallel", "version": "0.2.0", "skills": "./skills/", "rules": "./rules/", "commands": ["commands/parallel-setup.md", "commands/parallel-search.md"]}
            manifest_path = target / ".cursor-plugin/plugin.json"
            manifest_path.write_text(json.dumps(manifest))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(0, SYNC.sync(target, dry_run=True))
            self.assertFalse((target / "skills").exists())
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(0, SYNC.sync(target, dry_run=False))
            files_before = {p.relative_to(target): p.read_bytes() for p in target.rglob("*") if p.is_file()}
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(0, SYNC.sync(target, dry_run=False))
            self.assertIn("No changes", output.getvalue())
            self.assertEqual(files_before, {p.relative_to(target): p.read_bytes() for p in target.rglob("*") if p.is_file()})
            self.assertEqual("Keep the existing reviewed command.\n", wrapper.read_text())
            synced = json.loads(manifest_path.read_text())
            self.assertEqual("0.2.0", synced["version"])
            self.assertEqual(set(SYNC.SKILLS_TO_SYNC), {p.name for p in (target / "skills").iterdir()})
            self.assertNotIn("mcpServers", synced)
            self.assertEqual(set(manifest["commands"] + [f"commands/{cfg['command']}.md" for cfg in SYNC.COMMAND_WRAPPERS.values()]), set(synced["commands"]))


if __name__ == "__main__":
    unittest.main()
