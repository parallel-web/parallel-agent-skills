---
name: parallel-memory
description: "Recall past Parallel Task, Monitor, and FindAll runs when they may help; evict runs or clear memory when asked."
user-invocable: true
argument-hint: <retrieve|evict|clear> [args]
compatibility: Requires parallel-cli >=0.8.1 and internet access.
allowed-tools: Bash(parallel-cli:*)
metadata:
  author: parallel
---

# Parallel Memory

Action: $ARGUMENTS

> Requires `parallel-cli >=0.8.1`. If the installed version is older, or `parallel-cli memory --help` fails with `no such command` or similar, tell the user to update `parallel-cli`, then retry.

## When to use

- Inspect memory only when prior Parallel work may help fulfill the request or the user asks to retrieve, evict, or clear it.
- Memory results are excerpts from past runs; fetch the source run for full records, and launch a fresh run when current information is required.

## Choose the operation

| User intent | Operation |
|---|---|
| Recall prior work about a topic | Retrieve with a concise query |
| Show recent past runs | Retrieve without `query` |
| Remove one saved Task, Monitor, or FindAll source | Evict by exact `kind` and `id` |
| Permanently remove all entries from your personal Memory | Clear memory |
| Turn memory off | Direct the user to account settings; do not clear as a substitute |

## Use the CLI

Use `parallel-cli memory` for retrieve, evict, and clear operations.

- If memory is not eligible, report the returned reason; it distinguishes rollout, organization settings, account opt-in, and key eligibility.
- On a key-eligibility error, tell the user to reauthenticate.

## Retrieve memory

Form a short semantic query that describes the prior work to find. Apply filters when they help. Empty `results` is a successful retrieval with no matches, not an error.

- Set `kind` to `task`, `monitor`, or `findall` when it clearly narrows the retrieval.
- Set `since` for an explicit timestamp boundary (RFC 3339, e.g. `2026-08-01T00:00:00Z`).
- Omit `query` when retrieving recent memories rather than a topic.

Retrieve by query:

```bash
parallel-cli memory retrieve \
  --query "serverless inference vendors"
```

For recent memories:

```bash
parallel-cli memory retrieve \
  --limit 5
```

## Use results

Available fields vary by `kind`:

- `task`: use `id`, `updated_at`, `input_excerpt`, and `output_excerpt`.
- `monitor`: use the monitor `id`, status, query excerpt, and matching event IDs, timestamps, and excerpts.
- `findall`: use `id`, `updated_at`, objective excerpt, and `matched_count`.

- Fetch the original Task result, Monitor events, or FindAll result when exact output, entities, citations, or provenance matter.
- Summarize the useful findings and unresolved questions.
- Lead with what the prior work established, then list the contributing saved runs with kind, ID, and timestamp.
- Distinguish recalled information from any fresh verification.
- Parallel runs do not consult Memory. If recalled information may be useful, include the relevant details in the new run's input.

Expect ingestion to be asynchronous. Do not promise that a newly completed run will be immediately retrievable.

## Evict or clear memory

Evict a single run from your personal Memory, or clear it entirely. These do not delete the underlying Parallel runs. Ask for confirmation before clearing unless the user already asked for it.

```bash
parallel-cli memory evict \
  --kind task \
  --id "trun_example"
```

```bash
parallel-cli memory clear \
  --confirm-clear
```
