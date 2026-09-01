---
name: parallel-tech-deep-research
description: Commission a structured, source-cited report on a technical decision, a migration path, a framework or library evaluation, an architecture trade-off, with every claim traced to a live source. Use when the user wants to "research this migration", "compare X vs Y for our stack", "should we adopt Z", or wants an engineering-grade cited write-up. Runs on the user's own Parallel account via Deep Research.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__Parallel-Task-MCP__createDeepResearch, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# Technical Deep Research

Ask an open technical question, "what's the migration path from X to Y", "Postgres vs a hosted
alternative for our workload", "is this framework safe to adopt", and get back a **structured,
cited report** grounded in current docs, changelogs, RFCs, and real-world issue threads. Every
claim traces to a resolving source, and where the evidence is thin or the community is split,
the report says so instead of picking a side for you.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two ways to run, both maintained by Parallel so API changes are absorbed for you:
- **Chat / co-work:** the **Task MCP** `createDeepResearch`.
- **CLI / build-on-top:** `parallel-cli` + the installed **`parallel-deep-research`** skill
  (`parallel-cli skills install`).

Not set up yet?
If Parallel is not configured, run the relevant setup skill first. Processor tier guidance: the tier guidance in this skill.

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its stack framing (captured once at setup) to anchor the report
in your actual libraries and constraints, don't re-ask it.

Two quick questions before running (deep research is a higher-tier, billable run):
1. **What's the decision?** One sharp question (a migration, a comparison, an adopt / don't).
2. **What must it cover?** Default sections: current state, options, trade-offs, migration effort / risks, and a recommendation. Add or drop.

Confirm, then run.

## Run it

Deep research warrants a higher tier, default `pro` here. Give it the question and the sections
to cover. Poll `getStatus` until complete, then read with `getResultMarkdown`.

Prompt (substitute your question):

> Produce a structured technical report answering: "{TECHNICAL_QUESTION}". Cite a resolving
> source URL for every claim, and prefer primary sources (official docs, changelogs, RFCs,
> release notes, and the primary GitHub issue) over blog commentary. Cover, in order:
>
> 1) **Current state:** where each option stands today, with versions and dates.
> 2) **Options:** the real choices, with what each is good and bad at, sourced.
> 3) **Trade-offs:** performance, maintenance, ecosystem maturity, lock-in.
> 4) **Migration effort and risks:** what moving actually takes and what tends to break.
> 5) **Recommendation:** a direct, evidence-weighted call for the stated constraints, with the
> key uncertainties named.
>
> Never invent a version, a benchmark, or a source. Where the evidence is thin or the community
> is split, show both sides rather than resolving it artificially.

**Read it:** start with the recommendation and the two or three sourced facts that carry it,
then use current-state / options / trade-offs as the support, following the citations on
anything you'd put in an ADR or a migration plan. Where the report flags thin evidence, that's
a spike to run, not a gap to paper over.

## Config seams (build on top)

1. **The question**: one sharp technical decision; this is the whole input.
2. **Sections**: edit the section list to your ADR or RFC template (add cost, security, benchmarks).
3. **Tier**: `pro` default for a real report; `core2x` for a quicker read, `ultra` for the highest-stakes calls (see the tier guidance in this skill).

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Deep Research runs on
the Task API (stable, `v1`): `POST /v1/tasks/runs` with a deep-research processor and
`task_spec.output_schema`, then `GET /v1/tasks/runs/{run_id}/result`; citations in
`output.basis`. Auth via `x-api-key`, server-side only. Prefer the CLI/MCP unless you need raw
control.

## Next

- Resolve the current versions the report references → **current-scaffolding**.
- Watch the options for changes while you decide → **dependency-monitoring**.
- Review the migration diffs against live docs → **doc-grounded-review**.
