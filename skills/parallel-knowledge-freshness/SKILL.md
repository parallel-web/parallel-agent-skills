---
name: parallel-knowledge-freshness
description: Keep a feed or knowledge base current, watch the topics, sources, and entities your users care about and surface an update the moment something changes, deduped and cited, to power live feeds, alerts, and always-current knowledge. Use when the user wants to "keep my feed fresh", "update my product when X changes", "power a live feed", or keep a knowledge base current. Runs on the user's own Parallel account via Monitor.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(curl:*)
metadata:
  author: parallel
---

# Knowledge Freshness

Keep a feed or knowledge base **current**: watch the topics, sources, and entities your users
care about and surface an update the moment something changes. Powers live feeds, alerts, and
always-current knowledge. Dedup is handled, so your product only shows real changes, and each
update is structured and cited so it renders with a source and routes to the right user.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

- **CLI / build-on-top:** the installed **`parallel-monitor`** skill (`parallel-cli skills
  install`) is the maintained path.
- Monitor is the stable `v1` API; the raw endpoint is included below for pipelines.

If Parallel is not configured, run the relevant setup skill first. See [docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its keep_current framing (captured once at setup), that's usually
what to watch, don't re-ask it; only get the per-run specifics below.

Before creating monitors (each is a recurring, billable watch):
1. **What to watch?** The entities, topics, or sources your users track (one monitor per entity or topic).
2. **Which changes?** Default: job changes, fundraises, major announcements, and sentiment shifts. Trim to what your product surfaces.
3. **Cadence?** Daily (`1d`) is the usual default; tighter for a fast-moving feed.

Confirm, then create.

## Run it

The shape that works: run **one broad monitor per entity** (or per topic) and classify the
update downstream, not one monitor per change type. It's far cheaper per record and dedups
cleanly. A monitor runs on a schedule, catches new matches, and returns structured output your
product can render straight into a feed.

Output shape per detected update:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["change_type", "subject", "summary", "change_date", "source_url"],
  "properties": {
    "change_type": {"type": "string", "enum": ["job_change", "fundraise", "announcement", "acquisition", "sentiment_shift", "other"]},
    "subject":     {"type": "string", "description": "the entity or topic the update concerns"},
    "summary":     {"type": "string", "description": "one-line factual summary your product can show in the feed"},
    "change_date": {"type": "string", "description": "ISO 8601 date"},
    "route_to":    {"type": "string", "description": "which user / workspace this update belongs to"},
    "source_url":  {"type": "string", "description": "resolving source; must load"}
  }
}
```

Query per entity (substitute):

> Watch {ENTITY_OR_TOPIC} and notify me of any concrete, sourced change: a job change, a
> fundraise, a major announcement, an acquisition, or a clear shift in sentiment. Give a one-line
> summary, the date, and a resolving source. Prioritize named, dated, sourced facts; exclude
> rumor and generic commentary.

## Config seams (build on top)

1. **Watched set:** one monitor per entity or topic your users follow (loop from the workspace `PROFILE.md` file or your DB).
2. **Change types:** edit the `change_type` enum + the query to what your feed shows.
3. **Routing:** `route_to` maps each update to the user or workspace it belongs to (fan out from one monitor).
4. **Cadence:** daily (`1d`) default; tighter for a fast feed, cadence controls latency, not how much you catch.
5. **Processor:** `lite` is the cheap forward-watch default; `base` for heavier scans.

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ `POST /v1/monitors`
(`type: event_stream`, `frequency`, `processor`, `settings.query`, `settings.output_schema`),
read hits at `GET /v1/monitors/{id}/events`, optional `webhook` to push into your feed pipeline.
`event_stream` only catches change **going forward**, seed the current state with a Task first if
you need a baseline now. Auth via `x-api-key`, same key creates and reads.

## Next

- Act on a change instead of just showing it → **workspace-agent**.
- Enrich the entity behind an update → **entity-context**.
- Answer a user's follow-up on the update → **productivity-quickstart**.
