---
name: parallel-cli-setup
description: Set up and maintain the Parallel CLI (install, auth, balance, skills install)
user-invocable: true
allowed-tools: Bash(command:*), Bash(brew:*), Bash(uv:*), Bash(npm:*), Bash(pipx:*), Bash(curl:*), Bash(rm:*), Bash(parallel-cli:*)
metadata:
  author: parallel
---

# Parallel CLI Setup

Set up or maintain `parallel-cli` with minimal friction. If you are running this prompt, your goal is to follow the instructions below and set up `parallel-cli` for the user so that they can execute searches, run extracts, deep research, etc.

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

When `parallel-cli` is present, require version `>=0.4.0`. If older, identify the install method before advising an update. Use `command -v parallel-cli`, then inspect `readlink "$(command -v parallel-cli)"` if it is a symlink. Paths under `~/.local/share/uv/
  tools/` indicate `uv tool install`; paths under `~/.local/share/parallel-cli/` indicate the standalone installer.

Upgrade commands (choose based on how it was installed):

- standalone: `parallel-cli update`
- uv: `uv tool upgrade parallel-web-tools[cli]`
- pipx: `pipx upgrade parallel-web-tools[cli]`
- npm: `npm update -g parallel-web-cli`
- homebrew: `brew update && brew upgrade parallel-web/tap/parallel-cli`

## Step 2: Authenticate

Check auth status:

```bash
parallel-cli auth --json
```

You will get a response like:

```json
{
  "authenticated": true,
  "method": "oauth",
  "env_var_set": false,
  "has_stored_credentials": true,
  "stored_overridden_by_env": false,
  "token_file": "xxx",
  "version": 1,
  "selected_org_id": "legacy",
  "selected_org_name": null,
  "has_control_api_tokens": false
}
```

If `authenticated` is `false` or `selected_org_id` is `legacy`, prompt the user to log in:

```bash
parallel-cli login --json
```

If this is a headless session, append `--no-browser`.

This triggers device OAuth. The user will be prompted to go to a web browser and input the code the CLI outputs.

When invoking from an agent harness, prefer streaming stdout via a Monitor-style tool over blocking on completion.

The output will look like:

```json
{"event": "auth_start"}
{"event": "device_code", "verification_uri": "http://localhost:3000/getServiceKeys/device", "verification_uri_complete": "http://localhost:3000/getServiceKeys/device?user_code=CHQX-NQKP&onboard_variant=agent", "user_code": "CHQX-NQKP", "expires_in": 600, "browser_open_attempted": true, "browser_opened": true}
{"event": "auth_waiting"}
{"event": "auth_success"}
```

`{"event": "auth_success"}` is emitted only after the user has successfully authorized the CLI. Otherwise it blocks at `{"event": "auth_waiting"}`.

## Step 3: Check balance

After authentication, check the current balance:

```bash
parallel-cli balance get
```

If zero, prompt the user to add balance:

```bash
parallel-cli balance add <AMOUNT_IN_CENTS>
```

Make it clear that a payment method should have been added to the organization. If not, the user can go to <https://platform.parallel.ai/settings> to add one.

## Step 4: Install the Parallel skills

Install the skills for the user:

```bash
parallel-cli skills install
```

The user may need to restart their agent if it doesn't support hot reloading (e.g. Claude).

## Step 5: Suggest a first run

Prompt the user to use the newly installed skills in `~/.agents/skills` to run a search or extract right away. Suggest one of:

- `/parallel:parallel-web-search <query>` — fast web search
- `/parallel:parallel-web-extract <url>` — extract content from a URL
- `/parallel:parallel-deep-research <topic>` — comprehensive research
- `/parallel:parallel-data-enrichment <list>` — enrich a list of entities
