---
name: parallel-insurance-kyb-kyc
description: Verify any business or individual at submission, onboarding, or renewal, beneficial ownership, registry data, sanctions, licensing, and negative news, across thousands of entities in parallel, in one cited, confidence-scored profile. Use when the user wants to "verify this applicant", "run KYB/KYC on submission", "check ownership and sanctions", or screen a book at renewal. Runs on the user's own Parallel account via Task.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__Parallel-Task-MCP__createTaskGroup, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# KYB / KYC

Verify a business or individual at submission, onboarding, or renewal, and get back one
**cited, confidence-scored profile**: beneficial ownership, registry data, sanctions, licensing,
and negative news. Runs across thousands of entities in parallel, so a whole submission batch or
renewal book gets screened at once. The rule that makes it audit-ready: nothing is asserted
without a source, and a "no match" is a checked result, not a blank.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two ways to run, both maintained by Parallel so API changes are absorbed for you:
- **Chat / co-work:** the **Task MCP** (`createTaskGroup`), one input per entity.
- **CLI / build-on-top:** `parallel-cli` + the installed **`parallel-data-enrichment`** skill
  (`parallel-cli skills install`).

Not set up yet?
If Parallel is not configured, run the relevant setup skill first.
See [docs.parallel.ai](https://docs.parallel.ai).

> This surfaces public-record evidence with citations to speed a review. It is not legal or
> compliance advice and does not replace your regulated screening provider or a human decision;
> treat it as cited input, and confirm any sanctions hit against the official list.

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its jurisdictions framing (captured once at setup), don't re-ask
it; only get the per-run specifics below.

Before running (each entity is a billable screen):
1. **Which entity or batch?** A business (name + location) or individual, or the submission / renewal batch.
2. **Which checks?** Default: registry status, beneficial ownership, sanctions, licensing, negative news. Add PEP or litigation if your policy requires.
3. **At which stage?** Submission, onboarding, or renewal, so the framing matches your workflow.

Confirm, then run.

## Run it

One task per entity (batch the submission or renewal list). Output shape:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["entity", "checks", "verdict"],
  "properties": {
    "entity": {"type": "string"},
    "checks": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["check", "result", "source_url", "confidence"],
        "properties": {
          "check":      {"type": "string", "enum": ["registry_status", "beneficial_ownership", "sanctions", "licensing", "negative_news", "pep", "litigation", "other"]},
          "result":     {"type": "string", "description": "the finding, or an explicit 'No match found' / 'Not found'; never left blank"},
          "source_url": {"type": "string", "description": "resolving source that backs the result; must load"},
          "confidence": {"type": "integer", "description": "0-100"}
        }
      }
    },
    "verdict": {"type": "string", "enum": ["clear", "review", "decline", "insufficient_evidence"], "description": "use insufficient_evidence rather than guessing when checks can't be resolved"}
  }
}
```

Prompt (substitute the entity + stage):

> Verify {ENTITY} at {STAGE}. For each check, return the finding with a resolving source URL and
> a 0-100 confidence: (1) registry status, (2) beneficial ownership (named owners and stakes),
> (3) sanctions and watchlist screening, (4) licensing (required licenses and standing), (5)
> negative news. Where a check finds nothing, state "No match found" explicitly, never leave it
> blank. Then give a verdict of clear / review / decline, or "insufficient_evidence" if the
> checks can't be resolved. Never assert a sanction, an owner, or a license without a source;
> confirm any potential sanctions hit against the official list rather than inferring it.

**Read it:** the verdict is the routing call, "clear" moves the submission, "review" and
"decline" carry the sourced reason, and "insufficient_evidence" is distinct from clean, don't let
an unresolved screen read as passing.

## Config seams (build on top)

1. **Input:** one entity, or batch the submission / renewal book (one screen each).
2. **Checks:** edit the `check` enum + the prompt to your policy (add PEP, litigation, source-of-funds).
3. **Verdict routing:** map clear / review / decline / insufficient_evidence to your submission workflow.
4. **Tier:** `core2x` default here (compliance leans up); `core` for a lighter first pass (see the tier guidance in this skill).

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Task API (stable,
`v1`): `POST /v1/tasks/runs` with `task_spec.output_schema`, then
`GET /v1/tasks/runs/{run_id}/result`; per-field citations and confidence in `output.basis`. Auth
via `x-api-key`, server-side only. Prefer the CLI/MCP unless you need raw control.

## Next

- Build the risk profile behind the applicant → **underwriting-risk-profiles**.
- Keep the entity under watch after bind → **book-risk-monitoring**.
- Get the fast read first → **insurance-quickstart**.
