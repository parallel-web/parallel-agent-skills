---
name: setup
description: Set up the Parallel plugin (install CLI)
user-invocable: true
allowed-tools: Bash(curl:*), Bash(pipx:*), Bash(parallel-cli:*)
metadata:
  author: parallel
---

# Parallel Plugin Setup

## Install CLI

Install via `pipx`:

```bash
pipx install "parallel-web-tools[cli]"
pipx ensurepath
```

For other install methods (Homebrew, native binary, Windows), see https://docs.parallel.ai/integrations/cli.

## Authenticate

```bash
parallel-cli login
```

## Verify

```bash
parallel-cli auth
```

If `parallel-cli` not found, add `~/.local/bin` to PATH.

## Update later

```bash
parallel-cli update
```
