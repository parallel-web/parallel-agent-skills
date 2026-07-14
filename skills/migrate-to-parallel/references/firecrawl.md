# Firecrawl migration reference

Verified against the official Firecrawl and Parallel documentation on 2026-07-14. Firecrawl is a web-data platform, not one search endpoint. Classify each call before replacing it, and do not remove an unsupported capability as a side effect of migrating Search or Scrape.

## Contents

- [Detect the product boundary](#detect-the-product-boundary)
- [Choose the Parallel product](#choose-the-parallel-product)
- [Migrate Search](#migrate-search)
- [Migrate Scrape and Batch Scrape](#migrate-scrape-and-batch-scrape)
- [Migrate structured Extract and Agent](#migrate-structured-extract-and-agent)
- [Handle Research Index, Crawl, Map, Parse, Browser, Interact, and Monitor](#handle-research-index-crawl-map-parse-browser-interact-and-monitor)
- [Migrate response and operational behavior](#migrate-response-and-operational-behavior)
- [Detect SDKs, REST, wrappers, and MCP](#detect-sdks-rest-wrappers-and-mcp)
- [Stop conditions](#stop-conditions)
- [Official sources](#official-sources)

## Detect the product boundary

Inventory every Firecrawl call, configuration surface, and downstream consumer. Current Firecrawl v2 uses `https://api.firecrawl.dev/v2`; older repositories can use `/v1`, legacy SDK methods, or a self-hosted `FIRECRAWL_API_URL`.

- **Search:** `POST /v2/search` or SDK `search(...)`; returns separate arrays for requested `web`, `news`, and `images` sources. `scrapeOptions` can attach scraped page content to results.
- **Scrape:** `POST /v2/scrape` or SDK `scrape(...)`; fetches one URL and can produce markdown, HTML, screenshots, structured JSON, media, links, branding, product data, change tracking, and other formats.
- **Batch Scrape:** `/v2/batch/scrape` or SDK `batchScrape` / `batch_scrape`; has synchronous waiter and asynchronous job forms.
- **Extract:** `/v2/extract` or SDK `extract(...)`; uses a prompt and optional JSON Schema to synthesize structured data across URLs. It can expand beyond supplied URLs with web search.
- **Crawl:** `/v2/crawl` or SDK `crawl(...)` / `startCrawl` / `start_crawl`; discovers and scrapes many pages under traversal rules.
- **Map:** `/v2/map` or SDK `map(...)`; enumerates and ranks links from a site.
- **Parse:** `/v2/parse` or SDK `parse(...)`; accepts a local or non-public file as multipart form data and can return markdown, JSON, HTML, links, images, or a summary.
- **Agent:** `/v2/agent`, SDK `agent(...)`, or MCP agent tools perform autonomous search, navigation, and extraction. Current Agent requests require a prompt and can accept URL constraints, a JSON Schema, a credit budget, and either `spark-1-mini` or `spark-1-pro`.
- **FIRE-1:** a separate beta navigation model found in older `/v1/scrape` and `/v1/extract` `agent` options. Do not treat a FIRE-1 call as the current `/v2/agent` API.
- **Research Index:** `/v2/search/research/...`, JavaScript `research.*`, Python research methods, or CLI research commands search papers, read passages, traverse related-paper structure, and search research-related GitHub history.
- **Browser:** standalone sessions under `/v2/interact` with SDK `browser(...)`; exposes code execution, Playwright/CDP access, profiles, and live views.
- **Interact:** `/v2/scrape/{scrapeId}/interact` or SDK `interact(...)`; continues from a scrape and supports prompts or code. Current CLI/MCP agent guidance favors Scrape plus Interact over the hidden legacy Browser CLI.
- **Monitor:** `/v2/monitor` and SDK monitor methods schedule recurring scrape, crawl, or search targets and deliver page/check events through webhooks or notifications.
- **MCP and wrappers:** the `firecrawl-mcp` server, hosted `https://mcp.firecrawl.dev/v2/mcp`, LangChain `FireCrawlLoader`, workflow integrations, and model tools can expose several of the products above through one boundary.

Trace which response fields are used. A method named `extract` may mean structured synthesis, while a caller using `scrape` may depend on browser actions, screenshots, cache guarantees, or metadata rather than text alone.

## Choose the Parallel product

| Firecrawl behavior | Parallel route | Required decision |
| --- | --- | --- |
| Web Search result list | Search API | Preserve query intent, per-source limits, filters, grouping, and response fields. |
| Search plus scraped markdown/full content | Search followed by Extract | Preserve which result URLs are fetched, content budget, per-URL failures, and latency. |
| Scrape of public URLs for markdown, excerpts, or full content | Extract API | Verify content selection, cache/freshness, partial-failure, and metadata behavior. |
| Batch Scrape for public URL text | Chunked Extract calls | Parallel Extract accepts at most 20 URLs. Own concurrency, ordering, reconciliation, cancellation, and any job API in the application. |
| Structured multi-page Extract or research | Task API | Preserve prompt, JSON Schema, sources, citations, asynchronous status, cancellation, and failure behavior. |
| Deterministic structured extraction from known page content | Extract plus an application-owned model/parser | Preserve schema validation and per-document errors. Do not imply Parallel Extract itself returns arbitrary schema-shaped JSON. |
| Agentic research that needs only open-web research and structured synthesis | Task API, after evaluating the exact behavior | Preserve asynchronous lifecycle and source provenance. Approve the processor deliberately; do not map FIRE-1 or `spark-1-*` by name. |
| Crawl or Map | No direct one-call equivalent | Retain Firecrawl or add an application-owned discovery/crawler layer before Parallel Extract. Search does not guarantee complete site enumeration. |
| Research Index | No direct one-call equivalent | Parallel Search, Extract, or Task may cover the information need, but not Firecrawl's canonical paper identifiers, paper metadata contract, passage ranking, citation/reference graph expansion, or research-specific GitHub result shape. Retain it or redesign and normalize the caller contract explicitly. |
| Parse of a local/private uploaded file | No direct equivalent | Keep a file parser or choose an explicit upload/parsing product. Public document URLs may use Extract. |
| Browser, Interact, scrape actions, screenshots, or live view | No retrieval-only equivalent | Keep a browser-automation boundary or choose a browser product explicitly. |
| Firecrawl Monitor or scrape change tracking | Possibly Parallel Monitor after a product redesign | Compare target scope, schedule, trigger, judgment, snapshot, diff, delivery channels, webhook, retention, and privacy semantics before changing products. |

The route is selected from consumed behavior, not the Firecrawl method name. If one wrapper mixes supported and unsupported products, separate the boundary before removing its dependency or key.

## Migrate Search

### Query and result semantics

Firecrawl Search accepts one `query` string, up to 500 characters. Parallel requires one to five keyword-shaped `search_queries` and optionally accepts a self-contained `objective`.

- If the Firecrawl query is already a concise retrieval probe, it may be used as the one-query compatibility path and should be evaluated.
- If it is a question, research prompt, or operator-heavy expression, preserve the full goal as `objective` and obtain two or three keyword probes from the existing caller or planner. Do not add a hidden LLM call.
- Firecrawl documents quoted text, negation, `site:`, `filetype:`, `inurl:`, `allinurl:`, `intitle:`, `allintitle:`, `related:`, and image-size operators. Do not assume Parallel preserves those operators. Translate a hard domain restriction into source policy when the URL scope is equivalent; otherwise stop or implement explicit filtering.

Firecrawl `limit` defaults to 10, accepts 1 through 100, and applies per source type. Parallel `advanced_settings.max_results` limits one jointly ranked result list. A Firecrawl request for 10 web, 10 news, and 10 image results is not equivalent to one Parallel request with 10 results.

### Request field mapping

| Firecrawl Search field | Parallel treatment |
| --- | --- |
| `query` | Classify into `objective` and keyword-shaped `search_queries` as above. |
| `limit` | Set `advanced_settings.max_results` only for one mapped result group and after validating Parallel's current range. Preserve per-source limit behavior when multiple groups are caller-visible. |
| `sources: [{type: "web"}]` | Search API. Preserve the response's grouped `web` contract if callers depend on it. |
| `sources: [{type: "news"}]` | No dedicated news result group. Express a soft news/freshness preference in `objective`, use a hard domain policy only when a finite equivalent source set exists, or stop if a news-only corpus is required. |
| `sources: [{type: "images"}]` | No image-search response in Parallel Search. Keep an image-search provider or approve a separate design. |
| `categories: ["github", "research", "pdf"]` | No category field. Express a soft preference in `objective`; use source policy only when it preserves the exact required host set. Stop if the specialized corpus is hard policy. |
| `includeDomains` | Normalize and map to `source_policy.include_domains` only when host scope is equivalent. Firecrawl does not allow include and exclude lists together. |
| `excludeDomains` | Normalize and map to `source_policy.exclude_domains` only when host scope is equivalent. Do not broaden path or subdomain restrictions. |
| `tbs` | Parse the actual expression. A lower publication bound may map to inclusive `after_date`; upper bounds, last-updated semantics, arbitrary ranges, and sort-by-date do not have a one-field equivalent. |
| `location` | Firecrawl accepts a free-form place. Parallel accepts supported ISO country codes. Map only when the product requirement is country-level and inspect warnings. |
| `country` | Consider `advanced_settings.location`; Firecrawl defaults to `US`, so preserve or explicitly change that omitted default when location affects behavior. |
| `timeout` | Preserve at the SDK/HTTP/application boundary. Do not copy milliseconds into Parallel's seconds field. |
| `scrapeOptions` | Run Parallel Extract for selected result URLs when excerpts are insufficient. Translate only the supported text/content contract, not every nested scrape option. |
| `ignoreInvalidURLs` | Validate and reconcile URLs in the application if this behavior matters. Do not silently change fail-fast versus partial-success behavior. |
| `enterprise`, `anon`, `zdr`, `threatProtection` | No simple request-field mapping. Verify current Parallel privacy/security terms and stop if these are compliance requirements. |

Firecrawl's API introduction says every request uses Bearer auth, while its current rate-limit and product docs define a rate-limited keyless tier for official SDK, CLI, and MCP clients. That tier includes Scrape, Search, Interact, and Parse; the Research Index also documents keyless use. Detect authenticated, keyless, and self-hosted deployments. Do not treat a missing `FIRECRAWL_API_KEY` as dead code, assume arbitrary REST clients receive the official-client tier, promise keyless production capacity, or remove self-hosted infrastructure.

### Response mapping

Firecrawl groups results under `data.web`, `data.news`, and `data.images` according to the requested sources. Parallel returns one ranked `results` array.

- `url` maps to `url`.
- `title` maps to optional `title`; preserve missing-value handling.
- A Firecrawl description or attached markdown does not map to one Parallel field by name. Join or retain `excerpts` for concise evidence, or use Extract for full content.
- A Firecrawl publication date may map to optional date-only `publish_date` only when its semantics and precision satisfy the caller.
- Image URLs, dimensions, source-group positions, search job IDs, warnings, and credit counts need explicit consumers or approved removal.
- Preserve separate source arrays when callers render or rank them separately. Do not flatten groups silently.

## Migrate Scrape and Batch Scrape

Parallel Extract is a candidate only when the old caller consumes text from public URLs. Its `urls` input accepts at most 20 URLs, and each URL can independently appear in `results` or `errors`. Reconcile by unique URL; do not zip outputs to inputs or assume returned order.

### Safe text-content route

- Firecrawl markdown or a concise text excerpt can map to Parallel Extract `excerpts` when the context budget is sufficient.
- Firecrawl markdown/full-page needs can map to `advanced_settings.full_content`. Verify boilerplate, main-content selection, markdown shape, size, and truncation with representative pages.
- Search-then-scrape can map to Search followed by Extract, reusing the Parallel `session_id`.
- Preserve timeouts, retries, cancellation, and content-size guards at the application boundary.

### Non-isomorphic Scrape behavior

Do not claim an Extract migration preserves any of the following without an explicit implementation and tests:

- HTML or raw HTML;
- links, images, screenshots, audio, video, menus, branding, or product objects;
- JSON extraction, summaries, questions, or highlights generated by Firecrawl;
- browser actions, waits, cookies, headers, profiles, location/mobile emulation, proxy behavior, or TLS controls;
- PDF parser/OCR selection;
- `onlyMainContent`, include/exclude tag rules, and base64-image handling;
- cache-only reads, cache writes, `maxAge`, `minAge`, or Firecrawl's two-day v2 default;
- zero-data-retention, lockdown, PII redaction, threat protection, or other security/privacy controls;
- change-tracking snapshots and diffs.

Parallel has its own fetch policy, including `max_age_seconds`, `timeout_seconds`, and cache-fallback behavior. Preserve the application's freshness requirement after comparing semantics and units; do not copy Firecrawl cache fields mechanically.

### Batch lifecycle

If the old caller uses Firecrawl's waiter, asynchronous job ID, polling, `next` pagination, webhook, status counters, cancellation, or error endpoint, a loop of Extract requests is not the whole migration.

Create one application-owned batch abstraction that:

1. validates and chunks URLs into groups of at most 20;
2. uses bounded concurrency and preserves the old timeout/cancellation contract;
3. records an application request identifier when duplicate URLs are meaningful;
4. reconciles every input with a result or explicit error;
5. preserves stable caller-visible ordering if the old contract exposed it;
6. owns polling/webhook/job persistence when the caller was asynchronous;
7. reports partial completion instead of treating HTTP 200 as total success.

## Migrate structured Extract and Agent

Firecrawl Extract is an asynchronous structured-data workflow: it accepts URLs, a prompt, optional JSON Schema, optional web-search expansion, and site-scanning controls. Current SDK `extract(...)` methods wait for completion; `startExtract` / `start_extract` return a job, and `getExtractStatus` / `get_extract_status` reports `processing`, `completed`, `failed`, or `cancelled`. Firecrawl currently recommends Agent for new autonomous work and Scrape JSON mode for one known page, but existing Extract callers still require a complete migration.

Choose one route:

- Use Parallel Task when the behavior is multi-page research or schema-shaped synthesis and the caller accepts an asynchronous research workflow.
- Use Parallel Extract to fetch known public URLs and the application's existing model/parser to produce deterministic schema-shaped output.
- Keep Firecrawl for agentic navigation or extraction that relies on browser interaction and cannot be reduced to public-URL retrieval plus synthesis.

Preserve the prompt, JSON Schema validation, source disclosure, web-search expansion, subdomain/sitemap behavior, status lifecycle, expiration, token/usage telemetry, cancellation, retries, and partial data deliberately. Parallel Extract's name does not mean it implements Firecrawl's structured Extract contract. Parallel Task processors, schemas, statuses, and research basis are different interfaces and need an application-level normalizer when the caller contract must remain stable.

Current Firecrawl Agent can search and navigate across the web. Route it to Task only after verifying that the consumed behavior is research and structured synthesis rather than browser action, exhaustive collection, authenticated navigation, or stateful interaction. Treat legacy FIRE-1 scrape/extract navigation as a separate capability and retain or replace its browser behavior explicitly.

The current REST Agent start call returns a job ID, while SDK `agent(...)` methods provide a waiter-style interface. Agent status can be `processing`, `completed`, `failed`, or `cancelled`; cancellation is cooperative. Preserve polling, cancellation, the default 2,500-credit budget or an explicit `maxCredits`, URL constraints, `strictConstrainToURLs`, the selected `spark-1-mini` or `spark-1-pro` quality behavior, schema validation, sources, and terminal failures.

Treat these Agent fields as migration decisions, not mechanical mappings:

| Firecrawl Agent behavior | Parallel treatment |
| --- | --- |
| `urls` with `strictConstrainToURLs=True` | This is exact supplied-URL scope. A Task `source_policy.include_domains` allow-list is broader and must not be substituted silently. If known public URLs plus structured output are sufficient, fetch exactly those URLs with Parallel Extract and pass only that content to an application-owned model/parser. Otherwise retain Firecrawl or block until the user approves broader web research. |
| `maxCredits` / `max_credits` | Parallel Task has no direct per-run field with equivalent Firecrawl-credit semantics. If this value is a hard spend ceiling, retain or block until an application-owned budget design is approved. Never omit it while claiming behavior preservation, and do not compare Parallel usage SKU counts to Firecrawl credits. |
| `model="spark-1-mini"` or `model="spark-1-pro"` | Do not translate this name to `lite`, `base`, `core`, `pro`, or `ultra`. Parallel processors have different price, latency, and research-depth contracts. Choose one only from the application's quality, latency, and cost requirements and representative evaluation, or ask for approval. |
| SDK `agent(...)` waiter versus Agent job API | Preserve whether the caller blocks, polls, times out, cancels, receives partial status, and handles terminal failure. A long `task_run.result(...)` timeout is a new lifecycle choice, not automatic equivalence. |

When several of these constraints occur on one call, do not partially migrate it just to remove Firecrawl. Retaining the call is safer than broadening its URL scope, removing its spend ceiling, or guessing a processor. Continue independently separable Search or public-text extraction rows.

## Handle Research Index, Crawl, Map, Parse, Browser, Interact, and Monitor

### Research Index

Firecrawl Research is a specialized index, not the ordinary Search endpoint. It searches paper abstracts with research filters, exposes canonical and source-specific paper identifiers and metadata, returns question-relevant full-text passages, expands through similar papers, citers, or references, and searches GitHub issues, pull requests, discussions, and README history.

Parallel Search, Extract, and Task can research scientific or engineering topics, but they do not expose that same entity and graph contract. If callers consume only human-readable evidence, redesign and evaluate a Parallel workflow. If they consume paper IDs, structured metadata, ranked passages, graph-expansion modes, or research-specific GitHub fields, retain Firecrawl or add an application-owned scholarly index and normalizer.

### Crawl

Firecrawl Crawl can start from a URL and discover up to 10,000 pages by default. It supports path regexes, crawl depth, sitemap modes, query-parameter handling, siblings, subdomains, external links, robots policy, delay/concurrency, per-page scrape options, prompts, jobs, webhooks, and paginated status data.

Parallel Search is relevance retrieval, not deterministic traversal. If crawl coverage is required, keep Firecrawl or build an application-owned crawler/sitemap/link-discovery layer and pass discovered public URLs to Parallel Extract. Preserve robots/compliance policy, loop and deduplication rules, crawl budgets, concurrency, checkpointing, and per-page errors.

### Map

Firecrawl Map enumerates site links, returns URL/title/description records, defaults to 5,000 links, and can permit up to 100,000. Search cannot guarantee complete site URL enumeration or Map's sitemap, subdomain, query-stripping, cache, and ordering behavior. Keep Map or use an explicit sitemap/link-indexing component.

### Parse

Firecrawl Parse uploads `.html`, `.htm`, `.pdf`, `.docx`, `.doc`, `.odt`, `.rtf`, `.xlsx`, or `.xls` files as multipart form data, with documented uploads up to 50 MB. Parallel Extract accepts public URLs, not arbitrary local/private multipart files. Publicly reachable document URLs may use Extract after format validation; otherwise preserve or choose a file parser.

### Browser and Interact

Firecrawl Browser is a standalone API/SDK session under `/v2/interact`; Interact continues the browser state created by a scrape under `/v2/scrape/{scrapeId}/interact`. Both can expose Playwright or code execution, clicks, form fills, navigation, profiles, CDP URLs, live views, and session lifecycle. Current Firecrawl docs call the hidden Browser CLI legacy and recommend Scrape plus Interact for CLI/MCP agent workflows. Parallel Search, Extract, Chat, and Task do not provide a drop-in browser session. Keep this boundary or select a browser-automation product explicitly.

The same rule applies when browser actions are nested inside `scrape` options or exposed through MCP. A final text response does not prove retrieval-only behavior.

### Monitor and change tracking

Firecrawl Monitor schedules one or more `scrape`, `crawl`, or `search` targets, can judge changes against a goal, records page states such as `same`, `new`, `changed`, `removed`, or `error`, and can notify through webhooks, email, or Slack. Scrape and crawl targets may also use Firecrawl change-tracking formats.

Parallel Monitor may be a product candidate, not a field rename. Compare target scope, query semantics, cadence, judgment, snapshot ownership, diff and event shape, delivery channels, webhook verification and retry, retention, backfill, and privacy requirements. Do not replace either Firecrawl Monitor or scrape-level change tracking inside a search migration without an explicit behavior design and representative end-to-end tests.

## Migrate response and operational behavior

Firecrawl commonly exposes `success`, `data`, `status`, job `id`, `next`, `warning`, `creditsUsed`, metadata, and product-specific nested fields. Parallel response identifiers, session IDs, warnings, errors, usage SKU counts, and Task status are not interchangeable.

- Normalize only the application-owned fields callers actually need.
- Preserve mixed success and per-URL errors.
- Preserve pagination and status loops when a Firecrawl result can exceed one response page.
- Preserve webhook verification, retry, idempotency, and job persistence when used.
- Recalculate rate/concurrency controls; do not copy Firecrawl plan limits into Parallel settings.
- Keep usage and cost telemetry provider-neutral. Firecrawl credits and Parallel SKU counts are different units.
- Review data handling before moving ZDR, lockdown, PII-redacted, threat-protected, private, or authenticated traffic.
- Preserve self-hosted behavior or stop for an infrastructure decision. Replacing a self-hosted Firecrawl deployment with a hosted API is a security and operations change, not dependency cleanup.

## Detect SDKs, REST, wrappers, and MCP

Current and legacy signatures can coexist:

- Current JavaScript package/import: `firecrawl` and `import { Firecrawl } from "firecrawl"`.
- Legacy JavaScript package/client: `@mendable/firecrawl-js` and `FirecrawlApp`.
- Python distribution/imports: `firecrawl-py`, `Firecrawl`, `AsyncFirecrawl`, `firecrawl.types`, and `firecrawl.v2.types`. Feature-frozen v1 access can appear under `firecrawl.v1`.
- Legacy methods include `scrapeUrl` / `scrape_url`, `crawlUrl` / `crawl_url`, `asyncCrawlUrl`, `mapUrl`, `batchScrapeUrls`, status/error methods, and removed LLM-text methods.
- Current methods include `scrape`, `search`, `map`, `crawl`, `startCrawl`, `batchScrape`, `startBatchScrape`, `extract`, `startExtract`, `agent`, `startAgent`, `parse`, `interact`, `browser`, monitor lifecycle methods, research methods, related status/cancel methods, and snake_case Python forms.
- LangChain can expose Firecrawl through `FireCrawlLoader` in community document loaders.
- Current MCP package: `firecrawl-mcp`; the official hosted endpoint is `https://mcp.firecrawl.dev/v2/mcp`. Older configuration may use `@mendableai/mcp-server-firecrawl`. Detect `firecrawl_*` tool names and classify each tool separately.
- Configuration commonly uses `FIRECRAWL_API_KEY`; self-hosted integrations may also use `FIRECRAWL_API_URL`.

Do not delete a shared Firecrawl SDK, MCP server, or credential until every remaining surface has either migrated or been isolated as an approved retained capability.

## Stop conditions

Stop before deleting Firecrawl code when any of these remains unresolved:

- `news` or `images` is a required Search source, or a Firecrawl category/operator is a hard retrieval rule;
- Search source grouping, per-source limits, upper date bounds, sort-by-date, or attached scrape content is caller-visible without a replacement;
- Scrape callers consume HTML, screenshots, media, links, generated JSON/summary/questions/highlights, browser actions, rich metadata, or specialized PDF behavior;
- cache, freshness, ZDR, lockdown, PII redaction, threat protection, cookies, headers, proxy, self-hosting, or authenticated-page behavior is a requirement;
- Batch Scrape's job, webhook, pagination, ordering, duplicate, cancellation, or partial-failure contract is not implemented;
- structured Extract's schema, sources, web expansion, site-scanning behavior, or asynchronous lifecycle would change without approval;
- Agent exact-URL scope would become domain or open-web scope, a hard `maxCredits` ceiling would be dropped, a `spark-1-*` model would be guessed into a Parallel processor, or waiter/job behavior would change without approval;
- Research Index entity/graph behavior, Crawl, Map, local/private Parse, Browser, Interact, Agent navigation, Firecrawl Monitor, or scrape change tracking remains inside the requested boundary;
- MCP exposes any unsupported Firecrawl tool through the same server being removed.

Report the exact call site, consumed behavior, and smallest decision needed. Continue with cleanly separable Search or public-text extraction work when unsupported capabilities can remain isolated.

## Official sources

- [Firecrawl v2 introduction](https://docs.firecrawl.dev/api-reference/v2-introduction)
- [Firecrawl v2 migration guide](https://docs.firecrawl.dev/migrate-to-v2)
- [Search guide](https://docs.firecrawl.dev/features/search)
- [Search API reference](https://docs.firecrawl.dev/api-reference/endpoint/search)
- [Scrape guide](https://docs.firecrawl.dev/features/scrape)
- [Scrape API reference](https://docs.firecrawl.dev/api-reference/endpoint/scrape)
- [Batch Scrape guide](https://docs.firecrawl.dev/features/batch-scrape)
- [Batch Scrape API reference](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape)
- [Structured Extract guide](https://docs.firecrawl.dev/features/extract)
- [Structured Extract API reference](https://docs.firecrawl.dev/api-reference/endpoint/extract)
- [Extract status API source](https://github.com/firecrawl/firecrawl-docs/blob/main/api-reference/endpoint/extract-get.mdx)
- [Crawl guide](https://docs.firecrawl.dev/features/crawl)
- [Crawl API reference](https://docs.firecrawl.dev/api-reference/endpoint/crawl-post)
- [Crawl status API reference](https://docs.firecrawl.dev/api-reference/endpoint/crawl-get)
- [Map guide](https://docs.firecrawl.dev/features/map)
- [Map API reference](https://docs.firecrawl.dev/api-reference/endpoint/map)
- [Parse API reference](https://docs.firecrawl.dev/api-reference/endpoint/parse)
- [Research Index](https://docs.firecrawl.dev/features/research)
- [Interact guide](https://docs.firecrawl.dev/features/interact)
- [Browser guide](https://docs.firecrawl.dev/features/browser)
- [FIRE-1 Agent](https://docs.firecrawl.dev/agents/fire-1)
- [Agent guide](https://docs.firecrawl.dev/features/agent)
- [Agent API reference](https://docs.firecrawl.dev/api-reference/endpoint/agent)
- [Monitoring guide](https://docs.firecrawl.dev/features/monitoring)
- [Firecrawl rate limits and keyless access](https://docs.firecrawl.dev/rate-limits)
- [Firecrawl MCP documentation](https://docs.firecrawl.dev/mcp-server)
- [Official Firecrawl MCP repository](https://github.com/firecrawl/firecrawl-mcp-server)
- [Firecrawl Python SDK](https://pypi.org/project/firecrawl-py/)
- [Firecrawl JavaScript SDK](https://www.npmjs.com/package/firecrawl)
- [Firecrawl LangChain integration](https://docs.firecrawl.dev/integrations/langchain)
- [Parallel Search reference](https://docs.parallel.ai/api-reference/search/search)
- [Parallel Extract reference](https://docs.parallel.ai/api-reference/extract/extract)
- [Parallel Task quickstart](https://docs.parallel.ai/task-api/task-quickstart)
- [Parallel Monitor](https://docs.parallel.ai/monitor-api/monitor-quickstart)
