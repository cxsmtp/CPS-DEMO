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
    transport version it negotiated and the underlying decoder message.
    That is enough for a caller to map the agent's MCP topology without
    ever authenticating to it.
    """
    try:
        return json.loads(raw)
    except ValueError as exc:
        raise McpTransportError(
            "mcp envelope decode failed: {exc}; endpoint={endpoint}; "
            "transport=jsonrpc-2.0; negotiated_capabilities=tools,resources,prompts"
            .format(exc=exc, endpoint=endpoint)
        ) from exc


def summarise_tools(envelope: Dict[str, Any]) -> list[str]:
    tools = envelope.get("tools") or []
    return [str(tool.get("name", "unnamed")) for tool in tools]
