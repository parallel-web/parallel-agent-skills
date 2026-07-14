# Tavily migration reference

Verified against Tavily Search and Extract OpenAPI 1.0.0 and official SDK docs on 2026-07-14. Treat mappings as semantic decisions, not mechanical renames.

## Detect the integration

- Python package/import: `tavily-python`, `from tavily import TavilyClient` or `AsyncTavilyClient`.
- TypeScript package/import: `@tavily/core`, `import { tavily } from "@tavily/core"`.
- REST: `https://api.tavily.com/search`; keyed auth uses `Authorization: Bearer`. Current keyless paths may use `X-Tavily-Access-Mode: keyless`.
- Common wrappers include `langchain-tavily`, `@langchain/tavily`, community Tavily tools, `@tavily/ai-sdk`, LlamaIndex/CrewAI tools, Tavily MCP, and model-tool handlers.

Inspect the installed SDK version and wrapper contract. Python option names are snake_case; the TypeScript SDK generally exposes camelCase and returns camelCase fields.

Tavily's `results[].content` is not stable across depths: basic/ultra-fast return one NLP summary per URL, while advanced/fast are documented as returning relevant chunks joined with `[...]`. Verify the application's content assumptions rather than mapping the field name alone.

## Request mapping

| Tavily behavior | Parallel migration |
| --- | --- |
| `query` | Preserve the web-research goal in `objective`; use concise keyword probes for `search_queries`. Do not duplicate a full prompt only because it fits a length limit. |
| `search_depth: "ultra-fast"` | Consider `mode: "turbo"` for a latency-first path, then evaluate the excerpt contract. |
| `search_depth: "fast"` | Start the evaluation with `mode: "basic"`: Tavily describes Fast as lower latency with good relevance, not minimum latency. Use Turbo only if the quality eval passes. |
| `search_depth: "basic"` | Do not equate names mechanically. Choose Basic or Advanced from the application's latency and quality contract; Tavily Basic returns page summaries while Parallel returns excerpts. |
| `search_depth: "advanced"` | Treat `mode: "advanced"` as the candidate baseline and verify output shape, latency, and cost. |
| omitted `search_depth` | Tavily defaults to Basic while Parallel defaults to Advanced. Make the intended mode explicit or test the accepted behavior change. |
| `max_results` / `maxResults` | `advanced_settings.max_results`. Tavily allows 0–20; preserve a deliberate zero-result short circuit locally rather than assuming the API accepts 0. If Tavily omitted this field, set Parallel to 5 to preserve Tavily's documented default rather than silently taking Parallel's default of 10. |
| `chunks_per_source` / `chunksPerSource` | No count-for-count equivalent. Use `excerpt_settings.max_chars_per_result` only when the consumer has a character budget, then verify output shape. |
| Search `include_domains` / `exclude_domains` | Apply the domain normalization rules in [parallel-search.md](parallel-search.md); do not copy strings mechanically. Tavily Search permits up to 300 includes and 150 excludes and documents path-qualified and wildcard forms that are not one-to-one with Parallel source policy. If both lists are set, reconcile their effective legacy behavior and send one Parallel list. Never truncate or broaden scope silently. |
| `start_date` | `advanced_settings.source_policy.after_date` (`YYYY-MM-DD`) only with an approved semantic change: Tavily filters on publish **or last-updated** date, while Parallel filters on publish date only and is inclusive. |
| `time_range` | Compute an `after_date` at request time only with an approved semantic change: Tavily's rolling window considers publish or last-updated date, while Parallel considers publish date. Test day/week/month/year boundaries and timezone choice. |
| legacy `days` | Normalize to a current date control before migration; current core SDKs may still emit it although it is absent from the REST OpenAPI. |
| `end_date` | No direct Search API equivalent. A post-filter cannot recover pages omitted by retrieval and must handle missing `publish_date`; use it only with an approved behavior change. |
| `country` | Tavily boosts a country while Parallel geo-targets. Use `advanced_settings.location` only for a hard geographic requirement; otherwise express a soft preference in `objective` and evaluate. |
| `topic: "news"` or `"finance"` | Treat this as a retrieval hint, not an exact route. Describe the desired coverage and freshness in `objective`, then evaluate; stop if the old vertical/source behavior was contractual. |
| `include_answer` | Use the Chat API or the application's existing model over Search API excerpts; use the Task API for deeper synthesis. |
| `include_raw_content` | Use Search then Extract, reusing `session_id`. If the old consumer read raw content for every result, Extract every returned URL within the 20-URL limit or obtain an approved selection policy; do not silently reduce coverage to a subset. |
| `include_images`, image descriptions, or favicon | No general Search API equivalent. Treat required image behavior as a migration gap. |
| `auto_parameters` | Replace with explicit application-owned policy. Inspect production request/response samples to learn which depth/topic settings it selected, then choose and evaluate a Parallel policy; do not replace it with one guessed mode. |
| `exact_match: true` | No verified exact switch. Treat exact matching as a required filter: validate each returned source against the quoted phrase(s) with an application-owned extraction/normalization rule, or obtain an approved behavior change. Quoting a Parallel query does not recreate the filter. |
| `safe_search` | No verified one-field Search API equivalent. Treat a required safety filter as a blocker until it has an approved Parallel design. |
| `include_usage` | Parallel may return `usage` as SKU counts; update telemetry rather than assuming Tavily credit semantics. |
| standalone Tavily Extract (`extract`, `/extract`) | Use Parallel Extract. Tavily defines `query` as user intent for reranking chunks: map natural-language intent to `objective`, or an already keyword-shaped probe to `search_queries`. Do not copy the same value into both fields mechanically. Set `advanced_settings.full_content` when the caller needs page bodies, and handle separate `results` and `errors` arrays. Extraction depth, format, timeout, images, and favicon controls need explicit validation or a gap decision. |
| Tavily Research (`research`, `/research`) | Use the Task API when the caller needs asynchronous multi-step research. Preserve polling/webhook/SSE behavior, structured output, citations, terminal errors, and timeout budgets. Tavily Research `include_domains` is a soft preference, not a hard allow-list; preserve it as a research preference or explicitly approve hardening it. Map its hard `exclude_domains` only after testing host/subdomain behavior. |
| Tavily Crawl or Map | No verified one-call Parallel Search equivalent. Stop for an explicit design; do not silently reduce a site traversal to one Search or Extract call. |

## Response mapping

| Tavily field/behavior | Parallel handling |
| --- | --- |
| `results[].url` | `results[].url` |
| `results[].title` | `results[].title`; handle null |
| `results[].published_date` / `publishedDate` | `results[].publish_date`; Tavily commonly returns it for news results, and Parallel may return null |
| `results[].content` | Join `results[].excerpts` only when concise evidence satisfies the contract |
| `results[].score` | No equivalent. Preserve result order; redesign score thresholds with an eval. |
| `results[].raw_content` / `rawContent` | Search API then Extract API |
| `results[].images`, top-level `images`, `favicon` | No general Search API equivalent |
| top-level `answer` | Chat API, Task API, or the application's existing model |
| `query` | Preserve the original request in application state; the Search API does not echo it |
| `response_time` / `responseTime` | Measure end-to-end latency in the application if required |
| `request_id` / `requestId` | `search_id` is the closest request identifier; keep `session_id` separate |
| `auto_parameters` | Remove or replace with application-owned request metadata |
| legacy `follow_up_questions` / `followUpQuestions` | No current Search API equivalent; remove the consumer or own follow-up generation in the application |
| `usage.credits` | Parallel `usage` is a list of SKU counts, not Tavily credits |

Do not fabricate a numeric relevance score. If the application sorts by score, preserve the returned order. If it applies score thresholds, build a representative eval and redesign the threshold behavior.

Do not infer that a Tavily path is unused merely because `TAVILY_API_KEY` is absent: current SDKs can enter a rate-limited keyless mode.

Rewrite exception handling rather than only imports. Tavily Python exposes provider-specific request, auth, usage-limit, forbidden, and timeout exceptions; the JavaScript SDK generally throws `Error` plus special keyless-limit errors. Preserve retry and `Retry-After` behavior without retaining Tavily exception classes.

## Official sources

- [Tavily Search endpoint](https://docs.tavily.com/documentation/api-reference/endpoint/search)
- [Tavily Extract endpoint](https://docs.tavily.com/documentation/api-reference/endpoint/extract)
- [Tavily Search best practices](https://docs.tavily.com/documentation/best-practices/best-practices-search)
- [Tavily OpenAPI](https://docs.tavily.com/documentation/api-reference/openapi.json)
- [Python quickstart](https://docs.tavily.com/sdk/python/quick-start)
- [Python SDK reference](https://docs.tavily.com/sdk/python/reference)
- [JavaScript quickstart](https://docs.tavily.com/sdk/javascript/quick-start)
- [JavaScript SDK reference](https://docs.tavily.com/sdk/javascript/reference)
