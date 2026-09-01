---
name: parallel-literature-mining
description: Pull clean, structured data out of papers, trial registries, and regulatory filings, including efficacy, mechanism of action, endpoints, enrollment, and real-world evidence, each field cited to its source. Use when the user wants to "extract the trial data", "pull endpoints and efficacy from this paper/registry", "structure the clinical data for these assets", or mine the literature. Runs on the user's own Parallel account via Extract and Task.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__claude_ai_Parallel_Web_Search_Paid__web_fetch, mcp__Parallel-Task-MCP__createTaskGroup, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# Literature Mining

Pull clean, **structured data** out of the primary sources, papers, trial registries, and
regulatory filings, so an asset's efficacy, mechanism, endpoints, enrollment, and real-world
evidence land as fields instead of PDFs. Every field is cited to the exact source it came from;
a value that isn't in the source comes back empty, never approximated.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two ways to run, both maintained by Parallel so API changes are absorbed for you:
- **Chat / co-work:** the **Task MCP** (`createTaskGroup`) with the source(s) named, plus
  `web_fetch` for a specific page.
- **CLI / build-on-top:** `parallel-cli` + the installed **`parallel-web-extract`** and
  **`parallel-data-enrichment`** skills (`parallel-cli skills install`).

Not set up yet?
If Parallel is not configured, run the relevant setup skill first.
See [docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its therapeutic-area framing (captured once at setup), don't
re-ask it; only get the per-run specifics below.

Three quick questions before running (each source mined is a billable run):
1. **Which sources or assets?** A paper / registry entry / filing (URL or ID), or an asset whose data to mine across sources.
2. **Which fields?** Default: mechanism, indication, enrollment, primary endpoint + result, key efficacy, safety signal. Add or drop.
3. **How many now?** Start with a few to check fidelity, then batch.

Confirm, then run.

## Run it

One task per source or asset. Output shape:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["asset", "fields"],
  "properties": {
    "asset": {"type": "string", "description": "the asset / trial the data describes"},
    "fields": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "mechanism":        {"type": "string", "description": "mechanism of action / target"},
        "indication":       {"type": "string"},
        "enrollment":       {"type": "string", "description": "n, and population"},
        "primary_endpoint": {"type": "string", "description": "the endpoint and its result (with CI if reported)"},
        "key_efficacy":     {"type": "string", "description": "headline efficacy readout"},
        "safety_signal":    {"type": "string", "description": "notable safety / tolerability finding; empty if none reported"},
        "rwe":              {"type": "string", "description": "real-world evidence, if any; empty string if none"}
      }
    },
    "basis": {
      "type": "array",
      "description": "one entry per field: the exact source and a confidence",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["field", "source_url", "confidence"],
        "properties": {
          "field":      {"type": "string"},
          "source_url": {"type": "string", "description": "resolving source (paper, registry, filing); must load"},
          "confidence": {"type": "integer", "description": "0-100"}
        }
      }
    }
  }
}
```

Prompt (substitute the source / asset):

> Extract structured clinical data for {ASSET_OR_SOURCE}: mechanism of action, indication,
> enrollment (n and population), primary endpoint and its result (include the confidence
> interval if reported), headline efficacy, any notable safety signal, and any real-world
> evidence. Prefer ClinicalTrials.gov, the primary publication (PubMed / journal), and FDA/EMA
> documents. Cite the exact resolving source for every field and give a 0-100 confidence. Never
> approximate or infer a number, if a value isn't stated in a reachable source, return an empty
> string. Report results verbatim as stated (e.g. "ORR 41%, 95% CI 34-48").

**Read it:** it's a clean data row per asset, each figure clickable back to the paper or
registry that stated it. Treat empty fields as "not reported in source," and never let a
rounded or inferred number stand in for a cited one.

## Config seams (build on top)

1. **Input:** a source (URL / ID) or an asset to mine across sources; run one task each.
2. **Fields:** edit the `fields` object to your data model (add secondary endpoints, dosing, biomarker, comparator).
3. **Verbatim rule:** keep results as stated with units and CIs; don't normalize away precision.
4. **Tier:** `core2x` default (extraction fidelity from dense filings); `core` for a lighter pass (see the tier guidance in this skill).

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Extract via the
Extract endpoint for clean source text; structure via Task (`POST /v1/tasks/runs` with
`task_spec.output_schema`, then `GET /v1/tasks/runs/{run_id}/result`; citations in
`output.basis`). Auth via `x-api-key`, server-side only. Prefer the CLI/MCP unless you need raw
control.

## Next

- Do this across a whole competitive set → **competitive-landscape**.
- Watch for the next readout to mine → **pipeline-monitoring**.
- Write it up into a full report → **landscape-deep-research**.
