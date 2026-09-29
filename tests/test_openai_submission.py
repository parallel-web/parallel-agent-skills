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
            "https://parallel.ai/customer-terms",
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

    def test_submission_excludes_local_credentials_and_cli_skills(self):
        packaged_skills = {
            path.name for path in (PLUGIN_ROOT / "skills").iterdir() if path.is_dir()
        }
        self.assertEqual({"parallel-web-research"}, packaged_skills)

        forbidden_patterns = (
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
        for path in sorted(PLUGIN_ROOT.rglob("*")):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            for pattern in forbidden_patterns:
                with self.subTest(path=path, pattern=pattern):
                    self.assertNotIn(pattern, text)

    def test_review_case_counts_match_portal_requirements(self):
        cases = (SUBMISSION_ROOT / "review" / "test-cases.md").read_text(
            encoding="utf-8"
        )

        positive_section, negative_section = cases.split("## Negative cases", 1)
        self.assertEqual(5, len(re.findall(r"(?m)^### \d+\.", positive_section)))
        self.assertEqual(3, len(re.findall(r"(?m)^### \d+\.", negative_section)))


if __name__ == "__main__":
    unittest.main()
