---
name: parallel-workspace-agent
description: When something material changes about an entity your user tracks, act on it across the workspace, refresh the record, draft the follow-up, update the agenda, driven by a Monitor that detects the change and a Task that turns it into actions. Use when the user wants to "act when X changes", "keep my workspace in sync with the world", "trigger workflows on a signal", or build a proactive assistant. Runs on the user's own Parallel account via Monitor and Task.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), Bash(curl:*), ToolSearch, mcp__Parallel-Task-MCP__createTaskGroup, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# Workspace Agent

The proactive pattern: when something **material changes** about an entity your user tracks, act
on it across the workspace, refresh the record, draft the follow-up, update the agenda, before
the user asks. A **Monitor** detects the change and a **Task** turns it into the right actions,
each grounded and cited so the action is based on a real, sourced event, not a hallucinated one.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two primitives, both maintained by Parallel so API changes are absorbed for you:
- **Detect (the trigger):** the installed **`parallel-monitor`** skill, Monitor is the stable
  `v1` API.
- **Act (the follow-through):** the **Task MCP** (`createTaskGroup`), or `parallel-data-enrichment`
  on the CLI, to turn the change into structured, grounded actions.

The raw HTTP API is below for the server-side wiring. If Parallel is not configured, run the relevant setup skill first. See
[docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its product / surfaces / keep_current framing (captured once at
setup), don't re-ask it; only get the per-run specifics below.

Three quick questions before wiring it up:
1. **Watch what?** The entities your users track (one monitor per entity, fan out per user).
2. **Act how?** The actions to take on a material change (refresh a record, draft a message, update an agenda), and which need a human's approval before they fire.
3. **What counts as material?** The threshold, so routine noise doesn't trigger workspace actions.

Confirm, then wire it.

## Run it

Two stages. First a Monitor detects a material change (reuse the `parallel-knowledge-freshness` shape).
Then, on each event, a Task proposes the workspace actions:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["trigger", "actions"],
  "properties": {
    "trigger": {"type": "string", "description": "the sourced change that fired this, one line"},
    "source_url": {"type": "string", "description": "resolving source for the change; must load"},
    "actions": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["action", "target", "content", "needs_approval"],
        "properties": {
          "action":  {"type": "string", "enum": ["refresh_record", "draft_message", "update_agenda", "create_task", "notify", "other"]},
          "target":  {"type": "string", "description": "what in the workspace it touches (the account, the thread, the meeting)"},
          "content": {"type": "string", "description": "the drafted change / message, ready for the user to review"},
          "needs_approval": {"type": "boolean", "description": "true for anything user-facing or irreversible"}
        }
      }
    }
  }
}
```

Trigger query (Monitor) and action prompt (Task):

> **Monitor:** Notify me when anything material changes about {ENTITY}: a funding round, an exec
> change, a major announcement. Return the change, its date, and a resolving source.
>
> **Task (on each event):** Given this sourced change: {EVENT}, propose the actions to take
> across the workspace, refresh the entity's record with the new facts, draft a short follow-up
> message referencing the change, and update any relevant meeting agenda. For each action give the
> target and the ready-to-review content, and set needs_approval=true for anything user-facing.
> Ground every action in the sourced change; never act on an unverified rumor.

**Read it:** the Monitor is the always-on trigger; the Task output is a queue of proposed actions,
each tied to the sourced change. Auto-apply the safe ones (refresh a record) and hold
`needs_approval` actions (an outbound draft) for the user. Acting on a cited event, with a human
gate on anything outbound, is what keeps a proactive assistant trustworthy.

## Config seams (build on top)

1. **Trigger set:** one monitor per tracked entity; fan out per user from your DB.
2. **Action set:** edit the `action` enum + the prompt to the things your product can actually do.
3. **Approval gate:** `needs_approval` decides auto-apply vs human review, keep outbound and irreversible actions gated.
4. **Materiality threshold:** tune the monitor query so routine noise doesn't trigger workspace actions.
5. **Tiers:** `lite` Monitor for the watch, `core` Task for the action step (see the tier guidance in this skill).

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Monitor `POST
/v1/monitors` (`event_stream`) with a `webhook` that fires your action pipeline; on each event call
the Task API `POST /v1/tasks/runs` + `GET /v1/tasks/runs/{run_id}/result` (citations in
`output.basis`) to produce the actions. One `x-api-key`, server-side. This is the one skill you
wire directly against the API, so track the dated endpoints here.

## Next

- Just surface the change without acting → **knowledge-freshness**.
- Enrich the entity when its record refreshes → **entity-context**.
- Answer a user's question about the change → **productivity-quickstart**.
