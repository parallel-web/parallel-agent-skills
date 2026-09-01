---
name: parallel-account-briefs
description: Full, source-cited pre-meeting brief on a target account, a snapshot (what they do, how they make money, how they're doing), their current business initiatives, why-now triggers, and who to reach (the buying committee). Use when the user wants a "pre-call brief", "deep research on this account", or "prep me for this meeting". Runs on the user's own Parallel account via Task deep research.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__Parallel-Task-MCP__createTaskGroup, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# Account Briefs

A full, cited pre-meeting brief on a target account, the deep version of the quickstart. It
gives a rep, in order: a one-glance **snapshot** (what they do, how they make money, how
they're doing), their current **business initiatives**, **why now** (recent triggers), and
**who to reach** (the buying committee). Every point is sourced and dated so it's auditable,
and nothing is fabricated, if it can't be verified it says so.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

- **Chat / co-work:** the **Task MCP** (`createTaskGroup`).
- **CLI / build-on-top:** the installed **`parallel-deep-research`** skill (`parallel-cli
  skills install`), maintained by Parallel.

Raw HTTP API at the bottom for pipelines. If Parallel is not configured, run the relevant setup skill first. See [docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its ICP / value framing (captured once at setup), don't re-ask it; only get the per-run specifics below.

1. **Which target company?** One domain, or a priority list (one run each).
2. **Which sections?** Default: snapshot, initiatives, why-now, who-to-reach.
3. **Tier?** `pro` for a real brief; `core2x`/`core` for routine or high volume.

Confirm, then run.

## Run it

Deep research warrants a higher tier, default `pro` here. Substitute the target domain.
Output shape:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["company", "snapshot", "business_initiatives", "why_now", "buying_committee"],
  "properties": {
    "company": {"type": "string"},
    "snapshot": {
      "type": "object",
      "additionalProperties": false,
      "required": ["what_they_do", "how_they_make_money", "business_health"],
      "properties": {
        "what_they_do": {"type": "string", "description": "one line: the product/service and who it's for"},
        "how_they_make_money": {"type": "string", "description": "revenue model / main lines of business"},
        "business_health": {"type": "string", "description": "how they're doing: growth, funding, scale, or trouble signs (sourced)"}
      }
    },
    "business_initiatives": {
      "type": "array",
      "description": "current, public strategic initiatives / priorities",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["initiative", "why_it_matters", "source_url"],
        "properties": {
          "initiative": {"type": "string", "description": "a current initiative/priority, from a public source"},
          "why_it_matters": {"type": "string", "description": "one line on the implication / the opening it creates"},
          "source_url": {"type": "string", "description": "resolving source; must load"}
        }
      }
    },
    "why_now": {
      "type": "array",
      "description": "recent triggers (last ~6 months) making now a good time to reach out; empty array if none",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["signal", "signal_date", "source_url"],
        "properties": {
          "signal": {"type": "string"},
          "signal_type": {"type": "string", "enum": ["funding", "hiring", "product_launch", "exec_change", "expansion", "customer_win", "m_and_a", "other"]},
          "signal_date": {"type": "string", "description": "ISO 8601 date"},
          "source_url": {"type": "string"}
        }
      }
    },
    "buying_committee": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["person_name", "title", "role_in_deal", "source_url"],
        "properties": {
          "person_name": {"type": "string"},
          "title": {"type": "string"},
          "role_in_deal": {"type": "string", "enum": ["champion", "economic_buyer", "influencer", "technical_evaluator", "blocker", "other"]},
          "source_url": {"type": "string"}
        }
      }
    }
  }
}
```

Prompt (substitute the target domain):

> Produce a pre-meeting brief on the company at {TARGET_DOMAIN}. Cite a resolving source with
> a date for every claim; never invent anything, say "Not found" if you can't verify it.
>
> 1) **Snapshot** (one line each): what they do, how they make money, and how they're doing as
> a business (growth, funding, scale, or trouble signs).
>
> 2) **Business initiatives:** their current, public strategic priorities. For each: the
> initiative (sourced) and one line on why it matters / the opening it creates.
>
> 3) **Why now:** recent events (last ~6 months), funding, notable hiring, a product/AI
> launch, an exec change, expansion, a customer win, or M&A, with a one-line summary, date,
> and source.
>
> 4) **Who to reach:** champion, economic buyer, technical evaluator, influencers, blockers,
> with name, exact title, role in the deal, and source.
>
> Lead the reader to: who they are, what they're focused on, why now, and who to call.

## Read it

Top to bottom: the **snapshot** (who they are in three lines) → **initiatives** (what they're
focused on, each with why it matters) → the freshest **why-now** as the reason to reach out
now → **who to reach** (champion + economic buyer first). Where something came back "Not
found", say so, the refusal to fabricate is the point.

## Config seams (build on top)

1. **Input**: one company, or batch a priority list (one run each).
2. **Sections**: edit the schema to the sections your reps want.
3. **Tier**: `pro` for a real brief; `core2x`/`core` for routine (see the tier guidance in this skill).

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Task API (stable,
`v1`): `POST /v1/tasks/runs` with `task_spec.output_schema`, `GET /v1/tasks/runs/{run_id}/result`;
citations in `output.basis`. Auth `x-api-key`, server-side only. Prefer the CLI/MCP unless you
need raw control.

## Next

- Just need who-to-reach + why-now fast → **gtm-quickstart** (the light version).
- Whole list, lighter → **account-enrichment** (tear sheets).
- Keep the brief live → **signal-monitoring**.
