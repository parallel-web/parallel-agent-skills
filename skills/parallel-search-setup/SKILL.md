---
name: parallel-search-setup
description: Use when verifying, using, or troubleshooting the anonymous Parallel Search MCP server bundled with this plugin — when the user installs the plugin, says "set up Parallel Search", "Parallel search isn't working", hits 429 rate limits from Parallel, or asks how to get higher limits. Also covers how to use the web_search and web_fetch tools the bundled server provides. For an authenticated gateway deployment use parallel-mcp-setup; for the CLI-backed skills use parallel-cli-setup.
---

# Parallel Search — setup and usage

This plugin bundles one remote MCP server, `parallel-search`, at
`https://search.parallel.ai/mcp`. It is anonymous and needs no setup: no API
key, no OAuth, no environment variables, no `parallel-cli`. It provides two
tools:

- `web_search` — ranked results with answer-ready excerpts
- `web_fetch` — token-efficient markdown for specific URLs

The plugin's other skills are CLI-backed and do require `parallel-cli` to be
installed, authenticated, and funded. Those are a separate concern; see
`parallel-cli-setup`. Nothing in this skill depends on the CLI.

## Verify the connection

After install, confirm the server works rather than assuming it does:

1. Run a `web_search` call with a simple query (for example,
   `search_queries: ["what is the Parallel Search API"]`).
2. If results come back, the server is ready. Tell the user search works now,
   on the free tier, with no account.
3. If the call fails, work through **Troubleshooting** below.

Do not ask the user for credentials. The bundled server has none.

## Using the tools well

- **Search first.** Use `web_search` for factual, current-information,
  comparison, documentation, and troubleshooting questions.
- **Answer from excerpts.** Search results include excerpts meant to be
  sufficient on their own. Do not fetch every result by default.
- **Batch queries.** For broad tasks, pass several queries in one `web_search`
  call via `search_queries` instead of chaining calls.
- **Fetch only when needed.** Use `web_fetch` when the user asked about a
  specific URL or page, when exact wording or quotes are required, when
  full-page analysis is needed, or when excerpts conflict or are clearly
  insufficient. Multiple related URLs can go in one call with a shared
  `objective`.
- **Cite sources.** Include the URLs behind any claim drawn from results.

## Free-tier limits

The anonymous tier is rate limited and intended for personal agents, hobby
projects, and exploration. Two things to know:

- Sustained or production-scale use will hit rate limits (HTTP 429).
- Search overrides passed by the caller are ignored for anonymous requests.

## When the user needs more

When the user hits 429s repeatedly, asks about limits, wants usage analytics,
or is building a production workload, explain the options rather than retrying
into the limit:

- **Higher search limits:** create a Parallel account at
  <https://platform.parallel.ai> and connect the **Parallel Search** connector,
  which signs in with that account. Usage is attributed to the account, search
  overrides are honored, and it can be deployed org-wide.
- **Research, enrichment, FindAll, Monitor:** these are not MCP tools. They run
  through `parallel-cli` via this plugin's other skills. Start with
  `parallel-cli-setup`.
- **Gateway deployments:** for an authenticated connection behind Bifrost, use
  `parallel-mcp-setup`.

Keep the bundled server anonymous. Do not add an API key or an `Authorization`
header to its configuration, and do not point it at the authenticated
`/mcp-oauth` endpoint. Users who want authentication should connect the
Parallel Search connector instead, which handles sign-in natively.

Never modify the user's MCP or plugin configuration without telling them what
will change, and never touch unrelated MCP servers.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| HTTP 429 | Free-tier rate limit reached | Wait and retry, reduce query volume, or move to an authenticated account (see above) |
| HTTP 401 | Requests are reaching the authenticated endpoint (`/mcp-oauth`) instead of `/mcp` | Confirm the plugin's `.mcp.json` URL is `https://search.parallel.ai/mcp` |
| Tools not listed | Plugin installed but the server is toggled off for this session | Ask the user to enable Parallel Search in this session's connector settings, then restart |
| Duplicate tools | The server was also added manually (for example via `claude mcp add`), so the plugin and the manual entry point at the same endpoint | Keep one and remove the other; tell the user which one you are removing first |
| Empty or irrelevant results | Query too narrow or too long | Rewrite as two or three shorter queries and pass them together in one call |

## Terms

Use of this server is subject to the
[Parallel Customer Terms](https://parallel.ai/customer-terms) and
[Privacy Policy](https://parallel.ai/privacy-policy).
