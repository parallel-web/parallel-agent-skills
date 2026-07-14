# Perplexity migration reference

Verified against the official Perplexity and Parallel documentation on 2026-07-14. Perplexity exposes several products behind similar SDK clients; identify the product before replacing a call.

## Contents

- [Detect the product boundary](#detect-the-product-boundary)
- [Choose the Parallel product](#choose-the-parallel-product)
- [Migrate Search API requests](#migrate-search-api-requests)
- [Migrate Sonar and Agent API calls](#migrate-sonar-and-agent-api-calls)
- [Migrate response consumers](#migrate-response-consumers)
- [Stop conditions](#stop-conditions)
- [Official sources](#official-sources)

## Detect the product boundary

Classify every call and trace its consumers before editing:

- **Search API:** `POST /search` or `client.search.create(...)`; returns ranked result objects.
- **Sonar:** `POST /v1/sonar`, Sonar model IDs, or an OpenAI-compatible chat-completions client; returns a generated answer with web citations. Sonar is in maintenance mode but remains a real migration surface.
- **Agent API:** `POST /v1/agent`, the `/v1/responses` alias, or `client.responses.create(...)`; combines frontier-model routing with optional tools and presets.
- **Wrappers:** `ChatPerplexity`, Vercel AI SDK providers/tools, and MCP servers can expose Search, Sonar, or Agent behavior. Inspect the wrapper version and tool output rather than inferring behavior from its package name.
- **Embeddings:** embedding calls are not web search. Stop and keep them outside this migration.

The Agent API can own more than retrieval. Inventory models, presets, instructions, conversation state, tool choice, step limits, structured output, streaming, and every configured tool. Do not remove non-search capabilities while replacing `web_search`.

## Choose the Parallel product

| Perplexity behavior | Parallel route | Required decision |
| --- | --- | --- |
| Search API ranked results | Search API | Preserve result count, filters, grouped-query behavior, and response fields. |
| Sonar or Agent cited answer | Chat API or the application's existing synthesis step over Search excerpts | Preserve streaming, structured output, conversation history, citations, and answer ownership. |
| Sonar deep research, reasoning workflows, or asynchronous research | Task API | Preserve asynchronous lifecycle, progress, output schema, and research basis. Do not map a model name directly to a Parallel mode. |
| Agent `web_search` | Search API | Move model-selected query planning into the model tool schema or preserve the existing explicit planner. |
| Agent `fetch_url` | Extract API | Preserve URL limits, full-content needs, partial failures, and ordering contracts. |
| Agent `people_search` | Entity Search for synchronous lookup; consider FindAll or Task for broader discovery | Verify the old result contract and whether the caller expects people-only structured fields. |
| Agent `finance_search` | No direct structured equivalent in Parallel Search | Stop for a product decision; ordinary web search is not a substitute for structured market data. |
| Agent model routing, sandbox, MCP, or existing custom functions | Keep as a separate integration boundary | Replace only the web capability unless the user explicitly requests a broader redesign. |
| Embeddings | No Parallel Search equivalent | Stop and leave the embedding provider intact or choose another embedding product explicitly. |

## Migrate Search API requests

### Query semantics

Perplexity accepts one query string or up to five queries. A multi-query request executes each query independently and returns result groups in the same order. Parallel `search_queries` are multiple retrieval probes for one objective and return one jointly ranked result list.

- If the caller consumes per-query groups, make one Parallel Search call per Perplexity query and preserve the group key, order, error handling, concurrency, and result limit.
- If the caller intentionally merges all groups into one research task, use one Parallel request only after defining and testing the new joint-ranking and deduplication behavior.
- If a Perplexity query is already a concise keyword probe, it can be a one-query compatibility path. If it is a question or full prompt, keep it as `objective` and obtain keyword-shaped `search_queries` from the existing caller or planning step.
- Do not assume an Agent or Sonar prompt exposes the searches Perplexity generated internally. Change the model-tool contract or retain an explicit planner; do not add an invisible LLM call.

### Request field mapping

| Perplexity Search field | Parallel treatment |
| --- | --- |
| `query` | Classify into `objective` and `search_queries` using the rules above. Preserve grouped calls when an array's groups are consumed. |
| `max_results` | Set `advanced_settings.max_results` only after validating the Parallel range and preserving whether the limit applies per query or to the combined task. Perplexity defaults to 10 and permits 1–20. |
| `search_context_size` | Choose `max_chars_total` and optionally `max_chars_per_result` from the caller's actual context budget and an eval. The named levels are not Parallel modes. |
| `max_tokens`, `max_tokens_per_page` | Recalculate as character budgets. Never copy token counts into character fields. Preserve truncation behavior with representative long pages. |
| `country` | Consider `advanced_settings.location` when the ISO country is supported. Inspect Parallel warnings and preserve a fallback for unsupported locations. |
| `search_language_filter` | No direct Parallel filter. Use Basic or Advanced for multilingual search, then stop or implement an approved language-validation/filtering policy when language is a hard requirement. |
| `search_domain_filter` | Split unsigned allow entries from `-`-prefixed deny entries and apply the canonical domain-normalization rules in `parallel-search.md`. Do not mix allow and deny policies, broaden a path rule to an apex domain, or assume suffix/TLD syntax is identical. |
| `search_after_date_filter` | `source_policy.after_date` is only a candidate for a publication lower bound. Normalize the date and account for Parallel's inclusive boundary. |
| `search_before_date_filter` | No Parallel Search upper publication-date bound. Stop or implement an approved application-side filter with its recall tradeoff. |
| `last_updated_after_filter`, `last_updated_before_filter` | No direct last-modified filter. Do not relabel these as publication dates. |
| `search_recency_filter` | Materialize a publication lower bound only if publication-date semantics satisfy the product requirement. Relative last-updated behavior is not preserved. |

Perplexity domain rules support signed deny entries, paths, bare TLDs, and at most 20 entries. Parallel accepts a larger domain policy but has different normalization and path behavior. Preserve the set of allowed URLs, not the old strings.

## Migrate Sonar and Agent API calls

### Sonar

Sonar returns an answer, not merely search hits. Choose exactly one synthesis owner:

- Keep an existing application model and feed it Parallel Search excerpts.
- Use Parallel Chat for an interactive grounded answer.
- Use Task for deep, reasoning-heavy, asynchronous, or structured research whose latency contract permits it.

Preserve `messages`, system instructions, streaming, `response_format`, citation display, `search_results`, images, related questions, and usage reporting deliberately. Perplexity generation controls and `web_search_options` do not map by name to Parallel controls. Re-evaluate temperature/token parameters against the chosen answer product; Parallel Chat documents several OpenAI-compatible parameters as ignored.

Do not translate `sonar`, `sonar-pro`, `sonar-reasoning-*`, or `sonar-deep-research` directly into `turbo`, `basic`, or `advanced`. Model tiers combine retrieval and generation behavior, while Parallel Search modes configure retrieval.

Sonar `search_mode` values such as `academic` and `sec` are vertical search behavior, not Parallel mode equivalents. Express a soft source preference in `objective`, use an equivalent hard domain policy when one exists, or stop if the specialized corpus is required.

### Agent API

An Agent request may combine a routed model with multiple tools. Perplexity built-in tools are hosted capabilities, not callbacks that can be pointed at another URL. Replacing one requires one of these designs:

- Keep the Agent API as the model router, replace each hosted search tool with a custom `type: "function"` tool, execute the corresponding Parallel API in the application, and return a `function_call_output` with the same `call_id`.
- Move the model and tool loop into an existing application-owned agent harness, then register Parallel-backed tools there.

In either design, separate the contracts:

1. Preserve the model and non-search tools in their current owner unless broader migration is requested.
2. Replace `web_search` with an application-executed Search tool whose input requires a self-contained `objective` and exactly three diverse keyword `search_queries`.
3. Replace `fetch_url` with an application-executed Extract tool only when its input and result preserve URL limits, full content, and per-URL errors.
4. Replace `people_search` only after defining the application-owned person input and result types, then route it to Entity Search, FindAll, or Task as appropriate.
5. Stop on `finance_search` or embeddings.

Perplexity tool budgets such as `max_tokens` and `max_tokens_per_page` are token-based. Parallel Search and Extract excerpt budgets are character-based. Recalculate and test them; do not preserve the same integers.

When retaining Agent API routing, implement the complete custom-function loop: validate arguments, execute the Parallel call, preserve the original `function_call`, send its result back as `function_call_output` under the same `call_id`, and replay the required prior input items. Preserve `max_steps`, `tool_choice`, tool-call observability, cancellation, timeouts, retries, and output items at the application boundary. A Parallel Search call replaces retrieval, not a general Responses API orchestration loop.

## Migrate response consumers

### Search API

| Perplexity response | Parallel treatment |
| --- | --- |
| `results[].url` | `results[].url` |
| `results[].title` | Optional `results[].title`; preserve null handling. |
| `results[].snippet` | Join or retain `results[].excerpts` according to the application contract. Excerpts are markdown and there can be more than one. |
| `results[].date` | Optional `results[].publish_date`; do not restore missing time-of-day precision. |
| `results[].last_updated` | No equivalent. Remove the consumer, retain another data source, or approve a contract change. |
| grouped multi-query results | Separate Parallel responses when grouping matters. Do not flatten silently. |
| request `id` or server timing | Use Parallel identifiers only for tracing. Do not claim identical timing or session semantics. |

### Answer APIs

- Preserve generated text and structured output through Chat, Task, or the existing model layer.
- Preserve citations as provenance, including the UI's link-to-claim behavior. Parallel Chat research basis or Task research basis is not automatically the same annotation shape as Perplexity citations.
- Preserve streaming at the caller boundary; chunk and event shapes are not one-to-one.
- `search_results`, images/media, and related questions need explicit consumers or approved removal. Search excerpts alone do not reproduce them.
- Map usage only into an application-owned telemetry type. Perplexity tokens/search counts and Parallel SKU counts are not interchangeable costs.

## Stop conditions

Stop before deleting Perplexity code when any of these remains unresolved:

- embeddings are inside the requested boundary;
- `finance_search` supplies structured market data;
- domain paths, an upper publication bound, last-updated filtering, or a hard language filter is required;
- academic or SEC corpus behavior is a product requirement;
- images/media, related questions, positional citations, or grouped query results are caller-visible and have no approved replacement;
- Agent model routing, sandbox, MCP, existing custom functions, or orchestration would be removed as a side effect;
- a token budget has not been re-evaluated as a Parallel character budget;
- the chosen Chat or Task path changes synchronous, streaming, structured-output, or citation behavior without approval.

Report the exact call site, consumed behavior, and smallest decision required. Continue with unaffected migration work when the unresolved capability is cleanly separable.

## Official sources

- [Perplexity Search quickstart](https://docs.perplexity.ai/docs/search/quickstart)
- [Perplexity Search API reference](https://docs.perplexity.ai/api-reference/search-post)
- [Perplexity domain filters](https://docs.perplexity.ai/docs/search/filters/domain-filter)
- [Perplexity date and time filters](https://docs.perplexity.ai/docs/search/filters/date-time-filters)
- [Perplexity Sonar quickstart](https://docs.perplexity.ai/docs/sonar/quickstart)
- [Perplexity Sonar filters](https://docs.perplexity.ai/docs/sonar/filters)
- [Perplexity Agent API quickstart](https://docs.perplexity.ai/docs/agent-api/quickstart)
- [Perplexity Agent tools overview](https://docs.perplexity.ai/docs/agent-api/tools/overview)
- [Perplexity Agent custom functions](https://docs.perplexity.ai/docs/agent-api/tools/custom-functions)
- [Perplexity Agent web search](https://docs.perplexity.ai/docs/agent-api/tools/web-search)
- [Perplexity Agent fetch URL](https://docs.perplexity.ai/docs/agent-api/tools/fetch-url-content)
- [Perplexity Agent people search](https://docs.perplexity.ai/docs/agent-api/tools/people-search)
- [Perplexity Agent finance search](https://docs.perplexity.ai/docs/agent-api/tools/finance-search)
- [Perplexity SDK overview](https://docs.perplexity.ai/docs/sdk/overview)
- [Parallel Search reference](https://docs.parallel.ai/api-reference/search/search)
- [Parallel Extract reference](https://docs.parallel.ai/api-reference/extract/extract)
- [Parallel Chat quickstart](https://docs.parallel.ai/chat-api/chat-quickstart)
- [Parallel Task deep research](https://docs.parallel.ai/task-api/examples/task-deep-research)
- [Parallel Entity Search](https://docs.parallel.ai/findall-api/entity-search)
