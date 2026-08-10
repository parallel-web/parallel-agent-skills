# Parallel Agent Skills

[Agent Skills](https://agentskills.io/specification) for [Parallel](https://parallel.ai) — web search, content extraction, deep research, and data enrichment for AI coding agents.

## Prerequisites

Most execution skills require `parallel-cli` (installed, authenticated, and funded). The [`parallel-cli-setup`](skills/parallel-cli-setup/SKILL.md) skill walks an agent through install, auth, balance, and skills install end-to-end — install the plugin/skills below, then run `/parallel:parallel-cli-setup` from your agent.

`migrate-to-parallel` updates an application's own web-data integration. It uses the appropriate Parallel API or SDK and needs `PARALLEL_API_KEY` only for an explicitly authorized live smoke test.

## Installation

### Agent Skills

Use `parallel-cli` to install skills into Cursor, Cline, GitHub Copilot, and other compatible agents.

```bash
# Install all Parallel skills
parallel-cli skills install
```

### Claude Code

Available as a [Claude Code Plugin Marketplace](https://code.claude.com/docs/en/discover-plugins).

```bash
/plugin marketplace add parallel-web/parallel-agent-skills
/plugin install parallel
# restart Claude Code before continuing!

# this will install/update CLI and authenticate if not done already
/parallel:parallel-cli-setup
```

### OpenAI Codex

Install skills using the built-in skill installer (run inside Codex):

```text
$skill-installer parallel-web/parallel-agent-skills
```

Then run the setup skill to install/auth the CLI:

```text
/parallel:parallel-cli-setup
```

## CDN and discovery

A human + machine-readable catalog is published at [skills.parallel.ai](https://skills.parallel.ai).

Useful endpoints:

- [skills.parallel.ai](https://skills.parallel.ai) — human-friendly catalog and install instructions
- [skills.parallel.ai/index.json](https://skills.parallel.ai/index.json) — machine-readable skill index
- `https://skills.parallel.ai/<skill>/SKILL.md` — live raw skill file
- `https://skills.parallel.ai/<skill>/manifest.json` — file manifest + checksums
- `https://skills.parallel.ai/<skill>/versions.json` — release history for that skill
- `https://skills.parallel.ai/archives/<skill>/<version>.zip` — immutable GitHub Release archive via CDN redirect

## Skills

Skills follow the [Agent Skills](https://agentskills.io/specification) specification and double as Claude Code slash commands.

| Skill                        | Description                                               |
| ---------------------------- | --------------------------------------------------------- |
| **parallel-web-search**      | Web search (default for most research queries)            |
| **parallel-web-extract**     | Extract content from URLs, articles, PDFs                 |
| **parallel-deep-research**   | Comprehensive research and analysis                       |
| **parallel-data-enrichment** | Enrich lists of companies, people, products               |
| **parallel-findall**         | Discover entities matching a natural-language description |
| **parallel-monitor**         | Continuously track the web for changes (with webhooks)    |
| **parallel-memory**          | Recall and manage saved Parallel runs                     |
| **migrate-to-parallel**      | Migrate Exa, Tavily, Perplexity, or Firecrawl integrations to Parallel |
| **parallel-cli-setup**       | Install/update CLI, authenticate, and handle balance      |
| **status**                   | Check running research task status                        |
| **result**                   | Get completed research task result                        |

## Examples

```text
/parallel:parallel-web-search latest React 19 features
/parallel:parallel-web-extract https://docs.parallel.ai
/parallel:parallel-deep-research competitive landscape of AI code assistants
/parallel:parallel-data-enrichment Apple, Microsoft, Google - get CEO names
/parallel:parallel-findall AI startups that raised Series A in 2026
/parallel:parallel-monitor track price changes for the iPhone 16 Pro
/parallel:parallel-memory retrieve past research about AI code assistants
/parallel:migrate-to-parallel migrate this app from Tavily to Parallel
/parallel:migrate-to-parallel migrate this app from Perplexity to Parallel
/parallel:migrate-to-parallel migrate this app from Firecrawl to Parallel
/parallel:parallel-cli-setup
```

## Contributing

See [MAINTAINERS.md](MAINTAINERS.md) for maintainer workflows, release process, and dev setup.

## Resources

- [Documentation](https://docs.parallel.ai/home)
- [API Platform](https://platform.parallel.ai)
- [parallel-cli](https://github.com/parallel-web/parallel-web-tools)
- [Pricing](https://parallel.ai/pricing)

## Local Development

**Claude Code:**

```bash
git clone https://github.com/parallel-web/parallel-agent-skills.git
claude --plugin-dir /path/to/parallel-agent-skills
/parallel:parallel-cli-setup
```

**Codex:**

```bash
git clone https://github.com/parallel-web/parallel-agent-skills.git
cd parallel-agent-skills
codex
# Skills are auto-discovered via .agents/skills/
```

## License

MIT
