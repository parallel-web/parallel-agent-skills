# TypeScript recipe — `parallel-web`

## Install

```bash
npm install parallel-web         # or pnpm add / yarn add
export PARALLEL_API_KEY="your-api-key"   # get one at https://platform.parallel.ai
```

The SDK reads `PARALLEL_API_KEY` from the environment automatically. Use `new Parallel({ apiKey })` to override.

**`tsconfig.json` note:** `parallel-web` uses modern class features (private `#fields`). If you type-check with a bare `tsc file.ts`, set `"target": "ES2022"` and `"skipLibCheck": true` — or just use a runner (tsx, bun, ts-node) that already does this.

## Critical: snake_case, not camelCase

The TypeScript SDK mirrors the REST body verbatim, so **request fields stay in snake_case**:

- `task_spec`, not `taskSpec`
- `output_schema`, not `outputSchema`
- `json_schema`, not `jsonSchema`
- `search_queries`, not `searchQueries`
- `run_id`, not `runId` on the response

The `taskRun.result(runId, opts)` second argument uses `{ timeout: number }` (in seconds), **not** `apiTimeout`.

## Snippets by use case

### Web Search — `client.search`

```ts
import Parallel from "parallel-web";

const client = new Parallel();

// Best practices: both objective and 2-3 short search_queries (3-6 words each).
// Modes: "basic" = lowest latency, "advanced" = higher recall + reranking.
// advanced_settings.source_policy / fetch_policy / location for fine-grained control.
const search = await client.search({
  objective: "Find the latest information about <TOPIC>",
  search_queries: ["<query 1>", "<query 2>"],
  mode: "advanced",
  max_chars_total: 27000,
  advanced_settings: {
    max_results: 10,
    excerpt_settings: { max_chars_per_result: 10000 },
  },
});

for (const result of search.results) {
  console.log(`${result.title}: ${result.url}`);
  for (const excerpt of result.excerpts) {
    console.log(excerpt.slice(0, 200));
  }
}
```

### Research / structured task — `client.taskRun`

```ts
import Parallel from "parallel-web";

const client = new Parallel();

// Processors:
//   lite / base  — simple lookups, single-hop facts (seconds)
//   core         — up to ~10 output fields, light research (30 s – 2 min)
//   pro / ultra  — deep, multi-hop research (2 – 25 min; use webhooks!)
//   append "-fast" for lower-latency variants.
const taskRun = await client.taskRun.create({
  input: "<your research question or entity>",
  task_spec: {
    output_schema: {
      type: "json",
      json_schema: {
        type: "object",
        properties: {
          summary: { type: "string" },
          key_findings: { type: "array", items: { type: "string" } },
          sources: { type: "array", items: { type: "string" } },
        },
        required: ["summary", "key_findings", "sources"],
      },
    },
  },
  processor: "core",
  // webhook: { url: "https://your-app.com/webhook", event_types: ["task_run.status"] },
});

// Block until complete (timeout in seconds)
const result = await client.taskRun.result(taskRun.run_id, { timeout: 600 });
console.log(result.output);
```

### Data enrichment — `client.taskRun` with a structured schema

```ts
import Parallel from "parallel-web";

const client = new Parallel();

// Enrichment best practices: specific field names, exact formats in
// descriptions, explicit "Not Available" behavior on missing data.
const taskRun = await client.taskRun.create({
  input: "<entity, e.g. 'Stripe'>",
  task_spec: {
    output_schema: {
      type: "json",
      json_schema: {
        type: "object",
        properties: {
          founding_date: {
            type: "string",
            description: "Founding date in MM-YYYY format. Return 'Not Available' if unknown.",
          },
          employee_count: {
            type: "string",
            description: "Estimated employee count as a range (e.g. '500-1000').",
          },
          funding_sources: {
            type: "string",
            description: "Description of funding sources and total raised in USD.",
          },
        },
        required: ["founding_date", "employee_count", "funding_sources"],
      },
    },
  },
  processor: "core",
});

const result = await client.taskRun.result(taskRun.run_id, { timeout: 600 });
console.log(result.output);
```

### Lead discovery — FindAll API via `client.post`

FindAll is not yet a typed resource on the TS SDK. Use the generic `client.post`/`client.get` helpers:

```ts
import Parallel from "parallel-web";

const client = new Parallel();

// Tip: start with generator: "preview" to test your query (~10 candidates, low cost).
// Generators: preview (test), base (broad/common), core (specific), pro (rare/thorough).
const run = await client.post<{ findall_id: string }>(
  "/v1beta/findall/runs",
  {
    body: {
      objective: "<e.g. 'AI startups that raised Series A in 2024'>",
      entity_type: "companies",
      match_conditions: [
        {
          name: "series_a_2024",
          description:
            "Company must have raised a Series A funding round in 2024, confirmed by a reputable source.",
        },
        {
          name: "ai_focused",
          description: "Primary product must be AI-focused (LLMs, ML infra, AI apps).",
        },
      ],
      generator: "core",
      match_limit: 20,
    },
  }
);

// Blocks until complete — may take several minutes for "core" / "pro".
type FindAllResult = {
  candidates: Array<{ name: string; url: string; description: string }>;
};
const result = await client.get<FindAllResult>(
  `/v1beta/findall/runs/${run.findall_id}/result`
);

for (const candidate of result.candidates) {
  console.log(`${candidate.name}: ${candidate.url}`);
  console.log(`  ${candidate.description}`);
}
```

### Web Monitoring — Monitor API via `client.post`

Monitor is alpha; no typed resource yet. Use `client.post` with a response type generic:

```ts
import Parallel from "parallel-web";

const client = new Parallel();

// Write queries in natural language focused on intent, not keywords.
// Cadence: "hourly" (fast-moving), "daily" (most news), "weekly" (slow-changing).
// Don't include dates — Monitor tracks new updates automatically.
// Tip: simulate_event=true forces an immediate test event during dev.
type MonitorResponse = { monitor_id: string; status: string; cadence: string };
const monitor = await client.post<MonitorResponse>("/v1alpha/monitors", {
  body: {
    query: "<e.g. 'latest news about AI regulation'>",
    cadence: "daily",
    webhook: {
      url: "https://your-app.com/webhook",
      event_types: ["monitor.event.detected"],
    },
  },
});

console.log("Monitor created:", monitor.monitor_id, "status:", monitor.status);
```

### Content extraction — `client.extract`

```ts
import Parallel from "parallel-web";

const client = new Parallel();

// Best practices: always provide objective; up to 20 URLs per call;
// full_content=true only when you need the whole page as markdown;
// fetch_policy.max_age_seconds for freshness control.
const extract = await client.extract({
  urls: ["https://example.com/article"],
  objective: "<what to focus on in the page>",
  excerpt_settings: { max_chars_per_result: 5000 },
  // fetch_policy: { max_age_seconds: 3600 }, // uncomment for fresh content
});

for (const result of extract.results) {
  console.log(`${result.title}: ${result.url}`);
  for (const excerpt of result.excerpts) {
    console.log(excerpt.slice(0, 200));
  }
}
```

## Error handling

The SDK throws `Parallel.APIError` subclasses (`BadRequestError`, `AuthenticationError`, `RateLimitError`, `InternalServerError`, …). Catch and inspect `err.status` for retry logic.

```ts
import Parallel from "parallel-web";
try {
  await client.search({ /* ... */ });
} catch (err) {
  if (err instanceof Parallel.RateLimitError) {
    // back off and retry
  } else if (err instanceof Parallel.APIError) {
    console.error(err.status, err.message);
  } else {
    throw err;
  }
}
```
