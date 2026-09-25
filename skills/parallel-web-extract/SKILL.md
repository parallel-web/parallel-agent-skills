---
name: parallel-web-extract
description: "CLI-backed URL extraction. Use when the user explicitly invokes this skill, needs CLI-only controls or saved JSON output, or no Parallel web_fetch MCP tool is available. When the bundled Parallel Search MCP is available, prefer its web_fetch tool for ordinary webpages, articles, PDFs, and JavaScript-heavy sites."
user-invocable: true
argument-hint: <url> [url2] [url3]
context: fork
agent: parallel:parallel-subagent
compatibility: Requires parallel-cli and internet access.
allowed-tools: Bash(parallel-cli:*)
metadata:
  author: parallel
---

# URL Extraction

Extract content from: $ARGUMENTS

## Command

Choose a short, descriptive filename based on the URL or content (e.g., `vespa-docs`, `react-hooks-api`). Use lowercase with hyphens, no spaces. Substitute it into the command **inline** — `$FILENAME` is a placeholder, not a shell variable.

Pass each requested URL as a separate quoted positional argument, up to 20 per call. Do not collapse multiple URLs into one quoted `$ARGUMENTS` string or use `eval` to split them. Construct arguments directly from the requested URLs. For example:

```bash
parallel-cli extract "https://docs.parallel.ai/integrations/cli" "https://docs.parallel.ai/integrations/cursor-marketplace" --json -o "/tmp/parallel-docs.json"
```

`-o` saves JSON. Use a `.json` extension and inspect an existing path before use because Extract overwrites it. Read the saved file as authoritative; stdout may truncate and human-readable output previews only part of the content. Do not treat a stale file as a successful response after a failed call.

Options if needed:

- `--objective "focus area"` to focus extraction on a specific goal (also silences the "neither objective nor search_queries" warning that V1 emits when neither is set)
- `-q "keyword"` (repeatable) to prioritize keywords in excerpts
- `--full-content` to include the complete page body (for long articles, PDFs, or when excerpts may not capture what you need)
- `--full-content-max-chars N` to cap full-content size per result
- `--no-excerpts` to strip excerpts when you only want full content
- `--session-id "<returned-session-id>"` to group related Search/Extract calls. A session ID is not a Task interaction ID or run ID; never use it with research status/poll or `--previous-interaction-id`

## Handling failed extractions

Inspect the exit status, API error, `results`, per-URL `errors` and any warnings. `errors: []` is normal success. Nonempty errors can coexist with successful results: retain and present successful content, then name each failed URL and its returned reason. Empty results or missing content are not a successful extraction. Do not fabricate content. For affected URLs, suggest:

- Verifying the URL (the page may have moved)
- Requesting `--full-content` if excerpts are empty but the returned metadata supports that the page was fetched
- Using `parallel-cli search` to locate the current URL if the page was renamed

## Response format

Return content as:

**[Page Title](URL)**

Use returned `full_content` for full-page requests; excerpts alone are selected passages and must be labelled as such. Even full content may be capped by `--full-content-max-chars` or upstream limits; do not promise completeness when capped. Preserve retrieved content verbatim, with these rules:

- Keep content verbatim - do not paraphrase or summarize
- Preserve every numbered/bulleted item in the retrieved content; do not claim an excerpt contains the whole page
- Strip only obvious noise: nav menus, footers, ads
- Preserve all facts, names, numbers, dates, quotes

After the response, mention the output file path (`/tmp/$FILENAME.json`) so the user knows it's available for follow-up questions.

For large content, keep the full verbatim text in the saved file and provide a brief labelled preview plus its path. Never silently truncate content while claiming it is the complete extraction.

## Setup

If `parallel-cli` is not found, install and authenticate:

```bash
/parallel:parallel-cli-setup
```

If a documented command or option is missing, check the installed version and upgrade through its installation method: standalone `parallel-cli update`, pipx `pipx upgrade parallel-web-tools`, uv `uv tool upgrade parallel-web-tools`, Homebrew `brew upgrade parallel-web/tap/parallel-cli`, or npm `npm update -g parallel-web-cli`. Verify help in the same terminal before retrying.

For authentication errors, inspect `parallel-cli auth --json` and its `authenticated` boolean; exit zero alone does not prove authentication. A `403` can indicate permissions, policy or billing. Report the actual error; check balance only for a billing-specific failure and never add funds without explicit confirmation.
