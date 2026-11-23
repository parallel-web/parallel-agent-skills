---
name: parallel-image-search
description: "Find images on the web through the Parallel MCP image_search tool. Use when the user wants to see or find photos, logos, diagrams, or artwork. Fast mode works without sign-in; advanced mode only works when the Parallel MCP connection is signed in. For information about a subject use web_search."
user-invocable: true
argument-hint: <images to find>
compatibility: Requires a Parallel MCP connection that lists image_search. Advanced mode requires sign-in.
metadata:
  author: parallel
---

# Image Search

Find images of: $ARGUMENTS

## Sign-in

| Mode | Without sign-in | Signed in |
| --- | --- | --- |
| `fast` | Works, at anonymous usage limits | Works, billed to the account |
| `advanced` | Does not work: the call returns an error that asks for sign-in | Works, billed to the account. It is the default mode |

So `advanced` only works when the Parallel MCP connection is signed in, with OAuth or an API key. On an anonymous connection, use `fast`. If the user needs `advanced`, tell them it needs sign-in and follow `parallel-search-setup`. Never ask the user to paste credentials into chat.

If the tool is missing, the connection does not serve it. Follow `parallel-search-setup` to check which Parallel MCP URL the client uses.

## Run the search

Use the tool's advertised schema. In short:

- Put what the images should show in `objective`, with the subject and the style or context that should rank them, such as "official headshot" or "diagram, not a photo".
- Add 1 to 3 keyword queries of 2 to 6 words each in `search_queries`.
- Set `mode` only when you need to: `fast` on an anonymous connection, or when the user wants speed.

## Present the results

Each result has a direct image URL, the page the image appears on, the page title, and pixel dimensions when known.

- Show each image with a link to the page it came from.
- Results link to images; they do not describe them. Do not state what an image shows unless you have looked at it.
- Images on the web can be copyrighted. Point the user to the source page for usage rights.
- For facts about the subject, use `web_search`.
