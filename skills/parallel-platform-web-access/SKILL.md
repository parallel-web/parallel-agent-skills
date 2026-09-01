---
name: parallel-platform-web-access
description: Give every app built on your platform live-web access, search, research, and monitoring, through one integration through one integration, instead of a retrieval stack each of your users has to wire up themselves. Use when the user runs an app builder, agent platform, or codegen product and wants to "add web search to my platform", "let user apps research and monitor the web", or offer grounded retrieval as a feature. Runs on the user's own Parallel account via Search, Task, and Monitor.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), Bash(curl:*), ToolSearch, mcp__claude_ai_Parallel_Web_Search_Paid__web_search, mcp__Parallel-Task-MCP__createTaskGroup, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# Platform Web Access

If you run an app builder, an agent platform, or a codegen product, this is the pattern for
giving **every app your users build** live-web access, search, research, and monitoring,
through **one integration** you own, instead of a retrieval stack each user has to wire up
themselves. Same primitives as the other code skills, exposed as a capability your platform
offers, with the honesty and citation guarantees passed straight through to the end app.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

This skill is build-on-top by nature, you're embedding Parallel into your product. Ride the
maintained surfaces so API changes are absorbed on update:
- **Search** (`web_search`) for retrieval, **Task** (`createTaskGroup`) for structured
  research, **Monitor** for ongoing watches, all under one Parallel account (yours), scoped
  per end-user in your own layer.
- **CLI / skills:** `parallel-cli skills install` gives you the reference implementations to
  adapt (`parallel-web-search`, `parallel-deep-research`, `parallel-monitor`).

The raw HTTP API is below for the server-side integration you'll actually ship. Not set up yet?
If Parallel is not configured, run the relevant setup skill first. See [docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its product type and integration framing (captured once at
setup), don't re-ask it; only get the per-run specifics below.

Three quick questions before wiring it in:
1. **Which capabilities?** Search, research (Task), monitoring, or all three, exposed to the apps your users build.
2. **How is it called?** Per end-user request at runtime, at build time, or both.
3. **How do you meter it?** How you attribute and cap usage per end-user against your one Parallel account.

Confirm, then wire the reference calls below.

## Run it

Expose the three primitives behind your own thin API, one Parallel account, per-user scoping in
your layer. Reference calls:

- **Search** (an end app asks a live-web question):

  > Answer {END_USER_QUERY} from current, authoritative sources; return ranked results with a
  > resolving URL per claim; if it isn't on a reachable source, say so.

- **Research (Task)** (an end app needs a structured, cited answer): use the
  `parallel-doc-grounded-review` or `parallel-tech-deep-research` shapes, called server-side with the end-user's
  input substituted.

- **Monitor** (an end app wants a standing watch): create one Monitor per watch the end-user
  sets up, using the `parallel-dependency-monitoring` shape; route events back to that user.

Pass the **citation and honesty guarantees straight through**: the end app should show the same
resolving sources and the same "not found" over a guess. That is the feature you're reselling,
don't strip it in your wrapper.

## Config seams (build on top)

1. **Capability surface**: which of Search / Task / Monitor you expose, and the shapes you standardize on.
2. **Per-user scoping**: attribute, rate-limit, and cap usage per end-user against your single account.
3. **Metering**: map Parallel usage to your own billing / quotas.
4. **Passthrough**: surface citations and confidence to the end app; keep the honesty gate intact.
5. **Tier**: pick per capability: Search for lookups, `core` Task for research, `lite` Monitor for watches (see the tier guidance in this skill).

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Search `POST
/v1/search`; Task `POST /v1/tasks/runs` + `GET /v1/tasks/runs/{run_id}/result` (citations in
`output.basis`); Monitor `POST /v1/monitors` + `GET /v1/monitors/{id}/events` (optional
`webhook`). One `x-api-key` (yours), server-side; scope per end-user in your own layer. This is
the one skill you *do* build against the API directly, so track the dated endpoints here.

## Next

- Standardize the research shape you expose → **doc-grounded-review** or **tech-deep-research**.
- Standardize the watch shape you expose → **dependency-monitoring**.
- Resolve current versions for generated apps → **current-scaffolding**.
