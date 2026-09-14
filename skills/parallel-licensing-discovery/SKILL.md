---
name: parallel-licensing-discovery
description: Describe business-development criteria in plain language and get a researched, source-cited list of assets or companies, including private biotechs that traditional databases may omit. Use when the user wants to find licensing targets, find companies with an asset that matches defined criteria, build a BD target list, or discover M&A candidates. Runs on the user's own Parallel account via FindAll.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *)
metadata:
  author: parallel
---

# Licensing Discovery (FindAll)

Describe your BD criteria in plain language, get back a **researched, cited list of assets or
companies**, including the long tail of private biotechs that never make it onto commercial
databases. Founding year, modality, indication, development stage, IP-rights status, whatever
defines a good-fit target. Every match resolves to a source; noise and non-matches are filtered.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

FindAll is exposed through **`parallel-cli findall`** (installed by `parallel-cli skills
install`), this is the maintained path, and it's what you should build on. FindAll is in
**public beta**, so the raw HTTP endpoints can change (30 days' notice); riding the CLI means
Parallel absorbs those changes on update. If Parallel is not configured, run the relevant setup skill first. Check [docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its therapeutic-area / modality framing (captured once at setup),
it seeds the criteria so you're not starting blank; confirm-or-tweak rather than re-ask.

Before the paid run:
1. **Describe your criteria** in plain language, be specific about the entity (asset or company), the modality / indication, the stage, and any IP or ownership filter.
2. **How many candidates?** Start around 25 (`-n 25`) to gauge quality, then extend.
3. **Preview first?** Run `ingest` (below) to see the parsed query before paying.

Confirm, then run.

## Run it

Preview the parsed query before you pay:

```
parallel-cli findall ingest "<your BD criteria in plain language>"
```

Then run and poll results to disk:

```
parallel-cli findall run "private biotechs with a clinical-stage autoimmune asset, founded after 2019, with ex-US IP rights unlicensed" -g core -n 50 --no-wait --json
parallel-cli findall poll "<findall_id>" -o /tmp/targets.json --timeout 540
```

Add fields to each candidate (optional):

```
parallel-cli findall enrich "<findall_id>" '{"properties":{"lead_asset":{"type":"string"},"phase":{"type":"string"},"modality":{"type":"string"},"last_financing":{"type":"string"}}}'
```

Each candidate returns `name`, `url`, `description`, a `match_status` (`matched` is the keeper),
enriched fields under `output`, and per-field citations under `basis`.

## Config seams (build on top)

1. **The objective:** your BD criteria in plain language. This is the whole input; be specific
   about the entity type, the modality / indication, the stage, and the IP / ownership filter.
2. **Generator tier:** `-g core` default, `-g pro` for a comprehensive or sparse universe,
   `-g preview` for a fast scan, skip `-g base` for real data.
3. **Count:** `-n` (5 to 1000); start small to gauge quality, then `parallel-cli findall extend
   "<id>" 50` for more.
4. **Enrichment fields:** the `properties` you add become columns (lead asset, phase, modality,
   last financing); keys are yours to define.
5. **Exclude:** `--exclude '[{"name":"...","url":"..."}]'` to skip names already in your CRM.

## Production (raw HTTP API): beta, verify before hardcoding

_As of 2026-08; FindAll is public beta, confirm at [docs.parallel.ai](https://docs.parallel.ai)._
`POST /v1beta/findall/ingest` → `POST /v1beta/findall/entity-search` (fast candidates) or the
full run → `GET /v1beta/findall/runs/{findall_id}/result` (returns `candidates[]` with `output`
+ `basis`). Because it's `v1beta`, prefer `parallel-cli findall` so tier/shape changes don't
break your build.

## Next

- Profile a shortlisted target in full → **competitive-landscape** or **life-sciences-quickstart**.
- Watch the target for readouts and deals → **pipeline-monitoring**.
- Pull the clinical data behind its lead asset → **literature-mining**.
