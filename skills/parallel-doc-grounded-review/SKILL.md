---
name: parallel-doc-grounded-review
description: Review a code change against current library references, deprecated APIs, and standards, not the model's stale memory, and return findings with clean extracted source text the model can quote word-for-word. Use when the user wants to "review this diff", "check for deprecated APIs", "is this the current way to do X", or ground code review in live docs. Runs on the user's own Parallel account via Task and Extract.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__Parallel-Task-MCP__createTaskGroup, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# Doc-Grounded Review

Check a change against the **current** library references, deprecated APIs, and standards, not
what the model learned in training, and get back findings with clean **extracted source text**
it can quote word-for-word. The point is fewer false positives: a review that says "this is
deprecated" only when a live doc actually says so, with the quote attached.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two ways to run, both maintained by Parallel so API changes are absorbed for you:
- **Chat / co-work:** the **Task MCP** (`createTaskGroup`), one input per change or symbol.
- **CLI / build-on-top:** `parallel-cli` + the installed **`parallel-web-extract`** and
  **`parallel-data-enrichment`** skills (`parallel-cli skills install`).

Not set up yet?
If Parallel is not configured, run the relevant setup skill first. See [docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its stack and "current" framing (captured once at setup), don't
re-ask it; only get the per-run specifics below.

Three quick questions before running (each reviewed change is a billable check):
1. **What's the change?** A diff, a file, or the specific APIs / symbols to check.
2. **Against which versions?** Defaults to the current stable of each library; name pins if you target an older line.
3. **How strict?** Default flags deprecated / removed APIs and clear standard violations; add style or security if you want.

Confirm, then run.

## Run it

One task per change (or per symbol batch). Output shape:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["subject", "findings"],
  "properties": {
    "subject": {"type": "string", "description": "the file, symbol, or diff reviewed"},
    "findings": {
      "type": "array",
      "description": "empty array if nothing is flaggable against current sources; never invented",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["symbol", "verdict", "current_guidance", "quote", "source_url"],
        "properties": {
          "symbol":          {"type": "string", "description": "the API / method / pattern in question"},
          "verdict":         {"type": "string", "enum": ["deprecated", "removed", "changed", "discouraged", "current", "unverifiable"]},
          "current_guidance":{"type": "string", "description": "what the current, supported approach is"},
          "quote":           {"type": "string", "description": "verbatim text extracted from the source that backs the verdict; empty string if none"},
          "source_url":      {"type": "string", "description": "resolving source (doc, changelog, release note); must load"},
          "applies_to":      {"type": "string", "description": "the library version(s) this applies to"}
        }
      }
    }
  }
}
```

Prompt (substitute the change / symbols):

> Review the following change against the current, supported references for each library
> involved: {DIFF_OR_SYMBOLS}. For each API, method, or pattern, determine whether it is
> current, deprecated, removed, changed, or discouraged as of the latest stable version. Back
> every verdict with a verbatim quote extracted from a resolving source (official docs, the
> changelog, or the release note) and the version it applies to. State the current supported
> approach. Do not flag anything you cannot back with a live source, mark it "unverifiable"
> rather than guessing, and return an empty findings array if nothing is flaggable. For any
> blank field use an empty string, never the word "null".

**Read it:** lead with the deprecated/removed findings (each with its quote and the current
replacement), then changed/discouraged, and note anything "unverifiable" plainly. The quote is
what makes the finding trustworthy, no quote, no finding.

## Config seams (build on top)

1. **Input**: a diff, a file, or a symbol list; run one task per change or batch.
2. **Strictness**: extend the `verdict` enum and the prompt (add security, style, license).
3. **Quote handling**: `quote` + `source_url` are what your agent surfaces inline in the review comment.
4. **Tier**: `core` default; `core2x` for a stricter pass on a large or critical diff (see the tier guidance in this skill).

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Task API (stable,
`v1`): `POST /v1/tasks/runs` with `task_spec.output_schema`, then
`GET /v1/tasks/runs/{run_id}/result`; per-field citations in `output.basis`. Clean quotable text
via the Extract endpoint. Auth via `x-api-key`, server-side only. Prefer the CLI/MCP unless you
need raw control.

## Next

- Find the current source first → **code-quickstart**.
- Keep the libraries current going forward → **dependency-monitoring**.
- Generate new code against current versions → **current-scaffolding**.
