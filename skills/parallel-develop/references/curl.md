# cURL recipe — raw HTTP

All calls use header `x-api-key: $PARALLEL_API_KEY`. Get a key at [platform.parallel.ai](https://platform.parallel.ai).

```bash
export PARALLEL_API_KEY="your-api-key"
```

## Snippets by use case

### Web Search — `POST /v1/search`

```bash
# Best practices:
#   - Provide both "objective" and "search_queries" (2-3 short keyword queries).
#   - Modes: "basic" = lowest latency, "advanced" = higher recall.
#   - advanced_settings.source_policy restricts/blocks domains;
#     advanced_settings.fetch_policy.max_age_seconds controls freshness;
#     advanced_settings.location (ISO 3166 alpha-2) for geo-targeting.
curl -X POST https://api.parallel.ai/v1/search \
  -H "Content-Type: application/json" \
  -H "x-api-key: $PARALLEL_API_KEY" \
  -d '{
    "objective": "Find the latest information about <TOPIC>",
    "search_queries": ["<query 1>", "<query 2>"],
    "mode": "advanced",
    "max_chars_total": 27000,
    "advanced_settings": {
      "max_results": 10,
      "excerpt_settings": {"max_chars_per_result": 10000}
    }
  }'
```

### Research / structured task — `POST /v1/tasks/runs`

```bash
# Processors: lite/base (simple), core (~10 output fields), pro/ultra (deep).
# Append "-fast" for lower latency (e.g. "core-fast", "pro-fast").
# For pro/ultra tasks prefer a webhook over polling.

# 1. Create a task run and capture the run_id
RUN_ID=$(curl -s -X POST https://api.parallel.ai/v1/tasks/runs \
  -H "Content-Type: application/json" \
  -H "x-api-key: $PARALLEL_API_KEY" \
  -d '{
    "input": "<your research question>",
    "task_spec": {
      "output_schema": "A summary, key findings, and sources"
    },
    "processor": "core"
  }' | jq -r '.run_id')

# 2. Get the result (?timeout=N in seconds; max 600. Re-poll on timeout.)
curl -X GET "https://api.parallel.ai/v1/tasks/runs/$RUN_ID/result?timeout=600" \
  -H "x-api-key: $PARALLEL_API_KEY"
```

### Data enrichment — same endpoint, structured schema

```bash
# Processors: lite/base (1-2 fields), core (up to ~10 fields), pro (complex).

RUN_ID=$(curl -s -X POST https://api.parallel.ai/v1/tasks/runs \
  -H "Content-Type: application/json" \
  -H "x-api-key: $PARALLEL_API_KEY" \
  -d '{
    "input": "<entity, e.g. Stripe>",
    "task_spec": {
      "output_schema": {
        "type": "json",
        "json_schema": {
          "type": "object",
          "properties": {
            "founding_date": {
              "type": "string",
              "description": "Founding date in MM-YYYY format. Return \"Not Available\" if unknown."
            },
            "employee_count": {
              "type": "string",
              "description": "Estimated employee count as a range, e.g. \"500-1000\"."
            },
            "funding_sources": {
              "type": "string",
              "description": "Funding sources and total raised in USD."
            }
          },
          "required": ["founding_date", "employee_count", "funding_sources"]
        }
      }
    },
    "processor": "core"
  }' | jq -r '.run_id')

curl -X GET "https://api.parallel.ai/v1/tasks/runs/$RUN_ID/result?timeout=600" \
  -H "x-api-key: $PARALLEL_API_KEY"
```

### Lead discovery — `POST /v1beta/findall/runs`

```bash
# Start with "preview" generator to validate your query (~10 candidates, fast, cheap).
# Generators: preview (test), base (broad), core (specific), pro (rare matches).

FINDALL_ID=$(curl -s -X POST https://api.parallel.ai/v1beta/findall/runs \
  -H "Content-Type: application/json" \
  -H "x-api-key: $PARALLEL_API_KEY" \
  -d '{
    "objective": "<e.g. AI startups that raised Series A in 2024>",
    "entity_type": "companies",
    "match_conditions": [
      {
        "name": "series_a_2024",
        "description": "Company raised a Series A in 2024, confirmed by TechCrunch/Crunchbase/PR."
      },
      {
        "name": "ai_focused",
        "description": "Primary product must be AI-focused (LLMs, ML infra, or AI apps)."
      }
    ],
    "generator": "core",
    "match_limit": 20
  }' | jq -r '.findall_id')

# May take several minutes for core/pro. Use a webhook for large runs.
curl -X GET "https://api.parallel.ai/v1beta/findall/runs/$FINDALL_ID/result" \
  -H "x-api-key: $PARALLEL_API_KEY"
```

### Web Monitoring — `POST /v1alpha/monitors`

```bash
# Natural-language query focused on intent, not keywords.
# Cadence: "hourly" (fast-moving), "daily" (most news), "weekly" (slow-changing).
# Don't include dates — Monitor tracks new updates automatically.
# "simulate_event": true forces an immediate test event during development.
curl -X POST https://api.parallel.ai/v1alpha/monitors \
  -H "Content-Type: application/json" \
  -H "x-api-key: $PARALLEL_API_KEY" \
  -d '{
    "query": "<e.g. latest news about AI regulation>",
    "cadence": "daily",
    "webhook": {
      "url": "https://your-app.com/webhook",
      "event_types": ["monitor.event.detected"]
    }
  }'
```

Response shape: `{ "monitor_id": "...", "status": "...", "cadence": "...", "query": "...", ... }`.

### Content extraction — `POST /v1/extract`

```bash
# Always provide an "objective" — extraction is LLM-focused, not a raw scrape.
# Up to 20 URLs per call. PDFs and JS-heavy pages are handled.
# "full_content": true only when you need the whole page as markdown.
# "fetch_policy": {"max_age_seconds": 3600} for cache-vs-live control.
curl -X POST https://api.parallel.ai/v1/extract \
  -H "Content-Type: application/json" \
  -H "x-api-key: $PARALLEL_API_KEY" \
  -d '{
    "urls": ["https://example.com/article"],
    "objective": "<what to focus on in the page>",
    "excerpt_settings": {"max_chars_per_result": 5000}
  }'
```

## Error handling

- Non-2xx responses return `{ "error": { "message": "...", "type": "..." } }`. Check HTTP status first, then inspect the body.
- For 429 (rate limit), back off with exponential delay.
- For 5xx, retry with jitter. Runs that have been *created* are durable — refetch with the `run_id` / `findall_id` rather than recreating.
