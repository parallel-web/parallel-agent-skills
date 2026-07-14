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

- **Search API:** `POST /search` or `client.search.create(...)`; returns ranked result objects. Check `search_type`: `"people"` selects Perplexity's specialized People Search instead of general web search.
- **Sonar:** `POST /v1/sonar`, Sonar model IDs, or an OpenAI-compatible chat-completions client; returns a generated answer with web citations. Sonar is in maintenance mode but remains a real migration surface.
- **Agent API:** `POST /v1/agent`, the `/v1/responses` alias, or `client.responses.create(...)`; combines frontier-model routing with optional tools and presets.
- **Wrappers:** `ChatPerplexity`, `langchain-perplexity`, `@langchain/perplexity`, the older `@langchain/community/chat_models/perplexity` path, Vercel AI SDK providers/tools, and MCP servers can expose Search, Sonar, or Agent behavior. Inspect the wrapper version and tool output rather than inferring behavior from its package name.
- **Embeddings:** embedding calls are not web search. Stop and keep them outside this migration.

The Agent API can own more than retrieval. Inventory models, presets, instructions, conversation state, tool choice, step limits, structured output, streaming, and every configured tool. Do not remove non-search capabilities while replacing `web_search`.

## Choose the Parallel product

| Perplexity behavior | Parallel route | Required decision |
| --- | --- | --- |
| Search API ranked results | Search API | Preserve result count, filters, grouped-query behavior, and response fields. |
| Search API with `search_type="people"` | Entity Search for typed synchronous lookup; consider FindAll or Task for broader discovery | Preserve the people-only retrieval requirement and the old generic result shape. Do not silently turn it into general web search. |
| Sonar cited answer | Chat API or the application's existing synthesis step over Search excerpts | Default to Chat for a foreground OpenAI-compatible answer flow, but preserve streaming, structured output, conversation history, citations, `search_results`, media, and answer ownership. |
| Sonar deep research, reasoning workflows, or asynchronous research | Task API | Preserve asynchronous lifecycle, progress, output schema, and research basis. Do not map a model name directly to a Parallel mode. |
| Agent preset used for web research and synthesis | Task API after choosing a processor from the effective behavior; Chat when a foreground latency contract rules out Task | Inspect overrides, tools, step depth, output, latency, and freshness before using the preset starting points below. Task creation is asynchronous even when the old Agent request returned a completed response inline. |
| Agent `web_search` | Search API | Move model-selected query planning into the model tool schema or preserve the existing explicit planner. |
| Agent `fetch_url` | Extract API | Preserve URL limits, full-content needs, partial failures, and ordering contracts. |
| Agent `people_search` | Entity Search for synchronous lookup; consider FindAll or Task for broader discovery | Preserve both the final answer and any consumed `people_search_results` item. Its results are search-result records, not normalized person objects. |
| Agent `finance_search` | Search for source results, Chat for an interactive answer, or Task for multi-step or schema-shaped financial research | Use Parallel's general index, then preserve the consumer's actual contract. Raw `finance_results` need an application-owned output type and normalizer; hard coverage or freshness requirements need a representative evaluation. |
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
| `search_type` | `"web"` maps to ordinary Search. `"people"` is a product boundary, not a query hint: route it to Entity Search, FindAll, or Task according to whether the caller needs typed lookup, broad discovery, or synthesized research. Preserve its people-only behavior and response contract. |
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

Preserve `messages`, system instructions, streaming, `response_format`, citation display, `search_results`, image and document inputs, image/video outputs, related questions, and usage reporting deliberately. Perplexity generation controls and `web_search_options` do not map by name to Parallel controls. Re-evaluate temperature/token parameters against the chosen answer product; Parallel Chat documents several OpenAI-compatible parameters as ignored.

Do not translate the current `sonar`, `sonar-pro`, `sonar-reasoning-pro`, or `sonar-deep-research` models directly into `turbo`, `basic`, or `advanced`. Model tiers combine retrieval and generation behavior, while Parallel Search modes configure retrieval. Also detect the deprecated `sonar-reasoning` ID in older code instead of assuming it is a current model.

Sonar `search_mode` values such as `academic` and `sec` are vertical search behavior, not Parallel mode equivalents. Express a soft source preference in `objective`, use an equivalent hard domain policy when one exists, or stop if the specialized corpus is required.

Do not confuse the Search API's top-level `search_type` with Sonar Pro's `web_search_options.search_type`. The former selects `"web"` or `"people"`; the latter selects `"fast"`, `"pro"`, or `"auto"` retrieval behavior inside a generated-answer request. Preserve the observed depth, latency, streaming, and answer contract through the chosen synthesis route instead of renaming either value to a Parallel Search mode.

Sonar accepts image inputs and document `file_url` content parts. Documents may be PDF, DOC, DOCX, TXT, or RTF supplied by a public URL or raw base64 string; Perplexity documents a 50 MB per-file limit and at most 30 files per request. These inputs are not Search queries. Keep an existing multimodal/document model, or use Extract for accessible document URLs and pass the extracted content to the chosen synthesis owner. Base64/local documents need an explicit parsing or upload path. Preserve existing size/count validation, and do not delete or reinterpret these inputs without an approved contract change.

### Agent API

An Agent request may combine a routed model with multiple tools. Perplexity built-in tools are hosted capabilities, not callbacks that can be pointed at another URL. Replacing one requires one of these designs:

- Keep the Agent API as the model router, replace each hosted search tool with a custom `type: "function"` tool, execute the corresponding Parallel API in the application, and return a `function_call_output` with the same `call_id`.
- Move the model and tool loop into an existing application-owned agent harness, then register Parallel-backed tools there.

#### Choose from effective preset behavior

Perplexity presets are dynamic, unversioned bundles of a model, tools, search configuration, reasoning, step limits, output limits, and a system prompt. Their underlying configuration can change while the preset name stays the same. Detect both current names and older names still present in code:

| Previous name | Current name | Documented profile |
| --- | --- | --- |
| `fast-search` | `fast` | Single-fact lookups and short summaries where latency matters most |
| `pro-search` | `low` | Everyday research with light multi-step tool use |
| `deep-research` | `medium` | Multi-hop browsing and aggregation across many sources |
| `advanced-deep-research` | `high` | Expert reasoning and exhaustive source coverage |
| None | `xhigh` | Open-ended agentic work with sandbox execution and long tool-use loops |

Do not select a Parallel product or processor from that name alone. A request can override a preset's model, tools, step limit, reasoning effort, output budget, or search configuration. It can also copy the preset into a frozen configuration and omit `preset` entirely. Inventory the effective configuration and the behavior consumed by the caller, then decide:

1. Keep or rebuild the model/tool loop when sandbox, MCP, custom functions, or other non-research orchestration is caller-visible.
2. Use Chat when the application needs a foreground answer and cannot accept Task's create-and-retrieve lifecycle.
3. Use Task when the consumed behavior is web research or structured synthesis and the application can preserve the asynchronous lifecycle.
4. Only after choosing Task, use these as evaluation starting points rather than equivalences:

| Effective Perplexity profile | Candidate Task starting point | Evaluation gate |
| --- | --- | --- |
| `fast` | `base-fast`; consider `lite-fast` only for a very small, simple output | Verify foreground latency and answer quality; use Chat `speed` instead when Task's lifecycle is unacceptable. |
| `low` | `core-fast` | Verify light multi-step coverage, latency, and output complexity. Use standard `core` when freshness matters more than speed. |
| `medium` | `pro-fast` or `pro` | Choose fast versus standard from the caller's latency and freshness contract, then evaluate multi-hop coverage. |
| `high` | `ultra-fast` or `ultra` | Prefer the standard family when exhaustive coverage and freshness matter more than latency. |
| `xhigh` | No processor-only equivalent | Route only the open-web research slice to an evaluated `ultra*` processor; retain or rebuild sandbox execution and the long-running tool loop. |

Parallel processor tiers are selected by task complexity and output shape, while `-fast` variants trade some freshness priority for latency. Do not preserve a Perplexity preset's cost, model, tool-call count, token budget, or latency by copying a name. Record the selected processor as an application policy and evaluate it with representative requests.

#### Route finance through the consumed contract

Do not retain `finance_search` solely because it is a specialized Perplexity tool. Parallel's general index can support the financial research path, but choose the product from what the application reads:

- If the caller reads only the final generated answer, use Chat for a foreground answer or Task for multi-step, cited, or schema-shaped financial research.
- If the caller reads raw `finance_results`, define an application-owned type for the required categories, tickers, result content, and source URLs. Produce it with an explicit Task output schema, or with Search evidence plus the application's existing synthesis layer, then normalize it at the provider boundary. Do not substitute the final assistant message for those output items.
- If quotes, near-real-time or historical prices, OHLCV intervals, pre-market or after-hours data, statements, ratios, ETF constituents, or another coverage/freshness guarantee is contractual, test representative symbols, categories, regions, missing data, and timestamps. Retain or block only when the general-index route cannot satisfy that named requirement.

When `finance_search` appears beside `web_search`, `fetch_url`, or other tools, preserve one owner for the combined orchestration. Do not migrate one tool in isolation if the caller consumes their ordering, shared step budget, intermediate outputs, or final synthesis.

In either design, separate the contracts:

1. Preserve the model and non-search tools in their current owner unless broader migration is requested.
2. Replace `web_search` with an application-executed Search tool whose input requires a self-contained `objective` and exactly three diverse keyword `search_queries`.
3. Replace `fetch_url` with an application-executed Extract tool only when its input and result preserve URL limits, full content, and per-URL errors.
4. Replace `people_search` only after defining the application-owned person input and result types. The Agent response can include a `people_search_results` output item with model-generated queries and generic search-result entries before the final assistant message; it does not guarantee typed `name`, `company`, or `job_title` fields. Route it to Entity Search, FindAll, or Task as appropriate and normalize deliberately.
5. Route `finance_search` through the final-answer or structured-result path above, and stop on embeddings.

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
- Preserve citations as provenance, including the UI's link-to-claim behavior. Sonar exposes a `citations` URL array and citation markers in generated text. Agent output has an `annotations` schema with URL and position fields, but annotations can be empty and cited Agent text may instead contain inline source markers. Trace the actual consumer rather than assuming either shape. Parallel Chat research basis or Task research basis is not automatically the same contract.
- Preserve streaming at the caller boundary; chunk and event shapes are not one-to-one.
- `search_results`, images/media, and related questions need explicit consumers or approved removal. Search excerpts alone do not reproduce them.
- Preserve consumed `finance_results` through the application-owned finance type and normalizer. A Task result, research basis, or final answer is not automatically the same output-item contract.
- Map usage only into an application-owned telemetry type. Perplexity tokens/search counts and Parallel SKU counts are not interchangeable costs.

## Stop conditions

Stop before deleting Perplexity code when any of these remains unresolved:

- embeddings are inside the requested boundary;
- `finance_search` has a hard market-data coverage, freshness, raw-result, or source contract that the evaluated general-index route and application normalizer do not preserve;
- domain paths, an upper publication bound, last-updated filtering, or a hard language filter is required;
- academic or SEC corpus behavior is a product requirement;
- image or document inputs, image/video outputs, related questions, citation markers or annotations, or grouped query results are caller-visible and have no approved replacement;
- Agent model routing, sandbox, MCP, existing custom functions, or orchestration would be removed as a side effect;
- a token budget has not been re-evaluated as a Parallel character budget;
- the chosen Chat or Task path changes synchronous, streaming, structured-output, or citation behavior without approval.

Report the exact call site, consumed behavior, and smallest decision required. Continue with unaffected migration work when the unresolved capability is cleanly separable.

## Official sources

- [Perplexity Search quickstart](https://docs.perplexity.ai/docs/search/quickstart)
- [Perplexity Search API reference](https://docs.perplexity.ai/api-reference/search-post)
- [Perplexity domain filters](https://docs.perplexity.ai/docs/search/filters/domain-filter)
- [Perplexity date and time filters](https://docs.perplexity.ai/docs/search/filters/date-time-filters)
- [Perplexity Search API People Search](https://docs.perplexity.ai/docs/search/filters/people-search)
- [Perplexity Sonar quickstart](https://docs.perplexity.ai/docs/sonar/quickstart)
- [Perplexity Sonar models](https://docs.perplexity.ai/docs/sonar/models)
- [Perplexity Sonar filters](https://docs.perplexity.ai/docs/sonar/filters)
- [Perplexity Sonar media and attachments](https://docs.perplexity.ai/docs/sonar/media)
- [Perplexity Agent API quickstart](https://docs.perplexity.ai/docs/agent-api/quickstart)
- [Perplexity Agent presets](https://docs.perplexity.ai/docs/agent-api/presets)
- [Perplexity Agent tools overview](https://docs.perplexity.ai/docs/agent-api/tools/overview)
- [Perplexity Agent custom functions](https://docs.perplexity.ai/docs/agent-api/tools/custom-functions)
- [Perplexity Agent web search](https://docs.perplexity.ai/docs/agent-api/tools/web-search)
- [Perplexity Agent fetch URL](https://docs.perplexity.ai/docs/agent-api/tools/fetch-url-content)
- [Perplexity Agent people search](https://docs.perplexity.ai/docs/agent-api/tools/people-search)
- [Perplexity Agent finance search](https://docs.perplexity.ai/docs/agent-api/tools/finance-search)
- [Perplexity SDK overview](https://docs.perplexity.ai/docs/sdk/overview)
- [Perplexity LangChain integration](https://docs.perplexity.ai/docs/getting-started/integrations/langchain)
- [LangChain JavaScript Perplexity integration](https://docs.langchain.com/oss/javascript/integrations/chat/perplexity)
- [Parallel Search reference](https://docs.parallel.ai/api-reference/search/search)
- [Parallel Extract reference](https://docs.parallel.ai/api-reference/extract/extract)
- [Parallel Chat quickstart](https://docs.parallel.ai/chat-api/chat-quickstart)
- [Parallel Task processors](https://docs.parallel.ai/task-api/guides/choose-a-processor)
- [Parallel Task lifecycle](https://docs.parallel.ai/task-api/guides/execute-task-run)
- [Parallel Task quickstart](https://docs.parallel.ai/task-api/task-quickstart)
- [Parallel Task deep research](https://docs.parallel.ai/task-api/examples/task-deep-research)
- [Parallel Entity Search](https://docs.parallel.ai/findall-api/entity-search)
