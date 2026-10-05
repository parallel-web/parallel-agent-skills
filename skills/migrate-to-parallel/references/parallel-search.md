# Parallel Search reference

Verified against the official Parallel V1 OpenAPI and docs on 2026-07-14. Recheck the linked sources when the installed SDK or API has changed.

## Contents

- [Request contract](#request-contract)
- [Domain policy normalization](#domain-policy-normalization)
- [Mode and default decisions](#mode-and-default-decisions)
- [Auth and SDKs](#auth-and-sdks)
- [Response contract](#response-contract)
- [Product routing](#product-routing)
- [Official sources](#official-sources)

## Request contract

| Field | Current contract |
| --- | --- |
| `search_queries` | Required array of concise keyword probes. Docs recommend 2–3 diverse queries of 3–6 words; model tools should require exactly 3. Maximum 5 queries and 200 characters per query. |
| `objective` | Optional self-contained natural-language web-research goal. Put context, soft source preference, and freshness preference here; keep answer-format instructions elsewhere. Docs list a 5,000-character maximum. |
| `mode` | `turbo`, `basic`, or `advanced`; omission defaults to `advanced`. `turbo` targets the lowest latency/cost, `basic` lower latency, and `advanced` deeper retrieval/compression. |
| `max_chars_total` | Optional upper bound across all returned excerpts. Default is dynamic. |
| `client_model` | Optional consuming-model identifier used to tune defaults. |
| `session_id` | Optional string up to 1,000 characters. Reuse it across Search API and Extract API calls for one logical task. |
| `advanced_settings.max_results` | Optional upper bound; default is 10. |
| `advanced_settings.location` | ISO 3166-1 alpha-2 code such as `us`, `gb`, `de`, or `jp`. Support is a subset; inspect response warnings. |
| `advanced_settings.source_policy` | `include_domains`, `exclude_domains`, and `after_date`. Use one domain-list type per request: `include_domains` is a hard allow-list, and it takes precedence if both are sent. The combined limit is 200. Normalize entries with the rules below. `after_date` is an inclusive `YYYY-MM-DD` lower bound. |
| `advanced_settings.excerpt_settings` | `max_chars_per_result`. Omit unless the application has a real per-result budget. |
| `advanced_settings.fetch_policy` | `max_age_seconds`, `timeout_seconds`, and `disable_cache_fallback`. Live fetch increases latency; documented minimum cache age is 600 seconds. |

Search generally supports multilingual queries, but Turbo currently supports only queries in English and Japanese. Use Basic or Advanced for broader multilingual coverage. Treat this as part of mode selection when the legacy input language is dynamic.

## Domain policy normalization

Preserve the set of allowed or blocked URLs, not just the strings in the old array. Parallel's OpenAPI accepts plain domains, including subdomains, and bare domain extensions such as `.org`. Current source-policy guidance recommends apex domains, omitting schemes and `www.`, and does not support paths. An apex entry includes all of its subdomains, so converting an exact subdomain or path-qualified rule to an apex domain can silently broaden access.

Classify every legacy entry before translating it:

- Map a plain domain or subdomain only when Parallel's matching scope is equivalent.
- Do not mechanically strip a scheme, `www.`, or another subdomain prefix when doing so changes the allowed or blocked set.
- Treat URL paths as unsupported by source policy. Preserve them with an application-owned URL filter only if the resulting retrieval and recall behavior is acceptable; otherwise stop for a design decision.
- Translate wildcard or suffix patterns only after verifying that they match the same host set. Do not assume provider forms such as `*.example.com` or `*.com` are equivalent to Parallel's bare-extension form.
- If both include and exclude lists were effective in the legacy request, derive the intended combined policy before sending one Parallel list. Parallel ignores `exclude_domains` when `include_domains` is present.
- Reject, split with an explicit merge contract, or obtain approval for more than 200 combined entries. Never truncate or silently broaden the policy.

## Mode and default decisions

Treat provider-tier names as evidence, not equivalents. Choose Turbo only for an explicit latency-first requirement, Basic for interactive/foreground work with two or three good retrieval probes, and Advanced for quality-first or background work. Advanced is the omission default.

Inspect omitted provider values too. For example, a legacy provider's default result count or mode can differ from Parallel's default even when the call site sends no parameter. Preserve that behavior explicitly or record and test the approved change.

## Auth and SDKs

REST:

```bash
curl https://api.parallel.ai/v1/search \
  -H "Content-Type: application/json" \
  -H "x-api-key: $PARALLEL_API_KEY" \
  -d '{"objective":"...","search_queries":["..."]}'
```

Python:

```python
from parallel import Parallel

client = Parallel()  # reads PARALLEL_API_KEY
response = client.search(
    objective="Find the latest official release information.",
    search_queries=["official release notes", "latest product release"],
    mode="basic",
)
```

Install with `pip install parallel-web`.

Use `AsyncParallel` and await `client.search(...)` when the migrated path is asynchronous.

TypeScript:

```typescript
import Parallel from "parallel-web";

const client = new Parallel(); // reads PARALLEL_API_KEY
const response = await client.search({
  objective: "Find the latest official release information.",
  search_queries: ["official release notes", "latest product release"],
  mode: "basic",
});
```

Install with `npm install parallel-web`.

The current TypeScript SDK uses the API's snake_case request and response fields. Both official SDK registries published version `1.1.0` when this reference was verified; inspect the installed version before relying on an exact method signature.

## Response contract

```json
{
  "search_id": "search_...",
  "results": [
    {
      "url": "https://example.com",
      "title": "Example",
      "publish_date": "2026-07-10",
      "excerpts": ["Relevant markdown excerpt"]
    }
  ],
  "warnings": null,
  "usage": [{"name": "sku_search_additional_results", "count": 1}],
  "session_id": "session_..."
}
```

`search_id`, `results`, and `session_id` are required. Each result requires `url` and `excerpts`; `title` and `publish_date` may be null. Results are already ordered by decreasing relevance. `warnings` contains `{type, message, detail?}` objects. Treat unknown warning types as forward-compatible. `usage` is a list of SKU counts, not a relevance score or dollar-cost field.

The Search API OpenAPI declares a `422` validation response shaped as `{type: "error", error: {ref_id, message, detail?}}`. Preserve useful application-level timeout/retry handling, but do not assume another provider's status or exception taxonomy transfers unchanged.

## Product routing

| Required behavior | Use |
| --- | --- |
| Ranked pages with concise evidence | Search API |
| Relevant or full content from known URLs | Extract API; reuse `session_id` |
| Low-latency grounded completion | Chat API or the application's existing model over Search API excerpts |
| Multi-step research, citations, or structured synthesis | Task API |
| Fast people/company candidates | Entity Search |
| Verified, enriched people/company list | FindAll API |

## Official sources

- [Search OpenAPI](https://docs.parallel.ai/public-openapi.json)
- [Search API reference](https://docs.parallel.ai/api-reference/search/search)
- [Search quickstart](https://docs.parallel.ai/search/search-quickstart)
- [Search best practices](https://docs.parallel.ai/search/best-practices)
- [Search modes](https://docs.parallel.ai/search/modes)
- [Advanced Search settings](https://docs.parallel.ai/search/advanced-search-settings)
- [Source policy](https://docs.parallel.ai/resources/source-policy)
- [Beta-to-V1 migration guide](https://docs.parallel.ai/search/search-migration-guide)
- [Search and Extract global/multilingual update](https://parallel.ai/blog/parallel-search-api)
- [Extract quickstart](https://docs.parallel.ai/extract/extract-quickstart)
- [Task deep research](https://docs.parallel.ai/task-api/examples/task-deep-research)
- [Chat quickstart](https://docs.parallel.ai/chat-api/chat-quickstart)
- [Entity Search](https://docs.parallel.ai/findall-api/entity-search)
