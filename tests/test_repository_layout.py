from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"
PROJECT_SKILLS_ROOT = REPO_ROOT / ".agents" / "skills"
MCP_CONFIG = REPO_ROOT / ".mcp.json"
CLAUDE_PLUGIN_MANIFEST = REPO_ROOT / ".claude-plugin" / "plugin.json"
CLAUDE_MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"
CODEX_PLUGIN_MANIFEST = REPO_ROOT / ".codex-plugin" / "plugin.json"


class RepositoryLayoutTestCase(unittest.TestCase):
    def test_skill_directory_matches_frontmatter_name(self):
        for skill_directory in sorted(SKILLS_ROOT.iterdir()):
            skill_file = skill_directory / "SKILL.md"
            if not skill_file.is_file():
                continue

            match = re.search(
                r"^name:\s*([^\s]+)\s*$",
                skill_file.read_text(encoding="utf-8"),
                re.MULTILINE,
            )
            with self.subTest(skill=skill_directory.name):
                self.assertIsNotNone(match, f"{skill_file} has no frontmatter name")
                self.assertEqual(skill_directory.name, match.group(1))

    def test_project_skill_links_resolve_to_matching_skill_directories(self):
        for link in sorted(PROJECT_SKILLS_ROOT.iterdir()):
            expected_target = SKILLS_ROOT / link.name
            with self.subTest(link=link.name):
                self.assertTrue(link.is_symlink(), f"expected a skill link: {link}")
                self.assertTrue(link.exists(), f"broken skill link: {link}")
                self.assertEqual(expected_target.resolve(), link.resolve())
                self.assertTrue((link / "SKILL.md").is_file())

    def test_migration_skill_is_project_discoverable(self):
        link = PROJECT_SKILLS_ROOT / "migrate-to-parallel"

        self.assertTrue(link.is_symlink())
        self.assertTrue(link.exists())

    def test_memory_skill_is_project_discoverable(self):
        link = PROJECT_SKILLS_ROOT / "parallel-memory"

        self.assertTrue(link.is_symlink())
        self.assertTrue(link.exists())

    def test_parallel_search_setup_is_project_discoverable(self):
        link = PROJECT_SKILLS_ROOT / "parallel-search-setup"

        self.assertTrue(link.is_symlink())
        self.assertTrue(link.exists())

    def test_plugin_manifests_bundle_anonymous_search_mcp(self):
        mcp_config = json.loads(MCP_CONFIG.read_text(encoding="utf-8"))
        server = mcp_config["mcpServers"]["parallel-search"]

        self.assertEqual("http", server["type"])
        self.assertEqual("https://search.parallel.ai/mcp", server["url"])
        self.assertNotIn("headers", server)

        for manifest_path in (CLAUDE_PLUGIN_MANIFEST, CODEX_PLUGIN_MANIFEST):
            with self.subTest(manifest=manifest_path):
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                self.assertEqual("./.mcp.json", manifest["mcpServers"])

    def test_claude_marketplace_uses_productivity_category(self):
        marketplace = json.loads(CLAUDE_MARKETPLACE.read_text(encoding="utf-8"))

        self.assertEqual("productivity", marketplace["plugins"][0]["category"])

    def test_codex_manifest_uses_live_policy_urls(self):
        manifest = json.loads(CODEX_PLUGIN_MANIFEST.read_text(encoding="utf-8"))
        interface = manifest["interface"]

        self.assertEqual(
            "https://parallel.ai/privacy-policy", interface["privacyPolicyURL"]
        )
        self.assertEqual(
            "https://parallel.ai/customer-terms", interface["termsOfServiceURL"]
        )


if __name__ == "__main__":
    unittest.main()
