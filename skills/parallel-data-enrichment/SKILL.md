---
name: parallel-data-enrichment
description: "Bulk data enrichment. Adds web-sourced fields (CEO names, funding, contact info) to lists of companies, people, or products. Use for enriching CSV files or inline data. Supports multi-turn: pass --previous-interaction-id from a prior research or enrichment to carry context forward."
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

This returns a recommended processor tier and a structured `enriched-columns` schema you can pass to `enrich run`. Skip this step if the user already specified the fields they want.

> `enrich suggest` requires `parallel-cli` ≥ 0.3.0. If it errors with `no such command`, skip the suggestion step and proceed directly to step 1, then suggest the user run `parallel-cli update` afterwards.

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

If this is a **follow-up** to a previous research or enrichment task where you know the `interaction_id`, add context chaining:

```bash
parallel-cli enrich run --data '...' --intent "..." --target "output.csv" --no-wait --json --previous-interaction-id "$INTERACTION_ID"
```

By chaining `interaction_id` values across requests, each follow-up automatically has the full context of prior turns — so you can enrich entities discovered in earlier research without restating what was already found.

**IMPORTANT:** Always include `--no-wait` so the command returns immediately instead of blocking.

Tip: if you ran `enrich suggest` above and got back an `enriched_columns` schema, you can pass it through with `--enriched-columns '<json>'` instead of relying on `--intent`.

Parse the output to extract the `taskgroup_id` and monitoring URL. If the response also includes an `interaction_id`, capture it for possible follow-ups; otherwise skip. Immediately tell the user:
- Enrichment has been kicked off
- The monitoring URL where they can track progress

Tell them they can background the polling step to continue working while it runs.

## Step 2: Poll for results

Pick a concrete output path (e.g., `/tmp/enrichment-acme.json`). Note: the file is JSON regardless of the extension you choose — it's an array of `{input, output}` objects, not a CSV. Name it `.json` to avoid confusing yourself or the user.

```bash
parallel-cli enrich poll "$TASKGROUP_ID" --timeout 540 --output "/tmp/enrichment-<descriptive-name>.json"
```

Important:
- Use `--timeout 540` (9 minutes) to stay within tool execution limits
- The `--target` from step 1 is the source-of-truth target on the server side; the `--output` flag here is where the local poll saves a copy

### If the poll times out

Enrichment of large datasets can take longer than 9 minutes. If the poll exits without completing:
1. Tell the user the enrichment is still running server-side
2. Re-run the same `parallel-cli enrich poll` command to continue waiting

## Response format

**After step 1:** Share the monitoring URL (for tracking progress).

**After step 2:**
1. Report number of rows enriched
2. Preview first few rows from the output file (it's a JSON array of `{input, output}` objects)
3. Tell the user the full path to the output file
4. If you captured an `interaction_id` in step 1, share it and tell the user they can ask follow-up questions that build on this enrichment. If no `interaction_id` was returned, skip this point.

Do NOT re-share the monitoring URL after completion — the results are in the output file.

**Remember the `interaction_id` (if you have one)** — if the user asks a follow-up question that relates to this enrichment, use it as `--previous-interaction-id` in the next research or enrichment command.

## Setup

If `parallel-cli` is not found, install and authenticate:

```bash
curl -fsSL https://parallel.ai/install.sh | bash
```

If unable to install that way, install via pipx instead:

```bash
pipx install "parallel-web-tools[cli]"
pipx ensurepath
```

Then authenticate:

```bash
parallel-cli login
```

Or set an API key: `export PARALLEL_API_KEY="your-key"`
