---
name: parallel-web-monitor
description: "Watch the web for new events on a schedule through the Parallel MCP web_monitor tools. Only works when the Parallel MCP connection is signed in and has the monitor tools selected. Use when the user asks to monitor, track, or watch something on the web and read what it finds from the agent. For webhooks or other Monitor options use parallel-monitor, which runs through parallel-cli."
user-invocable: true
argument-hint: <create|list|events|cancel> [what to watch or monitor id]
compatibility: Requires a signed-in Parallel MCP connection (OAuth or API key) that lists the web_monitor tools.
metadata:
  author: parallel
---

# Web Monitor

Action: $ARGUMENTS

## Sign-in is required

The monitor tools only work when the Parallel MCP connection is signed in, with OAuth or an API key. A connection without sign-in cannot call them. Monitors belong to the signed-in organization, and every monitor run is billed to it at [Parallel API rates](https://parallel.ai/pricing).

The monitor tools are also not in the default tool list. The connection must select them, for example:

```text
https://mcp.parallel.ai/mcp?login&tools=default,monitors
```

Check the connection before promising a monitor:

- **`web_monitor_create`, `web_monitor_list`, `web_monitor_events`, and `web_monitor_cancel` are listed:** continue below.
- **The tools are missing:** tell the user that monitors need a signed-in connection that selects the monitor tools, and follow `parallel-search-setup`. Get agreement before changing the connection, because signed-in calls are billable. Never ask the user to paste credentials into chat.
- **The user declines to sign in:** stop. Do not create a monitor another way without asking.

## Pick the action

| The user wants to | Tool |
| --- | --- |
| Start watching something | `web_monitor_create` |
| See their monitors | `web_monitor_list` |
| Read what a monitor found | `web_monitor_events` |
| Stop a monitor | `web_monitor_cancel` |

Use each tool's advertised schema. Create or cancel only what the user asked for; do not create a monitor to demonstrate the skill.

## Create a monitor

A monitor runs once when it is created, then on its schedule, and records each new event it finds. **Every run is billed until the monitor is cancelled**, so confirm these three with the user before you call `web_monitor_create`:

- **`query`:** the events to watch for, in plain words, such as "funding rounds over $100M for AI startups".
- **`frequency`:** a number and a unit, `h`, `d`, or `w`, from `1h` to `30d`. The default is `1d`. A shorter interval costs more because it runs more often.
- **`processor`:** `lite`, `base`, or `core`. The default is `lite`. A larger processor costs more per run.

After creating it, give the user the monitor's id and say that it keeps running, and billing, until it is cancelled.

## List monitors and read events

- `web_monitor_list` returns the organization's monitors, newest first, with each one's query, status, frequency, and processor. Set `include_cancelled` to see cancelled ones. Pass `next_cursor` as `cursor` for more.
- `web_monitor_events` returns the events one monitor detected, newest first. Each event has the change it found, its date, and its citations. Pass `next_cursor` as `cursor` for older events.

Report events with their dates and citations. Never invent an event or a URL. If a monitor has no events yet, say so; it may not have found anything new.

The agent reads events by calling `web_monitor_events`. A monitor created here does not notify the agent or the user by itself, and it has no webhook.

## Cancel a monitor

`web_monitor_cancel` stops every future run and cannot be undone. Confirm the monitor's id and query with the user first.

## When to use something else

| Need | Use |
| --- | --- |
| A webhook, a snapshot monitor, or an update to an existing monitor | `parallel-monitor`, which runs through `parallel-cli` and needs its own authentication |
| A one-time answer about what is true now | `web_search` or `web_research` |
