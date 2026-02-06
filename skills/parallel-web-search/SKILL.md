---
name: parallel-web-search
description: "DEFAULT for all research and web queries. Use for any lookup, research, investigation, or question needing current info. Fast and cost-effective. Only use parallel-deep-research if user explicitly requests 'deep' or 'exhaustive' research."
context: fork
compatibility: Requires parallel-cli and internet access.
allowed-tools: Bash(parallel-cli:*)
metadata:
  author: parallel
---

# Web Search

Search the web for: $ARGUMENTS

## Command

```bash
parallel-cli search "$ARGUMENTS" -q "<keyword1>" -q "<keyword2>" --json --max-results 10 --excerpt-max-chars-total 27000
```

Choose relevant keywords from the query for the `-q` flags.

Options if needed:
- `--after-date YYYY-MM-DD` for time-sensitive queries
- `--include-domains domain1.com,domain2.com` to limit to specific sources

## Claude Code

If you are running in Claude Code, run this command in a **forked context** using the Task tool:

```
Task tool:
  subagent_type: "parallel:parallel-subagent"
  prompt: |
    Search the web for: "$ARGUMENTS"

    Run: parallel-cli search "$ARGUMENTS" -q "<keyword1>" -q "<keyword2>" --json --max-results 10 --excerpt-max-chars-total 27000

    Parse the JSON from stdout. For each result, extract:
    - title, url, publish_date
    - Useful content from excerpts (skip navigation noise)

    Synthesize a response with specific facts, cited as [Title](URL) with dates.
    ONLY cite URLs that appear in the JSON output. Do NOT invent URLs.
    End with a Sources list.
```

## Parsing results

The command outputs JSON to stdout. For each result, extract:
- title, url, publish_date
- Useful content from excerpts (skip navigation noise like menus, footers, "Skip to content")

## Response format

Synthesize a response that:
- Leads with the key answer/finding
- Includes specific facts, names, numbers, dates
- Cites sources as [Title](URL) with dates
- Organizes by theme if multiple topics

ONLY cite URLs that appear in the JSON output. Do NOT invent URLs.

End with a **Sources** list of [Title](URL) with dates.

## Setup

If `parallel-cli` is not found, install and authenticate:

```bash
curl -fsSL https://parallel.ai/install.sh | bash
parallel-cli login
```

Or set an API key: `export PARALLEL_API_KEY="your-key"`
