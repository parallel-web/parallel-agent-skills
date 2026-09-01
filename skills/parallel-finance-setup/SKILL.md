---
name: parallel-finance-setup
description: Connect a user's Parallel account and route finance workflows to the matching skill. Use this first, or when the user says "set up Parallel", "get me started", or isn't sure which use case they need.
allowed-tools: Bash(command:*), Bash(claude:*), Bash(parallel-cli:*), Bash(script:*), Bash(git:*)
metadata:
  author: parallel
---

# Finance Setup

Get connected once, then get pointed to the right use case. Everything runs on the user's
own Parallel account, no key is pasted.

## 1. Ask what they want to do first (route before installing)

Don't install or run anything yet. Ask one orienting question and route to the matching
skill, so the first thing they do is the thing they came for:

> **What do you want to do first?**
> - **Get up to speed on one company fast** → `parallel-finance-quickstart`
> - **Build cited tear sheets on a name or a list** → `parallel-company-profiles`
> - **Find targets matching your criteria** → `parallel-target-discovery`
> - **Get alerted when a position or target moves** → `parallel-portfolio-monitoring`
> - **Commission a research report on a thesis** → `parallel-thesis-research`
> - **Run KYB / KYC on a company or counterparty** → `parallel-kyb-kyc`

If they're unsure, start with `parallel-finance-quickstart`, it's the fastest to value.

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

## 3. Capture the finance profile once

So the user doesn't re-enter their context on every run, capture who *they* are here, once:

1. Ask: **what firm are you at, and what's your mandate?** (domain + firm type).
2. Research the firm on Parallel (a quick lookup) and infer the firm type, mandate (sectors,
   geographies, check size or EBITDA range), and screening criteria. **Show the user what you
   found and let them correct it, never assume**, a wrong guess on the first run is the thing
   that loses trust.
3. Write the confirmed result to `PROFILE.md` in the current workspace, using the shape in
   [references/PROFILE.example.md](references/PROFILE.example.md). `PROFILE.md` is gitignored, so their details stay local.

Every use-case skill reads `PROFILE.md` and uses that firm / mandate / screening framing, so
from here the user only supplies the per-run target (which company, list, or thesis), not
their whole context each time. This is optional, skip it and each skill will just ask per-run.

## 4. Hand off to the chosen use case

Open that use case's `SKILL.md` and follow its guided intake (each one asks 1-3 questions and
confirms before anything billable runs). The use-case skills carry the build logic; this
setup just gets you connected and cloned.
