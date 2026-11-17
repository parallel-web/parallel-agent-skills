---
name: parallel-mcp-setup
description: Use when installing, configuring, or troubleshooting an authenticated Parallel MCP connection in Bifrost, including gateway-level search settings and downstream tool access.
---

# Set up Parallel MCP

Connect Bifrost to authenticated Parallel MCP and verify Search and Fetch through the gateway.

## 1. Inspect the deployment

Identify the target Bifrost instance, its configuration source (dashboard or `config.json`), and the intended downstream agent or virtual key. Inspect existing MCP clients before changing anything. Reuse an authenticated Parallel MCP connection if it already has the intended access settings. Preserve unrelated clients, access rules, and tool approval settings.

Confirm access to Bifrost management and a Parallel account credential. These are separate from the downstream agent's Bifrost credential. If access or a secret is missing, prepare the configuration and report what is needed without claiming installation succeeded. Keep secrets in the deployment's secret manager or environment; never put them in skill files, source control, prompts, or tool arguments.

## 2. Configure the authenticated connection

Use `https://mcp.parallel.ai/mcp?login`, which requires authentication. Choose Headers auth for a shared Parallel API key, or Bifrost's OAuth flow when that is the deployment's chosen authentication method. Do not change an authentication failure into an unauthenticated connection.

For shared-key configuration, provision `PARALLEL_MCP_AUTHORIZATION` in the **Bifrost server environment** with the complete value `Bearer <Parallel API key>`. The `env.` reference substitutes the whole header value; it does not prepend `Bearer`.

In **MCP Gateway → New MCP Server**, choose HTTP, the URL above, and Headers auth. Use a client name without hyphens, such as `parallel_search`. Set `Authorization` to the environment-variable reference using the UI's env-var picker. For a fresh setup, use the wildcard tool setting (`["*"]` in the example below) so Bifrost can discover new default tools from Parallel MCP. Apply deployment-specific restrictions through Bifrost's tool and virtual key settings.

For a file-managed deployment, merge this client entry into the existing `mcp.client_configs` array:

```json
{
  "name": "parallel_search",
  "connection_type": "http",
  "connection_string": "https://mcp.parallel.ai/mcp?login",
  "auth_type": "headers",
  "headers": {
    "Authorization": "env.PARALLEL_MCP_AUTHORIZATION"
  },
  "is_ping_available": false,
  "tools_to_execute": ["*"]
}
```

For OAuth, use the same endpoint and tool settings. Choose **OAuth 2.0** in the dashboard or set `auth_type` to `oauth` in `config.json`. Omit the shared-key `Authorization` header. For a file-managed client, open the pending connection in the dashboard and click **Authorize** to complete the Parallel sign-in. Use per-user authentication only when each caller should use their own Parallel account. See [Bifrost authentication](https://docs.getbifrost.ai/mcp/auth/overview) for the chosen flow.

### Migrate an existing connection

Bifrost treats the URL and auth type as immutable. Create a replacement with a distinct client name and leave **Allow by Default** off while you set it up. Carry over the [search overrides](./references/gateway-controls.md#migrate-existing-search-mcp-overrides), allowed tools (`tools_to_execute`), and automatic approvals (`tools_to_auto_execute`). For a wildcard in either setting, list the tools it allowed or auto-approved on the old client if the replacement would expand that set. Verify the upstream connection.

For each [virtual key](https://docs.getbifrost.ai/features/governance/mcp-tools#setting-mcp-tool-restrictions) with an explicit binding to the old client, add a binding for the replacement alongside it. Copy the allowed tool list, including an empty list that blocks access. If a wildcard would grant additional tools, use the old grant's tool set explicitly. Keep the old and unrelated bindings in place.

After all replacement bindings are in place, enable **Allow by Default** on the replacement only if the old client used it and keys that inherit defaults get the same tools. Verify the replacement with both restricted keys and keys that inherit access. Disable the old client before removing its bindings. Removing those bindings while the old client is active can give restricted keys its default tools. Verify final access for affected keys and have downstream clients rediscover tools under the new prefix. Once the cutover is verified, remove the disabled client.

For file-managed deployments, make the same changes in the client entries and virtual-key bindings in `config.json`. Apply them in the same order so a reload preserves the access rules at each step.

## 3. Configure gateway controls and access

Keep Parallel’s defaults by omitting `x-parallel-mcp-config`. When the user explicitly requests a particular search mode, source policy, or response budget, read [gateway search controls](./references/gateway-controls.md). Apply these as upstream connection settings. Keep the chosen credential and search policy under gateway administration; do not enable caller-supplied overrides of these headers unless explicitly intended.

Confirm Bifrost discovers Search and Fetch upstream and exposes the intended subset to each downstream client or virtual key. Connect the agent to the deployment's Bifrost MCP gateway with its configured downstream authentication. Use the actual discovered tool names, which may be prefixed. Installing this skill does not itself register or expose the MCP tools.

## 4. Verify through Bifrost

1. Confirm the upstream connection is healthy and authenticated, with `web_search` and `web_fetch` discovered.
2. For each affected downstream key, confirm it discovers exactly the intended tools, including none if all access was blocked.
3. Where Search is allowed downstream, run a small search for official Python asyncio documentation. Where Fetch is allowed, fetch a documentation URL. Use the tools' current schemas and descriptions and a caller authorized for each tool. Confirm successful results and inspect per-URL errors. For restricted keys, also verify that calls outside their allowlists are rejected.
4. Inspect Bifrost's tool-call records to confirm the intended connection was used. Verify account attribution and any configured mode or source policy in available upstream request metadata or account logs; result quality alone does not prove the mode used.
5. Report exactly what was verified and what remains untested. A direct request to Parallel does not prove Bifrost routing, authentication, or downstream permissions.

On a 401/403, check the Parallel credential, account access, and upstream auth configuration. On a handshake 400, check the configured search overrides. For missing tools, inspect connection health and gateway filtering. Keep existing access controls while diagnosing failures.

## Optional: distribute this setup skill through Bifrost

In **Skills Repository → New Skill**, copy this file's name and description into Details, paste only the Markdown body into the SKILL.md editor, and attach `references/gateway-controls.md`. For an existing skill, create a new version. Publish an initial version such as `1.0.0`, then use **Register as Marketplace** and the dashboard's installation commands; the plugin name is `bifrost-parallel-mcp-setup`.

Bifrost serves newly created skills immediately and documents marketplace/download routes as public. Keep deployment credentials and private configuration out of published files. Skill publication is separate from MCP connection setup.

## Sources

- [Parallel MCP](https://docs.parallel.ai/integrations/mcp/quickstart)
- [Bifrost MCP connections](https://docs.getbifrost.ai/mcp/connecting-to-servers)
- [Bifrost header authentication](https://docs.getbifrost.ai/mcp/auth/headers)
- [Bifrost Skills Repository](https://docs.getbifrost.ai/features/skills-repository)
