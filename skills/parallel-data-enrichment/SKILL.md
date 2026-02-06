---
name: parallel-data-enrichment
description: "Bulk data enrichment. Adds web-sourced fields (CEO names, funding, contact info) to lists of companies, people, or products. Use for enriching CSV files or inline data."
compatibility: Requires parallel-cli and internet access.
allowed-tools: Bash(parallel-cli:*)
metadata:
  author: parallel
---

# Data Enrichment

Enrich: $ARGUMENTS

## Before starting

Inform the user that enrichment may take several minutes depending on the number of rows and fields requested.

## Command

Use ONE of these command patterns (substitute user's actual data):

For inline data:

```bash
parallel-cli enrich run --data '[{"company": "Google"}, {"company": "Microsoft"}]' --intent "CEO name and founding year" --target "output.csv"
```

For CSV file:

```bash
parallel-cli enrich run --source-type csv --source "input.csv" --target "output.csv" --source-columns '[{"name": "company", "description": "Company name"}]' --intent "CEO name and founding year"
```

**IMPORTANT:** Do NOT add `--json` flag - it doesn't exist for enrich.

The CLI will print a monitoring URL - share this with the user immediately.

## Claude Code

If you are running in Claude Code, run this command in a **forked context** using the Task tool:

```
Task tool:
  subagent_type: "parallel:parallel-subagent"
  prompt: |
    Run enrichment (substitute user's data):

    For inline data:
    parallel-cli enrich run --data '[...]' --intent "..." --target "output.csv"

    For CSV file:
    parallel-cli enrich run --source-type csv --source "input.csv" --target "output.csv" --source-columns '[...]' --intent "..."

    Do NOT add --json flag.
    Share the monitoring URL with the user immediately.

    When complete:
    1. Report number of rows enriched
    2. Preview first few rows of the output CSV
    3. Tell user the full path to the output CSV file
```

## Response format

When complete:
1. Report number of rows enriched
2. Preview first few rows of the output CSV
3. Tell user the full path to the output CSV file

## Setup

If `parallel-cli` is not found, install and authenticate:

```bash
curl -fsSL https://parallel.ai/install.sh | bash
parallel-cli login
```

Or set an API key: `export PARALLEL_API_KEY="your-key"`
