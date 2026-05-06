---
name: parallel-findall
description: "Discover entities (companies, people, products, etc.) matching a natural-language description. Use when the user asks to 'find all X' or 'list every Y that…' — e.g., 'Find AI startups that raised Series A in 2026', 'List roofing companies in Charlotte NC', 'Show me YC W24 dev tools companies'. Different from web-search (which returns webpages) and deep-research (which returns a narrative report). Use this when the user wants a structured list of entities."
user-invocable: true
argument-hint: <objective describing entities to find>
compatibility: Requires parallel-cli and internet access.
allowed-tools: Bash(parallel-cli:*)
metadata:
  author: parallel
---

# FindAll: Entity Discovery

Find: $ARGUMENTS

## When to use this skill

Use FindAll when the user wants a **structured list of entities** matching a description, not webpages or a narrative answer.

| User asks for… | Use |
|---|---|
| "Find all X that…" / "List every Y…" | **parallel-findall** (this skill) |
| Webpage results / quick answers / current info | parallel-web-search |
| Narrative report / analysis / "research X" | parallel-deep-research |
| Add fields to a list you already have | parallel-data-enrichment |

If the user already has a list and just wants to add fields, this is the wrong skill — use parallel-data-enrichment.

## Step 1: Start the run

```bash
parallel-cli findall run "$ARGUMENTS" --no-wait --json
```

Defaults: generator `core`, match limit `10`. Override when the user asks for more breadth or depth:
- `-g pro` — most thorough generator (slower, costlier)
- `-g base` — fastest generator (use for quick previews)
- `-n 50` — return up to 50 matched entities (5–1000 allowed)

If the user wants to exclude known entities (e.g., "find competitors but not Google or OpenAI"):

```bash
parallel-cli findall run "$ARGUMENTS" --no-wait --json \
    --exclude '[{"name":"Google","url":"google.com"},{"name":"OpenAI","url":"openai.com"}]'
```

Tip — preview the schema first if the objective is ambiguous: `parallel-cli findall ingest "$ARGUMENTS" --json` shows the entity type and match conditions the API inferred, so you can refine wording before paying for a run.

Parse the JSON output to extract the `findall_id` and any monitoring URL. Tell the user:
- A FindAll run has been started
- Approximate cadence (minutes for `core`, longer for `pro`)
- They can keep working while it runs

## Step 2: Poll for results

Choose a descriptive filename (e.g., `series-a-ai-2026`, `charlotte-roofers`). Use lowercase with hyphens, no spaces.

```bash
parallel-cli findall poll "$FINDALL_ID" -o "/tmp/$FILENAME.json" --timeout 540
```

Important:
- Use `--timeout 540` (9 minutes) to stay within tool execution limits
- Do NOT pass `--json` for large result sets — it will flood context. `-o` saves the full results to disk

### If the poll times out

Re-run the same `parallel-cli findall poll` command to continue waiting. Server-side the run continues regardless.

## Response format

After polling, present a markdown table or list of the matched entities. Lead with the count, then list each entity with its name, URL, and a one-line description if available. Cite each entity with its source URL.

Tell the user:
- How many entities were matched
- The full results path (`/tmp/$FILENAME.json`)
- That they can:
  - Add fields to these results: `parallel-cli findall enrich $FINDALL_ID '<output_schema_json>'`
  - Get more matches: `parallel-cli findall extend $FINDALL_ID 50`

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
