---
name: parallel-exposure-discovery
description: Describe a legal population in plain language and get back a researched, source-cited list of the entities in it, including the long tail that isn't in existing databases, "all companies subject to regulation X", "all litigation involving Y", "all entities on watchlist Z", "all portfolio companies exposed to sanctions regime W". Use when the user wants to "find all entities that...", "map exposure to...", "build a population of...", or enumerate a legal set. Runs on the user's own Parallel account via FindAll.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *)
metadata:
  author: parallel
---

# Exposure Discovery (FindAll)

Describe a legal population in plain language, get back a **researched, cited list of the
entities in it**. Works across companies, people, matters, and the long tail that doesn't fit
existing databases: everyone subject to a rule, everyone in a litigation, everyone exposed to
a sanctions regime. Every match resolves to a source; noise and non-matches are filtered.
It's a discovery layer to build a working set, verify each member against its primary source
before you act on it.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

FindAll is exposed through **`parallel-cli findall`** (installed by `parallel-cli skills
install`), this is the maintained path, and it's what you should build on. FindAll is in
**public beta**, so the raw HTTP endpoints can change (30 days' notice); riding the CLI means
Parallel absorbs those changes on update. If Parallel is not configured, run the relevant setup skill first. Check [docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its jurisdiction framing (captured once at setup) to scope the population, don't re-ask it; confirm-or-tweak rather than re-ask.

Before the paid run:
1. **Describe the population** in plain language, be specific about the entity type and the criteria that define membership (the rule, the jurisdiction, the matter, the threshold).
2. **How many candidates?** Start around 25 (`-n 25`) to gauge quality and precision, then extend.
3. **Preview first?** Run `ingest` (below) to see the parsed query before paying.

Confirm, then run.

## Run it

Preview the parsed query before you pay:

```
parallel-cli findall ingest "<your population in plain language>"
```

Then run and poll results to disk:

```
parallel-cli findall run "US-registered money services businesses that had a state regulator enforcement action in the last 24 months" -g core -n 50 --no-wait --json
parallel-cli findall poll "<findall_id>" -o /tmp/population.json --timeout 540
```

Add fields to each member (optional):

```
parallel-cli findall enrich "<findall_id>" '{"properties":{"jurisdiction":{"type":"string"},"action_date":{"type":"string"},"regulator":{"type":"string"}}}'
```

Each candidate returns `name`, `url`, `description`, a `match_status` (`matched` is the
keeper), enriched fields under `output`, and per-field citations under `basis`. Keep only
`matched`, and treat each as a lead to confirm against its cited primary source.

## Config seams (build on top)

1. **The objective**: your population in plain language. This is the whole input; be specific
   about the entity type and the membership criteria (rule, jurisdiction, matter, threshold).
2. **Generator tier**: `-g core` default, `-g pro` for comprehensive/sparse populations,
   `-g preview` for a fast scan, skip `-g base` for real data.
3. **Count**: `-n` (5 to 1000); start small to check precision, then `parallel-cli findall
   extend "<id>" 50` for more.
4. **Enrichment fields**: the `properties` you add become columns (jurisdiction, action date,
   regulator, docket); keys are yours to define.
5. **Exclude**: `--exclude '[{"name":"...","url":"..."}]'` to skip entities you've already cleared.

## Production (raw HTTP API): beta, verify before hardcoding

_As of 2026-08; FindAll is public beta, confirm at [docs.parallel.ai](https://docs.parallel.ai)._
`POST /v1beta/findall/ingest` → `POST /v1beta/findall/entity-search` (fast candidates) or the
full run → `GET /v1beta/findall/runs/{findall_id}/result` (returns `candidates[]` with
`output` + `basis`). Because it's `v1beta`, prefer `parallel-cli findall` so tier/shape changes
don't break your build.

## Next

- Run full diligence on each member → **entity-diligence** (tear sheet per entity).
- Watch the population for new members or status changes → **regulatory-monitoring**.
- Go deep on a priority member → **diligence-briefs**.
