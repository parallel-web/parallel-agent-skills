---
name: parallel-pipeline-monitoring
description: Watch the drugs, programs, and competitors you care about and get alerted the moment something material changes, trial readouts, phase transitions, FDA and EMA approvals, guidance, and commercialization events, deduped and cited. Use when the user wants to "monitor this drug/program", "alert me on readouts or approvals", "watch my competitors' pipelines", or set up pipeline surveillance. Runs on the user's own Parallel account via Monitor.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(curl:*)
metadata:
  author: parallel
---

# Pipeline Monitoring

Watch the drugs, programs, and competitors you care about and get alerted the moment something
material changes, a trial readout, a phase transition, an FDA or EMA approval, a guidance
update, or a commercialization event. Dedup is handled, so you only hear about real events, and
each is structured and cited so it can route straight to the analyst or team who owns the
program.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

- **CLI / build-on-top:** the installed **`parallel-monitor`** skill (`parallel-cli skills
  install`) is the maintained path.
- Monitor is the stable `v1` API; the raw endpoint is included below for pipelines.

If Parallel is not configured, run the relevant setup skill first. See [docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its focus / tracking framing (captured once at setup), don't
re-ask it; only get the per-run specifics below.

Before creating monitors (each is a recurring, billable watch):
1. **Which programs?** The drugs, targets, or companies to watch (one monitor per program, or per competitor).
2. **Which events?** Default: trial readout, phase transition, FDA/EMA approval, guidance, commercialization. Trim to what you act on.
3. **Cadence?** Daily (`1d`) is the usual default; go tighter around a known catalyst window.

Confirm, then create.

## Run it

The shape that works: run **one broad monitor per program** (or per competitor) and classify
the event downstream, not one monitor per event type. It's far cheaper per record and dedups
cleanly. A monitor runs on a schedule, catches new matches, and returns structured output.

Output shape per detected event:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["event_type", "asset", "summary", "event_date", "source_url"],
  "properties": {
    "event_type": {"type": "string", "enum": ["trial_readout", "phase_transition", "regulatory_approval", "regulatory_action", "guidance", "commercialization", "other"]},
    "asset":      {"type": "string", "description": "the drug / program / company the event concerns"},
    "summary":    {"type": "string", "description": "one-line factual summary of what changed"},
    "event_date": {"type": "string", "description": "ISO 8601 date"},
    "route_to":   {"type": "string", "description": "who/what this should route to, e.g. the program lead"},
    "source_url": {"type": "string", "description": "resolving source (ClinicalTrials.gov, FDA/EMA, company release); must load"}
  }
}
```

Query per program (substitute):

> Notify me whenever {PROGRAM} has a concrete, sourced event: a trial readout, a phase
> transition, an FDA or EMA approval or regulatory action, a guidance update, or a
> commercialization milestone. Give a one-line summary, the date, and a resolving source
> (ClinicalTrials.gov, an FDA/EMA record, or the company release). Prioritize named, dated,
> sourced facts; exclude rumor and pre-readout speculation.

## Config seams (build on top)

1. **Programs:** one monitor per drug / program / competitor you're tracking (loop your list).
2. **Event types:** edit the `event_type` enum + the query to what you act on.
3. **Cadence:** daily (`1d`) is the usual default; tighten around a catalyst window, cadence
   controls latency, not how much you catch.
4. **Routing:** `route_to` + an optional webhook push each event into your workflow.
5. **Processor:** `lite` is the cheap forward-watch default; `base` for heavier scans.

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ `POST /v1/monitors`
(`type: event_stream`, `frequency`, `processor`, `settings.query`, `settings.output_schema`),
read hits at `GET /v1/monitors/{id}/events`, optional `webhook` to push. `event_stream` only
catches change **going forward**, seed current pipeline state with a Task first if you need
history now. Auth via `x-api-key`, same key creates and reads.

## Next

- Map the whole competitive set you're watching → **competitive-landscape**.
- Feed new programs in from **licensing-discovery**.
- Pull the readout's clinical data into structured fields → **literature-mining**.
