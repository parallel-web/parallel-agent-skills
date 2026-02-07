# Parallel Agent Skills

[Agent Skills](https://agentskills.io/specification) for [Parallel](https://parallel.ai) — web search, content extraction, deep research, and data enrichment for AI coding agents.

## Prerequisites

1. **Install the CLI**

   ```bash
   curl -fsSL https://parallel.ai/install.sh | bash
   ```

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

Use the [Vercel Skills CLI](https://github.com/vercel-labs/skills) to install skills into Cursor, Cline, GitHub Copilot, and 30+ other agents.

```bash
# Install all skills globally (available in all projects)
npx skills add parallel-web/parallel-agent-skills --all --global

# Or install to current project only
npx skills add parallel-web/parallel-agent-skills --all

# Install a specific skill
npx skills add parallel-web/parallel-agent-skills --skill parallel-web-search

# Preview available skills
npx skills add parallel-web/parallel-agent-skills --list
```

### Claude Code

Available as a [Claude Code Plugin Marketplace](https://code.claude.com/docs/en/discover-plugins).

```bash
/plugin marketplace add parallel-web/parallel-agent-skills
/plugin install parallel
# restart Claude Code before continuing!

# this will install the CLI and authenticate if not done already
/parallel:setup
```

## Skills

Skills follow the [Agent Skills](https://agentskills.io/specification) specification.

- **parallel-web-search**: Current events, fact-checking, web search
- **parallel-web-extract**: Extract content from URLs, articles, PDFs
- **parallel-deep-research**: Comprehensive research and analysis
- **parallel-data-enrichment**: Enrich lists of companies, people, products

## Commands

Claude Code slash commands:

| Command | Description |
|---------|-------------|
| `/parallel:setup` | Install CLI and authenticate |
| `/parallel:search <query>` | Search the web |
| `/parallel:extract <url>` | Extract content from URL |
| `/parallel:research <topic>` | Deep research on a topic |
| `/parallel:enrich <data>` | Enrich data with web intelligence |
| `/parallel:status <run_id>` | Check task status |
| `/parallel:result <run_id>` | Get task results |

## Examples

```
/parallel:search latest React 19 features
/parallel:extract https://docs.parallel.ai
/parallel:research competitive landscape of AI code assistants
/parallel:enrich Apple, Microsoft, Google - get CEO names
```

## Resources

- [Documentation](https://docs.parallel.ai/home)
- [API Platform](https://platform.parallel.ai)
- [parallel-cli](https://github.com/parallel-web/parallel-web-tools)
- [Pricing](https://parallel.ai/pricing)

## Local Development

```bash
git clone https://github.com/parallel-web/parallel-agent-skills.git
claude --plugin-dir /path/to/parallel-agent-skills
/parallel:setup
```

## Releasing a New Version

Claude Code plugins are pinned to commit SHAs, and `npx skills add` pulls the latest from `main`.

1. Bump the version in all three locations:
   - `.claude-plugin/plugin.json` → `version`
   - `.claude-plugin/marketplace.json` → `metadata.version`
   - `.claude-plugin/marketplace.json` → `plugins[0].version`
2. Commit and push to `main`

## License

MIT
