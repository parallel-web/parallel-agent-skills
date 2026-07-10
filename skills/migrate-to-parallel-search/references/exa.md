# Exa migration reference

Verified against Exa Public API OpenAPI 2.0.0 and official SDK docs on 2026-07-10. Treat mappings as semantic decisions, not mechanical renames.

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
| `query` | Preserve full intent in `objective`; supply at least one concise `search_queries` item. Use 2–3 when the caller or tool schema can provide them. |
| `type: "instant"` or `"fast"` | Start with `mode: "turbo"`; verify latency and quality. |
| `type: "auto"` | Start with `mode: "basic"`; verify against representative queries. |
| `type: "deep-lite"`, `"deep"`, or `"deep-reasoning"` used only for ranked results | Start with Search API `mode: "advanced"`. |
| A deep type, `outputSchema`, `systemPrompt`, streaming synthesis, or code reading `output` | Use the Task API for asynchronous multi-step/structured research, or the Chat API/existing model for an interactive grounded completion. Do not map synthesized output to Search API results. |
| Exa `/answer`, `stream_answer`, or `streamAnswer` | Use the Chat API for an interactive answer or the Task API for deeper/structured research; preserve citations and streaming behavior explicitly. |
| `numResults` / `num_results` | `advanced_settings.max_results`. Exa permits up to 100; do not assume Parallel accepts the same upper range without live validation. |
| `includeDomains` / `excludeDomains` | `advanced_settings.source_policy.include_domains` / `exclude_domains`. Parallel's combined limit is 200 versus Exa's larger lists. Reject or redesign oversized runtime lists; never truncate silently. |
| `startPublishedDate` | Convert the ISO timestamp to `advanced_settings.source_policy.after_date` (`YYYY-MM-DD`) only if loss of time-of-day precision is acceptable. Exa says “after”; Parallel's boundary is inclusive, so test the boundary. |
| `endPublishedDate` | No direct Search API equivalent. Use an explicit post-filter only if missing `publish_date` values are handled safely, or choose another research path. |
| deprecated `startCrawlDate` / `endCrawlDate` | No direct equivalent. These filter when Exa discovered a link, not when it was published, and Parallel results do not expose a crawl date for post-filtering. Remove only if the behavior is confirmed unused; otherwise stop for an explicit design decision. |
| `userLocation` | Lowercase the ISO alpha-2 code into `advanced_settings.location`; inspect warnings for unsupported locations. |
| `additionalQueries` | Fold useful variants into the required `search_queries` array, respecting Parallel's maximum of 5. |
| `category: "company"` or `"people"` | Prefer Entity Search or the FindAll API, based on speed versus verification needs. |
| Other `category` values | Express the content/source intent in `objective`; verify results. |
| `contents.highlights` | Parallel Search API `excerpts` is the closest behavior. |
| `contents.text` | Use Search API excerpts only when relevant snippets satisfy the consumer. Use the Extract API for full content from selected URLs. |
| deprecated combined `context` | Treat it as a consumed full-content contract. Use excerpts only if the caller accepts snippets; otherwise use Extract and rebuild the application-owned combined context deliberately. |
| `contents.summary` | Use the Chat API, Task API, or the application's existing model. The Search API does not synthesize an answer or per-page summary. |
| `contents.text.maxCharacters` or highlight budget | Use `advanced_settings.excerpt_settings.max_chars_per_result` only for excerpt budgets; use Extract API settings for true page content. |
| `contents.maxAgeHours` | Convert positive hours to `advanced_settings.fetch_policy.max_age_seconds`. Exa `0` means always live crawl, while Parallel documents a 600-second minimum; this is not exact. |
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
| `results[].summary` | No Search API equivalent; synthesize through the Chat API, Task API, or the existing model |
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
- [Python SDK](https://exa.ai/docs/sdks/python-sdk)
- [JavaScript SDK](https://exa.ai/docs/sdks/javascript-sdk)
