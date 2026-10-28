# Parallel Agent Skills

Web search and page fetching for AI coding agents, through [Parallel](https://parallel.ai) — plus [Agent Skills](https://agentskills.io/specification) for deep research, data enrichment, entity discovery, and web monitoring.

The plugin ships two things:

- **A hosted MCP server** (`parallel-search`). In Claude, it provides `web_search`, `web_fetch`, `web_research`, and `web_decisions` after signing in to Parallel. Usage is billed to your Parallel account. The Codex and Antigravity packages retain anonymous, rate-limited search and fetch.
- **CLI-backed skills** for deep research, enrichment, FindAll, and Monitor. These run through `parallel-cli` and need it installed, authenticated, and funded.

You can use the first without ever setting up the second.

## Prerequisites

For the Claude MCP tools, you need a Parallel account with sufficient balance. Sign in through Claude; no API key or local CLI is needed. Codex and Antigravity retain anonymous search and fetch with no account required.

The execution skills require `parallel-cli` (installed, authenticated, and funded). The [`parallel-cli-setup`](skills/parallel-cli-setup/SKILL.md) skill walks an agent through install, auth, balance, and skills install end-to-end — install the plugin/skills below, then run `/parallel:parallel-cli-setup` from your agent.

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
```

After restarting, open `/mcp`, select the plugin-provided `parallel-search`
server, and complete the Parallel sign-in flow. Then confirm that search, fetch,
research, and decisions are available. MCP usage is billed to your Parallel
account at [Parallel pricing](https://parallel.ai/pricing).

Upgrading from v0.10.0 changes the plugin endpoint from anonymous Search MCP to
the authenticated unified MCP. Update the plugin, fully exit Claude Code, and
start a fresh session. Complete sign-in from `/mcp` when requested. An old
Search MCP login may not carry over to the new endpoint. Existing conversations
can retain old tool arguments after `/reload-plugins`; if a call rejects
`model_name` or `session_id`, start a fresh session instead of resuming the old
one. If you previously added a separate
Parallel connection, verify the new one works before disabling the duplicate.
Do not restore the anonymous URL to bypass sign-in.

For the CLI-backed skills (deep research, enrichment, FindAll, Monitor), install
and authenticate the CLI:

```bash
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

### Google Antigravity

Install the standalone Search MCP plugin with the Antigravity CLI:

```bash
git clone https://github.com/parallel-web/parallel-agent-skills.git
cd parallel-agent-skills
agy plugin install ./plugins/antigravity/parallel
```

This package provides free web search and page fetching without a Parallel account,
API key, or local Parallel CLI. Use the package directory above so Antigravity
loads only the Search MCP connection. See the [Antigravity package README](plugins/antigravity/parallel/README.md)
for project-local installation, validation, example prompts, and removal.

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
| **parallel-search-setup**    | Verify, authenticate, and troubleshoot the bundled Parallel MCP server     |
| **parallel-mcp-setup** | Set up authenticated Parallel MCP connections; Bifrost Search MCP is the first supported path |
| **parallel-web-search**      | CLI-backed search for explicit CLI use or when MCP is unavailable |
| **parallel-web-extract**     | CLI-backed extraction for explicit CLI use or when MCP is unavailable |
| **choose-your-parallel-api** | Choose the right Parallel API and configuration           |
| **parallel-search-evaluation** | Benchmark web search providers on your own workload. |
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
/parallel:parallel-search-evaluation compare search providers on production questions
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

## Accounts, billing, and free access

### Claude

The Claude plugin uses OAuth at
`https://mcp.parallel.ai/mcp?login&tools=web_search,web_fetch,web_research,web_decisions`.
A Parallel account is required and authenticated tool calls are billed under
your account's [pricing and limits](https://parallel.ai/pricing). Manage balance
and usage at [platform.parallel.ai](https://platform.parallel.ai).

MCP research returns a cited answer. The existing deep-research skill continues
to run asynchronous Task API reports through the CLI; it is a separate workflow.

### Codex and other anonymous Search MCP installations

The bundled `parallel-search` MCP server is anonymous by design: `web_search` and
`web_fetch` work with no account, API key, or login, subject to free-tier rate
limits. The free tier is intended for personal agents, hobby projects, and
exploration.

For higher search limits, usage analytics, and production workloads, create an
account at [platform.parallel.ai](https://platform.parallel.ai), then add a
separate authenticated Search MCP connection. The same service supports a
Parallel API key on `https://search.parallel.ai/mcp` or OAuth through
`https://search.parallel.ai/mcp-oauth`. Authenticated usage is billed under your
account's pricing and limits — see
[parallel.ai/pricing](https://parallel.ai/pricing).

Keep the plugin-provided connection anonymous rather than editing the installed
plugin. After the authenticated connection works, use `/mcp` to ensure only one
Parallel Search connection is enabled; if both appear, toggle the bundled
anonymous server off. See
[`parallel-search-setup`](skills/parallel-search-setup/SKILL.md) for the upgrade
steps.

The CLI-backed skills are separate: deep research, enrichment, FindAll, and
Monitor run through `parallel-cli` against your own funded Parallel account and
are billed as ordinary API usage.

## Privacy and terms

Parallel hosts the MCP service. Tool arguments sent to Parallel can include
objectives, search queries, requested URLs, research questions, decision inputs,
and optional session and model metadata. Parallel also receives standard
connection and MCP client metadata.
This data is handled under the
[Customer Terms](https://parallel.ai/customer-terms) and
[Privacy Policy](https://parallel.ai/privacy-policy). The MCP server does not
automatically receive the rest of your conversation or local files, but an agent
can include context in tool arguments when it is relevant. Do not send secrets,
credentials, or sensitive local content through MCP tools.

The CLI-backed skills run `parallel-cli` locally using credentials you have
already configured. They send task inputs to Parallel's API under the same terms.

Claude authenticates the bundled MCP connection through OAuth. Codex and
Antigravity retain anonymous MCP connections. No bundled connection forwards
CLI credentials. CLI-backed skills authenticate separately to Parallel through
`parallel-cli`; the setup skill can check authentication status and start the
CLI's sign-in flow.

Migration examples describe authentication for the application being migrated.
Provider credentials shown in scanner tests are synthetic source-code fixtures,
not real keys or live requests. Neither those examples nor the test fixtures run
automatically when the plugin loads.

## Support and security

- **Questions and bugs:** [open an issue](https://github.com/parallel-web/parallel-agent-skills/issues) with your client, version, and error message (leave out API keys and other credentials), or see the [documentation](https://docs.parallel.ai/home).
- **Product support:** contact Parallel at [support@parallel.ai](mailto:support@parallel.ai).
- **Security concerns:** report privately to [support@parallel.ai](mailto:support@parallel.ai) — see [SECURITY.md](SECURITY.md). Please don't file security reports as public issues.

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
