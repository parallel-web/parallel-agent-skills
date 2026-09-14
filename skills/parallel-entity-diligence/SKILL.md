---
name: parallel-entity-diligence
description: Turn a list of counterparties or target companies into structured, source-cited diligence tear sheets, corporate structure, ownership / UBO, jurisdictions, sanctions and watchlist exposure, litigation history, and regulatory status, with a confidence score and a source for every field. Use when the user wants to "run diligence on these companies", "KYB this list", "screen these counterparties", or turn a vendor/target list into diligence-ready intelligence. Runs on the user's own Parallel account.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__Parallel-Task-MCP__createTaskGroup, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# Entity Diligence

Start with a list of counterparties or targets, get back a structured, cited **diligence
tear sheet** for each: corporate structure, ownership, jurisdictions, sanctions/watchlist
exposure, litigation history, regulatory status. Every field carries a confidence score and a
resolving source; if a fact isn't on a reachable source, the field comes back empty, never
guessed. This is a research layer to speed triage, not a certified screening or legal advice,
verify hits against the primary registry or list before you rely on them.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two ways to run, both maintained by Parallel so API changes are absorbed for you:
- **Chat / co-work:** the **Task MCP** (`createTaskGroup`), one input per entity.
- **CLI / build-on-top:** `parallel-cli` + the installed **`parallel-data-enrichment`** skill
  (`parallel-cli skills install`).

If Parallel is not configured, run the relevant setup skill first. See
[docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its jurisdiction / priority framing (captured once at setup), don't re-ask it; only get the per-run specifics below.

Three quick questions before running (each entity is a billable enrichment):
1. **Your entity list?** Names, names + domains, or names + jurisdiction (jurisdiction sharply cuts wrong-entity matches).
2. **Which fields?** Default is the diligence tear sheet (structure, ownership, sanctions exposure, litigation, regulatory status). Add or drop to match your intake form.
3. **Run how many now?** Start with a small batch (5-10) to check quality and entity resolution, then scale.

Confirm, then run.

## Run it

One task per entity (batch the list), processor `core2x` (diligence default, recall matters,
see the tier guidance in this skill). Output shape, the tear sheet:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["entity", "fields"],
  "properties": {
    "entity": {"type": "string", "description": "the resolved entity (name + disambiguator)"},
    "fields": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "corporate_structure": {"type": "string", "description": "entity type, parent/subsidiary, registration; empty if not found"},
        "ownership":           {"type": "string", "description": "known owners / ultimate beneficial owners if publicly sourced; empty otherwise"},
        "jurisdictions":       {"type": "string", "description": "domicile + operating jurisdictions"},
        "sanctions_exposure":  {"type": "string", "description": "any sanctions / watchlist / debarment hits found; 'none found' if searched and clear"},
        "litigation_history":  {"type": "string", "description": "notable litigation / enforcement, one line each"},
        "regulatory_status":   {"type": "string", "description": "licenses, registrations, regulatory actions where applicable"}
      }
    },
    "basis": {
      "type": "array",
      "description": "one entry per field: the source behind it and a confidence",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["field", "source_url", "confidence"],
        "properties": {
          "field":      {"type": "string"},
          "source_url": {"type": "string", "description": "resolving source that backs the field; must load"},
          "confidence": {"type": "integer", "description": "0-100"}
        }
      }
    }
  }
}
```

Prompt (per entity, substitute):

> Build a diligence tear sheet for {ENTITY} (disambiguate to the correct legal entity first).
> Fields: corporate structure (type, parent/subsidiary, registration), ownership / ultimate
> beneficial owners where publicly sourced, jurisdictions, sanctions and watchlist exposure,
> litigation history, and regulatory status. For every field, cite a resolving source URL and
> give a 0-100 confidence. Never invent a value, an owner, a sanctions hit, or a case: if a
> fact isn't on a reachable source, return an empty string, and for a field you searched and
> found clean (e.g. sanctions), say "none found" rather than leaving it ambiguous. Prefer a
> small correct sheet over a full speculative one.

## Config seams (build on top)

1. **Input**: your entity list (names + domains, or names + jurisdiction); run one enrichment per row.
2. **Fields**: edit the `fields` object to your intake form. Keys become columns.
3. **Tier**: `core2x` default for diligence; `pro` for high-stakes single subjects, `core` for a lighter first pass.
4. **Screening discipline**: treat sanctions/watchlist fields as *leads*: confirm any hit against the issuing list's primary record before acting.

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Task API (stable,
`v1`): `POST /v1/tasks/runs` with `task_spec.output_schema`, then
`GET /v1/tasks/runs/{run_id}/result`; per-field citations return in `output.basis`. Auth via
`x-api-key`, server-side only. Hardcoding means you own keeping it current, prefer the CLI/MCP.

## Next

- Don't have the list yet → **exposure-discovery** (describe the population, get the entities).
- Go deeper on the priority subjects → **diligence-briefs** (full research report).
- Keep it fresh → **regulatory-monitoring** (alert when status changes or a new action lands).
