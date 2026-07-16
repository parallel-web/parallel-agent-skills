---
name: parallel-monitor
description: "Continuously track the web for changes on a recurring frequency. Use when the user asks to 'monitor', 'track changes to', 'watch', or 'alert me when' something on the web changes — e.g., 'Track price changes for iPhone 16', 'Alert me when Tesla files a new 8-K', 'Monitor competitor pricing pages weekly'. Also use to list, inspect, update, trigger, or cancel existing monitors and retrieve their events."
user-invocable: true
argument-hint: <create|list|events|get|update|trigger|cancel> [args]
compatibility: Requires parallel-cli >= 0.4.0 and internet access.
allowed-tools: Bash(parallel-cli:*)
metadata:
  author: parallel
---

# Web Monitor

Action: $ARGUMENTS

> Requires `parallel-cli` ≥ 0.4.0 for the GA Monitor commands. If a Monitor command or option is missing, tell the user to run `parallel-cli update` (or `pipx upgrade parallel-web-tools` if installed via pipx), then retry.

## What this skill does

Monitors are long-running, server-side jobs that check the web on a fixed frequency and emit events when a material change is detected. They persist until cancelled. Events accumulate server-side for polling and can optionally be delivered through a webhook.

## Decide the action

Parse the user's request and pick one:

| Intent | Action |
|---|---|
| "Track / watch / monitor / alert me when X" | **create** |
| "What am I monitoring?" / "List monitors" | **list** |
| "What changed?" / "Show me events for monitor X" | **events** |
| "Show monitor X" / "Get details for X" | **get** |
| "Change frequency / webhook / metadata for X" | **update** |
| "Check monitor X now" / "Run it now" | **trigger** |
| "Show the events from execution X" | **events** with `--event-group-id` |
| "Stop / cancel monitor X" | **cancel** (always confirm first) |

## Create a monitor

Create an `event_stream` monitor for a natural-language query:

```bash
parallel-cli monitor create "<query>" --frequency 1d --json
```

Frequency uses `<n><unit>` with `h`, `d`, or `w` (for example `1h`, `6h`, `1d`, or `2w`). The aliases `hourly`, `daily`, `weekly`, and `every_two_weeks` are also accepted. Match the frequency to how often the subject changes.

Useful options:

- `--processor lite|base` — `lite` is the default; use `base` for harder queries that need greater recall
- `--webhook https://example.com/hook` — deliver detected events to a webhook
- `--metadata '{"team":"competitive-intel"}'` — attach bookkeeping metadata
- `--output-schema '<json>'` — structure `event_stream` event output
- `--include-backfill` — include a historical sample on the first `event_stream` run

To monitor changes to an existing Task Run output, create a `snapshot` monitor without a query:

```bash
parallel-cli monitor create --type snapshot --task-run-id trun_abc --frequency 1d --json
```

Parse the JSON to extract the `monitor_id`. Tell the user the ID, type, frequency, and delivery method. Events can always be retrieved later with `parallel-cli monitor events "$MONITOR_ID" --json`, even without a webhook.

## List and inspect monitors

```bash
parallel-cli monitor list --limit 10 --json
parallel-cli monitor get "$MONITOR_ID" --json
```

`list` returns active monitors newest first by default. Use repeated `--status` flags to include both active and cancelled monitors, and use the returned `next_cursor` for another page:

```bash
parallel-cli monitor list --status active --status cancelled --limit 10 --json
parallel-cli monitor list --cursor "$NEXT_CURSOR" --limit 10 --json
```

Present monitors as a compact table with ID, type, tracked query or Task Run, frequency, and status. When verifying a newly created monitor, prefer `get` with the ID returned by `create`.

## View events

```bash
parallel-cli monitor events "$MONITOR_ID" --limit 20 --json
```

Events are returned newest first. If the response has `next_cursor`, pass it with `--cursor` to retrieve another page. To include executions where no material change was detected, add `--include-completions`.

Restrict results to one execution with its event group ID:

```bash
parallel-cli monitor events "$MONITOR_ID" --event-group-id "$EVENT_GROUP_ID" --json
```

Summarize what changed and when. Cite URLs from `output.basis[].citations[].url`. For repeated polling, deduplicate detected changes by stable `event_id`; do not invent a time-based lookback because the GA events endpoint uses cursor pagination.

## Update a monitor

```bash
parallel-cli monitor update "$MONITOR_ID" --frequency 1w --json
parallel-cli monitor update "$MONITOR_ID" --webhook https://example.com/hook --json
```

Frequency, webhook, metadata, and `event_stream` advanced settings are mutable. The query and snapshot Task Run ID are immutable; create a new monitor to change either one.

## Trigger a run now

```bash
parallel-cli monitor trigger "$MONITOR_ID" --json
```

`trigger` starts a real off-schedule run without changing the regular schedule. It emits a detected event only if a material change is found. It is not a synthetic webhook test, and cancelled monitors cannot be triggered.

## Cancel a monitor

Cancellation permanently stops future runs. Always confirm with the user immediately before executing:

```bash
parallel-cli monitor cancel "$MONITOR_ID" --json
```

Cancellation is irreversible. Create a new monitor if the user later wants to resume tracking.

## Setup

Requires `parallel-cli` installed and authenticated. If `parallel-cli --version` fails, or if a later command fails with an authentication error, tell the user to see <https://docs.parallel.ai/integrations/cli> and stop.
