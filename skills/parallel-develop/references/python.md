# Python recipe — `parallel-web`

## Install

```bash
pip install 'parallel-web>=0.5,<1.0'   # or: uv add 'parallel-web>=0.5,<1.0'
export PARALLEL_API_KEY="your-api-key" # get one at https://platform.parallel.ai
```

The current minor is `0.5.x` — pin against `>=0.5,<1.0` until v1.0 ships. The SDK reads `PARALLEL_API_KEY` from the environment automatically; use `Parallel(api_key=...)` to override.

### Package / import / types

| Item | Value |
|------|-------|
| PyPI package | `parallel-web` |
| Import | `from parallel import Parallel` |
| Exceptions | `from parallel import APIError, RateLimitError, AuthenticationError, BadRequestError, InternalServerError` |
| Typed params (strict mode) | `from parallel.types import TaskSpecParam, JsonSchemaParam, TextSchemaParam` |

Typed params are optional — plain `dict` bodies work fine at runtime. Reach for the TypedDicts when your project has pyright/mypy in strict mode and the plain-dict `task_spec` argument gets flagged.

### Result shape cheat-sheet

- `client.search(...)` → `.results[i].{title, url, publish_date, excerpts: list[str]}`
- `client.extract(...)` → same shape as search results, plus optional `.results[i].full_content`
- `client.task_run.create(...)` → `.run_id` (you pass this to `.result()`)
- `client.task_run.result(run_id, api_timeout=N)` → `.output.content` is a dict matching your `json_schema` (or a string if you passed a text/bare-string schema)
- `client.beta.findall.create(...)` → `.findall_id`
- `client.beta.findall.result(findall_id=...)` → `.candidates[i].{name, url, description, ...}`

## Snippets by use case

Pick the block that matches the user's goal, drop it into a script in their repo, and wire in their topic/entity/URL.

### Web Search — `client.search`

Deep dive: [Search Best Practices](https://docs.parallel.ai/search/best-practices) · [Advanced Settings](https://docs.parallel.ai/search/advanced-search-settings) · [Modes](https://docs.parallel.ai/search/modes).

```python
from parallel import Parallel

client = Parallel()

# Best practices:
#   - Provide BOTH objective (what/why) and search_queries. Either alone works;
#     together is best. Use 2-3 queries of 3-6 words each (max 5, ≤200 chars).
#   - Modes: "basic" = lowest latency, "advanced" = higher recall + reranking.
#   - Put freshness / source preferences in the objective ("official docs",
#     "post-2024 only") rather than as extra keywords.
#   - advanced_settings.source_policy restricts/blocks domains.
#   - advanced_settings.fetch_policy.max_age_seconds for freshness control.
#   - advanced_settings.location (ISO 3166 alpha-2) for geo-targeting.
#   - session_id: pass the same UUID across related Search + Extract calls
#     in one task, so Parallel treats them as one logical workflow.
#   - client_model: declare your consuming LLM for server-side optimization.
#   - If you expose Search as a tool to an agent, expose ONLY objective and
#     search_queries. Exposing advanced_settings tempts the model to
#     over-narrow the search and hurts recall.
search = client.search(
    objective="Find the latest information about <TOPIC>",
    search_queries=["<query 1>", "<query 2>"],
    mode="advanced",
    max_chars_total=27000,
    # session_id="<shared UUID>",
    # client_model="claude-opus-4-7",
    advanced_settings={
        "max_results": 10,
        "excerpt_settings": {"max_chars_per_result": 10000},
    },
)

for result in search.results:
    print(f"{result.title}: {result.url}")
    for excerpt in result.excerpts:
        print(excerpt[:200])
```

### Research / structured task — `client.task_run`

Deep dive: [Specify a Task](https://docs.parallel.ai/task-api/guides/specify-a-task) · [Choose a Processor](https://docs.parallel.ai/task-api/guides/choose-a-processor) · [Task Run Lifecycle](https://docs.parallel.ai/task-api/guides/execute-task-run) · [Webhooks](https://docs.parallel.ai/task-api/webhooks).

```python
from parallel import Parallel

client = Parallel()

# Processors (pick based on complexity + latency budget):
#   lite / base  — simple lookups, single-hop facts (seconds)
#   core         — up to ~10 output fields, light research (30 s – 2 min)
#   pro / ultra  — deep, multi-hop research (2 – 25 min; use webhooks!)
#   append "-fast" for lower-latency variants (e.g. "core-fast", "pro-fast")
#
# Schema rules (canonical, enforced by the API):
#   - Root MUST be {"type": "object"} with "properties". Arrays cannot be root.
#   - EVERY property must appear in "required". Optional fields use a union
#     like {"type": ["string", "null"]} instead of being omitted.
#   - Set "additionalProperties": false for strict validation.
#   - Prefer flat schemas — top-level properties beat nesting for output quality.
#   - The field "description" is your primary knob: specify format, sources,
#     and missing-value behavior per field.
task_run = client.task_run.create(
    input="<your research question or entity>",
    task_spec={
        "output_schema": {
            "type": "json",
            "json_schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "summary": {"type": "string"},
                    "key_findings": {"type": "array", "items": {"type": "string"}},
                    "sources": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["summary", "key_findings", "sources"],
            },
        }
    },
    processor="core",
    # webhook={"url": "https://your-app.com/webhook", "event_types": ["task_run.status"]},
)

# Block until the task completes (api_timeout is in seconds; bump for pro/ultra)
result = client.task_run.result(task_run.run_id, api_timeout=600)
print(result.output)
```

**Shortcut:** `client.task_run.execute(input=..., processor=..., output=<TypedDict>)` creates, waits, and parses into your Python type in one call. Great for throwaway scripts.

### Data enrichment — `client.task_run` with a structured schema

```python
from parallel import Parallel

client = Parallel()

# Enrichment best practices (see specify-a-task):
#   - Name fields specifically (ceo_name, not name; headquarters_address,
#     not address).
#   - Put EXACT format requirements in each description ("MM-YYYY", "USD",
#     "ISO 3166-1 alpha-2"). The model honors descriptions tightly.
#   - Tell the model what to do when data is missing ("Return 'Not Available'
#     if no source confirms"). This prevents hallucination.
#   - Every property MUST appear in "required"; for optional fields use a
#     union like {"type": ["string", "null"]} instead of omitting.
#   - Set "additionalProperties": false.
#   - Keep schemas flat.
task_run = client.task_run.create(
    input="<entity, e.g. 'Stripe'>",
    task_spec={
        "output_schema": {
            "type": "json",
            "json_schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "founding_date": {
                        "type": "string",
                        "description": "Founding date in MM-YYYY format. Return 'Not Available' if unknown.",
                    },
                    "employee_count": {
                        "type": "string",
                        "description": "Estimated employee count as a range, e.g. '500-1000'.",
                    },
                    "funding_sources": {
                        "type": "string",
                        "description": "Funding sources and total raised in USD.",
                    },
                },
                "required": ["founding_date", "employee_count", "funding_sources"],
            },
        }
    },
    processor="core",
)

result = client.task_run.result(task_run.run_id, api_timeout=600)
print(result.output)  # result.output.content is a dict matching your json_schema
```

### Batch enrichment with Task Groups

For 50+ rows, don't call `task_run.create + result` per row — it's wasteful. Use a **Task Group**, which accepts a batch of inputs, runs them concurrently under a shared spec, and streams progress events:

```python
from parallel import Parallel

client = Parallel()

group = client.beta.task_group.create(
    default_task_spec={
        "output_schema": {
            "type": "json",
            "json_schema": {
                "type": "object",
                "properties": {
                    "ceo_name": {
                        "type": "string",
                        "description": "Current CEO full name. Return 'Not Available' if unknown.",
                    },
                    "revenue_2024": {
                        "type": "string",
                        "description": "2024 annual revenue in USD (e.g. '$5.2B'). Return 'Not Available' if unknown.",
                    },
                },
                "required": ["ceo_name", "revenue_2024"],
            },
        }
    },
)

inputs = [{"input": name, "processor": "core"} for name in ["Stripe", "OpenAI", "Anthropic"]]
client.beta.task_group.add_runs(group.taskgroup_id, runs=inputs)

# Stream events until all runs finish
for event in client.beta.task_group.events(group.taskgroup_id):
    print(event)
```

### Lead discovery — `client.beta.findall`

Deep dive: [Generators & Pricing](https://docs.parallel.ai/findall-api/core-concepts/findall-generator-pricing).

```python
from parallel import Parallel

client = Parallel()

# Best practices:
#   - ALWAYS start with generator="preview" — ~10 candidates in seconds, low
#     cost. Use it to validate your approach before committing to a big run.
#   - Match generator to expected volume:
#       base  — broad criteria, many matches from common fields
#       core  — moderate specificity, ~20-50 results
#       pro   — rare / highly specific, thoroughness > cost
#   - 0 MATCHES?  Try UPGRADING THE GENERATOR before rewriting the query.
#     Usually the issue is candidate pool size, not query quality.
#   - Write DETAILED match_conditions. Each {name, description} is run
#     against every candidate for verification. Detailed = higher precision.
#   - For large runs, pass a webhook instead of polling .result().
#   - Enrichments multiply costs across matches — validate counts in preview
#     before adding enrichments. Extend runs are cheaper than fresh ones.
findall_run = client.beta.findall.create(
    objective="<e.g. 'AI startups that raised Series A in 2024'>",
    entity_type="companies",
    match_conditions=[
        {
            "name": "series_a_2024",
            "description": (
                "Company must have raised a Series A funding round in 2024, "
                "confirmed by a reputable source (TechCrunch, Crunchbase, "
                "company press release, etc.)."
            ),
        },
        {
            "name": "ai_focused",
            "description": "Primary product must be AI-focused (LLMs, ML infra, AI apps).",
        },
    ],
    generator="core",
    match_limit=20,
)

# Blocks until complete. For core/pro this can take several minutes.
result = client.beta.findall.result(findall_id=findall_run.findall_id)

for candidate in result.candidates:
    print(f"{candidate.name}: {candidate.url}")
    print(f"  {candidate.description}")
```

### Web Monitoring — Monitor API (alpha)

Monitor is an alpha API and doesn't yet have a typed SDK resource, so call it via `httpx` directly:

```python
import os
import httpx

API_KEY = os.environ["PARALLEL_API_KEY"]

# Write queries in natural language focused on intent, not keywords.
# Cadence: "hourly" (fast-moving), "daily" (most news), "weekly" (slow-changing).
# Don't include dates — Monitor tracks new updates automatically.
# Tip: "simulate_event": True forces an immediate test event during development.
res = httpx.post(
    "https://api.parallel.ai/v1alpha/monitors",
    headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
    json={
        "query": "<e.g. 'latest news about AI regulation'>",
        "cadence": "daily",
        "webhook": {
            "url": "https://your-app.com/webhook",
            "event_types": ["monitor.event.detected"],
        },
    },
    timeout=30,
).raise_for_status().json()

print(f"Monitor created: {res['monitor_id']} (status: {res['status']})")
```

Response shape: `{ "monitor_id": str, "status": str, "cadence": str, "query": str, ... }`.

### Content extraction — `client.extract`

Deep dive: [Extract Best Practices](https://docs.parallel.ai/extract/best-practices) · [Advanced Settings](https://docs.parallel.ai/extract/advanced-extract-settings).

```python
from parallel import Parallel

client = Parallel()

# Best practices:
#   - Always provide an "objective" — extraction ranks excerpts by relevance.
#   - Add 2-3 search_queries (3-6 words each) for focus.
#   - Up to 20 URLs per call. PDFs and JS-heavy pages are handled.
#   - Set full_content=True only when you need the whole page as markdown —
#     excerpts are usually enough and much cheaper. WARNING: full_content
#     without an objective is redundant (excerpts duplicate the full page).
#   - fetch_policy.max_age_seconds controls cache-vs-live freshness.
#   - session_id: pass the SAME UUID across related Search + Extract calls
#     in one task so Parallel treats them as one logical workflow.
#   - client_model: declare your consuming LLM for server-side optimization.
extract = client.extract(
    urls=["https://example.com/article"],
    objective="<what to focus on in the page>",
    excerpt_settings={"max_chars_per_result": 5000},
    # session_id="<shared UUID>",
    # client_model="claude-opus-4-7",
    # fetch_policy={"max_age_seconds": 3600},  # uncomment for fresh content
)

for result in extract.results:
    print(f"{result.title}: {result.url}")
    for excerpt in result.excerpts:
        print(excerpt[:200])
```

## Error handling

- The SDK raises `parallel.APIError` subclasses for 4xx/5xx responses. Wrap calls in `try/except parallel.APIError as e:` and inspect `e.status_code` for retry decisions.
- `client.task_run.result(...)` can time out if the run hasn't finished within `api_timeout`. Re-call it, or better: pass a webhook and skip polling.

## Typed outputs (optional)

If the user wants typed results rather than the generic dict, use Pydantic or a TypedDict with `client.task_run.execute(..., output=MyOutput)` and it will validate + parse the output for you.
