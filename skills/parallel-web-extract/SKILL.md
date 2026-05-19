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

Choose a short, descriptive filename based on the URL or content (e.g., `vespa-docs`, `react-hooks-api`). Use lowercase with hyphens, no spaces. Substitute it into the command **inline** — `$FILENAME` is a placeholder, not a shell variable.

```bash
parallel-cli extract "$ARGUMENTS" --json -o "/tmp/$FILENAME.json"
```

Concrete example:

```bash
parallel-cli extract "https://docs.parallel.ai" --json -o "/tmp/parallel-docs.json"
```

Note: `-o` always saves JSON. The extension must be `.json`.

Options if needed:

- `--objective "focus area"` to focus extraction on a specific goal (also silences the "neither objective nor search_queries" warning that V1 emits when neither is set)
- `-q "keyword"` (repeatable) to prioritize keywords in excerpts
- `--full-content` to include the complete page body (for long articles, PDFs, or when excerpts may not capture what you need)
- `--full-content-max-chars N` to cap full-content size per result
- `--no-excerpts` to strip excerpts when you only want full content

## Handling failed extractions

If the response has an `errors` field, an empty `results` array, or a 404/timeout for the URL, do NOT fabricate content. Tell the user the extraction failed, surface the upstream status, and suggest:

- Verifying the URL (the page may have moved)
- Retrying with `--full-content` if excerpts came back empty but the page exists
- Using `parallel-cli search` to locate the current URL if the page was renamed

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
/parallel:parallel-cli-setup
```

If `parallel-cli extract` returns `403`, tell the user balance is likely required. Offer to run `parallel-cli balance get`, and if needed ask for explicit confirmation before running `parallel-cli balance add <amount_cents>`. Then retry the original extract command.
