---
name: parallel-signal-monitoring
description: Watch your target accounts (or the open web) and get alerted the moment something noteworthy changes, new exec hires, funding rounds, product launches, job postings, competitive moves, deduped so you only hear about significant changes. Use when the user wants to "monitor my accounts", "alert me when X happens", "watch for buying signals", or set up signal-based outbound. Runs on the user's own Parallel account via Monitor.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(curl:*)
metadata:
  author: parallel
---

# Signal Monitoring

Watch your target accounts and get alerted the moment something noteworthy changes, a new
exec hire, a funding round, a product launch, a job posting, a competitive move. Dedup is
handled, so you only hear about significant changes, and each signal is structured and cited
so it can route straight to the right rep.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

- **CLI / build-on-top:** the installed **`parallel-monitor`** skill (`parallel-cli skills
  install`) is the maintained path.
- Monitor is the stable `v1` API; the raw endpoint is included below for pipelines.

If Parallel is not configured, run the relevant setup skill first. See [docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its company / ICP / value framing (captured once at setup), don't re-ask it; only get the per-run specifics below.

Before creating monitors (each is a recurring, billable watch):
1. **Which accounts?** The list to watch (one monitor per account).
2. **Which signals?** Default: exec hires, funding, launches, job postings, competitive moves. Trim to what your reps act on.
3. **Cadence?** Daily (`1d`) is the usual default.

Confirm, then create.

## Run it

The shape that works: run **one broad monitor per account** (or per market) and classify the signal downstream,
not one monitor per signal type. It's far cheaper per record and dedups cleanly. A monitor
runs on a schedule, catches new matches, and returns structured output.

Output shape per detected signal:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["signal_type", "summary", "signal_date", "source_url"],
  "properties": {
    "signal_type": {"type": "string", "enum": ["exec_hire", "funding", "product_launch", "job_posting", "competitive_move", "expansion", "other"]},
    "account":     {"type": "string"},
    "summary":     {"type": "string", "description": "one-line factual summary of what changed"},
    "signal_date": {"type": "string", "description": "ISO 8601 date"},
    "route_to":    {"type": "string", "description": "who/what this should route to, e.g. the account owner"},
    "source_url":  {"type": "string", "description": "resolving source; must load"}
  }
}
```

Query per account (substitute):

> Notify me whenever {ACCOUNT} shows a concrete, sourced buying signal: a new executive
> hire, a funding round, a product launch, a notable job posting, a competitive move, or an
> expansion. Prioritize named, dated, sourced facts. Exclude rumor and generic posts.

## Config seams (build on top)

1. **Accounts**: one monitor per account you're tracking (loop your list).
2. **Signal types**: edit the `signal_type` enum + the query to what your reps act on.
3. **Cadence**: daily (`1d`) is the usual default; hourly costs ~24x for the same volume
   over a day, cadence controls latency, not how much you catch.
4. **Routing**: `route_to` + an optional webhook push each signal into your pipeline.
5. **Processor**: `lite` is the cheap forward-watch default; `base` for heavier scans.

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ `POST /v1/monitors`
(`type: event_stream`, `frequency`, `processor`, `settings.query`, `settings.output_schema`),
read hits at `GET /v1/monitors/{id}/events`, optional `webhook` to push. `event_stream` only
catches change **going forward**, seed a populated feed with a Task first if you need history
now. Auth via `x-api-key`, same key creates and reads.

## Next

- Pair with **account-enrichment** so a fresh signal arrives already enriched.
- Feed new accounts in from **lead-discovery**.
