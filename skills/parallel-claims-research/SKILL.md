---
name: parallel-claims-research
description: Research a claim line by line, like-kind-and-quality matching, live pricing, and intake review, run against your own claim rules, with high-confidence lines cleared automatically and edge cases routed to a human, each line confidence-scored and cited. Use when the user wants to "research this claim", "match like-kind-and-quality", "price these lost items", or automate contents-claim intake. Runs on the user's own Parallel account via Task and Extract.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(sleep *), ToolSearch, mcp__claude_ai_Parallel_Web_Search_Paid__web_search, mcp__Parallel-Task-MCP__createTaskGroup, mcp__Parallel-Task-MCP__getStatus, mcp__Parallel-Task-MCP__getResultMarkdown
metadata:
  author: parallel
---

# Claims Research

Research a claim **line by line**: like-kind-and-quality matching, live pricing, and intake
review, run against your own claim rules. High-confidence lines clear automatically; edge cases
route to a human. Every line is confidence-scored and carries the source behind the match and
price, so the auto-cleared ones are auditable and the routed ones arrive with the evidence
already attached.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

Two ways to run, both maintained by Parallel so API changes are absorbed for you:
- **Chat / co-work:** the **Task MCP** (`createTaskGroup`), one input per claim (or per line batch).
- **CLI / build-on-top:** `parallel-cli` + the installed **`parallel-web-search`** and
  **`parallel-data-enrichment`** skills (`parallel-cli skills install`).

Not set up yet?
If Parallel is not configured, run the relevant setup skill first.
See [docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its lines and rules_source framing (captured once at setup), don't
re-ask it; only get the per-run specifics below.

Three quick questions before running (each claim researched is a billable run):
1. **The claim lines?** The lost / damaged items (description, and any make/model or age).
2. **Your rules?** The claim rules to apply (depreciation, caps, coverage limits) and the auto-clear confidence threshold.
3. **Run how many now?** Start with one claim to check fidelity, then batch.

Confirm, then run.

## Run it

One task per claim; each line gets a like-kind-and-quality match, a price, and a disposition.
Output shape:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["claim_ref", "lines"],
  "properties": {
    "claim_ref": {"type": "string"},
    "lines": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["lost_item", "like_kind_match", "price", "disposition", "confidence", "source_url"],
        "properties": {
          "lost_item":       {"type": "string"},
          "like_kind_match": {"type": "string", "description": "the current like-kind-and-quality equivalent"},
          "price":           {"type": "string", "description": "current price of the match, with currency"},
          "rule_applied":    {"type": "string", "description": "the claim rule applied (depreciation, cap), if any"},
          "disposition":     {"type": "string", "enum": ["auto_cleared", "human_review"], "description": "human_review when confidence is below threshold or a rule needs judgment"},
          "confidence":      {"type": "integer", "description": "0-100"},
          "source_url":      {"type": "string", "description": "resolving source for the match + price; must load"}
        }
      }
    }
  }
}
```

Prompt (substitute the claim + rules):

> Research claim {CLAIM_REF} line by line. For each lost or damaged item, find the current
> like-kind-and-quality equivalent, its current price with a resolving source, and apply these
> claim rules: {RULES}. Give each line a 0-100 confidence and a disposition: "auto_cleared" if
> confidence is at or above {THRESHOLD} and no rule needs human judgment, otherwise
> "human_review". Never invent a match, a price, or a source, if you can't source a line, set
> low confidence and route it to human_review rather than guessing.

**Read it:** the auto-cleared lines are done, each with its cited match and price; the
human_review lines are the queue, and they arrive with the evidence and the reason attached. The
threshold is the dial between throughput and touch, tune it on real claims.

## Config seams (build on top)

1. **Input:** the claim lines; run one task per claim, batch the queue.
2. **Rules:** encode your depreciation, caps, and coverage logic in the prompt (or a rules file you pass in).
3. **Threshold:** the auto-clear confidence cutoff is the throughput / touch dial.
4. **Tier:** `core` for volume (auto-clear the easy lines); `core2x` for a harder book or edge-case review (see the tier guidance in this skill).

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Task API (stable,
`v1`): `POST /v1/tasks/runs` with `task_spec.output_schema`, then
`GET /v1/tasks/runs/{run_id}/result`; per-field citations and confidence in `output.basis`.
Pricing lookups run through Search. Auth via `x-api-key`, server-side only. Prefer the CLI/MCP
unless you need raw control.

## Next

- Underwrite the risk behind the policy → **underwriting-risk-profiles**.
- Verify the claimant or business → **kyb-kyc**.
- Watch the book for fraud and catastrophe signals → **book-risk-monitoring**.
