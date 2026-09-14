---
name: parallel-kyb-kyc
description: Run an audit-ready KYB / KYC screen on a company or counterparty, registry status, beneficial ownership, sanctions and watchlist screening, and adverse media, in one cited, confidence-scored profile, then keep it under continuous watch. Use when the user wants to "run KYB on X", "screen this counterparty", "check beneficial ownership and sanctions", or set up onboarding and ongoing compliance. Runs on the user's own Parallel account via Task and Monitor.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), Bash(curl:*), ToolSearch, mcp__Parallel-Task-MCP__createTaskGroup, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# KYB / KYC

Screen a company or counterparty and get back one **audit-ready, cited compliance profile**,
registry status, beneficial ownership, sanctions and watchlist screening, and adverse media,
each field confidence-scored with a resolving source. Run it at onboarding as a Task, then
keep the name under a Monitor so a new sanction, filing, or adverse story surfaces the moment
it appears. The rule that makes it audit-ready: nothing is asserted without a source, and a
"no match" is stated as a checked result, not left blank.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two primitives, both maintained by Parallel so API changes are absorbed for you:
- **Onboarding screen (point in time):** the **Task MCP** (`createTaskGroup`), or the installed
  **`parallel-data-enrichment`** skill on the CLI.
- **Ongoing screen (continuous):** the installed **`parallel-monitor`** skill (`parallel-cli
  skills install`), Monitor is the stable `v1` API.

If Parallel is not configured, run the relevant setup skill first. See
[docs.parallel.ai](https://docs.parallel.ai).

> This surfaces public-record evidence with citations to speed a compliance review. It is not
> legal advice and does not replace your regulated screening provider or a human decision;
> treat it as cited input to your process, and confirm sanctions hits against the official
> list.

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its compliance-posture framing (jurisdictions, lists, risk
appetite, captured once at setup), don't re-ask it; only get the per-run specifics below.

Before running (each screen is a billable run; the Monitor is recurring):
1. **Which company or counterparty?** Name + domain, and country of registration if you know it.
2. **Which checks?** Default: registry status, beneficial ownership, sanctions/watchlist, adverse media. Add PEP, litigation, or others your policy requires.
3. **One-time or ongoing?** Onboarding screen only (Task), or also stand up the continuous Monitor.

Confirm, then run.

## Run it

### 1. Onboarding screen (Task)

One task per counterparty. Output shape:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["company", "checks", "overall_risk"],
  "properties": {
    "company": {"type": "string"},
    "checks": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["check", "result", "source_url", "confidence"],
        "properties": {
          "check":      {"type": "string", "enum": ["registry_status", "beneficial_ownership", "sanctions_watchlist", "adverse_media", "pep", "litigation", "other"]},
          "result":     {"type": "string", "description": "the finding, or an explicit 'No match found' / 'Not found'; never left blank"},
          "source_url": {"type": "string", "description": "resolving source that backs the result; must load"},
          "confidence": {"type": "integer", "description": "0-100"}
        }
      }
    },
    "overall_risk": {"type": "string", "enum": ["low", "medium", "high", "insufficient_evidence"], "description": "use insufficient_evidence rather than guessing when checks can't be resolved"}
  }
}
```

Prompt (substitute the counterparty):

> Run a KYB / KYC screen on {COMPANY} (country of registration: {COUNTRY_OR_UNKNOWN}). For each
> check, return the finding with a resolving source URL and a 0-100 confidence: (1) registry
> status (active/dissolved, jurisdiction, ID), (2) beneficial ownership (named owners /
> controllers), (3) sanctions and watchlist screening, (4) adverse media. Where a check finds
> nothing, state "No match found" explicitly, never leave it blank. Then give an overall risk
> of low / medium / high, or "insufficient_evidence" if the checks can't be resolved. Never
> assert a sanction, an owner, or a registry fact without a source; confirm any potential
> sanctions hit against the official list rather than inferring it.

### 2. Ongoing screen (Monitor)

Stand up one Monitor per counterparty so changes surface going forward. Query:

> Notify me of any new sanction or watchlist listing, ownership or control change, registry
> status change (e.g. dissolution), litigation, or adverse media concerning {COMPANY}.
> Prioritize named, dated, sourced facts; exclude rumor. Return the change, its date, and a
> resolving source.

Reuse the `parallel-portfolio-monitoring` output shape (swap the enum to the compliance events above),
`lite` processor, `1d` cadence.

## Config seams (build on top)

1. **Input**: one counterparty, or batch your onboarding queue (one screen each).
2. **Checks**: edit the `check` enum + the prompt to your policy (add PEP, litigation, source-of-funds).
3. **Risk model**: `overall_risk` is a summary; keep `insufficient_evidence` distinct from `low` so unresolved screens don't read as clean.
4. **Tier**: `core2x` default here (compliance leans up); `core` for a lighter first pass.
5. **Continuous**: the Monitor turns the point-in-time screen into ongoing coverage.

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Task API (stable,
`v1`): `POST /v1/tasks/runs` with `task_spec.output_schema`, `GET /v1/tasks/runs/{run_id}/result`;
citations in `output.basis`. Ongoing screening via `POST /v1/monitors` (`event_stream`), read at
`GET /v1/monitors/{id}/events`. Auth via `x-api-key`, server-side only. Prefer the CLI/MCP unless
you need raw control.

## Next

- Screen a whole target before the profile → **company-profiles** (full tear sheet).
- Screen the owners surfaced here as individuals → re-run this skill per person.
- Keep the whole book under watch → **portfolio-monitoring**.
