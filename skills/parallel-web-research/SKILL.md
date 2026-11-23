---
name: parallel-web-research
description: "Cited research answers through the Parallel MCP web_research tool. Only works when the Parallel MCP connection is signed in. Use when the user asks to research a question and wants a sourced answer in the same turn. For exhaustive multi-minute reports use parallel-deep-research; for quick lookups use web_search."
user-invocable: true
argument-hint: <question>
compatibility: Requires a signed-in Parallel MCP connection (OAuth or API key) that lists web_research.
metadata:
  author: parallel
---

# Web Research

Research question: $ARGUMENTS

## Sign-in is required

`web_research` only works when the Parallel MCP connection is signed in, with OAuth or an API key. An anonymous connection either does not list the tool or answers the call with a sign-in error. Signed-in calls are billed to the user's Parallel account at [Parallel API rates](https://parallel.ai/pricing).

Check the connection before promising research:

- **`web_research` is listed and the call succeeds:** continue below.
- **The client prompts for sign-in:** let the user finish it, then retry once the client confirms it succeeded.
- **The tool is missing, or the call returns a sign-in error with no prompt:** tell the user that Research needs sign-in, and follow `parallel-search-setup`. Never ask the user to paste credentials into chat.
- **The user declines to sign in:** stop. Offer `web_search` and `web_fetch`, which work without an account, and say that the answer comes from search and not from Research.

## Run the research

Call `web_research` with the question in `input`. Use the tool's advertised schema; this section covers how to use it well.

- Ask one focused question per call. Split unrelated questions into separate calls.
- Leave `reasoning_effort` out unless the user asks for a faster answer (`low`) or a deeper one (`high`). The default picks the effort for each question.
- The call returns when the answer is ready. There is no run to poll and no result to fetch.
- For a follow-up on the same research, pass the earlier result's `id` as `previous_response_id`. The follow-up inherits the earlier question and answer. Follow-ups are not available to organizations with Zero Data Retention.

## Present the answer

- Lead with the answer, then the supporting findings.
- Keep the citations the tool returned, as inline markdown links. Never invent or guess a URL.
- End with a Sources section that lists every URL you cited.
- On an error or an empty answer, report what happened. Do not fill the gap from memory.

## When to use something else

| Need | Use |
| --- | --- |
| A quick fact or a list of pages | `web_search` |
| The content of a specific URL | `web_fetch` |
| A probability, a pick among options, or a score | `web_decisions` |
| An exhaustive report that can take several minutes | `parallel-deep-research`, which runs through `parallel-cli` and needs its own authentication |
