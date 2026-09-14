---
name: parallel-emerging-risk-research
description: Commission a structured, source-cited report on a peril, a liability class, or a regulatory change affecting your book, exposure drivers, loss trends, the regulatory picture, and the implications for pricing and appetite, every claim traced to a source. Use when the user wants to research an emerging risk, assess exposure to a peril, determine how a regulation affects a book, or prepare an actuarial or portfolio research write-up. Runs on the user's own Parallel account via Deep Research.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__Parallel-Task-MCP__createDeepResearch, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# Emerging Risk Research

Ask an open question about a peril, a liability class, or a regulatory change, and get back a
**structured, cited report**: what's driving the exposure, the loss trends, the regulatory
picture, and what it means for pricing and appetite, with every claim traced to a resolving
source. Nothing is fabricated; where the data is thin or the trend is early, the report says so
instead of overstating it.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two ways to run, both maintained by Parallel so API changes are absorbed for you:
- **Chat / co-work:** the **Task MCP** `createDeepResearch`.
- **CLI / build-on-top:** `parallel-cli` + the installed **`parallel-deep-research`** skill
  (`parallel-cli skills install`).

Not set up yet?
If Parallel is not configured, run the relevant setup skill first.
Processor tier guidance: the tier guidance in this skill.

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its lines and jurisdictions framing (captured once at setup) to
anchor the report on your actual book; don't re-ask it.

Two quick questions before running (deep research is a higher-tier, billable run):
1. **What's the question?** One clear peril, liability class, or regulatory change.
2. **What must it cover?** Default sections: exposure drivers, loss trends, regulatory picture, and implications for pricing / appetite. Add or drop.

Confirm, then run.

## Run it

Deep research warrants a higher tier, default `pro` here. Give it the question and the sections
to cover. Poll `getStatus` until complete, then read with `getResultMarkdown`.

Prompt (substitute your question):

> Produce a structured research report answering: "{RISK_QUESTION}". Cite a resolving source URL
> for every claim, and prefer primary sources (regulator and agency data, catastrophe models and
> bulletins, court records, filings) over secondary commentary. Cover, in order:
>
> 1) **Exposure drivers:** what creates and concentrates the risk, with figures.
> 2) **Loss trends:** frequency and severity trends, sourced, with the period they cover.
> 3) **Regulatory picture:** the rules, filings, or actions that bear on it, and where they're headed.
> 4) **Implications:** what it means for pricing, terms, and appetite for a book like the reader's.
>
> Never invent a loss figure, a ruling, or a source. Where the data is thin or the trend is
> early, say so and show the uncertainty rather than resolving it artificially.

**Read it:** start with the implications and the two or three loss or exposure datapoints that
carry them, then use drivers / trends / regulatory as the support, following the citations on
anything you'd take to a pricing or appetite decision. Where the report flags thin data, treat it
as a monitoring target, not a settled conclusion.

## Config seams (build on top)

1. **The question:** one sharp peril, liability class, or regulatory change; this is the whole input.
2. **Sections:** edit the section list to your actuarial / portfolio template (add reinsurance, accumulation, comparables).
3. **Tier:** `pro` default for a real report; `core2x` for a quicker read, `ultra` for the highest-stakes questions (see the tier guidance in this skill).

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Deep Research runs on
the Task API (stable, `v1`): `POST /v1/tasks/runs` with a deep-research processor and
`task_spec.output_schema`, then `GET /v1/tasks/runs/{run_id}/result`; citations in
`output.basis`. Auth via `x-api-key`, server-side only. Prefer the CLI/MCP unless you need raw
control.

## Next

- Turn the exposure findings into a live watch → **book-risk-monitoring**.
- Re-underwrite the risks it flags → **underwriting-risk-profiles**.
- Get a fast read on a single flagged entity → **insurance-quickstart**.
