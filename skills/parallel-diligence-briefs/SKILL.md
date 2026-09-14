---
name: parallel-diligence-briefs
description: Full, source-cited pre-matter brief on a counterparty or target, a snapshot (what they are, how they're structured, how they're doing), corporate + ownership structure, litigation and regulatory history, key people, and red flags / why-now. Use when the user wants a "pre-deal brief", "deep diligence on this company", "prep me on this counterparty", or a full research memo on one entity. Runs on the user's own Parallel account via Deep Research.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__Parallel-Task-MCP__createTaskGroup, mcp__Parallel-Task-MCP__createDeepResearch, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# Diligence Briefs

A full, cited pre-matter brief on one counterparty or target, the deep version of the
quickstart. It gives you, in order: a one-glance **snapshot** (what they are, how they're
structured, how they're doing), **corporate + ownership structure**, **litigation and
regulatory history**, **key people**, and **red flags / why-now**. Every point is sourced and
dated so it's auditable, and nothing is fabricated, if it can't be verified it says so. It's a
research memo to prep a matter, not legal advice or a certified report.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

- **Chat / co-work:** the **Task MCP** (`createDeepResearch` for the full report, or
  `createTaskGroup` for the structured shape below).
- **CLI / build-on-top:** the installed **`parallel-deep-research`** skill (`parallel-cli
  skills install`), maintained by Parallel.

Raw HTTP API at the bottom for pipelines. If Parallel is not configured, run the relevant setup skill first. See [docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its jurisdiction / priority framing (captured once at setup), don't re-ask it; only get the per-run specifics below.

1. **Which entity?** One company (name + a disambiguator), or a priority list (one run each).
2. **Which sections?** Default: snapshot, structure + ownership, litigation + regulatory, key people, red flags.
3. **Tier?** `pro` for a real brief; `core2x`/`core` for routine or high volume (see the tier guidance in this skill).

Confirm, then run.

## Run it

Deep research warrants a higher tier, default `pro` here. Substitute the entity. Output shape:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["entity", "snapshot", "structure_ownership", "litigation_regulatory", "key_people", "red_flags"],
  "properties": {
    "entity": {"type": "string", "description": "the resolved entity (name + disambiguator)"},
    "snapshot": {
      "type": "object",
      "additionalProperties": false,
      "required": ["what_they_are", "how_structured", "business_health"],
      "properties": {
        "what_they_are": {"type": "string", "description": "one line: the business / activity and who it's for"},
        "how_structured": {"type": "string", "description": "entity type, domicile, parent/group at a glance"},
        "business_health": {"type": "string", "description": "how they're doing: scale, funding, trajectory, or trouble signs (sourced)"}
      }
    },
    "structure_ownership": {
      "type": "array",
      "description": "corporate structure and ownership, each point sourced",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["point", "source_url"],
        "properties": {
          "point": {"type": "string", "description": "e.g. registered as X in Y; parent is Z; UBO is W (only if sourced)"},
          "source_url": {"type": "string", "description": "resolving source; must load"}
        }
      }
    },
    "litigation_regulatory": {
      "type": "array",
      "description": "litigation, enforcement, and regulatory history; empty array if none found, never invented",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["matter", "type", "status", "date", "source_url"],
        "properties": {
          "matter": {"type": "string"},
          "type": {"type": "string", "enum": ["litigation", "enforcement", "regulatory_action", "investigation", "sanction", "other"]},
          "status": {"type": "string", "description": "e.g. filed, ongoing, settled, dismissed; empty if not sourced"},
          "date": {"type": "string", "description": "ISO 8601 date of the most relevant event"},
          "source_url": {"type": "string", "description": "resolving source (docket, filing, regulator, credible report)"}
        }
      }
    },
    "key_people": {
      "type": "array",
      "description": "directors, officers, or beneficial owners relevant to the matter",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["person_name", "role", "source_url"],
        "properties": {
          "person_name": {"type": "string"},
          "role": {"type": "string", "description": "title / relationship to the entity"},
          "source_url": {"type": "string"}
        }
      }
    },
    "red_flags": {
      "type": "array",
      "description": "concrete, sourced concerns and any why-now triggers; empty array if none, never speculative",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["flag", "source_url"],
        "properties": {
          "flag": {"type": "string", "description": "one line: the concern / trigger and why it matters"},
          "date": {"type": "string", "description": "ISO 8601 date if time-relevant; empty otherwise"},
          "source_url": {"type": "string"}
        }
      }
    }
  }
}
```

Prompt (substitute the entity):

> Produce a pre-matter diligence brief on {ENTITY} (disambiguate to the correct legal entity
> first). Cite a resolving source with a date for every claim; never invent anything, say
> "Not found" if you can't verify it.
>
> 1) **Snapshot** (one line each): what they are, how they're structured (entity type,
> domicile, parent/group), and how they're doing as a business.
>
> 2) **Structure + ownership:** corporate structure and ownership / ultimate beneficial owners,
> each point only where a source states it.
>
> 3) **Litigation + regulatory:** lawsuits, enforcement actions, regulatory actions,
> investigations, sanctions, each with description, type, status, date, and a resolving source.
>
> 4) **Key people:** directors, officers, or beneficial owners relevant to the matter, with
> role and source.
>
> 5) **Red flags / why-now:** concrete, sourced concerns and any recent triggers, with dates.
>
> Lead the reader to: what they are, how they're structured, what's on their record, who's
> behind them, and what to look at closely.

## Read it

Top to bottom: the **snapshot** (who they are in three lines) → **structure + ownership** →
**litigation + regulatory** (the record) → **key people** → **red flags / why-now** (what to
look at closely). Where something came back "Not found", say so, the refusal to fabricate is
the point, and the gaps tell you where to send a human or a paid database next.

## Config seams (build on top)

1. **Input**: one entity, or batch a priority list (one run each).
2. **Sections**: edit the schema to the sections your intake memo wants.
3. **Tier**: `pro` for a real brief; `core2x`/`core` for routine (see the tier guidance in this skill).

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Task API (stable,
`v1`): `POST /v1/tasks/runs` with `task_spec.output_schema`, `GET /v1/tasks/runs/{run_id}/result`;
citations in `output.basis`. Auth `x-api-key`, server-side only. Prefer the CLI/MCP unless you
need raw control.

## Next

- Just need the fast read → **legal-quickstart** (the light version).
- Whole list, lighter → **entity-diligence** (tear sheets).
- Quote the primary sources behind a finding → **source-grounded-research**.
- Keep the brief live → **regulatory-monitoring**.
