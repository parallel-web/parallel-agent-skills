# Parallel Agent Skills

[Agent Skills](https://agentskills.io/specification) for [Parallel](https://parallel.ai) — web search, content extraction, deep research, and data enrichment for AI coding agents.

## Prerequisites

1. **Install the CLI**

   ```bash
   pipx install "parallel-web-tools[cli]"
   pipx ensurepath
   ```

   For other install methods, see [docs.parallel.ai/integrations/cli](https://docs.parallel.ai/integrations/cli).

2. **Get an API key** at [parallel.ai](https://parallel.ai) and set it as an environment variable:

   ```bash
   export PARALLEL_API_KEY="your-key"
   ```

   Or authenticate interactively after installing the CLI:

   ```bash
   parallel-cli login
   ```

3. **Install the skills** into your AI agent (see below).

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

```
$skill-installer parallel-web/parallel-agent-skills
```

Then install the CLI and authenticate:

```bash
pipx install "parallel-web-tools[cli]"
pipx ensurepath
parallel-cli login
```

For other install methods, see [docs.parallel.ai/integrations/cli](https://docs.parallel.ai/integrations/cli).

## Skills

Skills follow the [Agent Skills](https://agentskills.io/specification) specification and double as Claude Code slash commands.

| Skill | Description |
|-------|-------------|
| **parallel-web-search** | Web search (default for most research queries) |
| **parallel-web-extract** | Extract content from URLs, articles, PDFs |
| **parallel-deep-research** | Comprehensive research and analysis |
| **parallel-data-enrichment** | Enrich lists of companies, people, products |
| **parallel-findall** | Discover entities matching a natural-language description |
| **parallel-monitor** | Continuously track the web for changes (with webhooks) |
| **parallel-cli-setup** | Install/update CLI, authenticate, and handle balance |
| **status** | Check running research task status |
| **result** | Get completed research task result |

## Examples

```
/parallel:parallel-web-search latest React 19 features
/parallel:parallel-web-extract https://docs.parallel.ai
/parallel:parallel-deep-research competitive landscape of AI code assistants
/parallel:parallel-data-enrichment Apple, Microsoft, Google - get CEO names
/parallel:parallel-findall AI startups that raised Series A in 2026
/parallel:parallel-monitor track price changes for the iPhone 16 Pro
/parallel:parallel-cli-setup
```

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

## Releasing a New Version

Claude Code plugins are pinned to commit SHAs, and `npx skills add` pulls the latest from `main`.

1. Bump the version in all four locations:
   - `.claude-plugin/plugin.json` → `version`
   - `.claude-plugin/marketplace.json` → `metadata.version`
   - `.claude-plugin/marketplace.json` → `plugins[0].version`
   - `.codex-plugin/plugin.json` → `version`
2. Commit and push to `main`

## License

MIT
