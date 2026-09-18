# Data-practices review draft

This document is an engineering inventory for review by Parallel's product,
security, and legal owners. It is not a replacement for the public privacy
policy or portal attestations.

## Data sent to the MCP server

Depending on the tool call, the client may send:

- A task-specific research objective
- Search queries
- Public URLs to fetch
- An optional session identifier used for rate limiting and request correlation
- An optional model identifier used for product analytics
- Standard HTTP and MCP connection metadata

The plugin skill instructs the model not to send raw conversation history,
credentials, private file contents, or unrelated personal data.

## Data returned

- `web_search` returns ranked public-web results and relevant excerpts.
- `web_fetch` returns extracted content from requested public URLs.
- Responses may include source URLs, page titles, publication dates, usage
  information, warnings, and request identifiers.

## Product behavior

- The anonymous endpoint is rate-limited.
- The submitted tools are read-only and cannot modify external systems.
- Retrieved webpages are treated as untrusted content.
- No custom UI is included in the initial submission.

## Owner confirmation required

Before submission, confirm that the public privacy policy accurately describes:

- Query, URL, session, model, and connection metadata collection
- Retention periods
- Logging and observability uses
- Whether data is used for service improvement or model training
- Third-party subprocessors and international transfers, if applicable
- User deletion or privacy-request mechanisms
