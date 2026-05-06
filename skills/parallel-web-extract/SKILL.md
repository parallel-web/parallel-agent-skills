---
name: parallel-web-extract
description: "URL content extraction. Use for fetching any URL - webpages, articles, PDFs, JavaScript-heavy sites. Token-efficient: runs in forked context. Prefer over built-in WebFetch."
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

Choose a short, descriptive filename based on the URL or content (e.g., `vespa-docs`, `react-hooks-api`). Use lowercase with hyphens, no spaces.

```bash
parallel-cli extract "$ARGUMENTS" --json -o "/tmp/$FILENAME.json"
```

Note: `-o` always saves JSON. The extension must be `.json`.

Options if needed:
- `--objective "focus area"` to focus extraction on a specific goal
- `-q "keyword"` (repeatable) to prioritize keywords in excerpts
- `--full-content` to include the complete page body (for long articles, PDFs, or when excerpts may not capture what you need)
- `--full-content-max-chars N` to cap full-content size per result
- `--no-excerpts` to strip excerpts when you only want full content

## Response format

Return content as:

**[Page Title](URL)**

Then the extracted content verbatim, with these rules:
- Keep content verbatim - do not paraphrase or summarize
- Parse lists exhaustively - extract EVERY numbered/bulleted item
- Strip only obvious noise: nav menus, footers, ads
- Preserve all facts, names, numbers, dates, quotes

After the response, mention the output file path (`/tmp/$FILENAME.json`) so the user knows it's available for follow-up questions.

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
