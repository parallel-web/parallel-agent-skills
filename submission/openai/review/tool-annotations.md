# MCP tool annotations

The production endpoint currently exposes two tools. Both are read-only but
access the open web.

## `web_search`

- `readOnlyHint: true` — searches and retrieves public information without
  changing external state.
- `openWorldHint: true` — accesses open-ended public internet sources.
- `destructiveHint: false` — cannot create, update, delete, send, publish, or
  trigger external actions.

## `web_fetch`

- `readOnlyHint: true` — retrieves content from user- or model-selected public
  URLs without changing them.
- `openWorldHint: true` — can access arbitrary public web origins.
- `destructiveHint: false` — cannot create, update, delete, send, publish, or
  trigger external actions.

Before submission, run **Scan Tools** and confirm these exact annotations are
still present on both tools. The live endpoint also currently provides input
and output schemas for both tools.
