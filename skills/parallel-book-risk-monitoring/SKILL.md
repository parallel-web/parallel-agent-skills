---
name: parallel-book-risk-monitoring
description: Watch the entities, locations, and regulations tied to your policies and get alerted the moment something material changes, adverse media, sanctions listings, litigation, catastrophe exposure, and fraud signals, deduped and cited. Use when the user wants to "monitor my book", "alert me on sanctions/catastrophe/litigation across policies", "watch these insureds", or set up book-of-business risk surveillance. Runs on the user's own Parallel account via Monitor.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(curl:*)
metadata:
  author: parallel
---

# Book Risk Monitoring

Watch the entities, locations, and regulations tied to your policies and get alerted the moment
something material changes, an adverse-media story, a sanctions listing, new litigation, a
catastrophe exposure, or a fraud signal. Dedup is handled, so you only hear about real changes,
and each alert is structured and cited so it can route straight to the underwriter or claims
handler who owns the policy.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

- **CLI / build-on-top:** the installed **`parallel-monitor`** skill (`parallel-cli skills
  install`) is the maintained path.
- Monitor is the stable `v1` API; the raw endpoint is included below for pipelines.

If Parallel is not configured, run the relevant setup skill first. See [docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its lines / jurisdictions framing (captured once at setup), don't
re-ask it; only get the per-run specifics below.

Before creating monitors (each is a recurring, billable watch):
1. **Which policies / entities?** The insureds, locations, or entities to watch (one monitor per entity, or per location cohort).
2. **Which signals?** Default: adverse media, sanctions, litigation, catastrophe exposure, fraud. Trim to what you act on.
3. **Cadence?** Daily (`1d`) is the usual default; tighten around an active catastrophe window.

Confirm, then create.

## Run it

The shape that works: run **one broad monitor per entity** (or per location cohort) and classify
the signal downstream, not one monitor per signal type. It's far cheaper per record and dedups
cleanly. A monitor runs on a schedule, catches new matches, and returns structured output.

Output shape per detected signal:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["signal_type", "subject", "summary", "signal_date", "source_url"],
  "properties": {
    "signal_type": {"type": "string", "enum": ["adverse_media", "sanctions", "litigation", "catastrophe", "fraud", "regulatory", "other"]},
    "subject":     {"type": "string", "description": "the insured / entity / location the signal concerns"},
    "policies_affected": {"type": "string", "description": "which policies this touches, if known (e.g. '14 policies in evacuation zone')"},
    "summary":     {"type": "string", "description": "one-line factual summary of what changed"},
    "signal_date": {"type": "string", "description": "ISO 8601 date"},
    "route_to":    {"type": "string", "description": "who/what this should route to, e.g. the policy owner"},
    "source_url":  {"type": "string", "description": "resolving source (OFAC, NOAA/NHC, court records, news); must load"}
  }
}
```

Query per entity (substitute):

> Notify me whenever {ENTITY_OR_LOCATION} shows a concrete, sourced material-risk signal: adverse
> media, a sanctions or watchlist listing, new litigation, a catastrophe exposure (storm,
> wildfire, flood), or a fraud indicator. Give a one-line summary, the date, and a resolving
> source (OFAC, NOAA/NHC, court records, or the news item). Where you can, note which policies it
> touches. Prioritize named, dated, sourced facts; exclude rumor.

## Config seams (build on top)

1. **Entities:** one monitor per insured, or per location cohort for catastrophe (loop your book).
2. **Signal types:** edit the `signal_type` enum + the query to what you act on.
3. **Policy mapping:** `policies_affected` + `route_to` push each signal to the right owner and file.
4. **Cadence:** daily (`1d`) default; tighten around an active catastrophe window, cadence controls latency, not how much you catch.
5. **Processor:** `lite` is the cheap forward-watch default; `base` for heavier scans.

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ `POST /v1/monitors`
(`type: event_stream`, `frequency`, `processor`, `settings.query`, `settings.output_schema`),
read hits at `GET /v1/monitors/{id}/events`, optional `webhook` to push into your claims / policy
system. `event_stream` only catches change **going forward**, seed current exposure with a Task
first if you need a baseline now. Auth via `x-api-key`, same key creates and reads.

## Next

- Re-underwrite an insured a signal flags → **underwriting-risk-profiles**.
- Re-screen an entity a sanctions hit flags → **kyb-kyc**.
- Research the peril behind a catastrophe cluster → **emerging-risk-research**.
