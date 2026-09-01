---
name: parallel-productivity-quickstart
description: Connect Parallel (if needed) and get a fresh, source-cited answer to any question with clean, quotable source text, fast enough to run in a product's request path. Use when the user asks to "answer this with current facts", "what's the latest on X", "give me a cited answer", or wants the Parallel productivity quickstart. Runs on the user's own Parallel account via Search and Extract.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__claude_ai_Parallel_Web_Search_Paid__web_search, mcp__claude_ai_Parallel_Web_Search_Paid__web_fetch
metadata:
  author: parallel
---

# Productivity Quickstart

The fastest way to see Parallel ground an assistant: ask any question and get back a **fresh,
cited answer** with clean, quotable source text, instead of stale training data. Fast enough to
run in the request path, so it can sit inline in a chat answer or a doc. Nothing is invented: if
the answer isn't on a reachable source, it says so.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two ways to run, both maintained by Parallel so API changes are absorbed for you:
- **Chat / co-work:** the **Parallel Web Search** tool (`web_search`, `web_fetch`).
- **CLI / build-on-top:** `parallel-cli` + the installed **`parallel-web-search`** and
  **`parallel-web-extract`** skills (`parallel-cli skills install`).

Not set up yet?
If Parallel is not configured, run the relevant setup skill first.

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its product / surfaces framing (captured once at setup) to bias
toward the entities and topics your product touches, don't re-ask it; only get the per-run
specifics below.

Two quick questions before running (a search costs credits):
1. **The question?** The user question to answer, phrased the way it comes into your product.
2. **In the request path?** If a user is waiting inline, keep the latency budget low; if it's async, you can go deeper.

Confirm, then run.

## Run it

Issue the search with the question as the objective. Read the ranked results; if the excerpts
answer it, answer from them, only `web_fetch` a URL when you need exact wording to quote.

Example objective:

> What industry changes are likely to have a major impact on the outcome of this project?
> Return the two or three most material, current trends with a one-line takeaway each and a
> resolving source URL, and pull a short quotable excerpt for each. Prefer recent, authoritative
> sources. If a claim isn't on a reachable source, leave it out rather than guessing.

**Read it:** give the answer in one or two lines, then the cited trends with their quotable
excerpts, each clickable to the source. The citation and the quote are what make it safe to show
a user inline, keep them attached.

## Config seams (build on top)

1. **The objective:** the user question; this is the whole input. Seed context from the workspace `PROFILE.md` file.
2. **Latency:** the Search / Responses path is latency-budgeted (`low` / `medium` / `high`); use `low` for sub-2s inline answers, higher for async depth (see the tier guidance in this skill).
3. **Quote handling:** keep the extracted quote + source so your product can cite word-for-word.
4. **Fetch only when needed:** answer from ranked excerpts by default; `web_fetch` for exact quotes or full-page reads.

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Search API: `POST
/v1/search` (objective + latency budget), returns ranked results with excerpts and URLs; `POST
/v1/extract` for clean quotable page text. Auth via `x-api-key`, server-side only. Hardcoding
means you own keeping it current, prefer the MCP/CLI.

## Next

- Enrich the entities in the answer → **entity-context**.
- Turn a big question into a full report → **in-product-research**.
- Keep the answer current over time → **knowledge-freshness**.
