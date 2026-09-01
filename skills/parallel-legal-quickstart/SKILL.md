---
name: parallel-legal-quickstart
description: Connect Parallel (if needed) and get the legal facts on any entity or matter fast, who they are legally, litigation and regulatory posture, and red flags, every fact backed by a resolving source. Use when the user asks to "run a quick check on this company", "what's the litigation/regulatory history of X", "get me up to speed on a counterparty", or wants the Parallel legal quickstart. Runs on the user's own Parallel account.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__Parallel-Task-MCP__createTaskGroup, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# Legal Quickstart

The fastest way to see Parallel work on a real entity: name one company, get back the things
you need before you touch a matter, **who they are legally** (entity profile + jurisdiction),
their **litigation and regulatory posture**, and any **red flags**. Every fact is backed by a
resolving source; if something can't be verified it comes back empty, never invented. This is
a research layer, not legal advice, treat outputs as cited leads to verify.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two ways to run, both maintained by Parallel so API changes are absorbed for you:
- **Chat / co-work:** the **Task MCP** (`createTaskGroup`).
- **CLI / build-on-top:** `parallel-cli` + the installed **`parallel-deep-research`** skill.

If Parallel is not configured, run the relevant setup skill first. Processor
tier guidance: the tier guidance in this skill.

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its organization / jurisdiction / priority framing (captured once at setup), don't re-ask it; only get the per-run specifics below.

Two quick questions before running (the run costs credits):
1. **Which entity?** A company name and, ideally, a domain or jurisdiction to disambiguate. Resolve a bare name and confirm which entity you mean first, wrong-entity is the classic diligence error.
2. **What angle matters most?** Litigation history, regulatory/enforcement posture, sanctions/ownership, or a general check. Default: general check across all.

Confirm, then run.

## Run it

Call `createTaskGroup` once with the entity as the input, processor `core`, and the output
shape below. Poll `getStatus` until complete, then read with `getResultMarkdown`.

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["entity", "profile", "litigation_and_regulatory", "red_flags"],
  "properties": {
    "entity": {"type": "string", "description": "the resolved entity you researched (name + a disambiguator)"},
    "profile": {
      "type": "object",
      "additionalProperties": false,
      "required": ["legal_name", "what_they_do", "jurisdiction", "source_url"],
      "properties": {
        "legal_name": {"type": "string", "description": "registered legal name if found; else best-known name"},
        "what_they_do": {"type": "string", "description": "one line: the business / activity"},
        "jurisdiction": {"type": "string", "description": "domicile / registration jurisdiction if sourced; else empty string"},
        "entity_type": {"type": "string", "description": "e.g. Delaware C-corp, LLP, GmbH; empty if not sourced"},
        "source_url": {"type": "string", "description": "a resolving source backing the profile; must load"}
      }
    },
    "litigation_and_regulatory": {
      "type": "array",
      "description": "notable litigation, enforcement, or regulatory matters; empty array if none found, never invented",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["matter", "type", "status", "date", "source_url"],
        "properties": {
          "matter": {"type": "string", "description": "one-line factual description"},
          "type": {"type": "string", "enum": ["litigation", "enforcement", "regulatory_action", "investigation", "sanction", "other"]},
          "status": {"type": "string", "description": "e.g. filed, ongoing, settled, dismissed; empty if not sourced"},
          "date": {"type": "string", "description": "ISO 8601 date of the most relevant event"},
          "source_url": {"type": "string", "description": "resolving source; must load (docket, filing, regulator, credible report)"}
        }
      }
    },
    "red_flags": {
      "type": "array",
      "description": "concrete, sourced concerns worth a closer look; empty array if none, never speculative",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["flag", "source_url"],
        "properties": {
          "flag": {"type": "string", "description": "one line: the concern and why it matters"},
          "source_url": {"type": "string"}
        }
      }
    }
  }
}
```

Prompt (substitute the entity):

> For {ENTITY}, produce a fast legal read and cite a resolving source URL for every fact.
> (1) Profile: registered legal name, one line on what they do, domicile / registration
> jurisdiction, and entity type, only when a source states it. (2) Litigation and regulatory:
> notable lawsuits, enforcement actions, regulatory actions, investigations, or sanctions,
> each with a one-line description, type, status, date, and a resolving source (a docket,
> filing, regulator page, or credible report). (3) Red flags: concrete, sourced concerns
> worth a closer look. Never invent a matter, name, date, status, or source. If you can't
> verify something, leave it out or return an empty array, do not speculate. First disambiguate
> which entity is meant if the name is ambiguous. For any blank field use an empty string,
> never the word "null".

> Via the MCP, `createTaskGroup` takes a natural-language output description, not a strict
> schema, so the shape above is guidance there, lean on the prompt wording to keep it clean.

**Read it:** lead with the entity and one-line profile, then anything in
`litigation_and_regulatory` and `red_flags` (these are the reason to look closer), each with
a clickable source. Where a section came back empty, say "none found in public sources", that
refusal to fabricate, and the honest "none found", is the point in legal work.

## Config seams (build on top)

1. **Input**: swap the single entity for your list (run one per entity).
2. **Fields**: edit the shape to the angles you triage on; keys become columns.
3. **Tier**: `core` default; `core2x`/`pro` for a deeper read, `lite` for a fast scan (see the tier guidance in this skill).

Riding the MCP/CLI means an API change is absorbed on update, you don't re-clone for it.

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Task API (stable,
`v1`): `POST /v1/tasks/runs` with `task_spec.output_schema`, then
`GET /v1/tasks/runs/{run_id}/result`; per-field citations in `output.basis`. Auth via
`x-api-key`, server-side only. Hardcoding means you own keeping it current, prefer the MCP/CLI.

## Next

- A whole list of counterparties → **entity-diligence** (batch this shape per entity).
- Need to quote the actual statute/case → **source-grounded-research**.
- Keep it live → **regulatory-monitoring** (alert when a new filing or action lands).
- Deeper on one subject → **diligence-briefs** (full research report).
