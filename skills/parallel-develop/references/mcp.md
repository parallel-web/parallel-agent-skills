# MCP recipe — Parallel's hosted Search + Task MCPs

Parallel ships two remote streamable-HTTP MCP servers. Almost every client just needs the URL:

- **Search MCP** — `https://search.parallel.ai/mcp` (web search + extract)
- **Task MCP** — `https://task-mcp.parallel.ai/mcp` (deep research tasks)

OAuth handles auth on first use in most clients. No `mcp-remote`, no API key in config, no npm package to install.

Canonical install docs per client: [docs.parallel.ai/integrations/mcp/search-mcp](https://docs.parallel.ai/integrations/mcp/search-mcp).

---

## Quick install by client

### Claude Code

```bash
claude mcp add --transport http "Parallel-Search-MCP" https://search.parallel.ai/mcp
claude mcp add --transport http "Parallel-Task-MCP"   https://task-mcp.parallel.ai/mcp
```

Run `/mcp` and complete the browser OAuth flow.

### Claude Desktop

Settings → Connectors → Add Custom Connector, once per server:

- **Parallel Search MCP** → `https://search.parallel.ai/mcp`
- **Parallel Task MCP** → `https://task-mcp.parallel.ai/mcp`

(Older Claude Desktop builds without the Connectors UI — see "Stdio fallback" below.)

### Cursor — `~/.cursor/mcp.json` (or `.cursor/mcp.json` per-project)

```json
{
  "mcpServers": {
    "Parallel Search MCP": { "url": "https://search.parallel.ai/mcp" },
    "Parallel Task MCP":   { "url": "https://task-mcp.parallel.ai/mcp" }
  }
}
```

Restart Cursor after editing. OAuth handles auth.

### VS Code — `settings.json`

```json
{
  "mcp": {
    "servers": {
      "Parallel Search MCP": { "type": "http", "url": "https://search.parallel.ai/mcp" },
      "Parallel Task MCP":   { "type": "http", "url": "https://task-mcp.parallel.ai/mcp" }
    }
  }
}
```

### Windsurf — `~/.codeium/windsurf/mcp_config.json`

```json
{
  "mcpServers": {
    "Parallel Search MCP": { "serverUrl": "https://search.parallel.ai/mcp" },
    "Parallel Task MCP":   { "serverUrl": "https://task-mcp.parallel.ai/mcp" }
  }
}
```

### Cline — MCP Servers → Remote Servers → Edit Configuration

```json
{
  "mcpServers": {
    "Parallel Search MCP": { "url": "https://search.parallel.ai/mcp", "type": "streamableHttp" },
    "Parallel Task MCP":   { "url": "https://task-mcp.parallel.ai/mcp", "type": "streamableHttp" }
  }
}
```

### Other clients

Gemini CLI, ChatGPT, Codex, Amp, Kiro, Antigravity — all covered in the [Search MCP install guide](https://docs.parallel.ai/integrations/mcp/search-mcp).

---

## Stdio fallback (older clients only)

If a client can't speak remote HTTP MCP, bridge via `mcp-remote`:

```json
{
  "mcpServers": {
    "Parallel Search MCP": {
      "command": "npx",
      "args": [
        "-y", "mcp-remote",
        "https://search.parallel.ai/mcp",
        "--header", "Authorization: Bearer YOUR-PARALLEL-API-KEY"
      ]
    }
  }
}
```

Paste your key from [platform.parallel.ai](https://platform.parallel.ai) into the header. **Don't** rely on `${PARALLEL_API_KEY}` expansion from a shell `export` — many GUI clients don't inherit shell env.

---

## Programmatic access with Bearer auth

For scripts or agents that aren't MCP-aware, hit the endpoints as plain HTTP:

```bash
curl https://search.parallel.ai/mcp \
  -H "Authorization: Bearer $PARALLEL_API_KEY"
```

See [Programmatic Use](https://docs.parallel.ai/integrations/mcp/programmatic-use).

---

## When to choose MCP vs direct SDK

**MCP** when the user lives in an MCP-native IDE and wants web tools inside that agent — sensible defaults, no custom request shaping needed.

**Direct SDK** (Python / TypeScript) when they're building a backend / agent / worker and need full control: custom output schemas, webhooks, batch workflows, structured task outputs.
