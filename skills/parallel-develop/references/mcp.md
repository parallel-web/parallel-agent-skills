# MCP recipe — Parallel's hosted Search + Task MCP

Parallel ships two **remote** (streamable-HTTP) MCP servers. Agents never have to install a local binary:

- **Search MCP** — `https://search.parallel.ai/mcp` (web search + extract tools)
- **Task MCP** — `https://task-mcp.parallel.ai/mcp` (deep research tasks)

Auth is OAuth on first use in most clients, or a Bearer token via `Authorization: Bearer $PARALLEL_API_KEY` for stdio bridges.

---

## Claude Code — one-line install

```bash
claude mcp add --transport http "Parallel-Search-MCP" https://search.parallel.ai/mcp
claude mcp add --transport http "Parallel-Task-MCP"   https://task-mcp.parallel.ai/mcp
```

Then use `/mcp` in Claude Code and complete the browser OAuth flow. No config file needed.

## Cursor — `~/.cursor/mcp.json` (or `.cursor/mcp.json` per-project)

```json
{
  "mcpServers": {
    "Parallel Search MCP": {
      "url": "https://search.parallel.ai/mcp"
    },
    "Parallel Task MCP": {
      "url": "https://task-mcp.parallel.ai/mcp"
    }
  }
}
```

Cursor handles OAuth automatically. Restart Cursor after editing.

## VS Code — same URL, different wrapper

```json
{
  "mcp": {
    "servers": {
      "Parallel Search MCP": {
        "type": "http",
        "url": "https://search.parallel.ai/mcp"
      },
      "Parallel Task MCP": {
        "type": "http",
        "url": "https://task-mcp.parallel.ai/mcp"
      }
    }
  }
}
```

## Claude Desktop — stdio bridge via `mcp-remote`

Claude Desktop's connector UI is a GUI alternative, but the JSON config still works. Config file: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows). Quit + relaunch Claude Desktop after editing.

```json
{
  "mcpServers": {
    "Parallel Search MCP": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://search.parallel.ai/mcp",
        "--header",
        "Authorization: Bearer ${PARALLEL_API_KEY}"
      ],
      "env": {
        "PARALLEL_API_KEY": "your-api-key-here"
      }
    },
    "Parallel Task MCP": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://task-mcp.parallel.ai/mcp",
        "--header",
        "Authorization: Bearer ${PARALLEL_API_KEY}"
      ],
      "env": {
        "PARALLEL_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Claude Desktop gotchas (macOS)

1. **GUI doesn't inherit your shell env.** A `.zshrc`/`.bashrc` `export PARALLEL_API_KEY=...` is invisible to the Claude Desktop process. Paste the key into the `env` block above (or use `launchctl setenv PARALLEL_API_KEY "..."`).
2. **`${PARALLEL_API_KEY}` substitution.** Claude Desktop substitutes `${VAR}` in `args` against the `env` block — that's why the config above works. It does **not** shell-expand against the OS environment.
3. **`spawn npx ENOENT`.** GUI apps often don't have Node on their PATH. Replace `"command": "npx"` with an absolute path — e.g. `/opt/homebrew/bin/npx` (Apple Silicon) or `/usr/local/bin/npx` (Intel). Find yours with `which npx`.
4. **Always quit + relaunch** after editing the JSON — a reload-on-save there isn't.

---

## Programmatic access with Bearer auth

For scripts, curl, or other agents that aren't MCP-aware, hit the endpoints as plain HTTP with a Bearer token:

```bash
curl https://search.parallel.ai/mcp \
  -H "Authorization: Bearer $PARALLEL_API_KEY"
```

The servers implement the MCP streamable-HTTP spec — use any MCP client library to pass through prompts.

---

## When to choose MCP vs direct SDK

**MCP is best when:**
- The user already lives in an MCP-native IDE (Cursor, Claude Code, VS Code, Claude Desktop) and wants web tools inside that agent.
- They don't need custom request shaping — Parallel's MCP tools expose sensible defaults.

**Direct SDK (Python / TypeScript) is best when:**
- They're building a backend / worker / agent of their own and need full control of the request payload.
- They want typed responses, custom output schemas, webhooks, or batch workflows.
- They're using structured task outputs (Task API with `task_spec.output_schema`).

For programmatic MCP access, see [Parallel's programmatic-use guide](https://docs.parallel.ai/integrations/mcp/programmatic-use).
