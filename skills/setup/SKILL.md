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

Install via `pipx` (preferred — pure Python source, no prebuilt binary):

```bash
pipx install "parallel-web-tools[cli]"
pipx ensurepath
```

If `pipx` isn't available, install the prebuilt binary instead:

```bash
curl -fsSL https://parallel.ai/install.sh | bash
```

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
