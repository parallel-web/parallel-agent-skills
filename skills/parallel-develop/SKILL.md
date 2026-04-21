---
name: parallel-develop
description: "Bootstrap a Parallel API integration in the user's codebase. Use when the user says 'integrate Parallel', 'add Parallel API', 'build with Parallel', 'use Parallel for web search / research / enrichment / monitoring / extraction / lead discovery', or asks for starter code that talks to api.parallel.ai. Produces install + env + working example code tailored to the user's language (Python / TypeScript / cURL / MCP) and the API that fits their use case."
user-invocable: true
argument-hint: <what you want to build — e.g. \"research agent in typescript\">
compatibility: Works in any agent/IDE. The generated code targets Python (`parallel-web`), TypeScript (`parallel-web`), raw cURL, or MCP clients (Cursor, Claude Desktop, VS Code, Claude Code).
allowed-tools: Read Write Edit Bash(ls:*) Bash(cat:*) Bash(mkdir:*) Bash(pip:*) Bash(npm:*) Bash(pnpm:*) Bash(uv:*) WebFetch
metadata:
  author: parallel
---

# Parallel API Bootstrap

Build a Parallel integration for: $ARGUMENTS

## Step 1 — identify the client + use case

Parallel has five main APIs. Pick the one that fits the user's goal:

| Use case | API | When |
|----------|-----|------|
| Single web lookup, RAG retrieval | **Search** | Fast, LLM-optimized excerpts for a given objective + keywords |
| Deep research / multi-hop question | **Task** (processor `pro`/`ultra`) | Complex queries that need several retrieval hops and structured output |
| Enrich a known list (people, companies, products) | **Task** (processor `core`) | You have the entities; fill in columns |
| Discover NEW entities matching criteria | **FindAll** (beta) | Building a list from scratch |
| Track web changes on a schedule | **Monitor** (alpha) | News tracking, change alerts with webhooks |
| Convert a specific URL to LLM-friendly markdown | **Extract** | Single-URL ingestion, PDFs, JS-heavy pages |

Likewise, pick the client the user is working in:

- **Python** — official `parallel-web` SDK (top-level `client.search`, `client.extract`, `client.task_run`, `client.beta.findall`)
- **TypeScript** — official `parallel-web` SDK (top-level `client.search`, `client.extract`, `client.taskRun`; FindAll / Monitor via generic `client.post<T>`)
- **cURL** — any language; just HTTP + `x-api-key` header
- **MCP** — if the user wants an MCP client (Cursor / Claude Desktop / VS Code / Claude Code) to call Parallel's hosted Search + Task MCPs

If the user's message doesn't make the client + use case obvious, **ask them once** (AskUserQuestion or a plain clarifying question). Don't guess.

## Step 2 — emit the integration

Read the matching recipe file and follow its instructions verbatim. Each recipe covers install, env setup, the minimal working code, and the top best practices.

- Python → [references/python.md](references/python.md)
- TypeScript → [references/typescript.md](references/typescript.md)
- cURL → [references/curl.md](references/curl.md)
- MCP → [references/mcp.md](references/mcp.md)

After reading the recipe, write the example into the user's repo (a sensible path like `scripts/parallel_<use_case>.py` or `examples/parallel-<use-case>.ts`), update the nearest `requirements.txt` / `package.json` if needed, and walk the user through getting an API key at [platform.parallel.ai](https://platform.parallel.ai).

## Step 3 — point at the canonical docs for follow-ups

Parallel publishes an agent-friendly docs index at **https://docs.parallel.ai/llms.txt** — a single markdown file with the full API surface. If the user asks for anything beyond the recipe (webhooks, source policies, task groups, advanced schemas), fetch that URL first and pull in the relevant section rather than guessing.

For deep-dive API questions the `/llms.txt` index is authoritative; do not invent parameter names.

## Guardrails

- **Snake_case everywhere.** Both the Python and TypeScript SDKs use **snake_case** body keys (`task_spec`, `output_schema`, `json_schema`, `run_id`, `event_types`). Do NOT camelCase these in TypeScript — it will silently be rejected by the server or produce a type error.
- **Never** invent an endpoint version. Current versions: Search/Extract/Task at `/v1`, FindAll at `/v1beta`, Monitor at `/v1alpha`.
- **For runs > 30 s** (Task `pro`/`ultra`, FindAll `core`/`pro`, any Monitor event), prefer a **webhook** over polling. Pass `webhook={"url": "...", "event_types": [...]}` at creation.
- **Always** give each Task/Enrichment field a *specific* description with exact format (e.g. `"MM-YYYY"`, `"USD"`, `"ISO 3166-1 alpha-2"`) and an explicit missing-value behavior (`"Return 'Not Available' if no source confirms"`).
- **Start FindAll with `generator="preview"`** to iterate on the objective and match_conditions before scaling up — it's cheap and fast.
- **Don't** use `parallel-cli` for these recipes — this skill is about writing integration code, not about invoking the CLI. For CLI workflows, use the `parallel-web-search`, `parallel-web-extract`, `parallel-deep-research`, or `parallel-data-enrichment` skills instead.

## When to choose a different skill

- User just wants to **run a web search right now** → use `parallel-web-search`.
- User just wants **one research task** run → use `parallel-deep-research`.
- User wants to **enrich a CSV right now** → use `parallel-data-enrichment`.
- User wants to **fetch a specific URL** → use `parallel-web-extract`.

This skill is for the *build-and-ship* case — when the user is adding Parallel to their own codebase.
