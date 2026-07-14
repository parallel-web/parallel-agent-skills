#!/usr/bin/env python3
"""Inventory legacy search-provider surfaces without exposing secret values."""

from __future__ import annotations

import argparse
from bisect import bisect_right
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Optional


SKILL_ROOT = Path(__file__).resolve().parent.parent

PROVIDERS = ("exa", "tavily", "perplexity", "firecrawl")


IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".next",
    ".nuxt",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".tox",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "target",
    "vendor",
}

TEXT_SUFFIXES = {
    ".py", ".pyi", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    ".json", ".jsonc", ".toml", ".yaml", ".yml", ".md", ".mdx",
    ".txt", ".ini", ".cfg", ".conf", ".sh", ".bash", ".zsh", ".fish",
    ".env", ".go", ".rs", ".java", ".kt", ".kts", ".rb", ".php", ".cs",
    ".xml", ".gradle", ".swift", ".lock", ".snap",
}

SPECIAL_TEXT_NAMES = {
    "Dockerfile", "Makefile", "Procfile", "Pipfile", "Pipfile.lock",
    "poetry.lock", "uv.lock", "requirements.txt", "package-lock.json",
    "pnpm-lock.yaml", "yarn.lock", "bun.lock", "bun.lockb",
    "requirements.in", "pom.xml", "build.gradle", "build.gradle.kts",
    "go.mod", "go.sum", "Cargo.toml", "Cargo.lock", "Gemfile",
    "Gemfile.lock", "composer.json", "composer.lock", "Package.swift",
    "Package.resolved",
}

MANIFEST_NAMES = {
    "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
    "bun.lock", "bun.lockb", "pyproject.toml", "poetry.lock", "uv.lock",
    "Pipfile", "Pipfile.lock", "requirements.txt", "requirements.in",
    "pom.xml", "build.gradle", "build.gradle.kts", "go.mod", "go.sum",
    "Cargo.toml", "Cargo.lock", "Gemfile", "Gemfile.lock", "composer.json",
    "composer.lock", "Package.swift", "Package.resolved",
}

LIMITATIONS = [
    "Generated and dependency directories are skipped by default.",
    "Binary, unreadable, oversized, and symlinked files are skipped.",
    "Provider-neutral downstream consumers require manual data-flow tracing.",
]

FIXTURE_MARKERS = {
    "fixture", "fixtures", "__fixtures__", "mock", "mocks",
    "snapshot", "snapshots", "__snapshots__", "testdata",
}


@dataclass(frozen=True)
class Rule:
    provider: str
    kind: str
    name: str
    pattern: re.Pattern[str]
    legacy: bool = True
    contextual: bool = False


def rule(
    provider: str,
    kind: str,
    name: str,
    pattern: str,
    *,
    legacy: bool = True,
    contextual: bool = False,
) -> Rule:
    return Rule(provider, kind, name, re.compile(pattern, re.IGNORECASE), legacy, contextual)


RULES = [
    rule("exa", "reference", "exa-provider-name", r"(?<![\w-])exa(?![\w-])", legacy=False),
    rule("exa", "dependency", "exa-package", r"(?<![\w-])(exa-py|exa_py|exa-js|@exalabs/ai-sdk|@ai-sdk/exa|@langchain/exa|langchain[-_]exa|exa-mcp-server|mcp-server-exa|exa-mcp)(?![\w-])"),
    rule("exa", "runtime", "exa-import-client", r"\b(from\s+exa_py\s+import|AsyncExa\b|ExaSearchRetriever\b|Exa\s*\(|new\s+Exa\s*\(|import\s+Exa\s+from\s+[\"']exa-js[\"']|require\s*\(\s*[\"']exa-js[\"']\s*\))"),
    rule("exa", "runtime", "exa-search-call", r"\bexa\s*\??\.\s*search\s*(?:\?\.)?\s*\("),
    rule("exa", "runtime", "exa-endpoint", r"\b(?:https?://)?(?:api|mcp)\.exa\.ai\b"),
    rule("exa", "config", "exa-api-key", r"\bEXA_API_KEY\b"),
    rule("exa", "runtime", "exa-legacy-method", r"\b(search_and_contents|searchAndContents|get_contents|getContents|find_similar|findSimilar|find_similar_and_contents|findSimilarAndContents|stream_answer|streamAnswer|stream_search|streamSearch|web_search_exa|web_fetch_exa|web_search_advanced_exa)\b"),
    rule("exa", "runtime", "exa-operation", r"\.(?:answer|research|stream_answer|streamAnswer|stream_search|streamSearch)\s*\(", contextual=True),
    rule("exa", "request-contract", "exa-request-field", r"\b(numResults|num_results|startPublishedDate|start_published_date|endPublishedDate|end_published_date|startCrawlDate|start_crawl_date|endCrawlDate|end_crawl_date|userLocation|user_location|additionalQueries|additional_queries|outputSchema|output_schema|systemPrompt|system_prompt|includeDomains|include_domains|excludeDomains|exclude_domains|maxAgeHours|max_age_hours|livecrawl|subpages|subpageTarget|subpage_target)\b|[\"']?(?:type|category|contents|context|moderation|compliance|stream)[\"']?\s*[:=]", contextual=True),
    rule("exa", "response-contract", "exa-response-field", r"\b(publishedDate|highlightScores|highlights|costDollars|resolvedSearchType|searchTime|autoDate)\b|(?:\.|\[['\"])(?:text|summary|output|author|image|favicon|score)(?:\b|['\"]\])|[\"'](?:text|summary|output|author|image|favicon|score)[\"']\s*:", contextual=True),
    rule("tavily", "reference", "tavily-provider-name", r"(?<![\w-])tavily(?![\w-])", legacy=False),
    rule("tavily", "dependency", "tavily-package", r"(?<![\w-])(tavily-python|@tavily/core|@tavily/ai-sdk|@langchain/tavily|langchain[-_]tavily|llama-index-tools-tavily-research|tavily-mcp|mcp-server-tavily)(?![\w-])"),
    rule("tavily", "runtime", "tavily-import-client", r"\b(from\s+tavily\s+import|TavilyClient\b|AsyncTavilyClient\b|TavilySearchResults\b|TavilySearchAPIRetriever\b|TavilySearch\b|TavilyToolSpec\b|TavilySearchTool\b|tavilySearch\b|tavily\s*\()"),
    rule("tavily", "runtime", "tavily-search-call", r"\btavily\s*\??\.\s*search\s*(?:\?\.)?\s*\("),
    rule("tavily", "runtime", "tavily-endpoint", r"\b(?:https?://)?(?:api|mcp)\.tavily\.com\b"),
    rule("tavily", "config", "tavily-keyless-mode", r"\bX-Tavily-Access-Mode\b|\btavily-search\b"),
    rule("tavily", "config", "tavily-api-key", r"\bTAVILY_API_KEY\b"),
    rule("tavily", "runtime", "tavily-legacy-method", r"\b(qna_search|get_search_context|searchQNA|searchContext)\s*\("),
    rule("tavily", "runtime", "tavily-surface-method", r"\.(?:extract|crawl|map|research)\s*\(", contextual=True),
    rule("tavily", "request-contract", "tavily-request-field", r"\b(search_depth|searchDepth|extract_depth|extractDepth|chunks_per_source|chunksPerSource|max_results|maxResults|include_answer|includeAnswer|include_raw_content|includeRawContent|include_images|includeImages|include_image_descriptions|includeImageDescriptions|include_domains|includeDomains|exclude_domains|excludeDomains|include_favicon|includeFavicon|include_usage|includeUsage|auto_parameters|autoParameters|exact_match|exactMatch|safe_search|safeSearch|time_range|timeRange|start_date|startDate|end_date|endDate|days)\b|[\"']?(?:topic|country|format)[\"']?\s*[:=]", contextual=True),
    rule("tavily", "response-contract", "tavily-response-field", r"\b(raw_content|rawContent|response_time|responseTime|request_id|requestId|follow_up_questions|followUpQuestions|published_date|publishedDate)\b|(?:\.|\[['\"])(?:score|content|answer|images|favicon)(?:\b|['\"]\])|[\"'](?:score|content|answer|images|favicon)[\"']\s*:", contextual=True),
    rule("perplexity", "dependency", "perplexity-package", r"(?<![\w-])(perplexityai|@perplexity-ai/perplexity_ai|@ai-sdk/perplexity|@perplexity-ai/ai-sdk|@perplexity-ai/mcp-server|@langchain/perplexity|@langchain/community/chat_models/perplexity|langchain[-_]perplexity|llama-index-llms-perplexity|llama_index_llms_perplexity)(?![\w-])"),
    rule("perplexity", "runtime", "perplexity-import-client", r"\b(from\s+perplexity\s+import\s+(?:Async)?Perplexity\b|from\s+llama_index\.llms\.perplexity\s+import\s+Perplexity\b|ChatPerplexity\b|import\s+Perplexity\s+from\s+[\"']@perplexity-ai/perplexity_ai[\"']|require\s*\(\s*[\"']@perplexity-ai/perplexity_ai[\"']\s*\)|perplexitySearch\s*\()"),
    rule("perplexity", "runtime", "perplexity-endpoint", r"\b(?:https?://)?api\.perplexity\.ai\b"),
    rule("perplexity", "config", "perplexity-api-key", r"\b(?:PERPLEXITY_API_KEY|PPLX_API_KEY)\b"),
    rule("perplexity", "runtime", "perplexity-model", r"(?<![\w-])sonar-(?:pro|deep-research|reasoning(?:-pro)?)(?![\w-])"),
    rule("perplexity", "runtime", "perplexity-routed-model", r"(?<![\w-])perplexity/sonar(?![\w-])"),
    rule("perplexity", "runtime", "perplexity-sonar-model", r"[\"']?model[\"']?\s*[:=]\s*[\"']sonar[\"']", contextual=True),
    rule("perplexity", "runtime", "perplexity-search-call", r"\.search\.create\s*\(", contextual=True),
    rule("perplexity", "runtime", "perplexity-answer-call", r"\.(?:chat\.completions|responses)\.create\s*\(", contextual=True),
    rule("perplexity", "runtime", "perplexity-agent-tool", r"(?:[\"']type[\"']|\btype)\s*:\s*[\"'](?:web_search|sandbox|fetch_url|people_search|finance_search|mcp|function)[\"']", contextual=True),
    rule("perplexity", "request-contract", "perplexity-request-field", r"\b(max_results|search_context_size|max_tokens|max_tokens_per_page|max_urls|max_steps|max_tool_calls|max_output_tokens|parallel_tool_calls|previous_response_id|search_language_filter|search_domain_filter|search_after_date_filter|search_before_date_filter|last_updated_after_filter|last_updated_before_filter|search_recency_filter|search_type|return_images|return_related_questions|return_videos|image_domain_filter|image_format_filter|image_url|file_url|pdf_url|media_response|search_mode|response_format|web_search_options)\b|[\"']?(?:query|country|stream|tools|tool_choice|preset|instructions|reasoning)[\"']?\s*[:=]", contextual=True),
    rule("perplexity", "response-contract", "perplexity-response-field", r"\b(search_results|people_search_results|finance_results|related_questions|citation_tokens|num_search_queries|reasoning_tokens|last_updated|server_time|output_text|function_call_output|tool_calls_details|call_id|annotations)\b|(?:\.|\[['\"])(?:snippet|citations|images|usage)(?:\b|['\"]\])|[\"'](?:snippet|citations|images|usage)[\"']\s*:", contextual=True),
    rule("firecrawl", "dependency", "firecrawl-package", r"(?<![\w-])(@mendable/firecrawl-js|firecrawl-py|firecrawl-mcp|@mendableai/mcp-server-firecrawl|(?:mendableai|firecrawl)/firecrawl-go)(?![\w-])|[\"']firecrawl[\"']\s*:|(?<![\w-])firecrawl@\d|(?:^|\n)\s*firecrawl(?:\[[^\]]+\])?\s*(?:[<>=~!]|$)"),
    rule("firecrawl", "runtime", "firecrawl-import-client", r"\b(from\s+firecrawl(?:\.(?:v1|v2|types|v2\.types))?\s+import\s+|FirecrawlApp\b|AsyncFirecrawl\b|FireCrawlLoader\b|import\s*\{[^}]*\bFirecrawl\b[^}]*\}\s*from\s*[\"']firecrawl[\"']|require\s*\(\s*[\"'](?:firecrawl|@mendable/firecrawl-js)[\"']\s*\))"),
    rule("firecrawl", "runtime", "firecrawl-endpoint", r"\b(?:https?://)?(?:api|mcp)\.firecrawl\.dev\b"),
    rule("firecrawl", "config", "firecrawl-config", r"\b(?:FIRECRAWL_API_KEY|FIRECRAWL_API_URL)\b"),
    # Firecrawl adds MCP tools over time. Match their lowercase tool namespace
    # without misclassifying uppercase FIRECRAWL_* environment variables.
    rule("firecrawl", "runtime", "firecrawl-mcp-tool", r"(?-i:\bfirecrawl_[a-z][a-z0-9_]*\b)"),
    rule("firecrawl", "runtime", "firecrawl-legacy-method", r"\b(scrapeUrl|scrape_url|crawlUrl|crawl_url|asyncCrawlUrl|async_crawl_url|mapUrl|map_url|batchScrapeUrls|batch_scrape_urls|asyncBatchScrapeUrls|async_batch_scrape_urls|checkCrawlStatus|check_crawl_status|checkCrawlErrors|check_crawl_errors|checkBatchScrapeStatus|check_batch_scrape_status|checkBatchScrapeErrors|check_batch_scrape_errors|asyncExtract|async_extract|generateLLMsText|generate_llms_text|checkGenerateLLMsTextStatus|get_generate_llms_text_status|crawlUrlAndWatch|crawl_url_and_watch|batchScrapeUrlsAndWatch|batch_scrape_urls_and_watch)\b"),
    rule("firecrawl", "runtime", "firecrawl-surface-method", r"\.(?:scrape|search|map|crawl|startCrawl|start_crawl|getCrawlStatus|get_crawl_status|getCrawlErrors|get_crawl_errors|getActiveCrawls|get_active_crawls|cancelCrawl|cancel_crawl|batchScrape|batch_scrape|startBatchScrape|start_batch_scrape|getBatchScrapeStatus|get_batch_scrape_status|getBatchScrapeErrors|get_batch_scrape_errors|cancelBatchScrape|cancel_batch_scrape|extract|startExtract|start_extract|getExtractStatus|get_extract_status|agent|startAgent|start_agent|getAgentStatus|get_agent_status|cancelAgent|cancel_agent|parse|interact|stopInteraction|stop_interaction|scrapeExecute|scrape_execute|stopInteractiveBrowser|stop_interactive_browser|deleteScrapeBrowser|delete_scrape_browser|browser|browserExecute|browser_execute|deleteBrowser|delete_browser|listBrowsers|list_browsers|createMonitor|create_monitor|listMonitors|list_monitors|getMonitor|get_monitor|updateMonitor|update_monitor|deleteMonitor|delete_monitor|runMonitor|run_monitor|listMonitorChecks|list_monitor_checks|getMonitorCheck|get_monitor_check|searchPapers|search_papers|getPaper|inspect_paper|read_paper|similarPapers|related_papers|searchGithub|search_github|watcher)\s*\(", contextual=True),
    rule("firecrawl", "request-contract", "firecrawl-request-field", r"\b(scrapeOptions|scrape_options|includeDomains|include_domains|excludeDomains|exclude_domains|ignoreInvalidURLs|ignore_invalid_urls|onlyMainContent|only_main_content|maxAge|max_age|minAge|min_age|storeInCache|store_in_cache|zeroDataRetention|zero_data_retention|threatProtection|threat_protection|riskScoreThreshold|risk_score_threshold|includePaths|include_paths|excludePaths|exclude_paths|maxDiscoveryDepth|max_discovery_depth|ignoreSitemap|ignore_sitemap|includeSubdomains|include_subdomains|allowExternalLinks|allow_external_links|crawlEntireDomain|crawl_entire_domain|maxConcurrency|max_concurrency|enableWebSearch|enable_web_search|showSources|show_sources|maxCredits|max_credits|strictConstrainToURLs|strict_constrain_to_urls|activityTtl|activity_ttl|skipTlsVerification|skip_tls_verification|waitFor|wait_for|blockAds|block_ads|removeBase64Images|remove_base64_images|changeTracking|change_tracking|retentionDays|retention_days|judgeEnabled|judge_enabled|saveChanges|save_changes)\b|[\"']?(?:query|url|urls|limit|sources|categories|authors|intent|targets|schedule|notification|goal|tbs|location|country|timeout|formats|actions|headers|cookies|proxy|mobile|profile|prompt|schema|model|webhook|parsers|enterprise|anon|zdr)[\"']?\s*[:=]", contextual=True),
    rule("firecrawl", "response-contract", "firecrawl-response-field", r"\b(rawHtml|raw_html|scrapeId|scrape_id|creditsUsed|credits_used|expiresAt|expires_at|completedAt|completed_at|totalPages|total_pages|concurrencyLimited|concurrency_limited|concurrencyQueueDurationMs|concurrency_queue_duration_ms|liveViewUrl|live_view_url|interactiveLiveViewUrl|interactive_live_view_url|cdpUrl|cdp_url|changeTracking|change_tracking|paperId|paper_id|primaryId|primary_id|nextRunAt|next_run_at|lastRunAt|last_run_at|estimatedCreditsPerMonth|estimated_credits_per_month|currentCheckId|current_check_id)\b|(?:\.|\[['\"])(?:markdown|summary|json|html|metadata|links|images|actions|branding|product|menu|warning|next|data|success|status|result|sources|output|stdout)(?:\b|['\"]\])|[\"'](?:markdown|summary|json|html|metadata|links|images|actions|branding|product|menu|warning|next|data|success|status|result|sources|output|stdout)[\"']\s*:", contextual=True),
]


@dataclass(frozen=True)
class Finding:
    provider: str
    kind: str
    rule: str
    path: str
    line: int
    legacy: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="Repository root (default: current directory)")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--provider", action="append", choices=PROVIDERS, default=[], help="Scan only this provider; repeatable")
    parser.add_argument("--exclude", action="append", default=[], help="Extra directory name or root-relative path to exclude; repeatable")
    parser.add_argument("--max-file-bytes", type=int, default=10_000_000, help="Skip larger files (default: 10000000)")
    parser.add_argument("--fail-on-legacy", action="store_true", help="Exit 1 when any legacy finding remains")
    return parser.parse_args()


def is_text_candidate(path: Path) -> bool:
    name = path.name
    if name in SPECIAL_TEXT_NAMES or name in MANIFEST_NAMES:
        return True
    if name.startswith(".env"):
        return True
    if name.startswith("requirements") and name.endswith(".txt"):
        return True
    return path.suffix.lower() in TEXT_SUFFIXES


def is_within(path: Path, directory: Path) -> bool:
    try:
        path.resolve().relative_to(directory.resolve())
    except (OSError, ValueError):
        return False
    return True


def should_ignore(path: Path, root: Path, extra_excludes: set[str]) -> bool:
    # A project-scoped installation lives under the repository being scanned.
    # Ignore this skill's own migration references without ignoring other skills,
    # which may contain real provider integrations that also need migration.
    if is_within(path, SKILL_ROOT):
        return True
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True
    relative_text = relative.as_posix()
    for part in relative.parts[:-1]:
        if part in IGNORED_DIRS or part in extra_excludes:
            return True
    return any(relative_text == item or relative_text.startswith(item.rstrip("/") + "/") for item in extra_excludes)


def iter_files(root: Path, extra_excludes: set[str], max_bytes: int) -> Iterable[Path]:
    for current, dirs, files in os.walk(root):
        current_path = Path(current)
        dirs[:] = sorted(
            d
            for d in dirs
            if d not in IGNORED_DIRS
            and d not in extra_excludes
            and not (current_path / d).is_symlink()
        )
        for filename in sorted(files):
            path = current_path / filename
            if (
                path.is_symlink()
                or should_ignore(path, root, extra_excludes)
                or not is_text_candidate(path)
            ):
                continue
            try:
                if path.stat().st_size > max_bytes:
                    continue
            except OSError:
                continue
            yield path


def read_text(path: Path) -> Optional[str]:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in data:
        return None
    return data.decode("utf-8", errors="replace")


def path_provider_hints(relative: Path) -> set[str]:
    """Activate response-field checks for clearly named fixtures and snapshots."""
    lowered_parts = {part.lower() for part in relative.parts[:-1]}
    stem = relative.stem.lower()
    fixture_context = bool(lowered_parts & FIXTURE_MARKERS) or any(
        marker in stem for marker in FIXTURE_MARKERS
    )
    response_context = any(marker in stem for marker in ("response", "result"))
    if not (fixture_context or response_context):
        return set()
    path_tokens = lowered_parts | {stem}
    return {
        provider
        for provider in PROVIDERS
        if any(
            re.search(rf"(?<![a-z0-9]){provider}(?![a-z0-9])", token)
            for token in path_tokens
        )
    }


def scan_file(
    path: Path,
    root: Path,
    providers: Optional[set[str]] = None,
) -> list[Finding]:
    text = read_text(path)
    if text is None:
        return []

    findings: list[Finding] = []
    relative_path = path.relative_to(root)
    relative = relative_path.as_posix()
    # Informational provider names alone must not activate generic field rules.
    # Require a strong legacy marker or a provider-named fixture/snapshot.
    direct_providers = {
        candidate.provider
        for candidate in RULES
        if not candidate.contextual
        and candidate.legacy
        and candidate.pattern.search(text)
    } | path_provider_hints(relative_path)
    line_starts = [0] + [index + 1 for index, character in enumerate(text) if character == "\n"]

    for candidate in RULES:
        if providers is not None and candidate.provider not in providers:
            continue
        if candidate.contextual and candidate.provider not in direct_providers:
            continue
        for match in candidate.pattern.finditer(text):
            line_number = bisect_right(line_starts, match.start())
            findings.append(
                Finding(
                    provider=candidate.provider,
                    kind=candidate.kind,
                    rule=candidate.name,
                    path=relative,
                    line=line_number,
                    legacy=candidate.legacy,
                )
            )
    return findings


def scan(
    root: Path,
    extra_excludes: set[str],
    max_bytes: int,
    providers: Optional[set[str]] = None,
) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_files(root, extra_excludes, max_bytes):
        findings.extend(scan_file(path, root, providers))
    return sorted(findings, key=lambda item: (item.provider, item.path, item.line, item.rule))


def counts(findings: list[Finding]) -> dict[str, object]:
    providers = sorted({item.provider for item in findings})
    by_provider = {provider: sum(item.provider == provider for item in findings) for provider in providers}
    by_kind = {
        kind: sum(item.kind == kind for item in findings)
        for kind in sorted({item.kind for item in findings})
    }
    return {
        "total": len(findings),
        "legacy": sum(item.legacy for item in findings),
        "providers": by_provider,
        "kinds": by_kind,
    }


def render_markdown(root: Path, findings: list[Finding]) -> str:
    summary = counts(findings)
    lines = [
        "# Legacy provider migration inventory",
        "",
        f"Root: `{root}`",
        f"Legacy findings: **{summary['legacy']}**",
        "",
    ]
    if not findings:
        lines.extend(["No legacy provider migration signatures found in scanned files.", ""])

    for provider in PROVIDERS:
        provider_findings = [item for item in findings if item.provider == provider]
        if not provider_findings:
            continue
        lines.extend([f"## {provider.title()}", ""])
        for item in provider_findings:
            lines.append(f"- `{item.path}:{item.line}` — **{item.kind}** / `{item.rule}`")
        lines.append("")
    lines.extend(["Coverage limits:", ""])
    lines.extend(f"- {item}" for item in LIMITATIONS)
    lines.extend([
        "",
        "Review response-contract findings manually; generic field names are reported only in files with a direct provider signature.",
        "Use `--fail-on-legacy` only for a provider boundary intended for full removal.",
    ])
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"error: repository root is not a directory: {root}", file=sys.stderr)
        return 2
    providers = set(args.provider) if args.provider else None
    findings = scan(root, set(args.exclude), args.max_file_bytes, providers)
    if args.format == "json":
        payload = {
            "root": str(root),
            "summary": counts(findings),
            "findings": [asdict(item) for item in findings],
            "limitations": LIMITATIONS,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_markdown(root, findings))
    if args.fail_on_legacy and any(item.legacy for item in findings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
