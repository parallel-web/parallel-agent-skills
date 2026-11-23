---
name: parallel-vertical-search
description: "Query specialized data sources (verticals) through the Parallel MCP find_verticals and search_vertical tools, such as biomedical literature, clinical trials, or local places. Use when a request needs structured records beyond web pages. Free verticals work without sign-in at anonymous limits; paid verticals and modes only work when the Parallel MCP connection is signed in."
user-invocable: true
argument-hint: <what to look up>
compatibility: Requires a Parallel MCP connection that lists find_verticals and search_vertical. Paid verticals and modes require sign-in.
metadata:
  author: parallel
---

# Vertical Search

Look up: $ARGUMENTS

## Sign-in

`find_verticals` lists only the verticals this connection can use, each with its price per call.

- **Without sign-in:** the free verticals, and the free mode of a vertical that has one. Calls are subject to anonymous usage limits.
- **Signed in, with OAuth or an API key:** paid verticals and paid modes as well. Calls are billed to the user's Parallel account at the listed price.

A paid vertical or mode only works when the connection is signed in. If a call returns an error that asks for sign-in, tell the user and follow `parallel-search-setup`. Never ask the user to paste credentials into chat.

If the two tools are missing, the connection does not serve them. Follow `parallel-search-setup` to check which Parallel MCP URL the client uses.

## Find the vertical

Call `find_verticals` with the request in `objective`. It returns every vertical the connection can use, best match first, with its id and price. The best matches also carry their description and input schema.

- Pick the vertical whose description fits the request.
- If none fits, use `web_search`. Do not force a request into a vertical.
- Check the price before a paid call. Tell the user the price when the call is not free.

## Query it

Call `search_vertical` with the vertical's `id` and `arguments` that match its input schema.

- Use only arguments the schema lists. The tool rejects a call that does not match and returns the schema.
- Fix an argument error the tool reports and retry once. Report any other error and do not loop.

## Present the results

- Report the records the source returned, with its citations. Never invent an identifier or a URL.
- Name the source, so the user knows the data came from it and not from a web search.
- On an empty result, say the source returned nothing. Offer `web_search` as a fallback.
