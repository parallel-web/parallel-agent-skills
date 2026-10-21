# Evaluation artifact contract

Use the application's existing formats where available. These fields are a starting contract for a new harness, not an API schema. Store secrets outside artifacts. Keep gold records accessible to the grader only.

## Gold dataset and agent inputs

One JSONL record per question can carry:

```json
{
  "id": "q001",
  "question": "Which vendors in the supplied set meet all eligibility conditions as of the cutoff?",
  "task_shape": "list",
  "as_of": "2026-10-01",
  "split": "holdout",
  "gold": {
    "items": ["Example Vendor"],
    "aliases": {},
    "inclusion_conditions": ["condition A", "condition B"],
    "exhaustive": true,
    "evidence": [{"url": "https://example.org/source", "verified_at": "2026-10-01"}]
  }
}
```

This is illustrative data, not a verified question. Replace it with reviewed records. Supply actual candidate sets and conditions in the question or agent-visible context, not solely in `gold`. Project only the question, ID, and necessary application context into agent input. Reference answers, aliases, and grading annotations belong in separate grader input.

For facts, store the answer and accepted alternatives; for structured records, expected fields; for research, the rubric and verified claims. Record provenance and cutoff. An incomplete reference list cannot establish exhaustive recall: resolve missing labels or mark the metric unavailable. Apply benchmark-specific duplicate and extra-item rules; otherwise normalize aliases and deduplicate before computing precision and recall. Define empty-set behavior before scoring.

## Run manifest

Save one immutable manifest per configuration:

- Run ID, code revision, dataset version/hash, split and question IDs, pilot/held-out designation, repetition count and trial IDs.
- Provider/product/mode, exact request settings and tool schemas, extraction implementation, endpoint/SDK versions, documentation date, price source and currency.
- Documented defaults and tool definition used as the baseline; each override, supporting workload or pilot evidence, and rationale (including explicit mode selection).
- Cost-parity targets for result count, content per page, product tier, and reasoning level; supported controls, expected differences, and why any mismatch is unavoidable. Keep a parity-adjusted configuration separate from the defaults baseline.
- Model/version, sampling settings, exact research prompt and output format; judge/version, prompt, rubric, and resolution threshold.
- Maximum Search/Extract calls, per-question deadline, total spend bound, concurrency and rate limits, retry/backoff limits, cache/freshness policy, and query-count policy.
- Failure/timeout scoring, contamination policy, and all deviations from an official benchmark protocol.

Freeze the manifest before scoring. A configuration correction creates a new run; retain the invalid run with an explanation. Keep pilot tuning separate from final results.

## Trial traces and grades

Key every trial by question ID, configuration ID, repetition, and session ID. Retain:

- Exact model and tool messages, tool-call IDs, request arguments, returned titles/URLs/excerpts, warnings/errors, and the actual context delivered to answer generation.
- Requested and actual result counts and content volume per page and trial; partial/dropped results, token truncation, HTTP status, rate-limit details, timeouts, and requested versus actual endpoints, including any fallback.
- Start/end times and elapsed time for each model/tool invocation and the whole task; individual retry attempts and backoff; concurrent batch membership.
- Final answer or terminal failure, token usage, itemized Search/Extract/model cost, pricing provenance, tool-call counts, and budget exhaustion.
- Grade, judge reasoning, evidence/citation audit, resolution status, failure category, and human review outcome.

Record unknown costs as unknown, not zero. Separate evaluation/judge spend from application inference cost. Include trial errors in the primary denominator; declare how partial answers, abstentions, and infrastructure failures score. A tool response lost before reaching the model is a harness fault. Inspect query quality before declaring a retrieval miss.

Retain every failure occurrence, including recovered attempts, with its trial ID, impact, and when it was surfaced to the user. No silent endpoint fallback or Parallel-side failures: flag them during execution and summarize counts with trace references in the report, separately from retrieval misses.

## Grading and report

Use official benchmark grading unchanged when claiming its score. Otherwise define the rubric before running:

| Shape | Primary measures |
| --- | --- |
| Fact | Correctness against verified alternatives; support for claimed facts |
| List | Precision = correct returned items / returned items; recall = correct returned items / gold items |
| Structured | Accuracy for each field and record, with missing/null policy |
| Research | Explicit coverage, correctness, and sourcing criteria |

Require reasoning with automated judgments. Human review should cover at least 10% of judged trials, including successes and failures. Investigate disagreements before trusting aggregate scores. Retain benchmark-specific abstention rules; report any additional misinformation-sensitive rubric separately.

The report should contain:

1. Workload, targets, dataset provenance, experiment boundary and configuration differences, including deviations from documented defaults and achieved versus intended cost parity. Show result counts, content per page, product tiers, and reasoning levels; disclose residual mismatches.
2. Question/trial counts, completion and resolution rates, quality by task shape/domain/freshness, and variation across at least three repetitions. Small pilots provide directional evidence; mark tail percentiles unstable when samples are small.
3. Total application spend across all trials divided by resolved trials, including failures' spend. With zero resolutions this is undefined. Also show cost per attempted trial, Search/Extract calls, and token usage so the denominator is clear.
4. Search-call latency and end-to-end latency p50/p95/p99, including documented retry effects; errors, timeouts, and budget exhaustion alongside percentiles. Query planning and synthesis count toward end-to-end time, not search-call time.
5. No-search, synthesis, provider-error and retrieval-miss counts, plus separately identified harness faults; rate-limit context and representative trace IDs.
6. Quality versus cost and quality versus latency plots or tables. Identify nondominated configurations, then recommend those meeting the user's thresholds. State uncertainty rather than forcing a winner.
7. Reproduction commands, artifact paths, limits, unexecuted steps, and 2–3 proposed follow-up configurations tied to observed failures or bottlenecks, with rationale, expected tradeoffs, and required spend. Keep follow-up results separate from the frozen scored run.

Source: [Parallel's public evaluation guide](https://docs.parallel.ai/search/evaluating-search). Consult the live guide for its benchmark research prompt and linked API best practices for current request definitions.
