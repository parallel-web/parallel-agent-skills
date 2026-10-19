# Parallel for Antigravity

Search the live web and fetch page content from your coding agent. This plugin
connects Antigravity to the hosted Parallel Search MCP server and provides
`web_search` and `web_fetch` without a Parallel account, API key, or local CLI.
Anonymous access is subject to free-tier rate limits.

## Install

Download `parallel-antigravity-<version>.zip` from the repository's
[releases](https://github.com/parallel-web/parallel-agent-skills/releases), extract
it, and use the [Antigravity CLI](https://antigravity.google/docs/cli/plugins/):

```bash
agy plugin validate ./parallel --strict
agy plugin install ./parallel
agy plugin list --json
```

The installed plugin is named `parallel`. Its component list should contain one
MCP server and no skills, agents, rules, or hooks. Antigravity may prefix the
server name with `parallel`.

For a project-local installation in the Antigravity app or IDE, copy the extracted
`parallel/` directory to `.agents/plugins/parallel/` in the target project. Keep
`.antigravity-plugin/plugin.json`, `mcp_config.json`, and `assets/antigravity.svg`
in their relative locations. Only the manifest belongs inside
`.antigravity-plugin/`; component and logo paths resolve from the plugin root.
See [Google's plugin documentation](https://antigravity.google/docs/plugins).

### Build from source

```bash
git clone https://github.com/parallel-web/parallel-agent-skills.git
cd parallel-agent-skills
pnpm install --frozen-lockfile
pnpm build:archives --version "$(cat VERSION)" --output release-assets
unzip "release-assets/parallel-antigravity-$(cat VERSION).zip" -d release-assets/unpacked
agy plugin validate ./release-assets/unpacked/parallel --strict
agy plugin install ./release-assets/unpacked/parallel
```

The source manifest is at `.antigravity-plugin/plugin.json` in the repository
root. The archive uses that same manifest and includes only the files needed
for Search MCP. Install the extracted archive to avoid loading this repository's
separate CLI skills and agent.

### Repository URL installation

Direct installation of the repository is not yet verified for Search-only use.
Antigravity CLI 1.4.2 discovers all 14 root skills even when the manifest specifies
an empty or alternate skills directory. Its validator also rejects the existing
Claude agent's `tools` frontmatter. Moving the manifest alone does not isolate
these components. Use the release archive until the publishing client supports
selecting only the Search MCP package files.

If you already enabled Parallel through the MCP store or a manual connection,
keep just one Parallel connection enabled while testing to avoid duplicate tools.
Installing this plugin does not remove or change another connection.

## Try it

Open Parallel's detail page under **Customizations → Installed** to use the three
starter prompts. Each button opens a new conversation with its prompt filled in.
Select your project before sending if the composer shows **No Project**. For the
feature and error prompts, include the feature description or exact error in the
new conversation so the agent has the context it needs.

Return to your own project before opening a new Antigravity conversation. This
source repository also contains separate CLI skills. Confirm the Parallel MCP
connection is available, and try:

- "Use Parallel to find the official Python documentation for asyncio.TaskGroup.
  Include source links."
- "Use Parallel to fetch <https://docs.python.org/3/library/asyncio-task.html> and
  summarize how TaskGroup handles exceptions."

Check the tool activity to confirm that the responses came from `web_search`
and `web_fetch`. Approve the tool calls if Antigravity asks. The plugin does not
require installing or signing in to `parallel-cli`.

## Validate a release

Run the native validator with a current Antigravity CLI, install the package, and
test both prompts above. Verify that the logo and starter prompts display in the
target marketplace build, and that no extra skills or agents are loaded. Record
the client version and results; a successful config check alone does not prove
that the tools work in a conversation.

The repository's existing release process includes
`parallel-antigravity-<version>.zip`. Extract it and install the resulting
`parallel/` directory. Every file needed by the plugin is inside that directory.
The CLI and marketplace release versions can differ, so repeat the installation
and conversation checks on the build used for publication.

For marketplace submission, the repository-root manifest is
`.antigravity-plugin/plugin.json`. The Search-only distributable is the extracted
`parallel/` release directory. Repository URL installation needs the component
isolation issue above resolved before it can replace the archive.
To remove a CLI-installed copy:

```bash
agy plugin uninstall parallel
```

For a project-local copy, remove only the `.agents/plugins/parallel/` directory
you added. Other Parallel MCP connections are managed separately.

## Data handling and support

Parallel hosts the search service. Tool calls send search queries, objectives,
requested URLs, and optional session metadata to Parallel, along with standard
MCP connection metadata. This plugin configures no authentication headers or
local commands and does not automatically upload your repository.

See the [Privacy Policy](https://parallel.ai/privacy-policy),
[Customer Terms](https://parallel.ai/customer-terms), and
[Search MCP documentation](https://docs.parallel.ai/search/search-mcp).

For help, email [support@parallel.ai](mailto:support@parallel.ai) or
[open an issue](https://github.com/parallel-web/parallel-agent-skills/issues)
with your Antigravity version and error message. Leave out credentials and
private task content.
