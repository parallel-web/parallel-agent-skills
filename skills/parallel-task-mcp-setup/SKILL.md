---
name: parallel-task-mcp-setup
description: Install, authenticate, and verify Parallel Task MCP in Claude Code by running one fast, lightweight Task Group and returning its result. Use when the user asks to connect, activate, test, or smoke-test Parallel Task MCP.
allowed-tools: Bash(command:*), Bash(claude:*), Bash(script:*)
metadata:
  author: parallel
---

# Parallel Task MCP Setup

Configure `https://task-mcp.parallel.ai/mcp` and prove it works with one `lite-fast` task. Do not install Parallel CLI, use an API key, create Deep Research, use a local proxy, or provide a backup UI flow.

## Workflow

1. Check Claude Code:

   ```bash
   command -v claude
   claude --version
   ```

   Require version `>=2.1.172`. If Claude is missing or older, report it and stop; do not install or update it.

2. Add the user-scoped server only if absent:

   ```bash
   claude mcp list
   claude mcp add --scope user --transport http "Parallel-Task-MCP" https://task-mcp.parallel.ai/mcp
   ```

3. If the server is not connected, authenticate it in a hidden pseudo-terminal:

   ```bash
   command -v script
   /usr/bin/script -q /dev/null claude mcp login "Parallel-Task-MCP"
   claude mcp list
   ```

   Let Claude open the browser and wait while the user approves access. Proceed only when `claude mcp list` reports `Parallel-Task-MCP` connected. If browser OAuth or `/usr/bin/script` fails, report it and stop. Do not ask the user to use a terminal or another setup path.

4. Ensure the fresh child Claude process can authenticate:

   ```bash
   claude auth status --json
   ```

   If `loggedIn` is not `true`, run:

   ```bash
   /usr/bin/script -q /dev/null claude auth login --claudeai
   claude auth status --json
   ```

   Wait for browser approval, then require `loggedIn: true`. This Claude login is separate from Parallel OAuth. Do not use Console billing or request an API key.

5. Run exactly one lightweight Task Group in a fresh child session. Keep the prompt immediately after `-p` because `--allowedTools` consumes trailing arguments:

   ```bash
   claude -p \
     "Use only Parallel-Task-MCP. Use ToolSearch if needed. Call createTaskGroup exactly once with exactly one input: United Nations. Use processor lite-fast and request exactly one output field: the founding date in MM-YYYY format. Follow the tool schema exactly. Save the task-group ID. Poll getStatus until terminal; honor a server-provided interval or run sleep 5 between checks. Do not ask the user for another message. On completion, call getResultMarkdown and return the ID, processor, final status, and full result. On failed, cancelled, canceled, or errored status, return the ID, status, and error. Never create Deep Research or a second task." \
     --no-session-persistence \
     --output-format json \
     --allowedTools "ToolSearch,Bash(sleep *),mcp__Parallel-Task-MCP__createTaskGroup,mcp__Parallel-Task-MCP__getStatus,mcp__Parallel-Task-MCP__getResultMarkdown"
   ```

   Keep the child running through polling. Report its ID, processor, final status, and result. Never retry the child automatically because it may already have created the task.

## After completion

Tell the user setup is complete. To start another task, they must open a new session in Claude Code, Claude chat, or Cowork so Task MCP loads at session start. Give them this example:

```text
Use Parallel Task MCP to run this task: <task>. Choose the lightest suitable processor, poll until complete, and return the final result.
```

Explain that their agent should handle polling and result retrieval autonomously. Do not start a second task in the setup session.
