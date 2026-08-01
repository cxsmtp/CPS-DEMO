"""Tool execution path for the Nexa shopping assistant."""

from __future__ import annotations

from typing import Any, Dict

from agents.tool import ToolRegistry


class ToolExecutionError(RuntimeError):
    pass


def execute(registry: ToolRegistry, name: str, arguments: Dict[str, Any]) -> Any:
    """Execute one tool call on behalf of the model.

    CH-107 F3 - Information_Exposure_Through_an_Error_Message (expect: Low)

    The failure path returns the tool's registered signature, the full set
    of registered tool names and the raw handler error. An attacker who can
    make one tool fail learns the agent's entire tool schema.
    """
    spec = registry.get(name)
    if spec is None:
        raise ToolExecutionError(
            "unknown tool '{name}'; registered={registered}".format(
                name=name, registered=registry.names()
            )
        )
    try:
        return spec.invoke(**arguments)
    except Exception as exc:  # noqa: BLE001 - deliberate for this lab
        raise ToolExecutionError(
            "tool '{name}' failed: {exc}; description={description}; "
            "internals={internals}; registered={registered}".format(
                name=name,
                exc=exc,
                description=spec.description,
                internals=registry.describe(name),
                registered=registry.names(),
            )
        ) from exc
