# Python recipe — `parallel-web`

## Install

```bash
pip install parallel-web     # or: uv add parallel-web
export PARALLEL_API_KEY="your-api-key"   # get one at https://platform.parallel.ai
```

The SDK reads `PARALLEL_API_KEY` from the environment automatically. Use `Parallel(api_key=...)` to override.

## Snippets by use case

Pick the block that matches the user's goal, drop it into a script in their repo, and wire in their topic/entity/URL.

### Web Search — `client.search`

```python
from parallel import Parallel

client = Parallel()

# Best practices:
#   - Provide BOTH objective (what/why) and search_queries (2-3 short
#     keyword queries, 3-6 words each). Either alone works; together is best.
#   - Modes: "basic" = lowest latency, "advanced" = higher recall + reranking.
#   - advanced_settings.source_policy restricts/blocks domains.
#   - advanced_settings.fetch_policy.max_age_seconds for freshness control.
#   - advanced_settings.location (ISO 3166 alpha-2) for geo-targeting.
search = client.search(
    objective="Find the latest information about <TOPIC>",
    search_queries=["<query 1>", "<query 2>"],
    mode="advanced",
    max_chars_total=27000,
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

```python
from parallel import Parallel

client = Parallel()

# Processors (pick based on complexity + latency budget):
#   lite / base  — simple lookups, single-hop facts (seconds)
#   core         — up to ~10 output fields, light research (30 s – 2 min)
#   pro / ultra  — deep, multi-hop research (2 – 25 min; use webhooks!)
#   append "-fast" for lower-latency variants (e.g. "core-fast", "pro-fast")
task_run = client.task_run.create(
    input="<your research question or entity>",
    task_spec={
        "output_schema": {
            "type": "json",
            "json_schema": {
                "type": "object",
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

# Enrichment best practices:
#   - Name fields specifically (ceo_name, not name).
#   - Put EXACT format requirements in each description ("MM-YYYY", "USD",
#     "ISO 3166-1 alpha-2"). The model honors descriptions tightly.
#   - Tell the model what to do when data is missing ("Return 'Not Available'
#     if no source confirms"). This prevents hallucination.
#   - Mark fields "required" only if the task should fail without them.
task_run = client.task_run.create(
    input="<entity, e.g. 'Stripe'>",
    task_spec={
        "output_schema": {
            "type": "json",
            "json_schema": {
                "type": "object",
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
print(result.output)

# For batches (say, 50+ rows), use client.beta.task_group.create(...) and
# stream events, or pass a webhook — polling per row is wasteful.
```

### Lead discovery — `client.beta.findall`

```python
from parallel import Parallel

client = Parallel()

# Best practices:
#   - START with generator="preview" — ~10 candidates in seconds, low cost.
#     Iterate on objective + match_conditions cheaply before scaling up.
#   - Write DETAILED match_conditions. Each {name, description} is run
#     against every candidate for verification. Detailed = higher precision.
#   - Generators: preview (test), base (broad/common), core (specific),
#                 pro (rare/hard-to-find, most thorough).
#   - For large runs, pass a webhook instead of polling .result().
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

```python
from parallel import Parallel

client = Parallel()

# Best practices:
#   - Always provide an "objective" — extraction ranks excerpts by relevance.
#   - Add search_queries alongside objective to emphasize specific keywords.
#   - Up to 20 URLs per call. PDFs and JS-heavy pages are handled.
#   - Set full_content=True only when you need the whole page as markdown —
#     excerpts are usually enough and much cheaper.
#   - fetch_policy.max_age_seconds controls cache-vs-live freshness.
extract = client.extract(
    urls=["https://example.com/article"],
    objective="<what to focus on in the page>",
    excerpt_settings={"max_chars_per_result": 5000},
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
