---
name: parallel-monitor
description: "Continuously track the web for changes on a recurring cadence. Use when the user asks to 'monitor', 'track changes to', 'watch', or 'alert me when' something on the web changes — e.g., 'Track price changes for iPhone 16', 'Alert me when Tesla files a new 8-K', 'Monitor competitor pricing pages weekly'. Also use to list, inspect, update, or stop existing monitors, including requests to delete them."
user-invocable: true
argument-hint: <create|list|events|get|update|trigger|cancel> [args]
compatibility: Requires parallel-cli >= 0.4.0 and internet access.
allowed-tools: Bash(parallel-cli:*)
metadata:
  author: parallel
---

# Web Monitor

Action: $ARGUMENTS

> Requires `parallel-cli` ≥ 0.4.0 for the GA Monitor commands. If a Monitor command or option is missing, tell the user to update through their installation method (see <https://docs.parallel.ai/integrations/cli>), then retry.

## What this skill does

Monitors are long-running, server-side jobs that re-check the web on a cadence and emit events when something changes. Unlike search/research/findall (one-shot lookups), monitors persist until cancelled and can optionally deliver detected events through a webhook.

## Decide the action

Parse the user's request and pick one:

| Intent | Action |
|---|---|
| "Track / watch / monitor / alert me when X" | **create** |
| "What am I monitoring?" / "List monitors" | **list** |
| "What changed?" / "Show me events for monitor X" | **events** |
| "Show monitor X" / "Get details for X" | **get** |
| "Change cadence / webhook for X" | **update** |
| "Check monitor X now" / "Run it now" | **trigger** |
| "Show me the full payload for event group X" | **events** with `--event-group-id` |
| "Stop / delete monitor X" | **cancel** (always confirm before cancelling) |

## Create a monitor

```bash
parallel-cli monitor create "<query>" --frequency 1d --json
```

Frequency accepts `<n><unit>` with `h`, `d`, or `w` (for example `1h`, `1d`, or `1w`). The aliases `hourly`, `daily`, `weekly`, and `every_two_weeks` are also accepted. Match cadence to how often the source actually changes — hourly for prices/news, weekly for filings/staffing.

Optional flags:

- `--webhook https://example.com/hook` — deliver detected events to a URL
- `--metadata '{"team":"competitive-intel"}'` — attach JSON metadata for your own bookkeeping
- `--output-schema '<json>'` — structure the event payload (advanced)

Parse the JSON to extract the `monitor_id`. Tell the user:

- The monitor has been created with its ID
- The frequency (so they know how often the monitor checks)
- That recent events are available server-side — they can run `parallel-cli monitor events $MONITOR_ID` later to see what changed

## List monitors

```bash
parallel-cli monitor list -n 10 --json
```

Default to `-n 10` for concise output. `list` returns active monitors only by default; add `--status active --status cancelled` when the user asks to include cancelled monitors. Raise the limit only for a larger set. Present as a table: ID, query or Task Run (truncated), frequency, created.

> Note: `monitor list` is sorted newest-first. If a user is verifying creation, prefer `monitor get $MONITOR_ID` (using the ID returned by create) over scanning the list.

## View events for a monitor

```bash
parallel-cli monitor events "$MONITOR_ID" --json
```

Events are returned newest-first. If the response contains `next_cursor`, pass it with `--cursor` to retrieve another page.

For deeper detail on a specific event group:

```bash
parallel-cli monitor events "$MONITOR_ID" --event-group-id "$EVENT_GROUP_ID" --json
```

Summarize for the user: count of events, then a bulleted list of what changed with dates or timestamps. Cite source URLs from the event payload.

## Get / update / trigger / cancel

```bash
parallel-cli monitor get "$MONITOR_ID" --json
parallel-cli monitor update "$MONITOR_ID" --frequency 1w --json
parallel-cli monitor trigger "$MONITOR_ID" --json
parallel-cli monitor cancel "$MONITOR_ID" --json
```

The current CLI does not expose query updates; create a new monitor to change the query.

`trigger` enqueues a real off-schedule run without changing the regular schedule. It is not a synthetic webhook test, and it emits an event only if the run detects a material change.

**Always confirm before cancelling** — cancellation is permanent.

## Setup

Requires `parallel-cli` (installed and authenticated). If `parallel-cli --version` fails, or if a later command fails with an authentication error, tell the user to see <https://docs.parallel.ai/integrations/cli> and stop.
