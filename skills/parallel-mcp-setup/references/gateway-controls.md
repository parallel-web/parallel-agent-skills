# Gateway-level search controls

Configure Parallel's search behavior on Bifrost's authenticated upstream MCP connection. Settings under `web_search.override` apply to every Search call. Fetch uses its own defaults.

## Configure search overrides

Set `x-parallel-mcp-config` as a static upstream header on the Bifrost client, alongside the existing authentication. Pass the settings under `web_search.override`. Include only the fields you want to set. Leave the header unset to use Parallel's defaults.

For example, enter this value in the Bifrost dashboard to use `basic` mode and return at most two results:

```json
{"web_search":{"override":{"mode":"basic","advanced_settings":{"max_results":2}}}}
```

In `config.json`, serialize the same object as a string in the client's `headers` map. This example includes the Authorization header for a shared API key:

```json
{
  "Authorization": "env.PARALLEL_MCP_AUTHORIZATION",
  "x-parallel-mcp-config": "{\"web_search\":{\"override\":{\"mode\":\"basic\",\"advanced_settings\":{\"max_results\":2}}}}"
}
```

For OAuth, keep `auth_type` set to `oauth` and add only the search config header. Bifrost supplies the OAuth token.

## Other controls

See the [supported override fields](https://docs.parallel.ai/integrations/mcp/quickstart#supported-fields) for modes, result limits, and source filters. Search filters apply to Search results. Manage access to Fetch through Bifrost's tool controls.

## Migrate existing Search MCP overrides

Resolve the old connection's effective settings first. In standalone Search MCP, a URL setting took precedence over the same field in `x-parallel-search-config`. Check those fields against the Parallel MCP override documentation, move the supported values into `web_search.override`, and remove the legacy header and search-setting query parameters. Keep `?login` in the Parallel MCP URL to require authentication.

Use `objective` and `search_queries` as per-call tool inputs. After saving the header and applying the deployment's reload procedure, run Search and Fetch through Bifrost and verify the expected limit or source filter. On HTTP 400, check the JSON, field names, values, and nesting against the override documentation. Use request logs to verify settings that are not visible in results.

## References

- [Parallel MCP override settings](https://docs.parallel.ai/integrations/mcp/quickstart#override-settings)
- [Search API schema](https://docs.parallel.ai/api-reference/search/search)
- [Bifrost header configuration](https://docs.getbifrost.ai/mcp/auth/headers)
