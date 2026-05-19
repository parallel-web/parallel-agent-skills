---
name: parallel-deep-research
description: "ONLY use when user explicitly says 'deep research', 'exhaustive', 'comprehensive report', or 'thorough investigation'. Slower and more expensive than parallel-web-search. For normal research/lookup requests, use parallel-web-search instead. Supports multi-turn: pass --previous-interaction-id from a prior research or enrichment to continue with context."
user-invocable: true
argument-hint: <topic>
compatibility: Requires parallel-cli >= 0.3.0 and internet access.
allowed-tools: Bash(parallel-cli:*)
metadata:
  author: parallel
---

# Deep Research

Research topic: $ARGUMENTS

> Requires `parallel-cli` ≥ 0.3.0. If any command below errors with `no such option`, `no such command`, or `unrecognized arguments`, the user is on an older CLI. Tell them to run `parallel-cli update` (or `pipx upgrade parallel-web-tools` if installed via pipx), then retry.

## When to use (vs parallel-web-search)

ONLY use this skill when the user explicitly requests deep/exhaustive research. Deep research is 10-100x slower and more expensive than parallel-web-search. For normal "research X" requests, quick lookups, or fact-checking, use **parallel-web-search** instead.

## Step 1: Start the research

Choose a descriptive filename based on the topic (e.g., `ai-chip-market-2026`, `react-vs-vue-comparison`). Use lowercase with hyphens, no spaces. Reuse this base name in step 2 as `-o "$FILENAME"`.

```bash
parallel-cli research run "$ARGUMENTS" --processor pro-fast --text --no-wait --json
```

The `--text` flag tells the API to return a markdown report (with inline citations) when the task completes, instead of the default structured JSON. Use it for narrative/report-style requests, which is what most users want from "deep research." Drop `--text` if the user explicitly wants structured JSON output.

Optional with `--text`: pass `--text-description "Keep under 1500 words, focus on M&A activity"` to steer length, format, or focus.

If this is a **follow-up** to a previous research or enrichment task where you know the `interaction_id`, add context chaining:

```bash
parallel-cli research run "$ARGUMENTS" --processor lite-fast --text --no-wait --json --previous-interaction-id "$INTERACTION_ID"
```

By chaining `interaction_id` values across requests, each follow-up question automatically has the full context of prior turns — so you can drill deeper without restating what was already researched. Use a lighter processor (`lite-fast` or `base-fast`) for follow-ups since the heavy lifting was done in the initial turn.

This returns instantly. Do NOT omit `--no-wait` — without it the command blocks for minutes and will time out.

Processor options (choose based on user request):

| Processor | Expected latency | Use when |
|-----------|-----------------|----------|
| `lite-fast` | 10–60s | Quick lookups, follow-ups |
| `base-fast` | 15–100s | Simple questions |
| `core-fast` | 1–5 min | Moderate research |
| `pro-fast` | 2–10 min | **Default** — exploratory research, good depth/speed balance |
| `ultra-fast` | 5–25 min | Multi-source deep research (~2× cost) |
| `ultra2x-fast` / `ultra4x-fast` / `ultra8x-fast` | up to 2 hr | Hardest questions, only when explicitly requested |

Notes on the `-fast` suffix: `-fast` tiers use cached web data and are quicker. The non-fast variants (`pro`, `ultra`, etc.) re-fetch fresher data — slower but better for very recent events. Default to `-fast` unless the user specifically asks about news from the last day or two.

Run `parallel-cli research processors` to see the full list with latencies.

Parse the JSON output to extract the `run_id`, `interaction_id`, and monitoring URL. Immediately tell the user:

- Deep research has been kicked off
- The expected latency for the processor tier chosen (from the table above)
- The monitoring URL where they can track progress

Tell them they can background the polling step to continue working while it runs.

## Step 2: Poll for results

```bash
parallel-cli research poll "$RUN_ID" -o "$FILENAME" --timeout 540
```

Important:

- Use `--timeout 540` (9 minutes) to stay within tool execution limits
- Do NOT pass `--json` — the full output is large and will flood context. The `-o` flag writes results to files instead.
- With `-o "$FILENAME"`:
  - `$FILENAME.json` is always written (metadata + basis)
  - `$FILENAME.md` is written **only if step 1 used `--text`** (markdown report)
- The poll command prints an **executive summary** to stdout when the research completes. Share this executive summary with the user — it gives them a quick overview without having to open the files.
- Pass `--force` if re-polling and you want to overwrite existing files

### If the poll times out

Higher processor tiers can take longer than 9 minutes. If the poll exits without completing:

1. Tell the user the research is still running server-side
2. Re-run the same `parallel-cli research poll` command to continue waiting

## Response format

**After step 1:** Share the monitoring URL (for tracking progress only — it is not the final report).

**After step 2:**

1. Share the **executive summary** that the poll command printed to stdout
2. Tell the user the generated file paths:
   - `$FILENAME.md` — formatted markdown report (if `--text` was used)
   - `$FILENAME.json` — metadata and basis
3. Share the `interaction_id` and tell the user they can ask follow-up questions that build on this research (e.g., "drill deeper into X" or "compare that to Y")

Do NOT re-share the monitoring URL after completion — the results are in the files, not at that link.

Ask the user if they would like to read through the files for more detail. Do NOT read the file contents into context unless the user asks.

**Remember the `interaction_id`** — if the user asks a follow-up question that relates to this research, use it as `--previous-interaction-id` in the next research or enrichment command.

## Setup

If `parallel-cli` is not found, install and authenticate:

```bash
/parallel:parallel-cli-setup
```

If any `parallel-cli research` command returns `403`, tell the user balance is likely required. Offer to run `parallel-cli balance get`, and if needed ask for explicit confirmation before running `parallel-cli balance add <amount_cents>`. Then retry the original research command.
