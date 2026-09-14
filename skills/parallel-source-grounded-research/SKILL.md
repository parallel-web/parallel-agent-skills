---
name: parallel-source-grounded-research
description: Answer a legal question grounded in live authoritative sources, statutes, regulations, case law, agency guidance, including hard-to-crawl government, court, and international domains, with clean extracted text you can quote word-for-word and a resolving source for every passage. Use when the user wants to "find the actual statute/rule/case", "what does the regulation say", "cite the primary source", or research the law rather than a summary. Runs on the user's own Parallel account via Search + Extract.
allowed-tools: Bash(command:*), Bash(parallel-cli:*), Bash(curl:*)
metadata:
  author: parallel
---

# Source-Grounded Research (Search + Extract)

Ask a legal question, get an answer built from the **primary sources themselves**, not a
model's stale memory of them. Parallel's retrieval reaches the authoritative and
hard-to-crawl corners (regulator sites, court dockets, government registries, international
and non-English domains) and extracts clean text you can **quote word-for-word**, with a
resolving source behind every passage. When the source can't be found, that's the answer, no
paraphrase stands in for a citation.

This is the distinctive legal use case: the value is in *grounding on the real source and
quoting it exactly*, so feedback and drafting rest on what the law actually says.

## Build on the maintained layer

> Shared contract: Use the user's own Parallel account and the maintained CLI or MCP layer. Cite every returned field, and leave unverifiable fields empty instead of fabricating values. Choose one processor tier. If a run falls short, increase the tier once and rerun it, then route the user to a Parallel DE if it still falls short. Use the rest of this file for the use case.

- **CLI / build-on-top:** the installed **`parallel-web-search`** and **`parallel-web-extract`**
  skills (`parallel-cli skills install`) are the maintained path. Search finds and ranks the
  authoritative sources; Extract pulls clean, quotable text from the exact pages.
- **Chat / co-work:** the Parallel Web Search MCP exposes the same `web_search` / `web_fetch`.

If Parallel is not configured, run the relevant setup skill first. See [docs.parallel.ai](https://docs.parallel.ai).

## Guided intake (ask first)

If the current workspace contains a `PROFILE.md` file, use its jurisdiction framing (captured once at setup) to scope the search, don't re-ask it; only get the per-run specifics below.

Before running:
1. **The question** in plain language, name the entity, statute, rule, or matter as precisely as you can.
2. **Jurisdiction + as-of.** Which legal system, and whether you need the currently-in-force version or the text as of a date. The law changes; grounding is only useful if it's the right version.
3. **Need verbatim text?** If you'll quote or draft from it, say so, that routes to Extract for word-for-word passages rather than summaries.

Confirm, then run.

## Run it

The shape that works: **Search to find the authoritative sources, then Extract to pull the
exact text**, and quote from Extract, never from a summary.

1. **Search** for the authoritative sources (prefer primary: the regulator, the court, the
   official code, the registry):

   ```
   parallel-cli search "text of {STATUTE/RULE}, official source, {JURISDICTION}, in force {AS_OF}" --max-results 10
   ```

   Bias toward `.gov`, official court, and official code domains; treat blogs and secondary
   summaries as pointers to the primary source, not the source.

2. **Extract** the exact pages so you can quote them verbatim:

   ```
   parallel-cli extract "https://<official-source-url>" "https://<second-source-url>"
   ```

   Pass the objective (the question) so Extract returns the passages that answer it.

3. **Answer from the extracted text only.** Quote the operative language, attribute each
   quote to its resolving URL, and note the version/date. If the primary source can't be
   reached, say so and stop, do not substitute a paraphrase for a citation.

Output shape to hold the answer (so it stays auditable):

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["question", "jurisdiction", "findings", "unresolved"],
  "properties": {
    "question": {"type": "string"},
    "jurisdiction": {"type": "string"},
    "as_of": {"type": "string", "description": "the version/date the answer reflects; empty if not constrained"},
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["point", "quote", "source_url", "source_type"],
        "properties": {
          "point": {"type": "string", "description": "one line: what this establishes"},
          "quote": {"type": "string", "description": "verbatim text from the source; exact, not paraphrased"},
          "source_url": {"type": "string", "description": "resolving source the quote came from; must load"},
          "source_type": {"type": "string", "enum": ["statute", "regulation", "case_law", "agency_guidance", "official_registry", "docket", "other"]},
          "source_date": {"type": "string", "description": "publication / effective date if shown; empty otherwise"}
        }
      }
    },
    "unresolved": {
      "type": "array",
      "description": "parts of the question no authoritative source could be found for; empty array if fully sourced",
      "items": {"type": "string"}
    }
  }
}
```

**Read it:** each finding is a claim + the exact quote + a source you can open. The
`unresolved` list is not a failure, it's the honest edge of what's sourceable, and in legal
work that boundary is the most important part of the output.

## Config seams (build on top)

1. **Source allowlist**: bias Search toward the primary domains for your jurisdiction (the
   official code, the regulator, the court system) and down-rank secondary summaries.
2. **Verbatim vs summary**: route to Extract whenever the text will be quoted or drafted
   from; Search excerpts are fine for orientation, not for quoting.
3. **As-of / versioning**: thread the effective date through the query so you ground on the
   in-force (or point-in-time) version, not whatever ranks highest.
4. **Multi-jurisdiction**: run one Search+Extract pass per jurisdiction and keep the answers
   separate; don't let one jurisdiction's text bleed into another's finding.

## Production (raw HTTP API): verify before hardcoding

_As of 2026-08; confirm at [docs.parallel.ai](https://docs.parallel.ai)._ Search API:
`POST /v1beta/search` (returns ranked results with excerpts + URLs). Extract / fetch: pull
full clean content from specific URLs for verbatim quoting. Auth via `x-api-key`, server-side
only. Prefer the CLI/MCP so retrieval changes are absorbed on update.

## Next

- Turn the sourced facts about an entity into a tear sheet → **entity-diligence**.
- Watch for when the rule or case status changes → **regulatory-monitoring**.
- Roll the research into a full subject brief → **diligence-briefs**.
