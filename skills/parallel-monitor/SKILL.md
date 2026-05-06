---
name: parallel-monitor
description: "Continuously track the web for changes on a recurring cadence. Use when the user asks to 'monitor', 'track changes to', 'watch', or 'alert me when' something on the web changes — e.g., 'Track price changes for iPhone 16', 'Alert me when Tesla files a new 8-K', 'Monitor competitor pricing pages weekly'. Also use to list, inspect, update, or delete existing monitors."
user-invocable: true
argument-hint: <create|list|events|get|update|delete> [args]
compatibility: Requires parallel-cli and internet access.
allowed-tools: Bash(parallel-cli:*)
metadata:
  author: parallel
---

# Web Monitor

Action: $ARGUMENTS

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

## List monitors

```bash
parallel-cli monitor list --json
```

Add `-n 10` to limit. Present as a table: ID, query (truncated), cadence, created.

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

If `parallel-cli` is not found, install and authenticate:

```bash
curl -fsSL https://parallel.ai/install.sh | bash
```

If unable to install that way, install via pipx instead:

```bash
pipx install "parallel-web-tools[cli]"
pipx ensurepath
```

Then authenticate:

```bash
parallel-cli login
```

Or set an API key: `export PARALLEL_API_KEY="your-key"`
