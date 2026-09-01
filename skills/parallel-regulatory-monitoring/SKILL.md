---
name: parallel-regulatory-monitoring
description: Watch regulators, courts, and lists and get alerted the moment something changes, a new rule or rulemaking, an enforcement action, a docket/filing update, a sanctions or watchlist change, deduped so you only hear about real changes and each one structured and cited so it can route to the right person. Use when the user wants to "monitor for new regulations", "alert me when X files/gets sued/gets sanctioned", "track this docket", or set up change-based legal alerts. Runs on the user's own Parallel account via Monitor.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(curl:*)
metadata:
  author: parallel
---

# Regulatory Monitoring

Watch the sources that matter, regulators, courts, official registries, sanctions lists, and
get alerted the moment something changes: a new rule or rulemaking, an enforcement action, a
docket or filing update, a sanctions/watchlist change. Dedup is handled, so you only hear
about real changes, and each event is structured and cited so it can route straight to the
right attorney or workflow.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

- **CLI / build-on-top:** the installed **`parallel-monitor`** skill (`parallel-cli skills
  install`) is the maintained path.
- Monitor is the stable `v1` API; the raw endpoint is included below for pipelines.

If Parallel is not configured, run the relevant setup skill first. See [docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its jurisdiction / priority framing (captured once at setup), don't re-ask it; only get the per-run specifics below.

Before creating monitors (each is a recurring, billable watch):
1. **Watch what?** The entities, dockets, regulators, or topics to track (one monitor per subject or per source).
2. **Which changes?** Default: new rules/rulemaking, enforcement actions, docket/filing updates, sanctions/watchlist changes. Trim to what you act on.
3. **Cadence?** Daily (`1d`) is the usual default; move to hourly only where latency matters (e.g. a live docket).

Confirm, then create.

## Run it

The shape that works: run **one broad monitor per subject** (an entity, a docket, a regulator
feed) and classify the change downstream, not one monitor per change type. It's far cheaper
per record and dedups cleanly. A monitor runs on a schedule, catches new matches going
forward, and returns structured output.

Output shape per detected change:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["change_type", "summary", "change_date", "source_url"],
  "properties": {
    "change_type": {"type": "string", "enum": ["new_rule", "rulemaking", "enforcement_action", "docket_update", "new_filing", "sanctions_change", "regulatory_guidance", "other"]},
    "subject":     {"type": "string", "description": "the entity, docket, or topic this monitor watches"},
    "summary":     {"type": "string", "description": "one-line factual summary of what changed"},
    "change_date": {"type": "string", "description": "ISO 8601 date"},
    "route_to":    {"type": "string", "description": "who/what this should route to, e.g. the responsible attorney or matter"},
    "source_url":  {"type": "string", "description": "resolving source; must load (regulator page, docket, official list)"}
  }
}
```

Query per subject (substitute):

> Notify me whenever {SUBJECT} has a concrete, sourced change: a new rule or rulemaking, an
> enforcement action, a docket or filing update, a change to its sanctions/watchlist status,
> or new regulatory guidance. Prioritize named, dated, officially-sourced changes from the
> regulator, court, or official list. Exclude commentary, rumor, and secondary summaries.

## Config seams (build on top)

1. **Subjects**: one monitor per entity, docket, or regulator feed you're tracking (loop your list).
2. **Change types**: edit the `change_type` enum + the query to what you act on.
3. **Cadence**: daily (`1d`) is the usual default; hourly costs ~24x for the same volume
   over a day, cadence controls latency, not how much you catch. Use hourly only for live dockets.
4. **Routing**: `route_to` + an optional webhook push each change into your matter system.
5. **Processor**: `lite` is the cheap forward-watch default; `base` for heavier scans.

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ `POST /v1/monitors`
(`type: event_stream`, `frequency`, `processor`, `settings.query`, `settings.output_schema`),
read hits at `GET /v1/monitors/{id}/events`, optional `webhook` to push. `event_stream` only
catches change **going forward**, seed the current state with a Task first if you need it now.
Auth via `x-api-key`, same key creates and reads.

## Next

- Pair with **entity-diligence** so a fresh change arrives already attached to a tear sheet.
- Feed subjects in from **exposure-discovery** (monitor the whole population).
- On a triggered change, pull the primary text → **source-grounded-research**.
