---
name: parallel-entity-context
description: Enrich the people, companies, places, and topics your product touches, in a query, a doc, or a meeting, with cited real-world background so your product responds with the right context automatically. Use when the user wants to "add background on this person/company", "build a meeting brief", "who is X and why do they matter", or enrich an entity inline. Runs on the user's own Parallel account via Task.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__Parallel-Task-MCP__createTaskGroup, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# Entity Context

Enrich the people, companies, places, and topics your product touches, in a query, a doc, or a
meeting, so it responds with the right **background automatically**. Give it an entity, get back
a tight, cited briefing your product can drop inline. Every fact resolves to a source; anything
unverifiable comes back empty, never invented, so a meeting brief never puts a made-up detail in
front of a user.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two ways to run, both maintained by Parallel so API changes are absorbed for you:
- **Chat / co-work:** the **Task MCP** (`createTaskGroup`), one input per entity.
- **CLI / build-on-top:** `parallel-cli` + the installed **`parallel-data-enrichment`** skill
  (`parallel-cli skills install`).

Not set up yet?
If Parallel is not configured, run the relevant setup skill first.
See [docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its product / surfaces framing (captured once at setup), don't
re-ask it; only get the per-run specifics below.

Two quick questions before running (each entity is a billable enrichment):
1. **Which entity?** A person, company, place, or topic (with any disambiguator, e.g. the company they're at).
2. **For which surface?** A meeting brief, a doc annotation, or an inline answer, so the length and framing fit.

Confirm, then run.

## Run it

One task per entity. Output shape (a person shown; adapt fields per entity type):

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["entity", "briefing", "facts"],
  "properties": {
    "entity":   {"type": "string"},
    "briefing": {"type": "string", "description": "2-4 sentence background your product can show inline"},
    "facts": {
      "type": "array",
      "description": "the discrete cited facts behind the briefing; empty array if little can be sourced",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["fact", "source_url", "as_of"],
        "properties": {
          "fact":       {"type": "string", "description": "one sourced fact (role, recent move, funding, notable event)"},
          "source_url": {"type": "string", "description": "resolving source; must load"},
          "as_of":      {"type": "string", "description": "date of the fact / source"}
        }
      }
    }
  }
}
```

Prompt (substitute the entity + surface):

> Enrich {ENTITY} for a {SURFACE}. Return a 2-4 sentence background briefing and the discrete
> facts behind it, role and organization, recent moves or funding, and anything a user would want
> to know before engaging. Cite a resolving source with a date for every fact. Never invent a
> role, a fact, or a source, if something can't be verified, leave it out and keep the briefing
> to what's sourced. Keep it tight enough to show inline.

**Read it:** the `briefing` is what your product renders; the `facts` are the citations behind
it, each dated and clickable. If the facts list is thin, the briefing should be short and honest,
not padded.

## Config seams (build on top)

1. **Input:** the entity + surface; run one per entity, batch a meeting's attendees or a doc's mentions.
2. **Fields:** adapt the shape per entity type (company: funding, headcount, news; place: what it is, recent events).
3. **Length:** tune the briefing length to the surface (a chip vs a full brief).
4. **Tier:** `core` default; `core2x` for a priority entity, `lite` for a quick inline chip (see the tier guidance in this skill).

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Task API (stable,
`v1`): `POST /v1/tasks/runs` with `task_spec.output_schema`, then
`GET /v1/tasks/runs/{run_id}/result`; per-field citations in `output.basis`. Auth via
`x-api-key`, server-side only. Prefer the CLI/MCP unless you need raw control.

## Next

- Answer a follow-up question about the entity → **productivity-quickstart**.
- Keep the entity's context fresh → **knowledge-freshness**.
- Go deep on a question the entity raises → **in-product-research**.
