---
name: parallel-monitor
description: "Continuously track the web for changes on a recurring cadence. Use when the user asks to 'monitor', 'track changes to', 'watch', or 'alert me when' something on the web changes — e.g., 'Track price changes for iPhone 16', 'Alert me when Tesla files a new 8-K', 'Monitor competitor pricing pages weekly'. Also use to list, inspect, update, or delete existing monitors."
user-invocable: true
argument-hint: <create|list|events|get|update|simulate|event-group|delete> [args]
compatibility: Requires parallel-cli >= 0.3.0 and internet access.
allowed-tools: Bash(parallel-cli:*)
metadata:
  author: parallel
---

# Web Monitor

Action: $ARGUMENTS

> Requires `parallel-cli` ≥ 0.3.0 (the `monitor` command was added in 0.3.0). If `parallel-cli monitor` errors with `no such command` or similar, tell the user to run `parallel-cli update` (or `pipx upgrade parallel-web-tools` if installed via pipx), then retry.

## What this skill does

Monitors are long-running, server-side jobs that re-check the web on a cadence and emit events when something changes. Unlike search/research/findall (one-shot lookups), monitors persist until deleted and can optionally fire a webhook on each event.

## Decide the action

Parse the user's request and pick one:

| Intent | Action |
|---|---|
| "Track / watch / monitor / alert me when X" | **create** |
| "What am I monitoring?" / "List monitors" | **list** |
| "What changed?" / "Show me events for monitor X" | **events** |
| "Show monitor X" / "Get details for X" | **get** |
| "Change cadence / query / webhook for X" | **update** |
| "Test the webhook" / "Fire a test event" | **simulate** (requires a webhook on the monitor) |
| "Show me the full payload for event group X" | **event-group** |
| "Stop / delete monitor X" | **delete** (always confirm before deleting) |

## Create a monitor

```bash
parallel-cli monitor create "<query>" --cadence daily --json
```

Cadence options: `hourly`, `daily` (default), `weekly`, `every_two_weeks`. Match cadence to how often the source actually changes — hourly for prices/news, weekly for filings/staffing.

Optional flags:

- `--webhook https://example.com/hook` — POST events to a URL as they happen
- `--metadata '{"team":"competitive-intel"}'` — attach JSON metadata for your own bookkeeping
- `--output-schema '<json>'` — structure the event payload (advanced)

Parse the JSON to extract the `monitor_id`. Tell the user:

- The monitor has been created with its ID
- The cadence (so they know when to expect first event)
- That events accumulate server-side — they can run `parallel-cli monitor events $MONITOR_ID` later to see what changed

If they configured a webhook, suggest testing it:

```bash
parallel-cli monitor simulate "$MONITOR_ID"
```

`simulate` requires a webhook to be configured on the monitor. Without one it errors with `Webhook not configured for this monitor` — do not run it on monitors created without `--webhook`.

## List monitors

```bash
parallel-cli monitor list -n 10 --json
```

Default to `-n 10` — accounts with many historical monitors can return megabytes of JSON otherwise. Raise the limit only if the user explicitly asks for "all" or a larger set. Present as a table: ID, query (truncated), cadence, created.

> Note: `monitor list` is not guaranteed to be sorted newest-first, so a monitor you just created may not appear in the first page of results. If a user is verifying creation, prefer `monitor get $MONITOR_ID` (using the ID returned by create) over scanning the list.

## View events for a monitor

```bash
parallel-cli monitor events "$MONITOR_ID" --lookback 10d --json
```

Lookback format: `Nd` (days) or `Nw` (weeks). Default `10d`.

For deeper detail on a specific event group:

```bash
parallel-cli monitor event-group "$MONITOR_ID" "$EVENT_GROUP_ID" --json
```

Summarize for the user: count of events in the period, then a bulleted list of what changed with timestamps. Cite source URLs from the event payload.

## Get / update / delete

```bash
parallel-cli monitor get "$MONITOR_ID" --json
parallel-cli monitor update "$MONITOR_ID" --cadence weekly --json
parallel-cli monitor delete "$MONITOR_ID" --json
```

**Always confirm before deleting** — deletion is permanent.

## Setup

Requires `parallel-cli` (installed and authenticated). If `parallel-cli --version` fails, or if a later command fails with an authentication error, tell the user to see <https://docs.parallel.ai/integrations/cli> and stop.
