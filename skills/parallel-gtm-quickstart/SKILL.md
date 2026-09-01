---
name: parallel-gtm-quickstart
description: Connect Parallel (if needed) and get go-to-market account intelligence for any company, who to reach (buying committee) and why now (recent cited signals). Use when the user asks to "research this account", "who do I reach at X and why now", "get me up to speed on a company before a call", or wants the Parallel GTM quickstart. Runs on the user's own Parallel account.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__Parallel-Task-MCP__createTaskGroup, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# GTM Quickstart

The fastest way to see Parallel work on a real account: name one company, get back the two
things a rep needs before touching it, **who to reach** (the buying committee) and **why
now** (a recent, cited signal). Every fact is backed by a resolving source; if something
can't be verified it comes back empty, never invented.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two ways to run, both maintained by Parallel so API changes are absorbed for you:
- **Chat / co-work:** the **Task MCP** (`createTaskGroup`).
- **CLI / build-on-top:** `parallel-cli` + the installed **`parallel-deep-research`** skill.

If Parallel is not configured, run the relevant setup skill first.
Processor tier guidance: the tier guidance in this skill.

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its company / ICP / value framing (captured once at setup), don't re-ask it; only get the per-run specifics below.

Two quick questions before running (the run costs credits):
1. **Which company?** A domain (e.g. `acme.com`). Resolve a bare name to a domain and confirm first.
2. **Technical or GTM/revenue sale?** Shapes which roles count as the committee. Default: technical.

Confirm, then run.

## Run it

Call `createTaskGroup` once with the company domain as the input, processor `core`, and the
output shape below. Poll `getStatus` until complete, then read with `getResultMarkdown`.

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["company", "buying_committee", "why_now"],
  "properties": {
    "company": {"type": "string"},
    "buying_committee": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["person_name", "title", "role_in_deal", "source_url", "confidence", "why_reach_them"],
        "properties": {
          "person_name": {"type": "string"},
          "title": {"type": "string"},
          "reports_to": {"type": "string", "description": "name/title this person reports to ONLY if a public source states it; else an empty string. Never inferred, never the literal 'null'"},
          "role_in_deal": {"type": "string", "enum": ["champion", "economic_buyer", "influencer", "technical_evaluator", "blocker", "other"]},
          "linkedin_url": {"type": "string", "description": "the person's LinkedIn; empty string if not found"},
          "source_url": {"type": "string", "description": "a resolving source backing this person + title; must load"},
          "confidence": {"type": "integer", "description": "0-100; low>=75, medium>=85, high>=95"},
          "why_reach_them": {"type": "string", "description": "one line on why this person matters"}
        }
      }
    },
    "why_now": {
      "type": "array",
      "description": "recent cited signals that make now a good time to reach out; empty array if none, never invented",
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
    }
  }
}
```

Prompt (substitute the domain):

> For the company at {COMPANY_DOMAIN}, produce go-to-market account intelligence, and cite a
> resolving source URL for every fact. (1) Buying committee: the likely champion, economic
> buyer, technical evaluator, and any clear influencers or blockers, with name, exact title,
> role in the deal, and LinkedIn to verify. Set reports_to only when a public source states
> the reporting line, else an empty string. (2) Why now: recent events (last ~6 months) that
> make now a good time to reach out (funding, notable hiring, a product/AI launch, an exec
> change, expansion, a customer win, M&A) with a one-line summary, date, and source. Never
> invent a name, title, signal, reporting line, or source. If you can't verify someone, say
> "Not found"; if there's no recent signal, return an empty why_now array. For any blank
> field use an empty string, never the word "null".

> Via the MCP, `createTaskGroup` takes a natural-language output description, not a strict
> schema, so the shape above is guidance there, lean on the prompt wording to keep it clean.

**Read it:** lead with the action, champion + economic buyer up top with a one-line why and a
clickable source, then the freshest "why now" as the reason to reach out. Where a role or
signal came back empty, say so, that refusal to fabricate is the point.

## Config seams (build on top)

1. **Input**: swap the single domain for your account list (run one per account).
2. **Fields**: edit the `buying_committee` / `why_now` shape to the columns you need; keys become columns.
3. **Tier**: `core` default; `core2x`/`pro` for depth, `lite` for a fast pass (see the tier guidance in this skill).

Riding the MCP/CLI means an API change is absorbed on update, you don't re-clone for it.

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Task API (stable,
`v1`): `POST /v1/tasks/runs` with `task_spec.output_schema`, then
`GET /v1/tasks/runs/{run_id}/result`; per-field citations in `output.basis`. Auth via
`x-api-key`, server-side only. Hardcoding means you own keeping it current, prefer the MCP/CLI.

## Next

- Whole book of accounts → **account-enrichment** (batch this shape per account).
- Keep it live → **signal-monitoring** (alert when a new signal fires or the org changes).
- Deeper on priority accounts → **account-briefs** (full research report).
