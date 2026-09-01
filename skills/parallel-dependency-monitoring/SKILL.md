---
name: parallel-dependency-monitoring
description: Watch a set of dependencies and get alerted the moment something material ships, a new release, a breaking change, a deprecation, or a CVE, deduped and cited, so you can apply safe updates instead of chasing changelogs. Use when the user wants to "monitor my dependencies", "alert me on breaking changes or CVEs", "watch for new releases", or set up safe-update automation. Runs on the user's own Parallel account via Monitor.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(curl:*)
metadata:
  author: parallel
---

# Dependency Monitoring

Watch the libraries you depend on and get alerted the moment something material ships, a new
release, a breaking change, a deprecation, or a CVE. Dedup is handled, so you only hear about
real changes, and each alert is structured and cited so an agent can decide whether the update
is safe to apply.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

- **CLI / build-on-top:** the installed **`parallel-monitor`** skill (`parallel-cli skills
  install`) is the maintained path.
- Monitor is the stable `v1` API; the raw endpoint is included below for pipelines.

If Parallel is not configured, run the relevant setup skill first. See [docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its stack and "current" framing (captured once at setup), that's
usually the set to watch, don't re-ask it; only get the per-run specifics below.

Before creating monitors (each is a recurring, billable watch):
1. **Which dependencies?** The libraries to watch (one monitor per library, or one per stack).
2. **Which events?** Default: new release, breaking change, deprecation, CVE / security advisory. Trim to what you act on.
3. **Cadence?** Daily (`1d`) is the usual default; hourly for security-critical deps.

Confirm, then create.

## Run it

The shape that works: run **one broad monitor per library** (or per stack) and classify the
event downstream, not one monitor per event type. It's far cheaper per record and dedups
cleanly. A monitor runs on a schedule, catches new matches, and returns structured output.

Output shape per detected event:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["event_type", "library", "summary", "event_date", "source_url"],
  "properties": {
    "event_type": {"type": "string", "enum": ["release", "breaking_change", "deprecation", "cve", "eol", "other"]},
    "library":    {"type": "string"},
    "version":    {"type": "string", "description": "the version the event concerns, if applicable"},
    "summary":    {"type": "string", "description": "one-line factual summary of what changed"},
    "safe_to_apply": {"type": "string", "enum": ["yes", "no", "needs_review"], "description": "needs_review when a breaking change or CVE is involved"},
    "event_date": {"type": "string", "description": "ISO 8601 date"},
    "source_url": {"type": "string", "description": "resolving source (release notes, advisory); must load"}
  }
}
```

Query per library (substitute):

> Notify me whenever {LIBRARY} has a concrete, sourced change: a new release, a breaking change,
> a deprecation, or a CVE / security advisory. Give the version, a one-line summary, the date,
> and a resolving source (release notes, changelog, or advisory). Mark whether it looks safe to
> apply, use "needs_review" for any breaking change or security issue. Prioritize named, dated,
> sourced facts; exclude rumor and pre-announcement chatter.

## Config seams (build on top)

1. **Libraries**: one monitor per dependency you track (loop your manifest or the workspace `PROFILE.md` file).
2. **Event types**: edit the `event_type` enum + the query to what you act on.
3. **Safe-update gate**: `safe_to_apply` drives automation: auto-PR the `yes` items, hold `needs_review` for a human.
4. **Cadence**: daily (`1d`) default; hourly for security-critical deps, cadence controls latency, not how much you catch.
5. **Processor**: `lite` is the cheap forward-watch default; `base` for heavier scans.

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ `POST /v1/monitors`
(`type: event_stream`, `frequency`, `processor`, `settings.query`, `settings.output_schema`),
read hits at `GET /v1/monitors/{id}/events`, optional `webhook` to push into CI. `event_stream`
only catches change **going forward**, seed current state with a Task first if you need it now.
Auth via `x-api-key`, same key creates and reads.

## Next

- Turn a `needs_review` alert into a grounded review → **doc-grounded-review**.
- Re-pin the manifest when a safe update lands → **current-scaffolding**.
- Offer monitoring to every app on your platform → **platform-web-access**.
