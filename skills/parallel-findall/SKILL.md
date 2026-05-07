---
name: parallel-findall
description: "Discover entities (companies, people, products, etc.) matching a natural-language description. Use when the user asks to 'find all X' or 'list every Y that…' — e.g., 'Find AI startups that raised Series A in 2026', 'List roofing companies in Charlotte NC', 'Show me YC W24 dev tools companies'. Different from web-search (which returns webpages) and deep-research (which returns a narrative report). Use this when the user wants a structured list of entities."
user-invocable: true
argument-hint: <objective describing entities to find>
compatibility: Requires parallel-cli >= 0.3.0 and internet access.
allowed-tools: Bash(parallel-cli:*)
metadata:
  author: parallel
---

# FindAll: Entity Discovery

Find: $ARGUMENTS

> Requires `parallel-cli` ≥ 0.3.0 (the `findall` command was added in 0.3.0). If `parallel-cli findall` errors with `no such command` or similar, tell the user to run `parallel-cli update` (or `pipx upgrade parallel-web-tools` if installed via pipx), then retry.

## When to use this skill

Use FindAll when the user wants a **structured list of entities** matching a description, not webpages or a narrative answer.

| User asks for… | Use |
|---|---|
| "Find all X that…" / "List every Y…" | **parallel-findall** (this skill) |
| Webpage results / quick answers / current info | parallel-web-search |
| Narrative report / analysis / "research X" | parallel-deep-research |
| Add fields to a list you already have | parallel-data-enrichment |

If the user already has a list and just wants to add fields, this is the wrong skill — use parallel-data-enrichment.

## Step 1: Start the run

```bash
parallel-cli findall run "$ARGUMENTS" --no-wait --json
```

Defaults: generator `core`, match limit `10`. Stick with `core` unless the user has a reason to escalate:
- `-g pro` — most thorough generator (slower, costlier). Use when the user asks for "comprehensive" coverage or matches are sparse on `core`
- `-g base` — fastest, but **markedly lower quality**. Often returns query-echo entities (e.g., directory pages, the literal query string), entries with no URL, or category placeholders. Only use if the user explicitly asks for a quick scan and accepts noise; otherwise prefer `core`
- `-n 50` — return up to 50 matched entities (5–1000 allowed)

If the user wants to exclude known entities (e.g., "find competitors but not Google or OpenAI"):

```bash
parallel-cli findall run "$ARGUMENTS" --no-wait --json \
    --exclude '[{"name":"Google","url":"google.com"},{"name":"OpenAI","url":"openai.com"}]'
```

Tip — preview the schema first if the objective is ambiguous: `parallel-cli findall ingest "$ARGUMENTS" --json` shows the entity type and match conditions the API inferred, so you can refine wording before paying for a run.

Parse the JSON output to extract the `findall_id` and any monitoring URL. Tell the user:
- A FindAll run has been started
- Approximate cadence (minutes for `core`, longer for `pro`)
- They can keep working while it runs

## Step 2: Poll for results

Choose a descriptive filename (e.g., `series-a-ai-2026`, `charlotte-roofers`). Use lowercase with hyphens, no spaces.

```bash
parallel-cli findall poll "$FINDALL_ID" -o "/tmp/$FILENAME.json" --timeout 540
```

Important:
- Use `--timeout 540` (9 minutes) to stay within tool execution limits
- Do NOT pass `--json` for large result sets — it will flood context. `-o` saves the full results to disk

### If the poll times out

Re-run the same `parallel-cli findall poll` command to continue waiting. Server-side the run continues regardless.

## Response format

Before presenting matches, **filter the results** for obvious noise:
- Drop entries with empty/missing `url`
- Drop entries whose `name` echoes the user's query (e.g., literal "YC W25 batch companies in developer tools") — those are search-result placeholders, not real entities
- Drop entries whose `url` is a third-party directory or profile page rather than the entity's own domain. Concretely: drop URLs on `linkedin.com`, `ycombinator.com/companies/...`, `crunchbase.com`, `pitchbook.com`, generic news/blog posts about the entity, etc. The URL should be something the entity itself owns (its product site, docs, or marketing site)

If filtering removes a meaningful share of matches, mention this to the user and suggest re-running with `-g pro` or a higher `-n`.

**Sanity-check `-g base` results.** The base generator can hallucinate categorical attributes (e.g., return a YC S22 company as a YC W25 match). The filter rules above only catch URL/name shape, not factual correctness. If the user's query has a falsifiable attribute (a specific batch, year, geography, etc.), spot-check the kept entries against the source URL and flag any that don't fit. Recommend re-running with `-g core` (or higher) if **either** multiple kept entries fail the spot-check **or** noise filtering dropped a meaningful share of the matched set (say, ≥40%) — both indicate `base` isn't producing reliable results for this query.

Present the remaining (real) entities as a markdown table or list. Lead with the count, then list each entity with its name, URL, and a one-line description if available. Cite each entity with its source URL.

Tell the user:
- How many entities were matched (and how many were filtered as noise, if any)
- The full results path (`/tmp/$FILENAME.json`)
- That they can:
  - Add fields to these results, e.g.:

    ```bash
    parallel-cli findall enrich $FINDALL_ID '{"properties":{"ceo":{"type":"string"},"employee_count":{"type":"number"}}}'
    ```

    The schema is a JSON Schema-style object with `properties` mapping field names → `{type, description?}`.
  - Get more matches: `parallel-cli findall extend $FINDALL_ID 50`

## Setup

Requires `parallel-cli` (installed and authenticated). If `parallel-cli --version` fails, or if a later command fails with an authentication error, tell the user to see https://docs.parallel.ai/integrations/cli and stop.
