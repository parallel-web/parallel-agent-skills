---
name: parallel-account-enrichment
description: Enrich a list of accounts into structured, source-cited tear sheets, revenue band, headcount, tech stack, funding, strategic initiatives, with a confidence score and a source for every field. Use when the user wants to "enrich these accounts", "build tear sheets", "fill in our CRM", or turn a prospect list into CRM-ready intelligence. Runs on the user's own Parallel account.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__Parallel-Task-MCP__createTaskGroup, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# Account Enrichment

Start with a list of accounts, get back a structured, cited **tear sheet** for each, ready
for your CRM. Every field carries a confidence score and a resolving source; if a fact
isn't on a reachable source, the field comes back empty, never guessed.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two ways to run, both maintained by Parallel so API changes are absorbed for you:
- **Chat / co-work:** the **Task MCP** (`createTaskGroup`), one input per account.
- **CLI / build-on-top:** `parallel-cli` + the installed **`parallel-data-enrichment`** skill
  (`parallel-cli skills install`).

If Parallel is not configured, run the relevant setup skill first. See
[docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its company / ICP / value framing (captured once at setup), don't re-ask it; only get the per-run specifics below.

Three quick questions before running (each account is a billable enrichment):
1. **Your account list?** Domains, names + domains, or a pasted list.
2. **Which fields?** Default is the tear sheet (revenue band, headcount, tech stack, funding, strategy). Add or drop to match your CRM.
3. **Run how many now?** Start with a small batch (5-10) to check quality, then scale.

Confirm, then run.

## Run it

One task per account (batch the list). Output shape, the tear sheet:

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
        "revenue_band":         {"type": "string", "description": "e.g. $20-50M; empty string if not found"},
        "headcount":            {"type": "string", "description": "e.g. 201-500; empty if not found"},
        "tech_stack":           {"type": "string", "description": "notable tools/platforms in use"},
        "funding":              {"type": "string", "description": "latest round + amount + date"},
        "strategic_initiatives":{"type": "string", "description": "current priorities / direction"}
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

Prompt (per account, substitute the domain):

> Build a tear sheet for the company at {COMPANY_DOMAIN}: revenue band, headcount, tech
> stack, latest funding (round, amount, date), and current strategic initiatives. For every
> field, cite a resolving source URL and give a 0-100 confidence. Never invent a value, if a
> fact isn't on a reachable source, return an empty string for that field. Prefer a small
> correct sheet over a full speculative one.

## Config seams (build on top)

1. **Input**: your account list (domains or names+domains); run one enrichment per row.
2. **Fields**: edit the `fields` object to the columns your CRM needs. Keys become columns.
3. **Tier**: `core` default; `core2x`/`pro` for depth, `lite` for a fast pass.

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Task API (stable,
`v1`): `POST /v1/tasks/runs` with `task_spec.output_schema`, then
`GET /v1/tasks/runs/{run_id}/result`; per-field citations return in `output.basis`. Auth via
`x-api-key`, server-side only. Hardcoding means you own keeping it current, prefer the CLI/MCP.

## Next

- Don't have the list yet → **lead-discovery** (describe your ICP, get candidates).
- Keep it fresh → **signal-monitoring** (re-enrich or alert when something changes).
- Go deeper on the priority accounts → **account-briefs** (full research report).
