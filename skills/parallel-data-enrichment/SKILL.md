---
name: parallel-data-enrichment
description: "Bulk data enrichment. Adds web-sourced fields (CEO names, funding, contact info) to lists of companies, people, or products. Use for enriching CSV files or inline data. Supports multi-turn: pass --previous-interaction-id from a prior research task to carry context forward."
user-invocable: true
argument-hint: <file or entities> with <fields to add>
compatibility: Requires parallel-cli and internet access.
allowed-tools: Bash(parallel-cli:*)
metadata:
  author: parallel
---

# Data Enrichment

Enrich: $ARGUMENTS

## Before starting

Inform the user that enrichment may take several minutes depending on the number of rows and fields requested.

## Optional: Suggest output columns

If the user gave a vague intent ("enrich these companies with useful info") and you're not sure what columns to add, ask the API for a suggestion before kicking off the run:

```bash
parallel-cli enrich suggest "Find CEO and recent funding info" --json
```

The response is an envelope: `{title, processor, enriched_columns, warnings}`. Extract just the **`enriched_columns` array** (not the whole envelope) and pass it as the value of `--enriched-columns` on `enrich run`, **in place of `--intent`**. These flags are alternative ways to specify what to enrich. If `suggest` returned a `processor`, pass it explicitly via `--processor` on the `run` call. Skip this section if the user already specified the fields they want.

> `enrich suggest` requires `parallel-cli` ≥ 0.3.0. If only that command is missing, skip the optional suggestion step and use `--intent` in step 1. Suggest an installation-specific upgrade from Setup. Do not classify authentication, API or invalid-input failures as an older CLI. An intent-based run itself requests a suggestion; explicit columns default to `core-fast`, while intent can select another processor unless `--processor` overrides it.

## Step 1: Start the enrichment

Use ONE of these command patterns (substitute user's actual data):

For inline data:

```bash
parallel-cli enrich run --data '[{"company": "Google"}, {"company": "Microsoft"}]' --intent "CEO name and founding year" --target "output.csv" --no-wait --json
```

For CSV file:

```bash
parallel-cli enrich run --source-type csv --source "input.csv" --target "output.csv" --source-columns '[{"name": "company", "description": "Company name"}]' --intent "CEO name and founding year" --no-wait --json
```

If this is a **follow-up** to a previous research task and you have its `interaction_id`, add context chaining:

```bash
parallel-cli enrich run --data '...' --intent "..." --target "output.csv" --no-wait --json --previous-interaction-id "$INTERACTION_ID"
```

This reuses the prior Task's context. Context chaining is unavailable for Zero Data Retention (ZDR) accounts, so omit the flag there and include the needed context explicitly. Enrichment does **not** return a new `interaction_id`; retain the prior Task ID for later follow-ups. A `taskgroup_id` or Search/Extract `session_id` is not a Task interaction ID.

**IMPORTANT:** Always include `--no-wait` so the command returns immediately instead of blocking.

Save the `--json` output's `taskgroup_id`, `url` and `num_runs` immediately. There is no `interaction_id` field. If creation is interrupted or its response is lost, inspect whether the group was created before submitting another run. Immediately tell the user:

- Enrichment has been kicked off
- The monitoring URL where they can track progress

The group runs server-side; polling can resume later using its saved ID.

## Step 2: Poll for results

Pick a persistent, run-specific output path (e.g., `enrichment-acme-tgrp-<id>.json`). Polling overwrites its output file, so inspect any existing file and use a new path unless replacement is intended. The output is JSON regardless of extension: an array of rows with `input` and either `output` or `error`. Async polling does not include basis or per-row interaction IDs; do not invent citations or context IDs.

```bash
parallel-cli enrich poll "$TASKGROUP_ID" --timeout 60 --output "enrichment-<descriptive-name>-<group-id>.json"
```

Important:

- Keep polls bounded; `--timeout 60` allows progress updates between waits.
- The `--target` from step 1 is unused in `--no-wait` mode. Only `--output` here determines where results are saved, and the file is always JSON.
- A completed group can include failed rows. Count rows containing `output` separately from rows containing `error` and compare their total with `num_runs`; an empty or incomplete file is not successful enrichment of the entire input.

### If polling times out or is interrupted

Timeout exit 5 or interruption ends the local wait. Check group state before saying it is still running:

```bash
parallel-cli enrich status "$TASKGROUP_ID" --json
```

Inspect `is_active`, `status_counts` and `num_runs`. Resume the same poll for an active group, or retrieve results for an inactive group and report failures or unresolved rows. Do not recreate the group on a timeout or automatically rerun failed rows. A local file-write failure can be retried with the same group ID and a writable output path.

### If the user requested CSV

Convert the saved JSON locally into a separate CSV. Preserve every original input column and row, including duplicate and failed rows; keep enrichment fields separate from conflicting input names and include an error column for failures. Do not assume streamed rows match original input order or guess a join when row identity is ambiguous. Validate the row count and leave the input CSV untouched. This is local conversion, not a CSV produced by async polling; report both JSON and CSV paths.

## Response format

**After step 1:** Share the monitoring URL (for tracking progress).

**After step 2:**

1. Report successful, failed and total row counts, with any missing results called out.
2. Preview a few successful rows and a representative failure if present, without claiming all rows succeeded.
3. Tell the user the full path to the output file

After completion, link the saved output rather than repeating the monitoring URL.

## Setup

If `parallel-cli` is not found, install and authenticate:

```bash
/parallel:parallel-cli-setup
```

If a documented option or command is missing, identify the install method and upgrade through that method: standalone `parallel-cli update`; pipx `pipx upgrade parallel-web-tools`; uv `uv tool upgrade parallel-web-tools`; Homebrew `brew upgrade parallel-web/tap/parallel-cli`; npm `npm update -g parallel-web-cli`. Recheck version and help in the agent's terminal before retrying.

For authentication or API errors, inspect the returned message. A `403` can indicate permissions, account policy or billing; it does not prove low balance. Check `parallel-cli auth --json` and its `authenticated` boolean when relevant without exposing credentials. Only a billing-specific error warrants a balance check, and adding funds needs explicit confirmation. Reuse saved group IDs; do not automatically retry an ambiguous creation.
