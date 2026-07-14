# Integration patterns

Use these patterns to keep provider complexity below a small application-owned interface.

## Contents

- [Static queries](#static-queries)
- [Dynamic user text](#dynamic-user-text)
- [Model tool calling](#model-tool-calling)
- [Application-owned normalization](#application-owned-normalization)
- [Full-content pipeline](#full-content-pipeline)
- [Synthesized answers](#synthesized-answers)
- [Verification fixtures](#verification-fixtures)

## Static queries

Write the full research goal once and pair it with concise keyword queries. Keep source preferences and freshness intent in the objective unless a hard filter is a product requirement.

```python
response = client.search(
    objective="Find current official release notes for React and Vite used in this project.",
    search_queries=["React release notes", "Vite release notes"],
)
```

## Dynamic user text

Separate full intent from retrieval terms at the caller boundary:

```python
def search_web(*, objective: str, search_queries: list[str], mode: str):
    if not search_queries:
        raise ValueError("search_queries must contain at least one query")
    return parallel_client.search(
        objective=objective,
        search_queries=search_queries,
        mode=mode,
    )
```

Prefer changing an upstream structured caller to provide both fields. A one-query compatibility path is valid only when the old value is already a short keyword-style query. A question or application prompt can be valid API input and still be a poor retrieval query; do not decide from length alone. Preserve that text as `objective`, then use caller-provided queries or an existing explicit planning step. Do not silently truncate long text, regex-split it, or add an unpriced, unobserved model call for query expansion.

Choose `mode` from the latency SLO, query quality, and a representative eval. Do not infer it from a provider-tier name alone.

## Model tool calling

Change the tool input contract instead of expanding queries inside the handler:

```json
{
  "type": "object",
  "properties": {
    "objective": {
      "type": "string",
      "description": "Self-contained research goal with necessary context."
    },
    "search_queries": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 3,
      "maxItems": 3,
      "description": "Exactly 3 diverse 3-6 word keyword queries. Each includes the key entity or topic. Never use sentences, instructions, or site: operators."
    }
  },
  "required": ["objective", "search_queries"]
}
```

Return a compact tool result containing titles, URLs, dates when present, and excerpts. Keep untrusted web content clearly separated from tool instructions in the model prompt.

## Application-owned normalization

Normalize only fields callers actually need. A useful contract often looks like:

```typescript
type SearchHit = {
  url: string;
  title: string | null;
  publishedAt: string | null;
  passages: string[];
};
```

Map Parallel fields once at the provider boundary. Keep results in returned order. Do not add a fake `score`, empty image URL, or synthetic author to mimic a legacy SDK.

Use an adapter when many callers consume a stable application contract. Replace calls directly when the provider is already isolated; a one-method pass-through wrapper adds complexity without hiding any.

## Full-content pipeline

When callers truly need page bodies:

1. Use the Search API to find relevant URLs.
2. Select only the URLs needed by the workflow.
3. Call the Extract API with those URLs and the Search API response's `session_id`.
4. Preserve concurrency limits, timeouts, partial-failure behavior, and content-size budgets.

Enable `advanced_settings.full_content` when the caller needs page bodies; it is disabled by default. Reconcile the separate `results` and `errors` arrays by URL rather than assuming input order. Follow the exact Extract contract in the `references/parallel-products.md` file loaded from the skill root.

Do not fetch every result automatically if the old application only consumed snippets. That increases latency and cost while changing the failure surface.

## Synthesized answers

Choose one owner for synthesis:

- Keep the application's existing LLM synthesis step and feed it Search API excerpts.
- Use the Chat API for an interactive grounded completion.
- Use the Task API for asynchronous multi-step research or structured output.

Parallel Chat uses the OpenAI SDK and bearer auth, while Search, Extract, and Task use `parallel-web` or `x-api-key` REST auth. Preserve streaming and citations explicitly. Follow the exact product contract in the `references/parallel-products.md` file loaded from the skill root.

Do not run both the old synthesis step and a new Parallel synthesis path unless the application intentionally needs two stages.

## Verification fixtures

Use provider-neutral fixtures at the application boundary. Include:

- multiple excerpts per result;
- null title and publish date;
- empty results;
- a non-empty warnings array;
- an Extract API partial failure when full content is used;
- response ordering without scores.

Keep one SDK-shaped fixture only at the Parallel boundary. This prevents provider field names from spreading back through the codebase.
