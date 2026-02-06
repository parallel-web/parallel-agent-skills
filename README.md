# Parallel Agent Skills

[Agent Skills](https://agentskills.io/specification) for [Parallel Web Tools](https://parallel.ai) - web search, content extraction, deep research, and data enrichment.

## Installation

### Claude Code

```bash
/plugin marketplace add parallel-web/agent-skills
/plugin install parallel
# restart claude before continuing!
/parallel:setup
```

### Other AI Agents

Use the [Vercel Skills CLI](https://github.com/vercel-labs/skills) to install skills into Cursor, Cline, GitHub Copilot, and 30+ other agents.

```bash
# Preview available skills
npx skills add parallel-web/agent-skills --list

# Install all skills
npx skills add parallel-web/agent-skills --all

# Install a specific skill
npx skills add parallel-web/agent-skills --skill parallel-web-search

# Install globally (available in all projects)
npx skills add parallel-web/agent-skills --all --global
```

## Commands

| Command | Description |
|---------|-------------|
| `/parallel:setup` | Install CLI and authenticate |
| `/parallel:search <query>` | Search the web |
| `/parallel:extract <url>` | Extract content from URL |
| `/parallel:deep-research <topic>` | Deep research on a topic |
| `/parallel:enrich <data>` | Enrich data with web intelligence |
| `/parallel:status <run_id>` | Check task status |
| `/parallel:result <run_id>` | Get task results |

## Skills

Skills follow the [Agent Skills](https://agentskills.io/specification) specification.

- **parallel-web-search**: Current events, fact-checking, web search
- **parallel-web-extract**: Extract content from URLs, articles, PDFs
- **parallel-deep-research**: Comprehensive research and analysis
- **parallel-data-enrichment**: Enrich lists of companies, people, products

## Authentication

```bash
parallel-cli login          # Interactive OAuth
export PARALLEL_API_KEY="key"  # CI/automation
```

## Examples

```bash
/parallel:search latest React 19 features
/parallel:extract https://docs.parallel.ai
/parallel:deep-research competitive landscape of AI code assistants
/parallel:enrich Apple, Microsoft, Google - get CEO names
```

## Resources

- [Documentation](https://docs.parallel.ai/home)
- [API Platform](https://platform.parallel.ai)
- [parallel-cli](https://github.com/parallel-web/parallel-web-tools)
- [Pricing](https://parallel.ai/pricing)

## Local Development

```bash
git clone https://github.com/parallel-web/agent-skills.git
claude --plugin-dir /path/to/agent-skills
/parallel:setup
```

## Releasing a New Version

Claude Code plugins are pinned to commit SHAs, and `npx skills add` pulls the latest from `main`. Version numbers are for display only.

1. Bump the version in all three locations:
   - `.claude-plugin/plugin.json` → `version`
   - `.claude-plugin/marketplace.json` → `metadata.version`
   - `.claude-plugin/marketplace.json` → `plugins[0].version`
2. Commit and push to `main`

## License

MIT
