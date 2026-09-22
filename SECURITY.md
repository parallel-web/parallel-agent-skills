# Security policy

## Reporting a vulnerability

If you find a security issue in this repository, in the skills it publishes, or
in the hosted Parallel Search MCP service (`search.parallel.ai`), report it
privately to **[support@parallel.ai](mailto:support@parallel.ai)**. Do not open a public GitHub issue for
security reports.

Include what you found, how to reproduce it, and the impact you believe it has.
We will acknowledge your report and follow up as we investigate.

## Scope

- This repository contains skills, documentation, and client configuration. The
  search service and the Task API run on Parallel's infrastructure.
- The bundled MCP server (`parallel-search`) is anonymous: it carries no
  credentials of any kind, and its tools (`web_search`, `web_fetch`) are
  read-only.
- The CLI-backed skills run `parallel-cli` locally and use the credentials you
  have already configured for it. They never transmit those credentials
  anywhere except to Parallel's API.
- Never share Parallel API keys or tokens in issues, pull requests, or reports.

## Service and data handling

Use of the hosted service is governed by the
[Customer Terms](https://parallel.ai/customer-terms) and
[Privacy Policy](https://parallel.ai/privacy-policy).
