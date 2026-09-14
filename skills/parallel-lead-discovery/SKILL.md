---
name: parallel-lead-discovery
description: Describe your ICP in plain language and get back a researched, source-cited list of candidate accounts (or people), including the long tail that isn't in existing databases. Use when the user wants to "find companies like X", "generate a prospect list", "find all Y matching Z", or build a net-new list. Runs on the user's own Parallel account via FindAll.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *)
metadata:
  author: parallel
---

# Lead Discovery (FindAll)

Describe your ideal customer in plain language, get back a **researched, cited list of
candidates**. Works across companies, people, and the long tail of entities that don't fit
existing databases. Every match resolves to a source; noise and non-matches are filtered.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

FindAll is exposed through **`parallel-cli findall`** (installed by `parallel-cli skills
install`), this is the maintained path, and it's what you should build on. FindAll is in
**public beta**, so the raw HTTP endpoints can change (30 days' notice); riding the CLI means
Parallel absorbs those changes on update. If Parallel is not configured, run the relevant setup skill first. Check [docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its company / ICP / value framing (captured once at setup), it seeds the ICP so you're not starting blank; confirm-or-tweak rather than re-ask.

Before the paid run:
1. **Describe your ICP** in plain language, be specific about the entity type and the criteria.
2. **How many candidates?** Start around 25 (`-n 25`) to gauge quality, then extend.
3. **Preview first?** Run `ingest` (below) to see the parsed query before paying.

Confirm, then run.

## Run it

Preview the parsed query before you pay:

```
parallel-cli findall ingest "<your ICP in plain language>"
```

Then run and poll results to disk:

```
parallel-cli findall run "B2B SaaS companies, 200 to 2000 employees, that raised a Series A or B this year and are hiring engineers to build AI agents" -g core -n 50 --no-wait --json
parallel-cli findall poll "<findall_id>" -o /tmp/leads.json --timeout 540
```

Add fields to each candidate (optional):

```
parallel-cli findall enrich "<findall_id>" '{"properties":{"funding_stage":{"type":"string"},"hq_location":{"type":"string"},"employee_count":{"type":"number"}}}'
```

Each candidate returns `name`, `url`, `description`, a `match_status` (`matched` is the
keeper), enriched fields under `output`, and per-field citations under `basis`.

## Config seams (build on top)

1. **The objective**: your ICP in plain language. This is the whole input; be specific
   about the entity type and the criteria.
2. **Generator tier**: `-g core` default, `-g pro` for comprehensive/sparse, `-g preview`
   for a fast scan, skip `-g base` for real data.
3. **Count**: `-n` (5 to 1000); start small to gauge quality, then `parallel-cli findall
   extend "<id>" 50` for more.
4. **Enrichment fields**: the `properties` you add become columns; keys are yours to define.
5. **Exclude**: `--exclude '[{"name":"...","url":"..."}]'` to skip what you already have.

## Production (raw HTTP API): beta, verify before hardcoding

_As of 2026-08; FindAll is public beta, confirm at [docs.parallel.ai](https://docs.parallel.ai)._
`POST /v1beta/findall/ingest` → `POST /v1beta/findall/entity-search` (fast candidates) or the
full run → `GET /v1beta/findall/runs/{findall_id}/result` (returns `candidates[]` with
`output` + `basis`). Because it's `v1beta`, prefer `parallel-cli findall` so tier/shape changes
don't break your build.

## Next

- Enrich the list into full tear sheets → **account-enrichment**.
- Watch the new accounts for the right time to reach out → **signal-monitoring**.
