---
name: parallel-landscape-deep-research
description: Commission a structured, source-cited report on a therapeutic area, mechanism, or life sciences investment question, every claim traced to a registry, filing, or paper. Use when the user wants to research a therapeutic area, assess whether to pursue a mechanism, size an indication, or prepare a cited report on a target or area. Runs on the user's own Parallel account via Deep Research.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__Parallel-Task-MCP__createDeepResearch, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# Landscape Deep Research

Ask an open question about a therapeutic area, a mechanism, or an investment thesis, and get
back a **structured, cited report**: the biology and unmet need, the competitive pipeline, the
clinical and regulatory picture, the risks, and a read on the question, with every claim traced
to a registry, a filing, or the primary literature. Nothing is fabricated; where the evidence
is early or conflicting, the report says so instead of overstating it.

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

If the current workspace contains a `PROFILE.md` file, use its therapeutic-area and modality framing (captured once at
setup) to focus the report; don't re-ask it.

Two quick questions before running (deep research is a higher-tier, billable run):
1. **What's the question?** One clear area, mechanism, or thesis question, the sharper the better.
2. **What must it cover?** Default sections: biology and unmet need, competitive pipeline, clinical and regulatory landscape, risks, and a verdict. Add or drop.

Confirm, then run.

## Run it

Deep research warrants a higher tier, default `pro` here. Give it the question and the sections
to cover. Poll `getStatus` until complete, then read with `getResultMarkdown`.

Prompt (substitute your question):

> Produce a structured research report answering: "{AREA_OR_THESIS_QUESTION}". Cite a resolving
> source URL for every claim, and prefer primary sources (ClinicalTrials.gov, FDA/EMA records,
> peer-reviewed literature, company filings) over secondary commentary. Cover, in order:
>
> 1) **Biology and unmet need:** the target/mechanism, the indication, and the gap in current care.
> 2) **Competitive pipeline:** the assets in development, their sponsors, and their clinical status.
> 3) **Clinical and regulatory landscape:** key readouts, endpoints, and the FDA/EMA path.
> 4) **Risks:** the things that would break the thesis (biological, clinical, regulatory, commercial).
> 5) **Verdict:** a direct, evidence-weighted read on the question, with the key uncertainties named.
>
> Never invent a trial result, an approval, or a source. Where the evidence is early or
> conflicting, show both sides and label the uncertainty rather than resolving it artificially.

**Read it:** start with the verdict and the two or three readouts or datapoints that carry it,
then use biology / pipeline / regulatory as the support, following the citations on anything
you'd put in front of a committee. Where the report flags thin or early evidence, treat that as
diligence to do, not a gap to smooth over.

## Config seams (build on top)

1. **The question:** one sharp area, mechanism, or thesis question; this is the whole input.
2. **Sections:** edit the section list to your diligence template (add deal comps, IP, market sizing, KOL view).
3. **Tier:** `pro` default for a real report; `core2x` for a quicker read, `ultra` for the highest-stakes questions (see the tier guidance in this skill).

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Deep Research runs on
the Task API (stable, `v1`): `POST /v1/tasks/runs` with a deep-research processor and
`task_spec.output_schema`, then `GET /v1/tasks/runs/{run_id}/result`; citations in
`output.basis`. Auth via `x-api-key`, server-side only. Prefer the CLI/MCP unless you need raw
control.

## Next

- Turn the pipeline section into a live map → **competitive-landscape**.
- Find net-new assets the report surfaces → **licensing-discovery**.
- Watch the area for the events that confirm or break the thesis → **pipeline-monitoring**.
