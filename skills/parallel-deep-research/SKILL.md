---
name: parallel-deep-research
description: "ONLY use when user explicitly says 'deep research', 'exhaustive', 'comprehensive report', or 'thorough investigation'. Slower and more expensive than parallel-web-search. For normal research/lookup requests, use parallel-web-search instead. Supports follow-ups with a known prior Task interaction ID."
user-invocable: true
argument-hint: <topic>
compatibility: Requires parallel-cli >= 0.3.0 and internet access.
allowed-tools: Bash(parallel-cli:*)
metadata:
  author: parallel
---

# Deep Research

Research topic: $ARGUMENTS

> Requires `parallel-cli` ≥ 0.3.0 for text output and context chaining. If a documented command or option is missing, check `parallel-cli --version` and that command's `--help`, then follow the installation-specific upgrade guidance in Setup. API, authentication and input errors are not evidence of an older CLI.

## When to use (vs parallel-web-search)

ONLY use this skill when the user explicitly requests deep/exhaustive research. It can take several minutes and costs more than a quick search, depending on the processor and task. For normal "research X" requests, quick lookups, or fact-checking, use **parallel-web-search** instead.

## Step 1: Start the research

Choose a descriptive output base in a persistent directory (e.g., `reports/ai-chip-market-2026`). Include the returned run ID to make it unique, then use this base in step 2 as `-o "$FILENAME"`. Check for existing `.json` and `.md` files before saving.

```bash
parallel-cli research run "$ARGUMENTS" --processor pro-fast --text --no-wait --json
```

The `--text` flag tells the API to return a markdown report (with inline citations) when the task completes, instead of the default structured JSON. Use it for narrative/report-style requests, which is what most users want from "deep research." Drop `--text` if the user explicitly wants structured JSON output.

Optional with `--text`: pass `--text-description "Keep under 1500 words, focus on M&A activity"` to steer length, format, or focus.

If this is a **follow-up** and you have a prior Task's returned `interaction_id`, add context chaining. An enrichment `taskgroup_id` and a Search/Extract `session_id` are not Task interaction IDs. Async enrichment does not return a new interaction ID; retain the prior Task ID instead. Context chaining is unavailable for Zero Data Retention (ZDR) accounts, so omit it there and provide the needed context explicitly.

```bash
parallel-cli research run "$ARGUMENTS" --processor lite-fast --text --no-wait --json --previous-interaction-id "$INTERACTION_ID"
```

This reuses the prior Task's context. A lighter processor (`lite-fast` or `base-fast`) can suit a focused follow-up; choose based on the new question's depth rather than assuming all follow-ups are simple.

Always use `--no-wait` to separate creation from bounded polling. Save the returned IDs immediately. If creation is interrupted or its response is lost, do not submit a replacement until you have checked whether the first task was created.

Use `pro-fast` by default for exploratory research. Run `parallel-cli research processors` for the installed CLI's processor list and latency estimates; these are not deadlines. Choose `ultra` tiers only when explicitly requested and within the user's approved budget. Check [current pricing](https://parallel.ai/pricing) rather than quoting fixed cost multipliers.

Fast variants prioritize speed and may use less fresh indexed data. Standard variants may suit freshness-sensitive work, but neither choice guarantees that every source was fetched live. State the relevant date or freshness requirement in the research prompt and check the returned evidence.

Parse the JSON output to save `run_id`, `interaction_id`, and `result_url`. Immediately tell the user:

- Deep research has been kicked off
- The estimated latency for the selected processor, if available
- The monitoring URL where they can track progress

The task runs server-side; polling can resume later using the saved `run_id`.

## Step 2: Poll for results

```bash
parallel-cli research poll "$RUN_ID" -o "$FILENAME" --timeout 60
```

Important:

- Keep each poll bounded; `--timeout 60` allows progress updates between waits.
- Avoid `--json` when polling a large report. The `-o` flag saves the full result to files.
- With `-o "$FILENAME"`:
  - `$FILENAME.json` is always written (metadata + basis)
  - `$FILENAME.md` is written only for returned text output, normally requested with `--text`; auto-schema results can remain JSON-only.
  - For text, JSON references `output.content_file` relative to the saved JSON file instead of duplicating the report body.
- Share the executive summary if one was printed. Some successful outputs have no summary; do not invent one or treat its absence as failure.
- Existing output files are refused unless `--force` is explicit. Prefer a new base; use `--force` only when overwriting those files is intended.
- Read the actual printed paths. On a write error, the CLI may fall back to the system temp directory, and writes may be partial. Inspect both locations before retrying. Copy a final report from temporary storage to the intended persistent location before presenting it as saved durably.

### If polling times out or is interrupted

Timeout exit 5 or interruption ends the local wait, not necessarily the server task. Check the saved task:

```bash
parallel-cli research status "$RUN_ID" --json
```

Resume the same poll only for a pending/running task; retrieve completed output and report failed/cancelled or `action_required` states accurately. The CLI's polling loop may not recognize `action_required`, so do not poll that state indefinitely. Never recreate the task merely because a local wait ended.

## Response format

**After step 1:** Share the monitoring URL for tracking progress.

**After step 2:**

1. Share the executive summary if printed; otherwise say the result is saved and provide a brief summary only from inspected output when needed.
2. Tell the user the generated file paths:
   - Actual `.md` path, if a text report exists
   - Actual `.json` path with metadata and basis (and structured content for JSON output)
3. Share the `interaction_id` and tell the user they can ask follow-up questions that build on this research (e.g., "drill deeper into X" or "compare that to Y")

After completion, link the saved files rather than repeating the monitoring URL.

Avoid loading the whole report into context. Read only the relevant sections when answering a requested summary or follow-up, and cite the returned sources.

**Remember the `interaction_id`:** use it for a related research or enrichment follow-up when context chaining is supported by the account.

## Setup

If `parallel-cli` is not found, install and authenticate:

```bash
/parallel:parallel-cli-setup
```

If a documented option or command is missing, identify the install method and upgrade through that method: standalone `parallel-cli update`; pipx `pipx upgrade parallel-web-tools`; uv `uv tool upgrade parallel-web-tools`; Homebrew `brew upgrade parallel-web/tap/parallel-cli`; npm `npm update -g parallel-web-cli`. Recheck version and help in the agent's terminal before retrying.

For authentication or API errors, inspect the returned message. A `403` can indicate permissions, account policy or billing; it does not prove low balance. Check `parallel-cli auth --json` and its `authenticated` boolean when relevant without exposing credentials. Only a billing-specific error warrants a balance check, and adding funds needs explicit confirmation. Reuse saved task IDs; do not automatically retry an ambiguous creation.
