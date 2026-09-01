---
name: parallel-thesis-research
description: Commission a structured, source-cited research report on any sector, market, or investment question, every claim traced to a source excerpt. Use when the user wants to "research this thesis", "is X an attractive market", "size this market", "write me a deep report on Y", or wants an analyst-grade cited document. Runs on the user's own Parallel account via Deep Research.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__Parallel-Task-MCP__createDeepResearch, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# Thesis Research (Deep Research)

Ask an open question about a sector, a market, or an investment, get back a **structured,
cited report** in minutes. Market size and growth, the drivers, the risks, the players, and a
read on the question you asked, with every claim traced to a resolving source excerpt so it's
auditable. Nothing is fabricated; where the evidence is thin, the report says so instead of
filling the gap.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two ways to run, both maintained by Parallel so API changes are absorbed for you:
- **Chat / co-work:** the **Task MCP** `createDeepResearch`.
- **CLI / build-on-top:** `parallel-cli` + the installed **`parallel-deep-research`** skill
  (`parallel-cli skills install`).

If Parallel is not configured, run the relevant setup skill first.
Processor tier guidance: the tier guidance in this skill.

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its mandate framing (captured once at setup) to focus the
report on the sectors, geographies, and size band you care about; don't re-ask it.

Two quick questions before running (deep research is a higher-tier, billable run):
1. **What's the question?** One clear thesis or market question, the sharper the better (a yes/no or a sizing question beats "tell me about X").
2. **What must the report cover?** Default sections: market size and growth, drivers, risks, key players, and a verdict on the question. Add or drop.

Confirm, then run.

## Run it

Deep research warrants a higher tier, default `pro` here. Give it the question and the
sections to cover. Poll `getStatus` until complete, then read with `getResultMarkdown`.

Prompt (substitute your question):

> Produce a structured research report answering: "{THESIS_OR_MARKET_QUESTION}". Cite a
> resolving source URL for every claim, and prefer primary sources (filings, regulator and
> industry data, company disclosures) over secondary commentary. Cover, in order:
>
> 1) **Market:** size, growth rate, and the segment structure, with figures and periods.
> 2) **Drivers:** what's growing or shrinking demand, sourced.
> 3) **Risks:** the things that would break the thesis (regulatory, cyclical, structural).
> 4) **Players:** who competes, their relative position, and any recent M&A or entrants.
> 5) **Verdict:** a direct, evidence-weighted read on the question, with the key uncertainties
> called out.
>
> Never invent a figure, a source, or a player. Where the evidence is thin or conflicting, say
> so and show both sides rather than resolving it artificially.

**Read it:** start with the verdict and the two or three figures that carry it, then use the
market / drivers / risks sections as the support, following the citations on anything you'd
put in front of a committee. Where the report flags thin evidence, treat that as a research
to-do, not a gap to paper over.

## Config seams (build on top)

1. **The question**: one sharp thesis or market question; this is the whole input.
2. **Sections**: edit the section list to your memo template (add unit economics, comps, a
   base/bull/bear, whatever your IC expects).
3. **Tier**: `pro` default for a real report; `core2x` for a quicker read, `ultra` for the
   highest-stakes questions (see the tier guidance in this skill).

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Deep Research runs on
the Task API (stable, `v1`): `POST /v1/tasks/runs` with a deep-research processor and
`task_spec.output_schema`, then `GET /v1/tasks/runs/{run_id}/result`; citations in
`output.basis`. Auth via `x-api-key`, server-side only. Prefer the CLI/MCP unless you need raw
control.

## Next

- Turn the players section into a live list → **target-discovery**.
- Profile the names the report surfaces → **company-profiles**.
- Watch the thesis for the events that would confirm or break it → **portfolio-monitoring**.
