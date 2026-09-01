---
name: parallel-underwriting-risk-profiles
description: From an address, business, or applicant, build a structured P&C underwriting risk profile drawn from the open web, COPE data (construction, occupancy, protection, exposure), operations, adverse history, and the long tail of fields no database covers, each cited and confidence-scored. Use when the user wants to "underwrite this risk", "build a risk profile for this property/business", "pull COPE data", or triage a submission. Runs on the user's own Parallel account via Task and Extract.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__claude_ai_Parallel_Web_Search_Paid__web_fetch, mcp__Parallel-Task-MCP__createTaskGroup, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# Underwriting Risk Profiles

Start from an address, a business, or an applicant and receive a structured **P&C risk profile**
drawn from the open web: COPE data (construction, occupancy, protection, exposure), operations,
adverse history, and the long tail of fields no commercial database covers. Every field is cited
to a public record and confidence-scored, so quotes go out faster and submission-to-bind rises
without giving up the audit trail.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two ways to run, both maintained by Parallel so API changes are absorbed for you:
- **Chat / co-work:** the **Task MCP** (`createTaskGroup`), one input per risk.
- **CLI / build-on-top:** `parallel-cli` + the installed **`parallel-web-extract`** and
  **`parallel-data-enrichment`** skills (`parallel-cli skills install`).

Not set up yet?
If Parallel is not configured, run the relevant setup skill first.
See [docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its lines / jurisdictions framing (captured once at setup), don't
re-ask it; only get the per-run specifics below.

Three quick questions before running (each risk profiled is a billable run):
1. **The risk?** An address, a business (name + location), or an applicant.
2. **Which fields?** Default is COPE + operations + adverse history. Add the long-tail fields your line needs (distance to coast, roof age, prior losses).
3. **Run how many now?** Start with a few to check quality, then batch the submission queue.

Confirm, then run.

## Run it

One task per risk. Output shape:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["risk", "fields"],
  "properties": {
    "risk": {"type": "string", "description": "the address / business / applicant profiled"},
    "fields": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "construction":   {"type": "string", "description": "COPE: materials, year built; empty string if not found"},
        "occupancy":      {"type": "string", "description": "COPE: use / operations of the premises"},
        "protection":     {"type": "string", "description": "COPE: sprinklers, distance to fire service, alarms"},
        "exposure":       {"type": "string", "description": "COPE: flood zone, wind / cat exposure, neighboring hazards"},
        "operations":     {"type": "string", "description": "what the business does, scale, notable hazards"},
        "adverse_history":{"type": "string", "description": "OSHA citations, prior losses, violations; empty if none found"}
      }
    },
    "basis": {
      "type": "array",
      "description": "one entry per field: the public-record source and a confidence",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["field", "source_url", "confidence"],
        "properties": {
          "field":      {"type": "string"},
          "source_url": {"type": "string", "description": "resolving public-record source; must load"},
          "confidence": {"type": "integer", "description": "0-100"}
        }
      }
    }
  }
}
```

Prompt (substitute the risk):

> Build a P&C underwriting risk profile for {RISK}. Return COPE data (construction: materials and
> year built; occupancy; protection: sprinklers and distance to fire service; exposure: flood
> zone and wind / catastrophe), the operations, and any adverse history (OSHA citations, prior
> losses, violations). Draw from public records (county / assessor records, FEMA, OSHA, permits)
> and cite a resolving source with a 0-100 confidence for every field. Never invent a value, if a
> field isn't on a reachable record, return an empty string and say so. Prefer a smaller correct
> profile over a padded one.

**Read it:** it's an underwriting worksheet, each COPE and history field clickable back to the
county or federal record behind it. Empty fields are "not in the public record," a prompt for a
question to the broker, not a value to assume.

## Config seams (build on top)

1. **Input:** an address / business / applicant; run one profile per submission, batch the queue.
2. **Fields:** edit the `fields` object to your line's rating factors (roof age, distance to coast, prior losses, protection class).
3. **Tier:** `core2x` default (long-tail public-record depth); `core` for a quick triage pass (see the tier guidance in this skill).

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Task API (stable,
`v1`): `POST /v1/tasks/runs` with `task_spec.output_schema`, then
`GET /v1/tasks/runs/{run_id}/result`; per-field citations and confidence in `output.basis`.
Clean record text via the Extract endpoint. Auth via `x-api-key`, server-side only. Prefer the
CLI/MCP unless you need raw control.

## Next

- Verify the applicant behind the risk → **kyb-kyc**.
- Research the claims that follow → **claims-research**.
- Keep the risk under watch after bind → **book-risk-monitoring**.
