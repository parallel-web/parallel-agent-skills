# Gateway-level search controls

Configure Parallel's search behavior on Bifrost's authenticated upstream MCP connection. These settings apply to every `web_search` call on that connection and do not affect `web_fetch`.

## Keep defaults unless overrides are requested

By default, omit `x-parallel-search-config` and search-setting URL parameters. Let Parallel use its current defaults for mode, excerpt size, and result count. The shared-key header configuration is:

```json
{
  "Authorization": "env.PARALLEL_MCP_AUTHORIZATION"
}
```

Use the plain `https://search.parallel.ai/mcp-oauth` connection URL. If a connection already has overrides, remove them only when the user requests returning to defaults; preserve unrelated settings and authentication.

## Optional search overrides

Only add `x-parallel-search-config` when the user explicitly requests custom search settings. Its value is a JSON string containing just those requested settings. In the dashboard header-value field, enter the JSON object text without outer string escaping. Leave unspecified settings omitted so they retain their defaults.

Search MCP calls the processing preset `mode`, not `processor`. Supported modes are `turbo`, `fast`, `basic`, and `advanced`; do not invent a `processor` field or copy Task API processors into this configuration.

Keep the Authorization header present when adding or changing search controls. For OAuth connections, preserve OAuth authentication and configure the search header through the connection's supported static-header settings.

## Other controls

Use only the settings the deployment needs. The header follows the current Search API request schema:

| Setting | Purpose |
| --- | --- |
| `mode` | Search processing preset |
| `max_chars_total` | Total excerpt character budget |
| `advanced_settings.max_results` | Maximum number of results |
| `advanced_settings.excerpt_settings.max_chars_per_result` | Per-result excerpt budget |
| `advanced_settings.source_policy.include_domains` | Restrict returned sources to specified domains or supported paths |
| `advanced_settings.source_policy.exclude_domains` | Exclude sources when no include list is set |
| `advanced_settings.source_policy.after_date` | Publication-date filter |
| `advanced_settings.location` | Two-letter country code for geographic relevance |
| `advanced_settings.fetch_policy` | Live-fetch/cache policy; can increase latency |

An include list takes precedence over exclusions. Domain/path prefixes require `fast`, `basic`, or `advanced`; they are unsupported in `turbo`. Source filters constrain search results, not which URLs `web_fetch` can read; do not treat them as a gateway-wide network access boundary.

## URL alternative and precedence

For explicitly requested overrides, URL query parameters are an alternative to the configuration header. Omit them for default behavior.

Nested fields use dotted paths. URL parameters override the same fields in `x-parallel-search-config`; unrelated header settings remain. Prefer one location for each setting to avoid an old URL parameter silently overriding a new header value. An existing Bifrost client's URL is immutable, so header changes are preferable for tuning an established connection.

`objective` and `search_queries` remain per-call tool inputs and cannot be pinned in the connection. Unknown fields, unsupported modes, malformed JSON, or attempts to pin those inputs cause a handshake 400. Reconnect/verify after changes and check the effective settings in available request logs without exposing credentials.

## References

- [Search MCP configuration and precedence](https://docs.parallel.ai/integrations/mcp/search-mcp#configure-search-behavior)
- [Search API schema](https://docs.parallel.ai/api-reference/search/search)
- [Bifrost header configuration](https://docs.getbifrost.ai/mcp/auth/headers)
