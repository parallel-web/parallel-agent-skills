---
name: parallel-org-chart
description: Build a structured, source-cited org chart for a company or a department, the people, exact titles, reporting lines, seniority, and likely deal roles, so you can see who to reach and who reports to whom. Use when the user wants to "build an org chart", "map the engineering org", "who reports to whom at X", "who are the decision makers", or multithread an account. Runs on the user's own Parallel account via Task deep research.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__Parallel-Task-MCP__createTaskGroup, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# Org Chart

Build a **structured, cited org chart** for a company or a single department: the people, their
exact titles, the reporting lines, seniority, and which of them map to buying roles for your
deal. It's the deep version of the quickstart's buying committee, a multi-level map you can
render as a tree and multithread against, instead of a one-line shortlist. Every person resolves
to a source; a reporting line is set only when a public source states it, never inferred.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two ways to run, both maintained by Parallel so API changes are absorbed for you:
- **Chat / co-work:** the **Task MCP** (`createTaskGroup`).
- **CLI / build-on-top:** `parallel-cli` + the installed **`parallel-deep-research`** skill
  (`parallel-cli skills install`).

If Parallel is not configured, run the relevant setup skill first. See [docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its ICP / what-you-sell framing (captured once at setup) to decide
which org to map and which roles count as the buying committee, don't re-ask it; only get the
per-run specifics below.

Three quick questions before running (a deep org map is a billable run):
1. **Which company, and which org?** A domain, and the department to map (default: Engineering, since that's usually where the technical buyer sits).
2. **How deep?** How many levels down from the top of that org (default: through front-line managers).
3. **Watch it after?** Whether to set a monitor for changes to the chart (new hires, departures, reporting shifts), see `parallel-signal-monitoring`.

Confirm, then run.

## Run it

Deep research warrants a higher tier, default `pro` here (a wrong reporting line sends a rep to
the wrong person). Substitute the company + org. Poll `getStatus`, then read with
`getResultMarkdown`.

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["company", "org", "people"],
  "properties": {
    "company": {"type": "string"},
    "org": {"type": "string", "description": "the department/org mapped, e.g. Engineering"},
    "people": {
      "type": "array",
      "description": "the org, top-down; empty array if nothing can be sourced, never invented",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["person_name", "title", "reports_to", "source_url", "confidence"],
        "properties": {
          "person_name": {"type": "string"},
          "title": {"type": "string", "description": "exact current title"},
          "department": {"type": "string"},
          "reports_to": {"type": "string", "description": "name/title of the manager ONLY if a public source states it; else an empty string. Never inferred, never the literal 'null'"},
          "seniority": {"type": "string", "enum": ["c_level", "vp", "director", "manager", "ic", "unknown"]},
          "role_in_deal": {"type": "string", "enum": ["champion", "economic_buyer", "influencer", "technical_evaluator", "blocker", "none"], "description": "likely role for this deal; 'none' if not a buyer"},
          "linkedin_url": {"type": "string", "description": "the person's LinkedIn; empty string if not found"},
          "source_url": {"type": "string", "description": "resolving source backing name + title (and the reporting line, if set); must load"},
          "confidence": {"type": "integer", "description": "0-100; low>=75, medium>=85, high>=95"}
        }
      }
    }
  }
}
```

Prompt (substitute the domain, org, depth):

> Build an org chart for {COMPANY_DOMAIN}'s {ORG} organization, from the top of that org down
> through {DEPTH} (e.g. front-line managers). For each person return: name, exact current title,
> department, who they report to, seniority, and LinkedIn. Set reports_to only when a public
> source states the reporting line, else an empty string, never infer it. Flag each person's
> likely role in a {WHAT_YOU_SELL} deal (champion, economic buyer, technical evaluator,
> influencer, blocker, or none). Cite a resolving source URL and a 0-100 confidence for every
> person. Never invent a person, a title, a reporting line, or a source; if you can't verify
> someone, leave them out rather than guess, and use an empty string for any blank field, never
> the word "null". Prefer a smaller correct chart over a padded speculative one.

**Read it:** render it top-down, C-level to VPs to directors to managers, with reporting lines
where they're sourced and the deal roles highlighted (champion and economic buyer first). An
empty `reports_to` means the reporting line wasn't on a public source, not that the person has no
manager, treat it as a gap to confirm, not a fact. To put a UI on top, hand the `people` array to
Claude and ask it to render the hierarchy.

## Config seams (build on top)

1. **Input:** the company + the org to map; run one per account, or batch your target list.
2. **Depth:** how many levels down (whole org vs just the leadership layer).
3. **Deal roles:** the `role_in_deal` mapping keys off what you sell (from the workspace `PROFILE.md` file); edit the enum to your motion.
4. **Tier:** `pro` default for a real chart; `core2x` for a lighter or higher-volume pass (see the tier guidance in this skill).
5. **Keep it live:** pair with **signal-monitoring** to watch the chart for new hires, departures, and reporting-line changes.

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Task API (stable,
`v1`): `POST /v1/tasks/runs` with a `pro` processor and `task_spec.output_schema`, then
`GET /v1/tasks/runs/{run_id}/result`; per-field citations and confidence in `output.basis`. Auth
via `x-api-key`, server-side only. Hardcoding means you own keeping it current, prefer the MCP/CLI.

## Next

- Just need who to reach + why now, fast → **gtm-quickstart** (the light version).
- Watch the chart for changes → **signal-monitoring** (new hires, departures, reporting shifts).
- Full pre-meeting brief on the account → **account-briefs**.
