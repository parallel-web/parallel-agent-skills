---
name: parallel-finance-quickstart
description: Connect Parallel (if needed) and get a fast, source-cited snapshot of any company, what they do, how they make money, latest financials, and key people, with a source for every fact. Use when the user asks to "get me up to speed on a company", "quick read on X before a call", or wants the Parallel finance quickstart. Runs on the user's own Parallel account.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__Parallel-Task-MCP__createTaskGroup, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# Finance Quickstart

The fastest way to see Parallel work on a real company: name one, get back a tight, cited
**snapshot**, what they do, how they make money, the latest financials that are public, and
the key people. Every fact is backed by a resolving source; if something can't be verified it
comes back empty, never invented.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two ways to run, both maintained by Parallel so API changes are absorbed for you:
- **Chat / co-work:** the **Task MCP** (`createTaskGroup`).
- **CLI / build-on-top:** `parallel-cli` + the installed **`parallel-deep-research`** skill.

If Parallel is not configured, run the relevant setup skill first.
Processor tier guidance: the tier guidance in this skill.

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its firm / mandate framing (captured once at setup), don't re-ask it; only get the per-run specifics below.

Two quick questions before running (the run costs credits):
1. **Which company?** A domain (e.g. `acme.com`), or a ticker / name you resolve to one and confirm first.
2. **Public or private company?** Shapes where the financials come from (filings vs. estimates and press). Default: infer from the company.

Confirm, then run.

## Run it

Call `createTaskGroup` once with the company as the input, processor `core`, and the output
shape below. Poll `getStatus` until complete, then read with `getResultMarkdown`.

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["company", "what_they_do", "how_they_make_money", "financials", "key_people"],
  "properties": {
    "company": {"type": "string"},
    "what_they_do": {"type": "string", "description": "one line: the business and who it serves"},
    "how_they_make_money": {"type": "string", "description": "revenue model / main lines of business"},
    "financials": {
      "type": "array",
      "description": "the public financial facts you can source; empty array if none are public",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["metric", "value", "as_of", "source_url"],
        "properties": {
          "metric": {"type": "string", "description": "e.g. revenue, EBITDA, headcount, last raise"},
          "value": {"type": "string"},
          "as_of": {"type": "string", "description": "period or date the figure covers"},
          "source_url": {"type": "string", "description": "resolving source; must load"}
        }
      }
    },
    "key_people": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["person_name", "title", "source_url"],
        "properties": {
          "person_name": {"type": "string"},
          "title": {"type": "string"},
          "source_url": {"type": "string", "description": "resolving source backing name + title; must load"}
        }
      }
    }
  }
}
```

Prompt (substitute the company):

> For the company at {COMPANY}, produce a fast snapshot and cite a resolving source URL for
> every fact. (1) What they do, in one line. (2) How they make money. (3) Financials: the
> public figures you can source, revenue, EBITDA, headcount, last financing, each with the
> period it covers and a source; prefer filings for public companies. (4) Key people: the
> executives who matter, with exact title and a source to verify. Never invent a figure, a
> name, or a source. If a fact isn't on a reachable source, leave it out rather than guess;
> for any blank field use an empty string, never the word "null".

> Via the MCP, `createTaskGroup` takes a natural-language output description, not a strict
> schema, so the shape above is guidance there, lean on the prompt wording to keep it clean.

**Read it:** lead with what they do and how they make money, then the freshest sourced
financials, then who to know. Where a figure came back empty, say so, that refusal to
fabricate is the point.

## Config seams (build on top)

1. **Input**: swap the single company for a list (run one per company).
2. **Fields**: edit the `financials` / `key_people` shape to what you track; keys become columns.
3. **Tier**: `core` default; `core2x`/`pro` for depth, `lite` for a fast pass (see the tier guidance in this skill).

Riding the MCP/CLI means an API change is absorbed on update, you don't re-clone for it.

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Task API (stable,
`v1`): `POST /v1/tasks/runs` with `task_spec.output_schema`, then
`GET /v1/tasks/runs/{run_id}/result`; per-field citations in `output.basis`. Auth via
`x-api-key`, server-side only. Hardcoding means you own keeping it current, prefer the MCP/CLI.

## Next

- Whole list, or a fuller sheet → **company-profiles** (financials, leadership, competitive position, trajectory).
- Keep it live → **portfolio-monitoring** (alert when a filing, an exec change, or an earnings signal fires).
- Deeper on a market question → **thesis-research** (a full cited report).
