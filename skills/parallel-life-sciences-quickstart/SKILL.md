---
name: parallel-life-sciences-quickstart
description: Connect Parallel (if needed) and get a fast, source-cited snapshot of any drug, target, or company, what it is, mechanism of action, indication, clinical phase, and sponsor, with a source for every fact. Use when the user asks for an overview of a drug or target, a quick read on an asset, or the Parallel life sciences quickstart. Runs on the user's own Parallel account via Task.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__Parallel-Task-MCP__createTaskGroup, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# Life Sciences Quickstart

The fastest way to see Parallel work on a real asset: name one drug, target, or company and get
back a tight, cited **snapshot**, what it is, its mechanism of action, the indication, the
current clinical phase, and the sponsor behind it. Every fact resolves to a source
(ClinicalTrials.gov, a label, a filing, or the primary paper); if something can't be verified
it comes back empty, never invented.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two ways to run, both maintained by Parallel so API changes are absorbed for you:
- **Chat / co-work:** the **Task MCP** (`createTaskGroup`).
- **CLI / build-on-top:** `parallel-cli` + the installed **`parallel-deep-research`** skill.

Not set up yet?
If Parallel is not configured, run the relevant setup skill first.
Processor tier guidance: the tier guidance in this skill.

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its therapeutic-area framing (captured once at setup), don't
re-ask it; only get the per-run specifics below.

Two quick questions before running (the run costs credits):
1. **Which asset?** A drug / asset code (e.g. NVX-301), a target / mechanism, or a company. Resolve an ambiguous name and confirm first.
2. **Asset or company view?** Snapshot a single asset, or a company and its lead programs. Default: infer from what they named.

Confirm, then run.

## Run it

Call `createTaskGroup` once with the asset as the input, processor `core`, and the output shape
below. Poll `getStatus` until complete, then read with `getResultMarkdown`.

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["subject", "what_it_is", "mechanism", "indication", "phase", "sponsor"],
  "properties": {
    "subject":    {"type": "string", "description": "the drug, target, or company"},
    "what_it_is": {"type": "string", "description": "one line: modality and what it does"},
    "mechanism":  {"type": "string", "description": "mechanism of action / target; empty string if not established"},
    "indication": {"type": "string", "description": "lead indication(s) under study or approved"},
    "phase":      {"type": "string", "description": "current clinical phase or approval status"},
    "sponsor":    {"type": "string", "description": "the company / sponsor developing it"},
    "basis": {
      "type": "array",
      "description": "one entry per field: the source behind it and a confidence",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["field", "source_url", "confidence"],
        "properties": {
          "field":      {"type": "string"},
          "source_url": {"type": "string", "description": "resolving source (registry, label, filing, paper); must load"},
          "confidence": {"type": "integer", "description": "0-100"}
        }
      }
    }
  }
}
```

Prompt (substitute the asset):

> For {ASSET}, produce a fast snapshot and cite a resolving source URL for every fact: what it
> is (modality and function), mechanism of action / target, lead indication(s), current
> clinical phase or approval status, and the sponsor. Prefer ClinicalTrials.gov, FDA/EMA
> records, and the primary literature over secondary summaries. Never invent a mechanism, a
> phase, or a source, if a fact isn't on a reachable source, return an empty string and say so.

> Via the MCP, `createTaskGroup` takes a natural-language output description, not a strict
> schema, so the shape above is guidance there, lean on the prompt wording to keep it clean.

**Read it:** lead with what it is and the mechanism, then indication and phase, then the
sponsor, each with its resolving source. Where a field came back empty, say so, that refusal to
fabricate is the point.

## Config seams (build on top)

1. **Input:** swap the single asset for a list (run one per asset).
2. **Fields:** edit the shape to what you track (add trial IDs, next milestone, partners); keys become columns.
3. **Tier:** `core` default; `core2x`/`pro` for depth, `lite` for a fast pass (see the tier guidance in this skill).

Riding the MCP/CLI means an API change is absorbed on update, you don't re-clone for it.

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Task API (stable,
`v1`): `POST /v1/tasks/runs` with `task_spec.output_schema`, then
`GET /v1/tasks/runs/{run_id}/result`; per-field citations in `output.basis`. Auth via
`x-api-key`, server-side only. Hardcoding means you own keeping it current, prefer the MCP/CLI.

## Next

- Map the whole space around it → **competitive-landscape**.
- Keep it live → **pipeline-monitoring** (alert on readouts, phase changes, approvals).
- Pull the trial data behind it → **literature-mining**.
