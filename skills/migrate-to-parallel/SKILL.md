---
name: migrate-to-parallel
description: Migrate Exa, Tavily, Perplexity, or Firecrawl web-data integrations completely to the appropriate Parallel products while preserving application behavior. Use when replacing these providers' SDKs or REST calls, dependencies, environment variables, request parameters, response parsing, model tools, search-plus-scrape paths, full-content or answer-synthesis paths, tests, and documentation; separating unsupported research-index, crawl, browser, file-parse, monitor, or other non-search capabilities; auditing for leftover provider usage; or finishing and verifying an in-progress provider migration.
---

# Migrate to Parallel

Replace the provider boundary end to end. Treat a successful HTTP response as the midpoint, not completion: migrate request construction, response consumers, dependencies, configuration, tests, and operational behavior.

Resolve `<skill-root>` to the directory containing this `SKILL.md`. Resolve every bundled reference and script from that directory, regardless of the current working directory. The scanner uses only the Python standard library. If Python 3.9 or newer is unavailable, perform equivalent repository searches with the harness's file-search tools and state that the bundled scan was not run.

## Load the right references

1. Read [references/exa.md](references/exa.md) when the repository contains Exa.
2. Read [references/tavily.md](references/tavily.md) when the repository contains Tavily.
3. Read [references/perplexity.md](references/perplexity.md) when the repository contains Perplexity Search, Sonar, Agent API web tools, or a Perplexity search wrapper.
4. Read [references/firecrawl.md](references/firecrawl.md) when the repository contains Firecrawl Search, Scrape, Batch Scrape, Extract, Agent, Research Index, Crawl, Map, Parse, Browser, Interact, Monitor, or MCP usage.
5. Read [references/parallel-search.md](references/parallel-search.md) when any call may route to Search or needs query, filter, freshness, mode, or result-list migration.
6. Read [references/parallel-products.md](references/parallel-products.md) when any call may route to Extract, Chat, Task, or entity discovery, or needs streaming, structured output, or citations.
7. Read [references/integration-patterns.md](references/integration-patterns.md) when queries are generated dynamically, the provider is exposed as a model tool, provider response types escape into multiple modules, or the application needs full content or synthesized answers.
8. Open current official documentation for any detected SDK, wrapper, parameter, or response field not covered by those references. Do not guess at provider behavior.

## Preserve these invariants

- Preserve caller-visible behavior unless the user explicitly authorizes a change.
- Never silently drop a filter, content field, synthesized answer, image, safety control, or score-based decision.
- Never print API keys or secret values. Check only whether a key is present.
- Do not add a hidden LLM call merely to manufacture `search_queries`.
- Do not treat an arbitrary user prompt as a keyword query merely because it fits an API length limit.
- Keep web-research intent, hard filters, handler policy, and answer-synthesis instructions in their separate contracts.
- Treat omitted provider parameters as behavior too: inspect their defaults before omitting a Parallel setting.
- Do not recreate the entire legacy provider SDK behind a compatibility shim. Normalize only the contract the application actually uses.
- Do not remove credentials from external secret managers or provider dashboards unless the user explicitly asks. Remove obsolete code references and update checked-in templates.
- Treat mode mappings as starting points. Verify latency, quality, and output behavior with the application's real queries.
- Stop before destructive edits when a required behavior has no supported Parallel equivalent and no in-scope substitute. Report the exact gap and the smallest decision needed.
- Stop when the Perplexity boundary requires embeddings; they are not a Parallel Search replacement. Route `finance_search` through Parallel's general index using Search, Chat, or Task according to the consumed contract, and stop only when a hard market-data coverage, freshness, or raw-result requirement remains unpreserved. Keep Agent API model routing, sandbox, MCP, and existing custom-function capabilities separate unless the user explicitly expands the migration scope.
- Stop when the Firecrawl boundary requires complete crawling or URL mapping, local/private file parsing, browser actions or sessions, screenshots or other rich scrape formats, change tracking, or Firecrawl-specific privacy/security controls without an approved replacement. Search and Extract do not reproduce those contracts.
- Follow repository-local instructions such as `AGENTS.md`, `CLAUDE.md`, and `CONTRIBUTING.md`. Preserve unrelated work and never reset or discard user changes.
- Complete safe repository-local migration work without stopping after an inventory or plan. Do not commit, push, change hosted secrets, or alter provider accounts unless the user asks.

## 1. Inventory the real migration surface

Record the current branch and working-tree state before editing. Run the bundled scanner from the target repository:

```bash
python3 <skill-root>/scripts/scan_provider_usage.py .
```

Use `--format json` for machine-readable output. The scanner intentionally skips dependency/generated directories, binaries, unreadable files, and oversized files; it cannot identify provider-neutral consumers from field names alone. Treat it as an inventory aid, not proof of completeness. Inspect the results and then trace each provider response to its consumers. Also inspect:

- package manifests and lockfiles;
- direct REST endpoints and auth headers;
- SDK clients, async clients, wrappers, and model-tool definitions;
- environment schemas, examples, deployment config, and docs;
- request builders, retries, timeouts, caches, observability, and error handling;
- response fields used for rendering, ranking, thresholds, citations, or model context;
- Firecrawl crawl, batch, extract, browser, interaction, webhook, and job-lifecycle consumers;
- tests, mocks, fixtures, and snapshots.

Run the existing focused tests before editing when feasible. Record which behavior is currently covered, which failures are pre-existing, and which behavior must be verified manually.

Before editing, write a decision row for every provider call site:

| Call site | Provider product | Consumed behavior | Parallel route | Semantic gap | Action |
| --- | --- | --- | --- | --- | --- |
| `path:line` | Search, Scrape, Agent, etc. | Inputs, outputs, lifecycle, and policy the caller relies on | Exact product path, if any | Anything the route cannot preserve | `migrate`, `retain`, or `block` |

Choose exactly one action before changing the call:

- `migrate` only when the proposed route preserves the consumed contract or the user has already approved the named difference;
- `retain` when the call is outside the migration boundary or is the smallest safe way to preserve an unsupported capability;
- `block` when the requested boundary cannot be completed without a user decision. Name the smallest decision, and continue any independent `migrate` rows.

Do not use a broader Parallel product merely to eliminate a provider import. A plausible result shape is not evidence that source scope, spend controls, model behavior, lifecycle, or privacy policy remains equivalent.

## 2. Choose the migration boundary

Consider both designs before editing:

- **Direct replacement:** Use when provider calls are few, nearby, and provider-specific response types do not escape. Replace each call and its consumers atomically.
- **Application-owned web-data module:** Use when calls are scattered, several Parallel products are needed, or provider fields escape into the application. Put request construction, response normalization, retries, and telemetry behind one small caller-facing interface. Make this a deep module that hides provider details; do not add a pass-through wrapper.

Prefer the design that localizes future search-provider changes and minimizes edits to unrelated callers. If the application publishes the old provider's raw response, either preserve only the documented application contract through a normalizer or update all consumers together.

## 3. Migrate requests intentionally

Build every Parallel Search API request around these facts:

- `search_queries` is required. Supply at least one non-empty keyword query; use two or three diverse keyword queries when the calling flow can provide them.
- `objective` is optional but recommended. Put the self-contained web-research goal there, not the whole user conversation or answer-format instructions.
- Use `https://api.parallel.ai/v1/search`, `x-api-key`, and `PARALLEL_API_KEY` for direct REST calls.
- Use the official `parallel-web` package for both Python and TypeScript unless the detected framework has a current first-party Parallel integration that preserves the needed contract.

Classify every legacy input before translating it:

- full web-research goal, context, or soft source/freshness preference → `objective`;
- concise retrieval probes → `search_queries`;
- must-only or must-never source restrictions → `advanced_settings.source_policy`;
- answer format, synthesis instructions, structured output, or streaming → the existing synthesis layer, Chat API, or Task API;
- latency, result count, cache, and excerpt controls → application-owned policy chosen and tested explicitly.

For static calls, write an explicit objective and two or three keyword probes. For model tools, use the exact-three-query schema in [references/integration-patterns.md](references/integration-patterns.md). A one-query direct-call fallback is only for an already keyword-style legacy value and must be evaluated. Do not silently truncate intent, invent keyword variants, add a hidden planner, or move hard filters into prose.

Apply the provider mapping only after that classification. Preserve only settings that implement a real product requirement; unnecessary `advanced_settings` can reduce quality.

Validate runtime values against the Parallel V1 contract before sending them. Pay particular attention to query count/length, objective length, the combined 200-domain limit, date normalization, and supported location codes. Do not carry the old provider's numeric ranges forward implicitly.

## 4. Migrate response behavior

Update every consumer to the Parallel response shape. The Search API returns ranked `results` with `url`, optional `title`, optional `publish_date`, and an `excerpts` array. It does not return the old provider's relevance score, generated answer, image fields, response time, or full-page body.

Preserve field semantics, not just field names. A date-only `publish_date` does not restore an old timestamp's time-of-day precision, a `search_id` is not a session identifier, and SKU usage counts are not provider credits or dollar cost. Normalize only when the application contract defines the conversion; otherwise make the contract change explicit.

Route non-search behavior explicitly:

- Use Search API excerpts directly for LLM context or concise evidence.
- Use the Extract API for full content from known result URLs, reusing the Search API `session_id`.
- Use the Chat API or the application's existing model for a grounded answer.
- Use the Task API for asynchronous multi-step research or structured synthesis.
- Use Entity Search for synchronous people or company discovery.

For Firecrawl, classify the product before choosing a route. Search generally maps to Search; public-URL markdown or full content may map to Extract; structured multi-page research may map to Task only when Task preserves the required source scope, spend policy, quality choice, and lifecycle. Exact known-URL structured extraction instead favors Extract plus an application-owned model/parser. Research Index, Crawl, Map, Parse uploads, Browser, Interact, Monitor, screenshots, and other rich scrape behavior are not Search field mappings. Follow [references/firecrawl.md](references/firecrawl.md) and preserve separate capabilities until an explicit replacement is approved.

Do not fill missing fields with plausible-looking constants. Remove obsolete consumers, redesign the application contract, or use the appropriate Parallel API.

## 5. Replace dependencies and configuration

- Add only the SDKs required by the chosen routes: `parallel-web` for Search, Extract, or Task; `openai` for Chat unless the application already has a compatible client; no SDK when direct REST is the simpler existing pattern.
- Remove a legacy provider package only when no `retain` row still depends on it, then regenerate the lockfile with the repository's package manager.
- Replace provider imports, client initialization, endpoints, and headers only inside `migrate` rows. Keep shared provider setup until retained calls have their own explicit boundary.
- Add `PARALLEL_API_KEY` to checked-in environment templates, validation schemas, setup scripts, deployment manifests, examples, and docs. Remove a legacy key from those surfaces only when no retained runtime capability still needs it.
- Preserve existing timeout, retry, cancellation, and logging behavior where the Parallel SDK supports it; otherwise implement the behavior at the application boundary and test it.
- Keep error messages provider-neutral unless the provider name helps the operator act.

Never expose or rewrite real secret values in logs, reports, patches, or fixtures.

## 6. Verify behavior, not just syntax

Add or update tests for:

- request construction, including `search_queries`, mode, filters, dates, and location;
- source-policy normalization for apex domains, subdomains, schemes, paths, wildcards, conflicting lists, and provider-specific limits;
- query-design behavior: static requests, direct one-query compatibility paths, and model-tool schemas;
- omitted legacy defaults, dual domain lists, and any approved semantic change;
- target-limit validation for dynamic queries and domain lists;
- response parsing and excerpt joining;
- empty results, missing optional titles/dates, warnings, and errors;
- any normalizer that preserves an application-owned contract;
- full-content, synthesis, or entity routes when used;
- removal of score thresholds or provider-specific fields.

Preserve the repository's test execution contract. If its focused tests previously stubbed the provider package and ran without installing that SDK, stub the replacement SDK or keep imports behind the injected boundary too. Rerun the exact pre-migration test command in an equivalently clean environment; a pass that depends on an ambient package is not evidence that the repository remains self-contained.

Then run, in order:

1. the narrow migration tests;
2. the repository's formatter, type checker, lint, build, and broader tests as appropriate;
3. `python3 <skill-root>/scripts/scan_provider_usage.py . --provider <legacy-provider> --fail-on-legacy` when that provider is being removed completely;
4. when approved non-search Perplexity or Firecrawl usage remains, run the provider scan without `--fail-on-legacy`, classify every finding, and then scan only the migrated roots or use narrow `--exclude` paths for isolated retained modules; never exclude a mixed search/non-search boundary;
5. an independent case-insensitive search for `exa`, `tavily`, `perplexity`, `sonar-`, `firecrawl`, exact `model` assignments to `sonar`, routed `perplexity/sonar` model IDs, package names, endpoints, and key names, excluding `<skill-root>` if the skill is installed inside the target repository;
6. a review of the final diff for unintended behavior changes, leaked values, unrelated edits, and stale lockfiles;
7. a live smoke test only when provider calls are explicitly authorized for this task and `PARALLEL_API_KEY` is already available, without printing it.

An ambient credential does not by itself authorize a paid network call. When authorized, use a small, non-sensitive synthetic query and inspect `warnings`, result ordering, excerpts, and error behavior. Compare representative production queries only when the user approves sending them to both providers or an existing repository test policy already permits that exact comparison. Do not require the user to paste secrets.

## Completion gate

Finish only when all applicable statements are true:

- No legacy-provider runtime dependency, import, endpoint, auth header, key reference, tool definition, fixture, or stale setup instruction remains inside the migrated boundary.
- Any Perplexity model-routing, embeddings, sandbox, MCP, or custom-function capability outside that boundary remains intact or is called out as an explicit blocker.
- Any migrated `finance_search` path preserves the consumed final-answer or `finance_results` contract through an evaluated Parallel route and, when needed, an application-owned normalizer; unresolved hard coverage or freshness requirements are explicit blockers.
- Any Firecrawl crawl, map, file-parse, browser, interaction, rich-format, change-tracking, security/privacy, MCP, or asynchronous-job capability outside that boundary remains intact or is called out as an explicit blocker.
- Every inventoried call has a recorded `migrate`, `retain`, or `block` decision, and no `block` row was edited as though the gap were resolved.
- Firecrawl exact-URL constraints, per-run credit ceilings, `spark-1-*` model choices, and synchronous/asynchronous behavior are preserved or changed only with explicit approval; a domain allow-list, omitted budget, or guessed Task processor does not satisfy this gate.
- Every used request feature and response field has an implemented Parallel path or an explicitly approved behavior change.
- Query construction preserves the research goal, uses keyword-shaped retrieval probes, and follows the applicable direct-call or model-tool contract.
- Source-policy migration preserves the intended URL scope; unsupported path or wildcard behavior is implemented explicitly or recorded as an approved gap.
- Tests and static checks pass, or unrelated pre-existing failures are identified with evidence.
- The provider-specific legacy scan passes when the provider was removed completely. Otherwise, every remaining finding belongs to an approved, isolated non-search boundary and every identified response has been traced through its downstream consumers.
- A live call passes when it was explicitly authorized and credentials are available; otherwise the missing live verification is stated clearly.
- The final report names the migrated boundary, important semantic choices, verification commands, and any external secret cleanup still left to the operator.
