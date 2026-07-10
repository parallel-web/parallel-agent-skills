# Tavily migration reference

Verified against Tavily Search and Extract OpenAPI 1.0.0 and official SDK docs on 2026-07-10. Treat mappings as semantic decisions, not mechanical renames.

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
| `query` | Preserve full intent in `objective`; supply at least one concise `search_queries` item. Use 2–3 when the caller or tool schema can provide them. |
| `search_depth: "fast"` or `"ultra-fast"` | Start with `mode: "turbo"`; verify latency and quality. |
| `search_depth: "basic"` | Start with `mode: "basic"`. |
| `search_depth: "advanced"` | Start with `mode: "advanced"`. |
| `max_results` / `maxResults` | `advanced_settings.max_results`. Tavily allows 0–20; preserve a deliberate zero-result short circuit locally rather than assuming the API accepts 0. |
| `chunks_per_source` / `chunksPerSource` | No count-for-count equivalent. Use `excerpt_settings.max_chars_per_result` only when the consumer has a character budget, then verify output shape. |
| `include_domains` / `exclude_domains` | `advanced_settings.source_policy.include_domains` / `exclude_domains`. Parallel's two lists have a combined limit of 200; Tavily permits larger lists. Never truncate silently. |
| `start_date` | `advanced_settings.source_policy.after_date` (`YYYY-MM-DD`). Tavily says “after” while Parallel's boundary is inclusive; test the boundary. |
| `time_range` | Compute an `after_date` at request time only if the application's rolling-window semantics tolerate date granularity. Test day/week/month/year boundaries and timezone choice. |
| legacy `days` | Normalize to a current date control before migration; current core SDKs may still emit it although it is absent from the REST OpenAPI. |
| `end_date` | No direct Search API equivalent. Use an explicit post-filter only if missing dates are handled safely, or choose another research path. |
| `country` | Convert the country name to an ISO alpha-2 code for `advanced_settings.location`. Tavily boosts a country; Parallel geo-targets and supports a subset, so verify behavior and warnings. |
| `topic: "news"` or `"finance"` | State the domain and freshness requirement in `objective`; do not assume an exact routing equivalent. |
| `include_answer` | Use the Chat API or the application's existing model over Search API excerpts; use the Task API for deeper synthesis. |
| `include_raw_content` | Use Search API then Extract API for selected result URLs, reusing `session_id`. If the consumer only needs concise evidence, excerpts may replace the old `content` path. |
| `include_images`, image descriptions, or favicon | No general Search API equivalent. Treat required image behavior as a migration gap. |
| `auto_parameters` | Replace with explicit application-owned request construction and a chosen starting mode. |
| `exact_match` | No verified exact switch. Preserve quoted terms in search queries/objective and add post-validation only if the exact-match guarantee is required. |
| `safe_search` | No verified one-field Search API equivalent. Treat a required safety filter as a blocker until it has an approved Parallel design. |
| `include_usage` | Parallel may return `usage` as SKU counts; update telemetry rather than assuming Tavily credit semantics. |
| standalone Tavily Extract (`extract`, `/extract`) | Use Parallel Extract. Set `advanced_settings.full_content` when the caller needs page bodies; it is off by default. Preserve focused-query behavior with `objective`/`search_queries`, and handle separate `results` and `errors` arrays. |
| Tavily Research (`research`, `/research`) | Use the Task API when the caller needs asynchronous multi-step research. Preserve polling/webhook/SSE behavior, structured output, citations, terminal errors, and timeout budgets. |
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
- [Tavily OpenAPI](https://docs.tavily.com/documentation/api-reference/openapi.json)
- [Python quickstart](https://docs.tavily.com/sdk/python/quick-start)
- [Python SDK reference](https://docs.tavily.com/sdk/python/reference)
- [JavaScript quickstart](https://docs.tavily.com/sdk/javascript/quick-start)
- [JavaScript SDK reference](https://docs.tavily.com/sdk/javascript/reference)
