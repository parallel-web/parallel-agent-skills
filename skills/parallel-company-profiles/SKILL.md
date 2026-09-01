---
name: parallel-company-profiles
description: Turn a company name or a list into structured, source-cited tear sheets, financials, leadership, competitive position, and strategic trajectory, with a confidence score and a source for every field. Use when the user wants to "build a tear sheet", "profile these companies", "prep a diligence one-pager", or profile a vendor or counterparty. Runs on the user's own Parallel account.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__Parallel-Task-MCP__createTaskGroup, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# Company Profiles

Give a company name, get back a structured, cited **tear sheet**, financials, leadership,
competitive position, and strategic trajectory, sourced from filings, investor materials, and
the web. Works the same for a target, a vendor, or a counterparty. Every field carries a
confidence score and a resolving source; if a fact isn't on a reachable source, the field
comes back empty, never guessed.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two ways to run, both maintained by Parallel so API changes are absorbed for you:
- **Chat / co-work:** the **Task MCP** (`createTaskGroup`), one input per company.
- **CLI / build-on-top:** `parallel-cli` + the installed **`parallel-data-enrichment`** skill
  (`parallel-cli skills install`).

If Parallel is not configured, run the relevant setup skill first. See
[docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its firm / mandate / diligence-focus framing (captured once at setup), don't re-ask it; only get the per-run specifics below.

Three quick questions before running (each company is a billable profile):
1. **Which company or list?** Names, names + domains, or a pasted list.
2. **Which fields?** Default is the tear sheet (financials, leadership, competitive position, strategic trajectory). Add or drop to match your diligence checklist.
3. **Run how many now?** Start with a small batch (5-10) to check quality, then scale.

Confirm, then run.

## Run it

One task per company (batch the list). Output shape, the tear sheet:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["company", "fields"],
  "properties": {
    "company": {"type": "string"},
    "fields": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "financials":            {"type": "string", "description": "revenue / EBITDA / margins with period; empty string if not public"},
        "ownership":             {"type": "string", "description": "public/private, owners or sponsor, last financing"},
        "leadership":            {"type": "string", "description": "CEO/CFO and other key executives"},
        "competitive_position":  {"type": "string", "description": "market, main competitors, how they differentiate"},
        "strategic_trajectory":  {"type": "string", "description": "current priorities and direction, sourced"}
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

Prompt (per company, substitute the name/domain):

> Build a tear sheet for {COMPANY}: financials (revenue, EBITDA, margins, with the period they
> cover), ownership (public or private, owners or sponsor, last financing), leadership (CEO,
> CFO, other key executives), competitive position (market, main competitors, how they
> differentiate), and strategic trajectory (current priorities and direction). Prefer SEC
> filings and investor materials for public companies. For every field, cite a resolving
> source URL and give a 0-100 confidence. Never invent a value, if a fact isn't on a reachable
> source, return an empty string for that field. Prefer a small correct sheet over a full
> speculative one.

## Config seams (build on top)

1. **Input**: your company list (names or names+domains); run one profile per row.
2. **Fields**: edit the `fields` object to your diligence checklist. Keys become columns.
3. **Tier**: `core` default; `core2x`/`pro` for depth on priority names, `lite` for a fast pass.

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Task API (stable,
`v1`): `POST /v1/tasks/runs` with `task_spec.output_schema`, then
`GET /v1/tasks/runs/{run_id}/result`; per-field citations return in `output.basis`. Auth via
`x-api-key`, server-side only. Hardcoding means you own keeping it current, prefer the CLI/MCP.

## Next

- Don't have the list yet → **target-discovery** (describe criteria, get candidates).
- Keep it fresh → **portfolio-monitoring** (re-profile or alert when something changes).
- Go deeper on a market or thesis → **thesis-research** (full cited report).
- Screening a counterparty → **kyb-kyc** (registry, ownership, sanctions, adverse media).
