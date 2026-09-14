---
name: parallel-portfolio-monitoring
description: Watch your positions, targets, and markets and get alerted the moment something material changes, regulatory filings, leadership changes, earnings signals, M&A, and competitor activity, deduped so you only hear about material changes. Use when the user wants to "monitor my portfolio", "alert me when X files or changes", "watch these targets", or set up market surveillance. Runs on the user's own Parallel account via Monitor.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(curl:*)
metadata:
  author: parallel
---

# Portfolio Monitoring

Watch your positions and targets and get alerted the moment something material changes, a
regulatory filing, a leadership change, an earnings signal, an M&A event, or a competitor
move. Dedup is handled, so you only hear about material changes, and each signal is structured
and cited so it can route straight to the analyst who owns the name.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

- **CLI / build-on-top:** the installed **`parallel-monitor`** skill (`parallel-cli skills
  install`) is the maintained path.
- Monitor is the stable `v1` API; the raw endpoint is included below for pipelines.

If Parallel is not configured, run the relevant setup skill first. See [docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its mandate / coverage framing (captured once at setup), don't re-ask it; only get the per-run specifics below.

Before creating monitors (each is a recurring, billable watch):
1. **Which names?** The positions or targets to watch (one monitor per name, or one per market).
2. **Which signals?** Default: regulatory filings, leadership changes, earnings signals, M&A, competitor activity. Trim to what you act on.
3. **Cadence?** Daily (`1d`) is the usual default; go hourly only for names where latency matters.

Confirm, then create.

## Run it

The shape that works: run **one broad monitor per name** (or per market) and classify the
signal downstream, not one monitor per signal type. It's far cheaper per record and dedups
cleanly. A monitor runs on a schedule, catches new matches, and returns structured output.

Output shape per detected signal:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["signal_type", "summary", "signal_date", "source_url"],
  "properties": {
    "signal_type": {"type": "string", "enum": ["regulatory_filing", "leadership_change", "earnings_signal", "m_and_a", "financing", "competitor_move", "other"]},
    "company":     {"type": "string"},
    "summary":     {"type": "string", "description": "one-line factual summary of what changed"},
    "signal_date": {"type": "string", "description": "ISO 8601 date"},
    "route_to":    {"type": "string", "description": "who/what this should route to, e.g. the analyst who owns the name"},
    "source_url":  {"type": "string", "description": "resolving source; must load"}
  }
}
```

Query per name (substitute):

> Notify me whenever {COMPANY} shows a concrete, sourced material change: a regulatory filing
> (8-K, S-1, 13D/G, or equivalent), a leadership change, an earnings or guidance signal, an
> M&A event, a financing, or a notable competitor move. Prioritize named, dated, sourced
> facts. Exclude rumor and generic commentary.

## Config seams (build on top)

1. **Names**: one monitor per position or target you're tracking (loop your list).
2. **Signal types**: edit the `signal_type` enum + the query to what you act on.
3. **Cadence**: daily (`1d`) is the usual default; hourly costs ~24x for the same volume over
   a day, cadence controls latency, not how much you catch.
4. **Routing**: `route_to` + an optional webhook push each signal into your workflow.
5. **Processor**: `lite` is the cheap forward-watch default; `base` for heavier scans.

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ `POST /v1/monitors`
(`type: event_stream`, `frequency`, `processor`, `settings.query`, `settings.output_schema`),
read hits at `GET /v1/monitors/{id}/events`, optional `webhook` to push. `event_stream` only
catches change **going forward**, seed a populated feed with a Task first if you need history
now. Auth via `x-api-key`, same key creates and reads.

## Next

- Pair with **company-profiles** so a fresh signal arrives against an up-to-date profile.
- Feed new names in from **target-discovery**.
- Turn a recurring compliance watch into **kyb-kyc** (continuous screening on counterparties).
