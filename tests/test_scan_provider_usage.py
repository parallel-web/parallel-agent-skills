from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[1]
SCANNER_PATH = (
    REPO_ROOT
    / "skills"
    / "migrate-to-parallel-search"
    / "scripts"
    / "scan_provider_usage.py"
)

SPEC = importlib.util.spec_from_file_location("scan_provider_usage", SCANNER_PATH)
assert SPEC and SPEC.loader
SCANNER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SCANNER
SPEC.loader.exec_module(SCANNER)


class ScannerTestCase(unittest.TestCase):
    def scan(self, files: dict[str, str], providers: set[str] | None = None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative, content in files.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            return SCANNER.scan(root, set(), 10_000_000, providers)

    def legacy_rules(self, files: dict[str, str]) -> set[str]:
        return {finding.rule for finding in self.scan(files) if finding.legacy}

    def test_detects_official_python_and_typescript_sdks(self):
        rules = self.legacy_rules(
            {
                "search.py": """
from perplexity import Perplexity
client = Perplexity()
result = client.search.create(query=["one", "two"], search_context_size="high")
""",
                "agent.ts": """
import Perplexity from "@perplexity-ai/perplexity_ai";
const result = await client.responses.create({
  preset: "low",
  tools: [{ type: "web_search" }],
});
""",
            }
        )

        self.assertTrue(
            {
                "perplexity-import-client",
                "perplexity-package",
                "perplexity-search-call",
                "perplexity-answer-call",
                "perplexity-agent-tool",
                "perplexity-request-field",
            }.issubset(rules)
        )

    def test_detects_openai_compatible_sonar_and_agent_clients(self):
        rules = self.legacy_rules(
            {
                "client.py": """
client = OpenAI(
    api_key=os.environ["PERPLEXITY_API_KEY"],
    base_url="https://api.perplexity.ai/v1",
)
sonar = client.chat.completions.create(
    model="sonar-pro",
    messages=messages,
    stream=True,
    response_format={"type": "json_schema"},
)
agent = client.responses.create(input="Research this", tools=[{"type": "fetch_url"}])
"""
            }
        )

        self.assertTrue(
            {
                "perplexity-endpoint",
                "perplexity-api-key",
                "perplexity-model",
                "perplexity-answer-call",
                "perplexity-agent-tool",
                "perplexity-request-field",
            }.issubset(rules)
        )

    def test_detects_bare_sonar_model_only_with_perplexity_context(self):
        contextual = self.legacy_rules(
            {
                "client.ts": """
const baseURL = "https://api.perplexity.ai";
const options = {"model": "sonar"};
"""
            }
        )
        standalone = self.legacy_rules(
            {"models.py": "DEFAULT_MODEL = \"sonar\"\n"}
        )

        self.assertIn("perplexity-sonar-model", contextual)
        self.assertNotIn("perplexity-sonar-model", standalone)

    def test_detects_ecosystem_packages_and_imports(self):
        rules = self.legacy_rules(
            {
                "package.json": """
{"dependencies":{"@ai-sdk/perplexity":"latest","@perplexity-ai/ai-sdk":"latest","@perplexity-ai/mcp-server":"latest"}}
""",
                "requirements.txt": """
langchain-perplexity==1.4.0
llama-index-llms-perplexity==0.5.1
""",
                "app.ts": "import { perplexitySearch } from '@perplexity-ai/ai-sdk';",
                "chain.py": "from langchain_perplexity import ChatPerplexity",
                "llama.py": "from llama_index.llms.perplexity import Perplexity",
            }
        )

        self.assertIn("perplexity-package", rules)
        self.assertIn("perplexity-import-client", rules)

    def test_detects_agent_budgets_sandbox_and_routed_model(self):
        findings = self.scan(
            {
                "agent.py": """from perplexity import Perplexity
max_tokens=10000
tools=[{"type": "sandbox"}, {"type": "function"}]
model="perplexity/sonar"
result={"type": "function_call_output", "call_id": "call_123"}
"""
            }
        )

        self.assertTrue(
            any(
                finding.rule == "perplexity-request-field" and finding.line == 2
                for finding in findings
            )
        )
        self.assertTrue(
            any(
                finding.rule == "perplexity-agent-tool" and finding.line == 3
                for finding in findings
            )
        )
        self.assertTrue(
            any(finding.rule == "perplexity-routed-model" for finding in findings)
        )
        self.assertTrue(
            any(finding.rule == "perplexity-response-field" for finding in findings)
        )

    def test_reports_generic_fields_only_with_perplexity_context(self):
        contextual = self.legacy_rules(
            {
                "search.ts": """
const endpoint = "https://api.perplexity.ai/search";
const request = { query: "AI news", country: "US", stream: false };
const snippet = response.results[0].snippet;
"""
            }
        )
        generic = self.legacy_rules(
            {
                "search.ts": """
const request = { query: "AI news", country: "US", stream: false };
const snippet = response.results[0].snippet;
"""
            }
        )

        self.assertIn("perplexity-request-field", contextual)
        self.assertIn("perplexity-response-field", contextual)
        self.assertNotIn("perplexity-request-field", generic)
        self.assertNotIn("perplexity-response-field", generic)

    def test_fail_on_legacy_returns_one_for_perplexity(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, ".env.example").write_text(
                "EXA_API_KEY=\nPERPLEXITY_API_KEY=\n"
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCANNER_PATH),
                    directory,
                    "--provider",
                    "perplexity",
                    "--fail-on-legacy",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(1, result.returncode)
        self.assertIn("## Perplexity", result.stdout)
        self.assertNotIn("## Exa", result.stdout)

    def test_ignores_sonarqube_generic_openai_and_ordinary_prose(self):
        findings = self.scan(
            {
                "quality.yml": "sonar.projectKey=example\nsonar.host.url=https://sonarqube.example.com\n",
                "openai.py": "client.chat.completions.create(model='gpt-4o', stream=True)\n",
                "notes.md": "Perplexity is sometimes used as a measure of language-model quality.\n",
            }
        )

        self.assertEqual([], findings)


if __name__ == "__main__":
    unittest.main()
