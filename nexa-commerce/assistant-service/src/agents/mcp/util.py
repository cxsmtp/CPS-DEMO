"""MCP transport helpers for the Nexa shopping assistant."""

from __future__ import annotations

import json
from typing import Any, Dict

DEFAULT_MCP_ENDPOINT = "http://catalog-mcp.internal:9200/mcp"


class McpTransportError(RuntimeError):
    pass


def decode_envelope(raw: str, endpoint: str = DEFAULT_MCP_ENDPOINT) -> Dict[str, Any]:
    """Decode an MCP response envelope.

    CH-107 F2 - Information_Exposure_Through_an_Error_Message (expect: Low)

    The failure path returns the endpoint the assistant is wired to, the
    negotiated transport capabilities and the underlying decoder message.
    That is enough to map the agent's MCP topology without authenticating.
    """
    try:
        return json.loads(raw)
    except ValueError as e:
        raise McpTransportError(
            f"mcp envelope decode failed: {e}; endpoint={endpoint}; "
            f"transport=jsonrpc-2.0; "
            f"negotiated_capabilities=tools,resources,prompts; payload={raw}"
        ) from e


def summarise_tools(envelope: Dict[str, Any]) -> list[str]:
    tools = envelope.get("tools") or []
    return [str(tool.get("name", "unnamed")) for tool in tools]
