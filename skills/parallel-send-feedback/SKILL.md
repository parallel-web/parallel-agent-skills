---
name: parallel-send-feedback
description: "Report a problem with Parallel to the Parallel team through the Parallel MCP send_feedback tool. Use when a Parallel tool failed, rate-limited you unexpectedly, contradicted its docs, or returned empty, wrong, or stale results. Always ask the user before sending. Only available on connections that list send_feedback."
user-invocable: true
argument-hint: <what went wrong>
compatibility: Requires a Parallel MCP connection that lists send_feedback.
metadata:
  author: parallel
---

# Send Feedback

Problem to report: $ARGUMENTS

## Availability

`send_feedback` is listed only on connections Parallel has enabled it for. It can be listed with or without sign-in. If the tool is not listed, it is not available on this connection: tell the user, and point them to <support@parallel.ai>. Do not look for another way to send it.

## When to report

Report a problem you saw while working with Parallel:

- A Parallel tool returned an error you did not cause: a server error, a timeout, or a rate limit you did not expect.
- Results were wrong, irrelevant, stale, or missing something you know exists.
- Parallel's docs, tool descriptions, and behavior disagree, or you could not work out how to call a tool.
- An evaluation or comparison you ran shows Parallel doing worse than expected.

Problems you worked around count too. Do not report a mistake in your own request, and do not use it to ask a question.

## Ask first

1. Tell the user what went wrong.
2. Offer to report it, and show exactly what you would send: the message and the IDs.
3. Send only if the user agrees. Then tell them it was sent.

Never send feedback the user has not seen and approved.

## What to send

Use the tool's advertised schema. In short:

- Describe the problem in `message`: what you asked for, what you expected, and what came back.
- Put the IDs involved in `examples`, each with a short note: `search_id`, `extract_id`, or `run_id`.
- `web_decisions` returns no ID. Put its subject and the questions it answered wrongly in `message`.

Parallel receives only the fields you fill in, plus the account and client the request came from. Leave out secrets and personal data.
