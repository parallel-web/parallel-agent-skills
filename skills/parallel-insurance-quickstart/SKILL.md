---
name: parallel-insurance-quickstart
description: Connect Parallel (if needed) and get a fast, source-cited snapshot of a business, address, or claim, what it is, the key risk flags, and a KYB status at a glance, with a source and confidence on every field. Use when the user asks to "get a quick read on this business/address", "any red flags on this applicant", or wants the Parallel insurance quickstart. Runs on the user's own Parallel account via Task.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__Parallel-Task-MCP__createTaskGroup, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# Insurance Quickstart

The fastest way to see Parallel work on a real risk: name one business, address, or claim and
get back a tight, cited **snapshot**, what it is, the handful of risk flags that matter, and a
KYB status at a glance. Every field carries a source and a confidence; if something can't be
verified it comes back empty, never invented, so a low-confidence or empty field is a signal,
not a gap.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two ways to run, both maintained by Parallel so API changes are absorbed for you:
- **Chat / co-work:** the **Task MCP** (`createTaskGroup`).
- **CLI / build-on-top:** `parallel-cli` + the installed **`parallel-data-enrichment`** skill.

Not set up yet?
If Parallel is not configured, run the relevant setup skill first.
Processor tier guidance: the tier guidance in this skill.

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its lines / workflows framing (captured once at setup), don't
re-ask it; only get the per-run specifics below.

Two quick questions before running (the run costs credits):
1. **What's the subject?** A business (name + location), an address, or a claim reference.
2. **What matters most?** The default flags: registry status, obvious catastrophe / hazard exposure, and any adverse news. Add or drop.

Confirm, then run.

## Run it

Call `createTaskGroup` once with the subject as the input, processor `core`, and the output
shape below. Poll `getStatus` until complete, then read with `getResultMarkdown`.

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["subject", "what_it_is", "risk_flags"],
  "properties": {
    "subject":    {"type": "string"},
    "what_it_is": {"type": "string", "description": "one line: the business / property / claim in plain terms"},
    "registry_status": {"type": "string", "description": "active / dissolved / not found; empty string if not resolvable"},
    "risk_flags": {
      "type": "array",
      "description": "the notable risk signals found; empty array if none surfaced (say so, don't invent)",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["flag", "detail", "source_url", "confidence"],
        "properties": {
          "flag":       {"type": "string", "enum": ["catastrophe_exposure", "adverse_media", "sanctions", "litigation", "licensing", "safety_record", "other"]},
          "detail":     {"type": "string", "description": "one-line factual detail"},
          "source_url": {"type": "string", "description": "resolving source; must load"},
          "confidence": {"type": "integer", "description": "0-100"}
        }
      }
    }
  }
}
```

Prompt (substitute the subject):

> For {SUBJECT}, produce a fast risk snapshot and cite a resolving source with a 0-100
> confidence for every field: what it is in one line, its registry status, and the notable risk
> flags (catastrophe or hazard exposure, adverse media, sanctions, litigation, licensing, or
> safety record). Prefer official and public-record sources. Never invent a flag, a detail, or a
> source, if nothing surfaces for a category, leave it out rather than guess, and return an empty
> risk_flags array if the subject looks clean. For any blank field use an empty string, never the
> word "null".

> Via the MCP, `createTaskGroup` takes a natural-language output description, not a strict
> schema, so the shape above is guidance there, lean on the prompt wording to keep it clean.

**Read it:** lead with what it is and registry status, then the risk flags worth a human's
attention, each with its source and confidence. An empty flags list is a clean read, not a
missing one, say so.

## Config seams (build on top)

1. **Input:** swap the single subject for a list (run one per subject).
2. **Flags:** edit the `flag` enum + the shape to the signals your workflow acts on.
3. **Tier:** `core` default; `core2x`/`pro` for depth on a priority risk, `lite` for a fast triage pass (see the tier guidance in this skill).

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Task API (stable,
`v1`): `POST /v1/tasks/runs` with `task_spec.output_schema`, then
`GET /v1/tasks/runs/{run_id}/result`; per-field citations and confidence in `output.basis`. Auth
via `x-api-key`, server-side only. Hardcoding means you own keeping it current, prefer the MCP/CLI.

## Next

- Full underwriting workup → **underwriting-risk-profiles**.
- Full compliance check → **kyb-kyc**.
- Keep the subject under watch → **book-risk-monitoring**.
