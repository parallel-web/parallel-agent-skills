#!/usr/bin/env python3
"""Check the production MCP tools and submission-required annotations."""

from __future__ import annotations

import json
import urllib.request
from typing import Any


ENDPOINT = "https://search.parallel.ai/mcp"
EXPECTED_ANNOTATIONS = {
    "readOnlyHint": True,
    "openWorldHint": True,
    "destructiveHint": False,
}
EXPECTED_TOOLS = {"web_search", "web_fetch"}


def decode_response(raw: str) -> dict[str, Any]:
    if raw.lstrip().startswith("{"):
        return json.loads(raw)
    data_lines = [line[5:].strip() for line in raw.splitlines() if line.startswith("data:")]
    if not data_lines:
        raise RuntimeError(f"unexpected MCP response: {raw[:200]}")
    return json.loads(data_lines[-1])


def post(payload: dict[str, Any], session_id: str | None = None) -> tuple[dict[str, Any] | None, str | None]:
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "User-Agent": "parallel-openai-submission-check/1.0",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
        returned_session = response.headers.get("Mcp-Session-Id") or session_id
    return (decode_response(body) if body else None, returned_session)


def main() -> None:
    initialized, session_id = post(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {
                    "name": "parallel-openai-submission-check",
                    "version": "1.0.0",
                },
            },
        }
    )
    if not initialized or not initialized.get("result", {}).get("serverInfo"):
        raise SystemExit("MCP initialize did not return serverInfo")
    post(
        {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
        session_id,
    )
    listed, _ = post(
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        session_id,
    )
    tools = listed.get("result", {}).get("tools", []) if listed else []
    names = {tool.get("name") for tool in tools}
    if names != EXPECTED_TOOLS:
        raise SystemExit(f"expected tools {sorted(EXPECTED_TOOLS)}, got {sorted(names)}")

    summary: list[dict[str, Any]] = []
    for tool in tools:
        annotations = tool.get("annotations", {})
        for key, expected in EXPECTED_ANNOTATIONS.items():
            if annotations.get(key) is not expected:
                raise SystemExit(
                    f"{tool['name']} annotation {key} must be {expected!r}; "
                    f"got {annotations.get(key)!r}"
                )
        if not tool.get("inputSchema") or not tool.get("outputSchema"):
            raise SystemExit(f"{tool['name']} must provide input and output schemas")
        summary.append(
            {
                "name": tool["name"],
                "annotations": annotations,
                "inputSchema": True,
                "outputSchema": True,
            }
        )

    print(json.dumps({"endpoint": ENDPOINT, "tools": summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
