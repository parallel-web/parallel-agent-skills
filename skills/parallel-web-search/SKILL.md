---
name: parallel-web-search
description: "DEFAULT for all research and web queries. Use for any lookup, research, investigation, or question needing current info. Fast and cost-effective. Only use parallel-deep-research if user explicitly requests 'deep' or 'exhaustive' research."
user-invocable: true
argument-hint: <query>
context: fork
agent: parallel:parallel-subagent
compatibility: Requires parallel-cli and internet access.
allowed-tools: Bash(parallel-cli:*)
metadata:
  author: parallel
---

# Web Search

Search the web for: $ARGUMENTS

## Command

Choose a short, descriptive filename based on the query (e.g., `ai-chip-news`, `react-vs-vue`). Use lowercase with hyphens, no spaces. Substitute it into the command **inline** — `$FILENAME` and `<keyword>` below are placeholders, not shell variables; do not copy them verbatim.

```bash
parallel-cli search "$ARGUMENTS" -q "<keyword1>" -q "<keyword2>" --json --max-results 10 --excerpt-max-chars-total 27000 -o "/tmp/$FILENAME.json"
```

Concrete example for a query about React 19:

```bash
parallel-cli search "latest React 19 features and adoption" -q "React 19" -q "concurrent rendering" --json --max-results 10 --excerpt-max-chars-total 27000 -o "/tmp/react-19-features.json"
```

The first argument is the **objective** — a natural language description of what you're looking for. It replaces multiple keyword searches with a single call for broad or complex queries. Add `-q` flags for specific keyword queries to supplement the objective. The `-o` flag saves the full results to a JSON file for follow-up questions.

Options if needed:
- `--after-date YYYY-MM-DD` for time-sensitive queries
- `--include-domains domain1.com,domain2.com` to limit to specific sources
- `--exclude-domains domain.com` to filter out noisy sources
- `--mode advanced` for harder questions (multi-step, agentic search). Default `basic` is right for almost everything; only escalate when basic results are insufficient
- `--location us` (ISO 3166-1 alpha-2) for geo-targeted results

## Parsing results

Do not set `max_output_tokens` on the command execution — the output is already bounded by `--max-results` and `--excerpt-max-chars-total`. Capping output tokens will truncate the JSON and break parsing.

**Prefer reading from the saved `-o` file**, not stdout. Even bounded output regularly exceeds harness stdout limits and gets truncated. Read `/tmp/$FILENAME.json` for the authoritative payload. For each result, extract:
- title, url, publish_date
- Useful content from excerpts (skip navigation noise like menus, footers, "Skip to content")

## Response format

**CRITICAL: Every claim must have an inline citation.** Use markdown links like [Title](URL) pulling only from the JSON output. Never invent or guess URLs.

Synthesize a response that:
- Leads with the key answer/finding
- Includes specific facts, names, numbers, dates
- Cites every fact inline as [Source Title](url) — do not leave any claim uncited
- Organizes by theme if multiple topics

**End with a Sources section** listing every URL referenced:

```
Sources:
- [Source Title](https://example.com/article) (Feb 2026)
- [Another Source](https://example.com/other) (Jan 2026)
```

This Sources section is mandatory. Do not omit it.

After the Sources section, mention the output file path (`/tmp/$FILENAME.json`) so the user knows it's available for follow-up questions.

## Setup

Requires `parallel-cli` (installed and authenticated). If `parallel-cli --version` fails, or if a later command fails with an authentication error, tell the user to see https://docs.parallel.ai/integrations/cli and stop.
