---
name: parallel-cli-setup
description: Install or upgrade the Parallel CLI and install its skills without reading, requesting, or handling credentials. Authentication stays in the user's trusted terminal.
user-invocable: true
allowed-tools: Bash(command:*), Bash(brew:*), Bash(uv:*), Bash(npm:*), Bash(pipx:*), Bash(curl:*), Bash(rm:*), Bash(parallel-cli:*)
metadata:
  author: parallel
---

# Parallel CLI Setup

Install or maintain `parallel-cli` without handling the user's credentials. This
skill may install or upgrade the CLI and install its skills. Authentication is a
separate user-controlled step in a trusted terminal.

## Step 1: Install or upgrade the CLI

Check whether the CLI exists:

```bash
command -v parallel-cli
```

If missing, install with any of these methods:

1. macOS only: `brew install parallel-web/tap/parallel-cli`
2. Linux/macOS/Windows (uv): `uv tool install "parallel-web-tools[cli]"`
3. Linux/macOS/Windows (npm): `npm install -g parallel-web-cli`
4. Linux/macOS/Windows (pipx): `pipx install "parallel-web-tools[cli]" && pipx ensurepath`

When `parallel-cli` is present, require version `>=0.9.2`. If older, identify the install method before advising an update. Use `command -v parallel-cli`, then inspect `readlink "$(command -v parallel-cli)"` if it is a symlink. Paths under `~/.local/share/uv/
  tools/` indicate `uv tool install`; paths under `~/.local/share/parallel-cli/` indicate the standalone installer.

Upgrade commands (choose based on how it was installed):

- standalone: `parallel-cli update`
- uv: `uv tool upgrade parallel-web-tools[cli]`
- pipx: `pipx upgrade parallel-web-tools[cli]`
- npm: `npm update -g parallel-web-cli`
- homebrew: `brew update && brew upgrade parallel-web/tap/parallel-cli`

## Step 2: Keep authentication user-controlled

Do not inspect environment variables, credential files, operating-system keychains,
or CLI authentication status. Do not ask the user to paste a key into chat, and do
not start an authentication flow from this skill.

If a Parallel command reports that authentication is required, stop and ask the
user to complete the CLI's documented sign-in flow in a trusted terminal. Link to
<https://docs.parallel.ai/integrations/cli>. Resume only after the user confirms
that sign-in completed. Report the original error without printing or probing any
credential metadata.

## Step 3: Check balance after sign-in

Only after the user confirms sign-in, check the current balance:

```bash
parallel-cli balance get
```

If zero, prompt the user to add balance:

```bash
parallel-cli balance add <AMOUNT_IN_CENTS>
```

Make it clear that a payment method should have been added to the organization. If not, the user can go to <https://platform.parallel.ai/settings> to add one.

If this command reports an authentication error, return to the user-controlled
flow above. Do not inspect stored credentials to diagnose it.

## Step 4: Install the Parallel skills

Install the skills for the user:

```bash
parallel-cli skills install
```

The user may need to restart their agent if it doesn't support hot reloading.

## Step 5: Suggest a first run

Prompt the user to use the newly installed skills to run a search or extract right away. Suggest one of (use `$` instead of `/` for Codex):

- `/parallel-web-search <query>` — fast web search
- `/parallel-web-extract <url>` — extract content from a URL
- `/parallel-deep-research <topic>` — comprehensive research
- `/parallel-data-enrichment <list>` — enrich a list of entities
