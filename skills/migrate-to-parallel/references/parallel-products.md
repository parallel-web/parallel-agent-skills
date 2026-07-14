# Parallel product contracts

Verified against the official Parallel OpenAPI and product docs on 2026-07-14. Use this reference only when Search excerpts do not preserve the old behavior.

## Contents

- [Extract API](#extract-api)
- [Chat API](#chat-api)
- [Task API](#task-api)
- [Migration rules](#migration-rules)
- [Official sources](#official-sources)

## Extract API

Use Extract for known URLs when the application needs focused excerpts or page bodies.

- Endpoint: `POST https://api.parallel.ai/v1/extract`
- Auth: `x-api-key: $PARALLEL_API_KEY`
- SDK: `parallel-web` exposes `client.extract(...)` in Python and TypeScript.
- Input: `urls` is required and accepts up to 20 URLs. `objective`, `search_queries`, `max_chars_total`, `session_id`, `client_model`, and `advanced_settings` are optional.
- Full page body: set `advanced_settings.full_content` to `true` or to `{max_chars_per_result: ...}`. Full content is off by default.
- Output: `results`, `errors`, and `session_id` are required arrays/fields. Each successful result has `url`, `excerpts`, optional `title`, optional `publish_date`, and optional `full_content`.

Example:

```python
extract = client.extract(
    urls=selected_urls,
    objective=objective,
    search_queries=search_queries,
    session_id=search_response.session_id,
    advanced_settings={"full_content": {"max_chars_per_result": 20_000}},
)
```

Treat an HTTP 200 as a possibly partial success. A requested URL can appear in `errors` instead of `results`. Do not zip the returned results to the input list or assume result order. Reconcile unique URLs explicitly, preserve per-URL errors, and test mixed success. If duplicate input URLs are meaningful to the caller, preserve an application-owned request identifier because URL alone is ambiguous.

`full_content` and `excerpts` are markdown. If the old application promised plain text, convert at the application boundary and test the conversion. Preserve old timeout and content-size limits deliberately; legacy-provider numeric settings do not transfer one for one.

## Chat API

Use Chat for an interactive grounded completion when the old path returned an answer rather than only sources.

- Endpoint: `POST https://api.parallel.ai/chat/completions`
- Auth: `Authorization: Bearer $PARALLEL_API_KEY`
- SDK: use the `openai` package with `base_url`/`baseURL` set to `https://api.parallel.ai`. This is not a `parallel-web` client method.
- Models: `speed` is the low-latency option; `lite`, `base`, and `core` are research models with research-basis support.
- Streaming and `response_format` are supported. Several OpenAI-compatible controls, including token limits, `top_p`, and `stop`, are documented as ignored.

Example:

```python
from openai import OpenAI

chat = OpenAI(api_key=parallel_key, base_url="https://api.parallel.ai")
response = chat.chat.completions.create(
    model="speed",
    messages=[{"role": "user", "content": question}],
    stream=False,
)
```

Preserve whether the old contract streamed, returned JSON, exposed citations, or accepted conversation history. Do not copy unsupported generation controls and assume they still work. For research models, preserve the Parallel-specific `basis` data when the application exposed citations or provenance.

## Task API

Use Task for multi-step research, structured synthesis, or deep provider modes whose consumed output is not a ranked page list.

- Create: `POST https://api.parallel.ai/v1/tasks/runs` with `x-api-key` auth, or `client.task_run.create(...)` / `client.taskRun.create(...)` from `parallel-web`.
- Execution is asynchronous. Creation normally returns a running task; completion can take many minutes.
- Poll with the SDK retrieve/result methods, use a webhook for completion notification, or consume server-sent events for progress. A webhook reports status and metadata; fetch the result separately.
- Preserve the selected processor, input, output schema, citations/research basis, terminal failure states, cancellation, timeout budget, and streaming/progress behavior.

Do not replace an old synchronous handler with an unbounded blocking call. Choose polling, webhook, or SSE based on the existing caller contract. Bound polling, handle failed and cancelled terminal states, and make retries idempotent where the surrounding application requires it.

## Migration rules

- Tavily `include_raw_content` or Extract `raw_content` maps to Parallel Extract with full content enabled, not to Search excerpts unless snippets satisfy the caller contract.
- Exa `contents.text`, standalone Contents, or combined deprecated `context` maps to Search excerpts only when snippets suffice; otherwise use Extract.
- Tavily `include_answer`, Exa Answer, and other interactive synthesis can map to Chat or the application's existing model.
- Exa deep output, Tavily Research, and structured multi-step synthesis can map to Task.
- Perplexity Search API maps to Search, but grouped multi-query results require separate calls when grouping is caller-visible.
- Perplexity Sonar cited answers default to Chat or the application's existing synthesis layer for foreground answer flows; use Task when the consumed behavior is deep, structured, or asynchronous research. Preserve latency, streaming, citations, `search_results`, media, and structured output rather than treating OpenAI-compatible request shapes as behavioral equivalence.
- Perplexity Agent presets are research profiles, not stable equivalents of Parallel processors. When the Agent call's consumed behavior is web research and synthesis, select a Task processor from the actual effective tools, step depth, latency, freshness, and output contract. Use the behavior-first starting points in [perplexity.md](perplexity.md), and preserve any synchronous handler through an explicit lifecycle design.
- Perplexity Agent `web_search` maps to Search, `fetch_url` to Extract, and `people_search` to Entity Search or an explicitly chosen discovery workflow such as FindAll or Task. Perplexity Search API calls with `search_type="people"` need the same explicit entity route rather than ordinary web Search. Hosted Agent tools cannot be redirected; expose these routes through application-executed custom functions or move the tool loop to another orchestrator.
- Perplexity Agent `finance_search` can use Parallel's general index: Search for source results, Chat for an interactive financial answer, or Task for multi-step or schema-shaped research. If the caller consumes raw `finance_results`, add an application-owned normalizer and verify the required market-data coverage and freshness instead of treating the final answer as the same contract.
- Perplexity embeddings and general Agent model/tool orchestration are not Parallel Search replacements. Keep them separate or stop for a product decision.
- Firecrawl Search `web` results generally map to Search. Preserve source-group behavior, query semantics, filters, and any attached `scrapeOptions` content deliberately.
- Firecrawl Scrape and Batch Scrape can map to Extract only when the caller needs public-URL markdown, focused excerpts, or full content. Chunk more than 20 URLs and preserve per-URL errors, ordering, concurrency, and any asynchronous job contract in the application.
- Firecrawl Extract can map to Task for multi-page open-web structured research, or to Parallel Extract plus an application-owned model for deterministic structured extraction from known public URLs. Preserve the JSON Schema and asynchronous lifecycle; the similarly named APIs are not one-to-one.
- Firecrawl Agent with `strictConstrainToURLs=True` does not map to a Task domain allow-list. Use Extract plus an application-owned model/parser when exact known-URL retrieval satisfies the contract; otherwise retain or block until broader source scope is approved. Task has no direct Firecrawl `maxCredits` equivalent, and `spark-1-*` names do not determine a Parallel processor.
- Firecrawl Crawl, Map, Parse uploads, Browser, Interact, screenshots, and rich scrape formats have no verified one-call Parallel replacement. Stop or retain those capabilities until an explicit design is approved.
- Tavily Crawl/Map and provider-specific images have no verified one-call Parallel Search equivalent. Stop and propose an explicit design instead of silently deleting them.

## Official sources

- [Parallel OpenAPI](https://docs.parallel.ai/public-openapi.json)
- [Extract quickstart](https://docs.parallel.ai/extract/extract-quickstart)
- [Extract API reference](https://docs.parallel.ai/api-reference/extract/extract)
- [Chat quickstart](https://docs.parallel.ai/chat-api/chat-quickstart)
- [Task processors](https://docs.parallel.ai/task-api/guides/choose-a-processor)
- [Task lifecycle](https://docs.parallel.ai/task-api/guides/execute-task-run)
- [Task deep research quickstart](https://docs.parallel.ai/task-api/examples/task-deep-research)
- [Task polling, webhooks, and SSE](https://docs.parallel.ai/task-api/examples/task-deep-research#polling-vs-webhooks-vs-sse)
- [Research basis](https://docs.parallel.ai/task-api/guides/access-research-basis)
