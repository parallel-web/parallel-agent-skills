# Exa migration reference

Verified against Exa Public API OpenAPI 2.0.0 and official SDK docs on 2026-07-14. Treat mappings as semantic decisions, not mechanical renames.

## Detect the integration

- Python package/import: `exa-py`, `from exa_py import Exa` or `AsyncExa`.
- TypeScript package/import: `exa-js`, `import Exa from "exa-js"`.
- REST: `https://api.exa.ai/search`; auth commonly uses `x-api-key` and may also use bearer auth.
- Common wrappers include `@exalabs/ai-sdk`, LangChain/LlamaIndex/CrewAI tools, Exa MCP, OpenAI-compatible clients pointed at Exa, and handwritten model-tool handlers.

Current direct SDK calls use `exa.search(...)`; older code may use `search_and_contents`, `searchAndContents`, or separate contents calls. Inspect the installed version and lockfile before editing.

Important: the current direct Exa SDKs add a 10,000-character text request when `search(...)` is called without an explicit `contents` value. Raw REST `/search` does not have that SDK default. Trace whether callers depend on implicit full text before replacing a seemingly bare SDK call.

## Request mapping

| Exa behavior | Parallel migration |
| --- | --- |
| `query` | Preserve the web-research goal in `objective`; use concise keyword probes for `search_queries`. Do not duplicate a full prompt only because it fits a length limit. |
| `type: "instant"` | Consider `mode: "turbo"` only for a latency-first path. Verify result quality and output shape. |
| `type: "fast"` | Start the evaluation with `mode: "basic"`, not Turbo: Exa describes this as high-quality reduced-latency search. |
| `type: "auto"` | No direct equivalent. Choose Basic for a foreground latency SLO or Advanced for quality-first/background work, then evaluate. |
| omitted `type` | Exa defaults to Auto while Parallel defaults to Advanced. Make the intended mode explicit or test the accepted behavior change. |
| `type: "deep-lite"`, `"deep"`, or `"deep-reasoning"` used only for ranked results | Treat Search API `mode: "advanced"` as a candidate baseline, not an equivalent. Verify latency and result shape. |
| `outputSchema`, streaming synthesis, or code reading `output` | Use the Task API for asynchronous multi-step or structured research, or Chat/the existing model for an interactive grounded completion. Do not map synthesized output to Search API results. |
| `systemPrompt` | Classify its purpose. Move soft source/freshness preferences into `objective`; keep hard source restrictions in source policy; preserve output instructions in the chosen synthesis layer. Implement and test duplicate suppression or other agent behavior at that boundary; Search has no one-field equivalent. Do not route every `systemPrompt` to Chat or Task. |
| Exa `/answer`, `stream_answer`, or `streamAnswer` | Use the Chat API for an interactive answer or the Task API for deeper/structured research; preserve citations and streaming behavior explicitly. |
| `numResults` / `num_results` | `advanced_settings.max_results`. Exa permits up to 100; do not assume Parallel accepts the same upper range without validation. Current public defaults are 10 in both APIs, but inspect SDK-wrapper behavior before relying on omission. |
| `includeDomains` / `excludeDomains` | Apply the domain normalization rules in [parallel-search.md](parallel-search.md); do not copy strings mechanically. Exa permits up to 1,200 entries per list and supports schemes, path-qualified filters, and subdomain wildcards that are not one-to-one with Parallel source policy. If both lists are set, reconcile their effective legacy behavior and send one Parallel list. Never truncate or broaden scope silently. |
| `startPublishedDate` | Convert the ISO timestamp to `advanced_settings.source_policy.after_date` (`YYYY-MM-DD`) only if loss of time-of-day precision is acceptable. Exa says “after”; Parallel's boundary is inclusive, so test the boundary. |
| `endPublishedDate` | No direct Search API equivalent. Use an explicit post-filter only if missing `publish_date` values are handled safely, or choose another research path. |
| deprecated `startCrawlDate` / `endCrawlDate` | No direct equivalent. These filter when Exa discovered a link, not when it was published, and Parallel results do not expose a crawl date for post-filtering. Remove only if the behavior is confirmed unused; otherwise stop for an explicit design decision. |
| `userLocation` | Use `advanced_settings.location` only when geo-targeting was a product requirement. If the old value was a soft preference, state it in `objective` and evaluate; inspect warnings for unsupported locations. |
| `additionalQueries` | Exa uses these only with deep-search types. First verify whether a non-deep legacy call ignored or rejected them. When they were effective, Exa can send the main query plus up to 10 variants while Parallel accepts at most 5 total. Select/rewrite variants with an explicit strategy, split into multiple calls with an explicit merge/dedup/order contract, or get an approved behavior change. Never silently keep the first few. |
| `category: "company"` or `"people"` | Use Entity Search or FindAll only when the application needs entity candidates or enrichment. If it still consumes page URLs, highlights, or text, keep Search and express the category as an objective hint, then evaluate. |
| Other `category` values | Express the content/source intent in `objective`; verify results. |
| `contents.highlights` | Parallel Search API `excerpts` is the closest behavior. If Exa supplied `highlights.query`, fold that focus into the objective/query design and test per-page relevance. |
| `contents.text` | Use Search API excerpts only when relevant snippets satisfy the consumer. Otherwise Extract every result whose text the old caller observes, preserve URL association and partial errors, and select a subset only if the old caller already did. Text rendering, section, and HTML controls need an application-layer normalization or an explicit behavior change. |
| deprecated combined `context` | Treat it as a consumed full-content contract. Use excerpts only if the caller accepts snippets; otherwise use Extract and rebuild the application-owned combined context deliberately. |
| `contents.summary` | This is a per-page contract. Extract each legacy-consumed URL, synthesize one summary per URL, and preserve association/partial errors. Treat a separate Chat or Task answer as request-level synthesis, not as a replacement. Search synthesizes neither form. |
| `contents.text.maxCharacters` or highlight budget | Use `advanced_settings.excerpt_settings.max_chars_per_result` only for excerpt budgets; use Extract API settings for true page content. |
| `contents.maxAgeHours` | Treat `0` (fresh), `-1` (always cache), omission (fallback fetch), and stale-cache failure as separate behaviors. Convert positive hours to `advanced_settings.fetch_policy.max_age_seconds` only after deciding stale-fallback behavior; set `disable_cache_fallback: true` when the old path must fail rather than return stale content. Parallel's documented 600-second minimum is not an exact match for Exa `0`. |
| `contents.livecrawl`, subpages, extras, or code blocks | No single Search API field equivalent. Route known URLs through the Extract API or redesign the feature explicitly. |
| deprecated `find_similar` / `findSimilar` variants | No direct URL-similarity switch. Redesign as a natural-language Search API objective and verify the new semantics. |
| `moderation` or `compliance: "hipaa"` | No verified one-field Search API equivalent. Treat this as a security/compliance blocker until the requirement has an approved Parallel design. |

## Response mapping

| Exa field/behavior | Parallel handling |
| --- | --- |
| `results[].url` | `results[].url` |
| `results[].title` | `results[].title`; handle null |
| `results[].publishedDate` | `results[].publish_date`; handle null and the date-only format |
| `results[].highlights` | `results[].excerpts` |
| `results[].text` | Join excerpts only if snippets meet the contract; otherwise use Search API then Extract API |
| `results[].highlightScores` | No equivalent. Results are already ranked. Remove display/threshold logic or replace it with a tested application rule. |
| `results[].summary` | No Search API equivalent; preserve the per-URL contract by extracting and synthesizing one summary per result |
| `results[].author`, `id`, `image`, `favicon`, `subpages`, `entities`, extras | No general Search API equivalent. Remove the consumer or implement an explicit alternative. |
| `requestId` | `search_id` is the closest request identifier; do not conflate it with `session_id`. |
| `costDollars` | Parallel `usage` reports SKU counts, not dollars. Update telemetry semantics. |
| `output.content` / `output.grounding` | Task API/Chat API result contract, not Search API |

Exa `contents.summary` is a per-page summary, while top-level `output.content` is request-level synthesis. Preserve that distinction when choosing the Extract API plus a model, the Chat API, or the Task API.

Rewrite exception handling too: current Exa Python commonly raises `ValueError` for HTTP failures, while TypeScript throws `ExaError`. Do not leave catches keyed to those provider-specific classes after replacing the client. Inspect partial per-URL failures when migrating Contents to Extract.

Do not fabricate a numeric relevance score. If the application sorts by score, preserve the returned order. If it applies score thresholds, build a representative eval and redesign the threshold behavior.

## Official sources

- [Exa OpenAPI source-of-truth page](https://exa.ai/docs/reference/openapi-spec)
- [Exa raw OpenAPI](https://exa.ai/docs/exa-spec.json)
- [Search API reference for coding agents](https://exa.ai/docs/reference/search-api-guide-for-coding-agents)
- [Search endpoint](https://exa.ai/docs/reference/search)
- [Domain path filter support](https://exa.ai/docs/changelog/domain-path-filter)
- [Python SDK](https://exa.ai/docs/sdks/python-sdk)
- [JavaScript SDK](https://exa.ai/docs/sdks/javascript-sdk)
