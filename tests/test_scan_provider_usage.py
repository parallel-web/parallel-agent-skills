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
    / "migrate-to-parallel"
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
{"dependencies":{"@ai-sdk/perplexity":"latest","@perplexity-ai/ai-sdk":"latest","@perplexity-ai/mcp-server":"latest","@langchain/perplexity":"latest"}}
""",
                "requirements.txt": """
langchain-perplexity==1.4.0
llama-index-llms-perplexity==0.5.1
""",
                "app.ts": "import { perplexitySearch } from '@perplexity-ai/ai-sdk';",
                "chain.ts": "import { ChatPerplexity } from '@langchain/perplexity';",
                "legacy-chain.ts": "import { ChatPerplexity } from '@langchain/community/chat_models/perplexity';",
                "chain.py": "from langchain_perplexity import ChatPerplexity",
                "llama.py": "from llama_index.llms.perplexity import Perplexity",
            }
        )

        self.assertIn("perplexity-package", rules)
        self.assertIn("perplexity-import-client", rules)

        for package in (
            "@langchain/perplexity",
            "@langchain/community/chat_models/perplexity",
        ):
            with self.subTest(package=package):
                self.assertIn(
                    "perplexity-package",
                    self.legacy_rules({"package.txt": package}),
                )

    def test_detects_people_search_mode_and_sonar_media_contracts(self):
        findings = self.scan(
            {
                "client.py": '''from perplexity import Perplexity
search = client.search.create(query="Stripe engineering leaders", search_type="people")
completion = client.chat.completions.create(
    model="sonar-pro",
    messages=[{"role": "user", "content": [
        {"type": "file_url", "file_url": {"url": encoded_document}},
    ]}],
    media_response={"overrides": {"return_videos": True}},
)
people = {"type": "people_search_results", "results": []}
finance = {"type": "finance_results", "results": []}
'''
            }
        )

        request_lines = {
            finding.line
            for finding in findings
            if finding.rule == "perplexity-request-field"
        }
        self.assertTrue({2, 6, 8}.issubset(request_lines))
        response_lines = {
            finding.line
            for finding in findings
            if finding.rule == "perplexity-response-field"
        }
        self.assertTrue({10, 11}.issubset(response_lines))

    def test_detects_current_and_deprecated_sonar_reasoning_models(self):
        rules = self.legacy_rules(
            {
                "models.py": '''
CURRENT_MODEL = "sonar-reasoning-pro"
DEPRECATED_MODEL = "sonar-reasoning"
'''
            }
        )

        self.assertIn("perplexity-model", rules)

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
                "generic-search.py": "search_type='people'\nfile_url='https://example.com/report.pdf'\n",
                "notes.md": "Perplexity is sometimes used as a measure of language-model quality.\n",
            }
        )

        self.assertEqual([], findings)

    def test_detects_current_firecrawl_python_and_typescript_sdks(self):
        rules = self.legacy_rules(
            {
                "package.json": '{"dependencies":{"firecrawl":"^4.3.0"}}',
                "search.ts": """
import { Firecrawl } from "firecrawl";
const app = new Firecrawl({ apiKey: process.env.FIRECRAWL_API_KEY });
const result = await app.search("parallel web search", {
  limit: 10,
  sources: [{ type: "web" }],
  scrapeOptions: { formats: ["markdown"] },
});
""",
                "scrape.py": """
from firecrawl import Firecrawl, AsyncFirecrawl
app = Firecrawl()
page = app.scrape("https://example.com", formats=["markdown"])
""",
            }
        )

        self.assertTrue(
            {
                "firecrawl-package",
                "firecrawl-import-client",
                "firecrawl-config",
                "firecrawl-surface-method",
                "firecrawl-request-field",
            }.issubset(rules)
        )

    def test_detects_firecrawl_legacy_clients_methods_and_endpoints(self):
        rules = self.legacy_rules(
            {
                "package.json": '{"dependencies":{"@mendable/firecrawl-js":"latest"}}',
                "legacy.ts": """
const endpoint = "https://api.firecrawl.dev/v1";
const app = new FirecrawlApp({ apiKey: process.env.FIRECRAWL_API_KEY });
const page = await app.scrapeUrl(url, { onlyMainContent: true });
const job = await app.asyncCrawlUrl(url, { includePaths: ["/docs/**"] });
""",
                ".env.example": "FIRECRAWL_API_URL=http://localhost:3002\n",
            }
        )

        self.assertTrue(
            {
                "firecrawl-package",
                "firecrawl-import-client",
                "firecrawl-endpoint",
                "firecrawl-config",
                "firecrawl-legacy-method",
                "firecrawl-request-field",
            }.issubset(rules)
        )

    def test_detects_firecrawl_python_distribution_and_langchain_loader(self):
        rules = self.legacy_rules(
            {
                "requirements.txt": "firecrawl-py==4.3.0\n",
                "loader.py": """
from langchain_community.document_loaders import FireCrawlLoader
loader = FireCrawlLoader(api_key=os.environ["FIRECRAWL_API_KEY"], url=url)
""",
            }
        )

        self.assertIn("firecrawl-package", rules)
        self.assertIn("firecrawl-import-client", rules)
        self.assertIn("firecrawl-config", rules)

    def test_detects_firecrawl_mcp_surfaces(self):
        rules = self.legacy_rules(
            {
                "mcp.json": """
{
  "mcpServers": {
    "firecrawl": {
      "url": "https://mcp.firecrawl.dev/v2/mcp",
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"]
    }
  }
}
""",
                "tools.ts": """
const tools = ["firecrawl_search", "firecrawl_scrape", "firecrawl_crawl", "firecrawl_parse", "firecrawl_interact"];
""",
            }
        )

        self.assertTrue(
            {
                "firecrawl-package",
                "firecrawl-endpoint",
                "firecrawl-mcp-tool",
            }.issubset(rules)
        )

    def test_detects_firecrawl_non_search_products_and_contract_fields(self):
        rules = self.legacy_rules(
            {
                "client.py": """
from firecrawl import Firecrawl
app = Firecrawl()
crawl = app.start_crawl(url, include_paths=["/docs/**"], max_discovery_depth=3)
batch = app.start_batch_scrape(urls, zero_data_retention=True)
structured = app.start_extract(urls=urls, prompt=prompt, schema=schema, enable_web_search=True)
agent = app.agent(prompt=prompt, schema=schema, max_credits=500, strict_constrain_to_urls=True, model="spark-1-pro")
session = app.browser(ttl=120, activity_ttl=60, profile={"name": "docs"})
result = {"scrape_id": "id", "credits_used": 4, "live_view_url": "https://example.com", "sources": []}
"""
            }
        )

        self.assertTrue(
            {
                "firecrawl-surface-method",
                "firecrawl-request-field",
                "firecrawl-response-field",
            }.issubset(rules)
        )

    def test_reports_firecrawl_generic_fields_only_with_context(self):
        contextual = self.legacy_rules(
            {
                "scrape.ts": """
const endpoint = "https://api.firecrawl.dev/v2/scrape";
const request = { url, formats: ["markdown"], timeout: 30000 };
const markdown = response.data.markdown;
"""
            }
        )
        generic = self.legacy_rules(
            {
                "scrape.ts": """
const request = { url, formats: ["markdown"], timeout: 30000 };
const markdown = response.data.markdown;
"""
            }
        )

        self.assertIn("firecrawl-request-field", contextual)
        self.assertIn("firecrawl-response-field", contextual)
        self.assertNotIn("firecrawl-request-field", generic)
        self.assertNotIn("firecrawl-response-field", generic)

    def test_detects_firecrawl_response_fields_in_named_fixture(self):
        rules = self.legacy_rules(
            {
                "fixtures/firecrawl-response.json": """
{"success":true,"data":{"markdown":"# Page","metadata":{}},"creditsUsed":1}
"""
            }
        )

        self.assertIn("firecrawl-response-field", rules)

    def test_fail_on_legacy_returns_one_for_firecrawl(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, ".env.example").write_text("FIRECRAWL_API_KEY=\n")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCANNER_PATH),
                    directory,
                    "--provider",
                    "firecrawl",
                    "--fail-on-legacy",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(1, result.returncode)
        self.assertIn("## Firecrawl", result.stdout)
        self.assertNotIn("## Perplexity", result.stdout)

    def test_ignores_ordinary_firecrawl_prose_and_generic_web_code(self):
        findings = self.scan(
            {
                "notes.md": "Firecrawl is one of several web-data vendors.\n",
                "generic.py": """
request = {"url": url, "formats": ["markdown"], "timeout": 30000}
result = client.scrape(url)
""",
            }
        )

        self.assertEqual([], findings)


if __name__ == "__main__":
    unittest.main()
