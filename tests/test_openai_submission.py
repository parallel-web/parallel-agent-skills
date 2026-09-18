from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SUBMISSION_ROOT = REPO_ROOT / "submission" / "openai"
PLUGIN_ROOT = SUBMISSION_ROOT / "parallel"
MANIFEST = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
SKILL_ROOT = PLUGIN_ROOT / "skills" / "parallel-web-research"


class OpenAISubmissionTestCase(unittest.TestCase):
    def test_manifest_is_portal_ready(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

        self.assertEqual(PLUGIN_ROOT.name, manifest["name"])
        self.assertRegex(manifest["version"], r"^\d+\.\d+\.\d+$")
        self.assertEqual("./skills/", manifest["skills"])
        self.assertNotIn("mcpServers", manifest)
        self.assertLessEqual(len(manifest["interface"]["displayName"]), 30)
        self.assertLessEqual(len(manifest["interface"]["shortDescription"]), 30)
        self.assertLessEqual(len(manifest["interface"]["defaultPrompt"]), 3)
        self.assertEqual(
            "https://parallel.ai/privacy-policy",
            manifest["interface"]["privacyPolicyURL"],
        )
        self.assertEqual(
            "https://parallel.ai/terms-of-service",
            manifest["interface"]["termsOfServiceURL"],
        )
        for prompt in manifest["interface"]["defaultPrompt"]:
            self.assertLessEqual(len(prompt), 128)

    def test_skill_is_focused_and_mcp_backed(self):
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        openai_yaml = (SKILL_ROOT / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )

        self.assertRegex(skill_text, r"(?m)^name: parallel-web-research$")
        self.assertNotIn("TODO", skill_text)
        self.assertIn("web_search", skill_text)
        self.assertIn("web_fetch", skill_text)
        self.assertIn('value: "parallel-search"', openai_yaml)
        self.assertIn('url: "https://search.parallel.ai/mcp"', openai_yaml)

    def test_review_case_counts_match_portal_requirements(self):
        cases = (SUBMISSION_ROOT / "review" / "test-cases.md").read_text(
            encoding="utf-8"
        )

        positive_section, negative_section = cases.split("## Negative cases", 1)
        self.assertEqual(5, len(re.findall(r"(?m)^### \d+\.", positive_section)))
        self.assertEqual(3, len(re.findall(r"(?m)^### \d+\.", negative_section)))


if __name__ == "__main__":
    unittest.main()
