---
name: parallel-life-sciences-setup
description: Connect a user's Parallel account and route life sciences workflows to the matching skill. Use this first, or when the user says "set up Parallel", "get me started", or isn't sure which use case they need.
allowed-tools: Bash(command:*), Bash(claude:*), Bash(parallel-cli:*), Bash(script:*), Bash(git:*)
metadata:
  author: parallel
---

# Life Sciences Setup

Get connected once, then get pointed to the right use case. Everything runs on the user's own
Parallel account, no key is pasted.

## 1. Ask what they want to do first (route before installing)

Don't install or run anything yet. Ask one orienting question and route to the matching skill,
so the first thing they do is the thing they came for:

> **What do you want to do first?**
> - **Get up to speed on one drug, target, or company** → `parallel-life-sciences-quickstart`
> - **Map a therapeutic area or mechanism's competitive landscape** → `parallel-competitive-landscape`
> - **Find licensing / M&A targets by criteria** → `parallel-licensing-discovery`
> - **Get alerted on readouts, phase transitions, and approvals** → `parallel-pipeline-monitoring`
> - **Pull structured data out of papers, registries, and filings** → `parallel-literature-mining`
> - **Commission a research report on an area or thesis** → `parallel-landscape-deep-research`

If they're unsure, start with `parallel-life-sciences-quickstart`, it's the fastest to value.

## 2. Pick the surface and connect (once)

**Non-technical (co-work / chat): just want output:**
Connect the Task MCP and run the use case in chat. See the `parallel-task-mcp-setup` skill.

**Technical (build on top):**
Run the `parallel-cli-setup` skill to install and authenticate the CLI. Clone the repository only when the user wants to work from the source:

```bash
git clone https://github.com/parallel-web/parallel-agent-skills
```

> If a call returns `401 Invalid API key`, a stale `PARALLEL_API_KEY` in your shell is
> overriding the login, run `unset PARALLEL_API_KEY` and retry.

## 3. Capture the life sciences profile once

So the user doesn't re-enter their context on every run, capture what *they* work on here, once:

1. Ask: **what's your organization, and what areas do you focus on?** (domain + org type).
2. Research the organization on Parallel (a quick lookup) and infer the org type, therapeutic
   areas, modalities, and what they track. **Show the user what you found and let them correct
   it, never assume**, a wrong guess on the first run is the thing that loses trust.
3. Write the confirmed result to `PROFILE.md` in the current workspace,
   using the shape in [references/PROFILE.example.md](references/PROFILE.example.md). `PROFILE.md` is gitignored, so their details
   stay local.

Every use-case skill reads `PROFILE.md` and uses that therapeutic-area and tracking framing, so
from here the user only supplies the per-run target (which drug, area, or thesis), not their
whole context each time. This is optional, skip it and each skill will just ask per-run.

## 4. Hand off to the chosen use case

Open that use case's `SKILL.md` and follow its guided intake (each one asks 1-3 questions and
confirms before anything billable runs). The use-case skills carry the build logic; this setup connects your account and chooses the next skill.
