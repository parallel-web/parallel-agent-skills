# Parallel Agent Skills

[Agent Skills](https://agentskills.io/specification) for [Parallel](https://parallel.ai): web search, content extraction, deep research, data enrichment, and domain workflows for AI coding agents.

## Prerequisites

Most execution skills require `parallel-cli` (installed, authenticated, and funded). The [`parallel-cli-setup`](skills/parallel-cli-setup/SKILL.md) skill walks an agent through installation, authentication, balance checks, and skill installation. Install the plugin or skills below, then run `/parallel:parallel-cli-setup` from your agent.

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

- [skills.parallel.ai](https://skills.parallel.ai): human-friendly catalog and install instructions
- [skills.parallel.ai/index.json](https://skills.parallel.ai/index.json): machine-readable skill index
- `https://skills.parallel.ai/<skill>/SKILL.md`: live raw skill file
- `https://skills.parallel.ai/<skill>/manifest.json`: file manifest and checksums
- `https://skills.parallel.ai/<skill>/versions.json`: release history for that skill
- `https://skills.parallel.ai/archives/<skill>/<version>.zip`: immutable GitHub Release archive via CDN redirect

## Core skills

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
| **parallel-task-mcp-setup**  | Install, authenticate, and verify Parallel Task MCP       |
| **status**                   | Check running research task status                        |
| **result**                   | Get completed research task result                        |

## Domain workflow skills

Each domain includes a setup router and focused skills for its common workflows.

| Domain | Skills |
| ------ | ------ |
| **Code** | [`parallel-code-setup`](skills/parallel-code-setup/SKILL.md), [`parallel-code-quickstart`](skills/parallel-code-quickstart/SKILL.md), [`parallel-current-scaffolding`](skills/parallel-current-scaffolding/SKILL.md), [`parallel-dependency-monitoring`](skills/parallel-dependency-monitoring/SKILL.md), [`parallel-doc-grounded-review`](skills/parallel-doc-grounded-review/SKILL.md), [`parallel-platform-web-access`](skills/parallel-platform-web-access/SKILL.md), [`parallel-tech-deep-research`](skills/parallel-tech-deep-research/SKILL.md) |
| **Finance** | [`parallel-finance-setup`](skills/parallel-finance-setup/SKILL.md), [`parallel-company-profiles`](skills/parallel-company-profiles/SKILL.md), [`parallel-finance-quickstart`](skills/parallel-finance-quickstart/SKILL.md), [`parallel-kyb-kyc`](skills/parallel-kyb-kyc/SKILL.md), [`parallel-portfolio-monitoring`](skills/parallel-portfolio-monitoring/SKILL.md), [`parallel-target-discovery`](skills/parallel-target-discovery/SKILL.md), [`parallel-thesis-research`](skills/parallel-thesis-research/SKILL.md) |
| **GTM** | [`parallel-gtm-setup`](skills/parallel-gtm-setup/SKILL.md), [`parallel-account-briefs`](skills/parallel-account-briefs/SKILL.md), [`parallel-account-enrichment`](skills/parallel-account-enrichment/SKILL.md), [`parallel-gtm-quickstart`](skills/parallel-gtm-quickstart/SKILL.md), [`parallel-lead-discovery`](skills/parallel-lead-discovery/SKILL.md), [`parallel-org-chart`](skills/parallel-org-chart/SKILL.md), [`parallel-signal-monitoring`](skills/parallel-signal-monitoring/SKILL.md) |
| **Insurance** | [`parallel-insurance-setup`](skills/parallel-insurance-setup/SKILL.md), [`parallel-book-risk-monitoring`](skills/parallel-book-risk-monitoring/SKILL.md), [`parallel-claims-research`](skills/parallel-claims-research/SKILL.md), [`parallel-emerging-risk-research`](skills/parallel-emerging-risk-research/SKILL.md), [`parallel-insurance-kyb-kyc`](skills/parallel-insurance-kyb-kyc/SKILL.md), [`parallel-insurance-quickstart`](skills/parallel-insurance-quickstart/SKILL.md), [`parallel-underwriting-risk-profiles`](skills/parallel-underwriting-risk-profiles/SKILL.md) |
| **Legal** | [`parallel-legal-setup`](skills/parallel-legal-setup/SKILL.md), [`parallel-diligence-briefs`](skills/parallel-diligence-briefs/SKILL.md), [`parallel-entity-diligence`](skills/parallel-entity-diligence/SKILL.md), [`parallel-exposure-discovery`](skills/parallel-exposure-discovery/SKILL.md), [`parallel-legal-quickstart`](skills/parallel-legal-quickstart/SKILL.md), [`parallel-regulatory-monitoring`](skills/parallel-regulatory-monitoring/SKILL.md), [`parallel-source-grounded-research`](skills/parallel-source-grounded-research/SKILL.md) |
| **Life sciences** | [`parallel-life-sciences-setup`](skills/parallel-life-sciences-setup/SKILL.md), [`parallel-competitive-landscape`](skills/parallel-competitive-landscape/SKILL.md), [`parallel-landscape-deep-research`](skills/parallel-landscape-deep-research/SKILL.md), [`parallel-licensing-discovery`](skills/parallel-licensing-discovery/SKILL.md), [`parallel-life-sciences-quickstart`](skills/parallel-life-sciences-quickstart/SKILL.md), [`parallel-literature-mining`](skills/parallel-literature-mining/SKILL.md), [`parallel-pipeline-monitoring`](skills/parallel-pipeline-monitoring/SKILL.md) |
| **Productivity** | [`parallel-productivity-setup`](skills/parallel-productivity-setup/SKILL.md), [`parallel-entity-context`](skills/parallel-entity-context/SKILL.md), [`parallel-in-product-research`](skills/parallel-in-product-research/SKILL.md), [`parallel-knowledge-freshness`](skills/parallel-knowledge-freshness/SKILL.md), [`parallel-productivity-quickstart`](skills/parallel-productivity-quickstart/SKILL.md), [`parallel-workspace-agent`](skills/parallel-workspace-agent/SKILL.md) |

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
