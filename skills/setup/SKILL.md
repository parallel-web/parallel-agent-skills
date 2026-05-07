---
name: setup
description: Set up the Parallel plugin (install CLI)
user-invocable: true
allowed-tools: Bash(parallel-cli:*)
metadata:
  author: parallel
---

# Parallel Plugin Setup

## Install CLI

See https://docs.parallel.ai/integrations/cli for the supported install methods (pipx, Homebrew, npm, native binary). Walk the user through whichever they pick.

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
