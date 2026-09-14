---
name: parallel-in-product-research
description: Ship a research feature backed by a web subagent, give it an objective, get back a structured, cited report, with compute you dial per task. Use when the user wants to "add a research feature to my product", "give my agent a deep-research capability", "objective in, cited report out", or offer research as a product surface. Runs on the user's own Parallel account via Deep Research and Task.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__Parallel-Task-MCP__createDeepResearch, mcp__Parallel-Task-MCP__createTaskGroup, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# In-Product Research

Offer a **research capability** inside your product, backed by a web subagent: your user (or
your agent) gives it an objective, and it returns a structured, cited report. The compute is a
**dial per task**, a quick comparison and a deep multi-source report use the same shape at
different tiers, so you spend per request what the request is worth. Every claim traces to a
resolving source; thin evidence is flagged, not filled in.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two ways to run, both maintained by Parallel so API changes are absorbed for you:
- **Chat / co-work:** the **Task MCP** `createDeepResearch` (deep) or `createTaskGroup` (lighter,
  structured).
- **CLI / build-on-top:** `parallel-cli` + the installed **`parallel-deep-research`** skill
  (`parallel-cli skills install`).

Not set up yet?
If Parallel is not configured, run the relevant setup skill first.
Processor tier guidance: the tier guidance in this skill.

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its product framing (captured once at setup), don't re-ask it;
only get the per-run specifics below.

Two quick questions before running (deep research is a higher-tier, billable run):
1. **The objective?** The research question your user or agent submits.
2. **How much compute?** How deep this task is worth, the dial from a quick structured answer to a full multi-source report.

Confirm, then run.

## Run it

Give it the objective and the report shape. For a deep report use `createDeepResearch` at `pro`;
for a lighter structured answer use `createTaskGroup` at `core`/`core2x`. Poll `getStatus`, then
read with `getResultMarkdown`.

Example objective (a comparison your product might expose):

> Compare how two named companies each acquired their first million users: what each did
> differently, and how customer sentiment changed over time. Return a short strategy summary per
> company and a brief comparative analysis. Cite a resolving source URL for every claim, and
> prefer primary and contemporaneous sources. Never invent a figure, a tactic, or a source;
> where the record is thin, say so rather than filling it in.

**Read it:** lead with the comparative takeaway, then the per-entity detail, each claim clickable
to its source. Expose the compute dial to your product so a user can ask for "quick" vs "deep,"
and pass that straight to the tier.

## Config seams (build on top)

1. **The objective:** the user's research question; this is the input your feature accepts.
2. **Compute dial:** map your product's "quick / standard / deep" to `core` / `core2x` / `pro` (that is the "dial per task").
3. **Report shape:** define the sections your surface renders (summary, per-entity, comparison, sources).
4. **Async UX:** deep reports run seconds-to-minutes; stream status or notify on completion rather than blocking.

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Runs on the Task API
(stable, `v1`): `POST /v1/tasks/runs` with a deep-research processor and `task_spec.output_schema`,
then `GET /v1/tasks/runs/{run_id}/result`; citations in `output.basis`. The processor is your
compute dial. Auth via `x-api-key`, server-side only. Prefer the CLI/MCP unless you need raw
control.

## Next

- Serve the fast inline answers alongside it → **productivity-quickstart**.
- Enrich the entities the report surfaces → **entity-context**.
- Keep the report's topic current after → **knowledge-freshness**.
