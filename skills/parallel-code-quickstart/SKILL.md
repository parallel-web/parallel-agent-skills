---
name: parallel-code-quickstart
description: Connect Parallel (if needed) and get ranked, current, source-cited answers for any library, framework, or error, from the official docs to the GitHub issue or Stack Overflow thread that explains the fix. Use when the user asks to "search the docs for X", "why is this error happening", "what's the current way to do Y in this library", or wants the Parallel code quickstart. Runs on the user's own Parallel account via Search.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__claude_ai_Parallel_Web_Search_Paid__web_search, mcp__claude_ai_Parallel_Web_Search_Paid__web_fetch
metadata:
  author: parallel
---

# Code Quickstart

The fastest way to see Parallel ground a coding agent: name a library, framework, or error and
get back **ranked, current sources**, the official doc, the changelog entry, the GitHub issue,
or the Stack Overflow thread where the fix actually lives, each with a link that resolves.
Replaces a brittle in-house web-search stack with one call, and nothing is invented: if the
answer isn't on a reachable source, it says so.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two ways to run, both maintained by Parallel so API changes are absorbed for you:
- **Chat / co-work:** the **Parallel Web Search** tool (`web_search`, `web_fetch`).
- **CLI / build-on-top:** `parallel-cli` + the installed **`parallel-web-search`** and
  **`parallel-web-extract`** skills (`parallel-cli skills install`).

Not set up yet?
If Parallel is not configured, run the relevant setup skill first.

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its stack and "current" framing (captured once at setup) to bias
the query toward your libraries and versions, don't re-ask it; only get the per-run specifics
below.

Two quick questions before running (a search costs credits):
1. **What are you trying to resolve?** A library + task ("Next.js 15 app router middleware config"), or an exact error string.
2. **Any version to pin to?** Defaults to the current stable; name a version if you're on an older line.

Confirm, then run.

## Run it

Issue the search with the objective phrased the way a developer would ask it. Prefer official
docs and the primary issue/thread over blog reposts. Read the ranked results; if excerpts are
enough, answer from them, only `web_fetch` a URL when you need exact wording to quote.

Example objective:

> Next.js 15 app router middleware config: the current, supported way to match dynamic routes,
> and any recent breaking change. Prefer nextjs.org docs, the relevant GitHub issue, and the
> accepted Stack Overflow answer. Return ranked sources with a one-line takeaway each, and cite
> a resolving URL for every claim. If the current behavior isn't documented on a reachable
> source, say so rather than guessing.

**Read it:** lead with the current answer and the one authoritative source behind it (docs or
changelog), then the corroborating issue/thread, with the version the answer applies to. Where
a claim can't be sourced, say so out loud, that refusal to fabricate is what makes it safe to
hand to an agent.

## Config seams (build on top)

1. **The objective**: the library + task or the error string; this is the whole input. Seed it from the workspace `PROFILE.md` file so results skew to your stack.
2. **Source preference**: bias toward official docs, changelogs, and the primary issue/thread; down-rank blog reposts.
3. **Latency**: the Search / Responses path is latency-budgeted (`low` / `medium` / `high`) for when an agent is waiting on the result; see the tier guidance in this skill.
4. **Fetch only when needed**: answer from ranked excerpts by default; `web_fetch` a URL only for exact quotes or full-page analysis.

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Search API: `POST
/v1/search` (objective + optional constraints), returns ranked results with excerpts and URLs;
`POST /v1/extract` (or the fetch endpoint) for clean quotable page text. Auth via `x-api-key`,
server-side only. Hardcoding means you own keeping it current, prefer the MCP/CLI.

## Next

- Review a diff against what you just found → **doc-grounded-review**.
- Scaffold against the current versions → **current-scaffolding**.
- Keep watching a library for changes → **dependency-monitoring**.
