---
name: parallel-current-scaffolding
description: Resolve the latest stable versions for a stack and scaffold or generate against live library references, so the apps you (or your users) generate run on what's current, not on deprecated methods the model learned in training. Use when the user wants to "scaffold an app", "pin the latest stable versions", "generate against current libraries", or ground a codegen step in the live web. Runs on the user's own Parallel account via Search and Task.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__claude_ai_Parallel_Web_Search_Paid__web_search, mcp__Parallel-Task-MCP__createTaskGroup, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# Current Scaffolding

Before you scaffold, resolve the **latest stable version** of every library in the stack and
pull the **current** reference for how to wire them together, so the app that gets generated
runs on what's current, not on the training-era defaults a model would otherwise emit. Every
version and pattern resolves to a source; unknowns are surfaced, not filled with a plausible
guess.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two ways to run, both maintained by Parallel so API changes are absorbed for you:
- **Chat / co-work:** the **Parallel Web Search** tool (`web_search`) to resolve versions, the
  **Task MCP** (`createTaskGroup`) to assemble the cited stack manifest.
- **CLI / build-on-top:** `parallel-cli` + the installed **`parallel-web-search`** and
  **`parallel-deep-research`** skills (`parallel-cli skills install`).

Not set up yet?
If Parallel is not configured, run the relevant setup skill first.

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its stack and "current" framing (captured once at setup), that
is usually the stack to resolve, don't re-ask it; only get the per-run specifics below.

Two quick questions before running (resolving + assembling costs credits):
1. **Which libraries?** The dependency set to resolve (or "the stack in my profile").
2. **Which channel?** Latest stable (default), latest minor within a pinned major, or include betas / RCs.

Confirm, then run.

## Run it

Resolve each library to its current version and the current wiring reference, then assemble a
cited manifest. Output shape:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["stack", "dependencies"],
  "properties": {
    "stack": {"type": "string", "description": "what's being scaffolded, one line"},
    "dependencies": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["name", "latest_stable", "as_of", "source_url"],
        "properties": {
          "name":          {"type": "string"},
          "latest_stable": {"type": "string", "description": "current stable version, e.g. ^15.5.x; empty string if not resolvable"},
          "as_of":         {"type": "string", "description": "date the version was confirmed"},
          "note":          {"type": "string", "description": "a current-usage caveat or breaking change to respect; empty if none"},
          "source_url":    {"type": "string", "description": "resolving source (registry, release notes, docs); must load"}
        }
      }
    }
  }
}
```

Prompt (substitute the stack):

> Resolve the latest {CHANNEL} version of each of these libraries and the current, supported way
> to wire them together: {LIBRARIES}. For each, return the version, the date you confirmed it,
> a resolving source (package registry, release notes, or official docs), and any current-usage
> caveat or breaking change a generated app must respect. Do not guess a version, if you can't
> resolve one from a reachable source, return an empty string and say so. Prefer official
> registries and docs over blog posts.

**Read it:** it's a manifest to hand to your scaffolder, each dependency pinned to a current
version with the source that confirmed it and any caveat the generated code must respect. Where
a version couldn't be resolved, that's flagged, don't let the generator invent one.

## Config seams (build on top)

1. **Input**: the dependency set (or read it from the workspace `PROFILE.md` file); this is the whole input.
2. **Channel**: latest stable (default), latest minor within a pinned major, or include betas.
3. **Manifest fields**: extend `dependencies` (peer deps, min runtime, license) to what your scaffolder consumes.
4. **Tier**: `core` for assembling the manifest; the version lookups run through Search.

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Resolve versions via
Search (`POST /v1/search`), assemble via Task (`POST /v1/tasks/runs` with
`task_spec.output_schema`, then `GET /v1/tasks/runs/{run_id}/result`; citations in
`output.basis`). Auth via `x-api-key`, server-side only. Prefer the CLI/MCP unless you need raw
control.

## Next

- Review the generated code against those versions → **doc-grounded-review**.
- Keep the manifest fresh as libraries move → **dependency-monitoring**.
- Offer this to every app on your platform → **platform-web-access**.
