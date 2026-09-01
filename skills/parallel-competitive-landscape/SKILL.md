---
name: parallel-competitive-landscape
description: Map a therapeutic area, target, or mechanism, approved and investigational assets, the companies behind them, clinical status, and the investors active in the space, as one structured, source-cited output. Use when the user wants to map the landscape for a target or area, identify who else is developing a mechanism, view the competitive set, or run a landscape analysis. Runs on the user's own Parallel account via Task.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__Parallel-Task-MCP__createTaskGroup, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# Competitive Landscape

Give it a therapeutic area, a target, or a mechanism, and get back the **competitive set** as
one structured, cited output: the approved and investigational assets, the companies behind
them, each asset's clinical status, and the investors active in the space. Every asset resolves
to a source; the long-tail programs that don't sit in a commercial database are surfaced too.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two ways to run, both maintained by Parallel so API changes are absorbed for you:
- **Chat / co-work:** the **Task MCP** (`createTaskGroup`).
- **CLI / build-on-top:** `parallel-cli` + the installed **`parallel-deep-research`** skill
  (`parallel-cli skills install`).

Not set up yet?
If Parallel is not configured, run the relevant setup skill first.
See [docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its therapeutic-area / focus framing (captured once at setup), it
often names the target or area to map, don't re-ask it; only get the per-run specifics below.

Three quick questions before running (a landscape map is a billable run):
1. **What's the space?** A target (e.g. KRAS G12D), a mechanism, or a therapeutic area / indication.
2. **Which fields per asset?** Default: asset, company, phase, modality, indication, latest milestone. Add investors, deal status, or trial IDs.
3. **Scope?** All phases (default), or restrict (e.g. clinical-stage only, or a modality).

Confirm, then run.

## Run it

One task for the space. Output shape:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["space", "assets"],
  "properties": {
    "space": {"type": "string", "description": "the target, mechanism, or area mapped"},
    "assets": {
      "type": "array",
      "description": "the competitive set; empty array if none are found on a reachable source",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["asset", "company", "phase", "source_url"],
        "properties": {
          "asset":      {"type": "string", "description": "asset name / code"},
          "company":    {"type": "string", "description": "developer / sponsor"},
          "phase":      {"type": "string", "description": "clinical status or approval"},
          "modality":   {"type": "string", "description": "small molecule, biologic, etc."},
          "indication": {"type": "string"},
          "investors":  {"type": "string", "description": "investors active in the asset/company, if public; empty string if not found"},
          "source_url": {"type": "string", "description": "resolving source; must load"}
        }
      }
    }
  }
}
```

Prompt (substitute the space):

> Map the competitive landscape for {SPACE}. Return every approved and investigational asset you
> can source: the asset, the company developing it, its clinical phase or approval status, the
> modality, the indication, and the investors active in the asset or company where public.
> Include long-tail and private-company programs, not just the well-covered ones. Cite a
> resolving source (ClinicalTrials.gov, FDA/EMA, company or investor disclosure, or the primary
> literature) for every asset. Never invent an asset, a phase, or a source, if you can't source
> a field, return an empty string. Prefer a smaller correct map over a padded speculative one.

**Read it:** it's a competitive table, sort by phase to see who's ahead, and treat empty
`investors` or `phase` cells as "not sourced," not "none." The long-tail private programs are
usually the ones a commercial database misses.

## Config seams (build on top)

1. **Input:** the target, mechanism, or area; this is the whole input. Seed it from the workspace `PROFILE.md` file.
2. **Fields:** edit the `assets` shape to your landscape template (add deal status, next catalyst, patents).
3. **Scope:** all phases vs a filter (clinical-stage only, a modality, a geography).
4. **Tier:** `core2x` default for a thorough map; `core` for a quick scan, `pro` for a board-ready one (see the tier guidance in this skill).

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Task API (stable,
`v1`): `POST /v1/tasks/runs` with `task_spec.output_schema`, then
`GET /v1/tasks/runs/{run_id}/result`; per-field citations in `output.basis`. Auth via
`x-api-key`, server-side only. Prefer the CLI/MCP unless you need raw control.

## Next

- Enrich or snapshot a single asset from the map → **life-sciences-quickstart**.
- Find net-new assets by BD criteria → **licensing-discovery**.
- Watch the set for changes → **pipeline-monitoring**.
