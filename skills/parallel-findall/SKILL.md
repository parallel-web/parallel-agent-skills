---
name: parallel-findall
description: "Discover entities (companies, people, products, etc.) matching a natural-language description. Use when the user asks to 'find all X' or 'list every Y that…' — e.g., 'Find AI startups that raised Series A in 2026', 'List roofing companies in Charlotte NC', 'Show me YC W24 dev tools companies'. Different from web-search (which returns webpages) and deep-research (which returns a narrative report). Use this when the user wants a structured list of entities."
user-invocable: true
argument-hint: <objective describing entities to find>
compatibility: Requires parallel-cli >= 0.6.0 and internet access.
allowed-tools: Bash(parallel-cli:*)
metadata:
  author: parallel
---

# FindAll: Entity Discovery

Find: $ARGUMENTS

> Full FindAll requires `parallel-cli` ≥ 0.3.0; the optional `entity-search` path requires ≥ 0.6.0. If a documented command or option is missing, update through the installation method used for this CLI, then retry. See <https://docs.parallel.ai/integrations/cli>.

## When to use this skill

Use FindAll for a structured list of entities matching a description. Use parallel-web-search for webpages or quick answers, parallel-deep-research for narrative analysis, and parallel-data-enrichment to add fields to a list the user already has.

Default to the comprehensive, asynchronous `findall run`. It supports match conditions, exclusions, enrichment, evidence, and entity types beyond companies and people. “Find all” does not guarantee exhaustive internet coverage.

Use the synchronous `entity-search` path only when the user explicitly wants a quick or rough list of companies or people and accepts results without individual verification. Do not choose it just because the entity type is supported. It has no exclusions, generator selection, enrichment, or FindAll condition/enrichment citations.

## Step 1: Start and retain the run

Choose an unused, descriptive, run-specific `$FILENAME` for the saved JSON files. Pass the user's objective as one quoted argument, without shell evaluation.

```bash
parallel-cli findall run "$ARGUMENTS" --no-wait --json -o "/tmp/$FILENAME-create.json"
```

Defaults are generator `core` and match limit `10`. Use `-n 50` for up to 50 matched entities; the allowed limit is 5–1000. Stay with `core` unless the user requests a different tradeoff. `pro` searches a larger pool and is slower/costlier; `base` is a faster, lower-quality option for an explicitly requested rough scan. Spot-check specific claims such as batch, year, and geography against available evidence, especially for `base`.

For requested exclusions:

```bash
parallel-cli findall run "$ARGUMENTS" --no-wait --json \
    --exclude '[{"name":"Google","url":"google.com"},{"name":"OpenAI","url":"openai.com"}]' \
    -o "/tmp/$FILENAME-create.json"
```

If the objective needs clarification, `parallel-cli findall ingest "$ARGUMENTS" --json` previews the inferred entity type, conditions, and suggested enrichments. This calls the API; it is not an offline or free test. Refine the objective before creating the run if the inferred conditions differ from the user's intent.

Capture the returned `findall_id` immediately, along with the objective, generator, match limit and exclusions. Report that the run started and give a monitoring URL only if one was actually returned. Do not infer a URL or a guaranteed completion time. If the creation response is lost, resolve the existing job before submitting again.

## Step 2: Add requested fields explicitly

`--no-wait` ingests and creates the run but does **not** apply suggested enrichments. Requested output fields such as CEO name or employee count need a separate enrichment request; mentioning them in the objective is insufficient.

```bash
parallel-cli findall enrich "$FINDALL_ID" \
    '{"type":"object","properties":{"ceo":{"type":"string","description":"CEO name"},"employee_count":{"type":"number","description":"Number of employees"}}}' \
    -p core --json
```

Use a JSON Schema object describing the user's fields, not the complete ingest envelope. Retain the exact submitted schema and processor locally with the run ID, including multiple requests if used. Do not rely on schema summaries to reconstruct them later. Enrichment adds non-boolean output data; it does not change match conditions.

Enrichment can be added while the run is active or after completion. A terminal run can requeue to process the fields. Creation, enrichment acceptance, and populated results are separate outcomes. Do not claim the fields are ready from the enrichment response or a completed poll alone.

## Step 3: Check status and retrieve results

```bash
parallel-cli findall status "$FINDALL_ID" --json
parallel-cli findall poll "$FINDALL_ID" -o "/tmp/$FILENAME.json" --timeout 60
parallel-cli findall result "$FINDALL_ID" -o "/tmp/$FILENAME-snapshot.json"
```

Use bounded waits. A timeout (exit 5) or interrupt is local wait exhaustion, not cancellation. Check status and resume the same ID while it is active, within the user's waiting window; do not submit another run. The shared poller does not recognize the compatibility status `action_required`. If that status, `failed`, `cancelled`, or an inactive unfinished state appears, stop automatic waiting and report the state and saved ID as needing attention.

`result` returns a snapshot and does not prove completion. Read `status` and `is_active` together. After enrichment, inspect each matched candidate's `output` for every requested field. If fields are missing, take further result snapshots within a bounded waiting window, even if the first poll said completed. Report missing, null, or failed values rather than inventing them; if the window expires, return partial results and the ID for resumption. An empty matched set is not proof of successful enrichment.

Avoid `--json` for large result sets; `-o` retains the complete JSON. These commands can overwrite their selected files, so use paths belonging to this run. Preserve the raw candidate list and status. `/tmp` is temporary; copy requested deliverables to a persistent user location when needed.

## Present matches and evidence

Present only candidates with `match_status: "matched"` as matches. Preserve generated, unmatched, and discarded candidates in the raw file. Review obvious query-echo placeholders and unsupported entries rather than treating every candidate as an entity.

Review URLs in the context of the entity. LinkedIn profiles can legitimately identify people, and YC or Crunchbase profiles can identify companies. Do not discard these solely because the entity does not own the domain. Flag missing or unverifiable URLs and use available evidence to resolve uncertainty.

Use condition and enrichment basis for factual claims, with its source URLs. The entity's primary URL and a supporting citation may differ. Do not label a primary/profile URL as evidence for an attribute unless it supports the claim.

Lead with the number of matched entities presented, note exclusions or unresolved entries, and use a table or list with names, URLs, and requested fields. Include the saved raw-results path, run ID, current state, and any incomplete fields. Sparse or noisy results can warrant suggesting a revised objective or generator; do not automatically create a replacement paid run.

## Get more matches

Extend only when the user requests additional matches:

```bash
parallel-cli findall schema "$FINDALL_ID" --json
parallel-cli findall extend "$FINDALL_ID" 50 --json
```

`50` is an increment, not the new total. Check the known creation limit or current schema, including prior extensions, so the resulting total stays at or below 1000. Preview runs cannot be extended. A completed run is eligible only if its termination reason was `match_limit_met`; status/result in the CLI omit that reason and cannot prove eligibility. For an explicitly requested extension within the limit, let the API validate eligibility and surface any rejection without creating a new run automatically.

Retain the updated limit and poll the same ID for new results. Recheck requested enrichment fields; if the existing enrichment must be reapplied, use the original retained request payload and processor within the user's authorized scope.

## Fast entity search

Use only for explicit speed/rough-list intent and entity type `companies` or `people`. It is synchronous and returns `entity_set_id` plus ranked `entities`, not `findall_id` or verified candidates.

```bash
parallel-cli findall entity-search "$ARGUMENTS" -t companies -n 10 -o "/tmp/$FILENAME.json"
```

The `-n` limit is 5–1000, default 10. Choose a limit proportional to the user's request. Avoid highly restrictive criteria on this path: relevance can decline toward the tail. Use full FindAll when individual condition checks or enrichment are required.

Keep legitimate directory/profile links and review empty URLs or query-echo names. Present these as unverified leads, cite their links as links to the entities, and avoid attributing absent FindAll basis or verification to them. Report the saved path and returned count. Never pass an `entity_set_id` to FindAll poll/status/result/enrich/extend. If the user later requests those capabilities, explain that a separate full run is needed and retain the original quick results.

## Setup

Requires an installed and authenticated `parallel-cli`. Check `parallel-cli --version` and `parallel-cli auth --json`; auth can exit successfully while `authenticated` is false. Missing binary, unsupported command/option, and authentication failure need different remedies: installation, upgrade through the existing installation method, or terminal login respectively. See <https://docs.parallel.ai/integrations/cli>. Stop the affected request on auth failure, do not ask for secrets in chat, and do not change account policy to work around blocked setup.
