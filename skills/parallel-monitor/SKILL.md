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

Monitors are long-running, server-side jobs that re-check the web on a cadence and emit events when something changes. Unlike search/research/findall (one-shot lookups), monitors persist until cancelled and can optionally deliver detected events through a webhook. Creation does not establish an ongoing agent notification service: explain how to read server-side events or use the configured webhook, without promising chat or email alerts.

The default type is `event_stream`, with frequency `1d` and server processor `lite`. A `snapshot` monitor requires an existing Task run ID. Create or modify only the resource requested by the user; do not create a monitor just to demonstrate the skill.

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
| "Stop / delete monitor X" | **cancel** (permanent; verify authority and exact ID) |

## Create a monitor

```bash
parallel-cli monitor create "<query>" --frequency 1d --json
```

Frequency accepts `<n><unit>` with `h`, `d`, or `w` (for example `1h`, `1d`, or `1w`), within the supported range of 1 hour to 30 days. The aliases `hourly`, `daily`, `weekly`, and `every_two_weeks` are also accepted. Match cadence to the user's request and how often the source actually changes.

Optional flags:

- `--webhook https://example.com/hook` — deliver detected events to a URL
- `--metadata '{"team":"competitive-intel"}'` — attach JSON metadata for your own bookkeeping
- `--output-schema '<json>'` — structure the event payload (advanced)

Capture the returned `monitor_id` immediately with the query, frequency and requested settings. Verify creation with `get` using that ID. Tell the user:

- The monitor has been created with its ID
- The frequency (so they know how often the monitor checks)
- That recent events are available server-side — they can run `parallel-cli monitor events $MONITOR_ID` later to see what changed

If creation or another mutation times out or the response is lost, resolve the existing monitor/action before retrying. Resume with the saved ID, `get` and `events`; do not automatically recreate it. Recreating can duplicate persistent monitoring and billing.

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

An empty event list does not prove that a check completed without changes. To inspect completion history as well as detected events:

```bash
parallel-cli monitor events "$MONITOR_ID" --include-completions --limit 10 --json
```

Distinguish typed detected events, no-change `completion` events and `error` events. Use their actual timestamps and report failures. An empty completion history is not execution proof. Retain `event_id` and `event_group_id` when present; these identify events and executions, not monitor IDs.

For deeper detail on a specific event group:

```bash
parallel-cli monitor events "$MONITOR_ID" --event-group-id "$EVENT_GROUP_ID" --json
```

Event-group detail ignores pagination arguments. Summarize detected changes separately from completions/errors, with dates or timestamps. Read typed `output` or `changed_output` and available `basis`; cite its source URLs for factual claims. Do not invent provenance when the payload lacks basis. Surface response warnings and continue pagination only as needed for the requested period.

## Get / update / trigger / cancel

```bash
parallel-cli monitor get "$MONITOR_ID" --json
parallel-cli monitor update "$MONITOR_ID" --frequency 1w --json
parallel-cli monitor update "$MONITOR_ID" --webhook https://example.com/hook --json
parallel-cli monitor trigger "$MONITOR_ID" --json
parallel-cli monitor cancel "$MONITOR_ID" --json
```

Only supply fields the user requested to update. A webhook-only update leaves frequency unchanged; update has no default frequency. Metadata and advanced event-stream settings can also be updated through the CLI, but query and Task run identity are immutable. A different query needs a new monitor with separate authority and a deliberate decision about the old monitor; do not silently recreate or cancel it.

`trigger` enqueues a real billed off-schedule execution without changing the regular schedule. It is not a synthetic webhook test and must not substitute for a request to test notification delivery. A successful trigger response confirms enqueueing, not completion. It emits a detected event only if material change is found; inspect completion history for no-change execution. Cancelled monitors cannot be triggered.

Cancellation is irreversible, not deletion or a temporary pause. Explain this and obtain confirmation for the exact monitor ID unless the user has already authorized that permanent cancellation or cleanup of the specific disposable monitor. After cancelling, verify its state with `get`. Never recreate it automatically to resume monitoring.

On authentication or API errors, report the actual error and retain IDs for recovery. Do not classify every error as an outdated CLI or every permission error as insufficient credit. Failed reads are not evidence that a monitor stopped; reading events does not cancel it.

## Setup

Requires an installed and authenticated `parallel-cli`. Check `parallel-cli --version` and `parallel-cli auth --json`; auth can exit successfully while `authenticated` is false. Missing binary, unsupported command/option, and authentication failure need different remedies: installation, upgrade through the existing installation method, or terminal login respectively. See <https://docs.parallel.ai/integrations/cli>. Stop the affected request on auth failure, do not ask for secrets in chat, and do not change account policy to work around blocked setup.
