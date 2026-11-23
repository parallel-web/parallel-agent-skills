---
name: parallel-web-decisions
description: "Evidence-backed probabilities, choices, and scores through the Parallel MCP web_decisions tool. Use when the user asks for Parallel Decisions by name, how likely something is, a pick among options they give, or a score on a scale they give. Works without sign-in at anonymous limits; signed-in calls are billed. For ordinary questions use web_search."
user-invocable: true
argument-hint: <subject and question>
compatibility: Requires a Parallel MCP connection that lists web_decisions.
metadata:
  author: parallel
---

# Web Decisions

Decide: $ARGUMENTS

## Sign-in

`web_decisions` works without a Parallel account, subject to anonymous usage limits. When the connection is signed in, calls are billed to the user's Parallel account at [Parallel API rates](https://parallel.ai/pricing) and get higher limits.

If the tool is missing, the connection does not serve it. Follow `parallel-search-setup` to check which Parallel MCP URL the client uses. If a call hits a rate limit, say so and offer sign-in for higher limits. Do not retry in a loop.

## When to use it

Call `web_decisions` only when the user asks for it by name, or asks for one of these:

- **A probability:** "How likely is it that …?"
- **A pick among options the user gives:** "Is this vendor a startup, a mid-size company, or an enterprise?"
- **A score on a scale the user gives:** "Rate this company's security posture from 1 to 5."

For every other question, including yes-or-no facts, lookups, and research, use `web_search`. If Decisions looks like a better fit and the user did not ask for it, suggest it and let the user choose.

## Build the call

Use the tool's advertised schema. In short:

- Describe the subject in `state` as JSON, for example `{"company": "Acme", "website": "https://acme.example"}`.
- Put each question in `questions` under a name you choose. Names use only ASCII letters, numbers, underscores, and hyphens. The answer comes back under the same name.
- Give each question a `type`, `instructions`, and the `criteria` its type needs.

| Type | Use it for | Answer |
| --- | --- | --- |
| `noul` | A statement that can be true or false | A probability from 0 to 1 |
| `choice` | One option from 2 to 255 named options | The chosen option and a probability for each option |
| `score` | A rating on 2 to 10 ordered levels, lowest first | A probability-weighted score |

One search grounds every question in a call, so group only related questions about one subject. Use a separate call for each subject.

Leave citation excerpts off unless the user wants to read the evidence. They can add more than 15,000 characters to a response.

## Present the answer

- Report each answer with its number: the probability, the choice with its probability, or the score.
- Call them estimates from current web evidence, not facts.
- Cite the sources the call returned. Never invent a URL.
- A question can come back as a refusal. Report it as unanswered and do not guess.
