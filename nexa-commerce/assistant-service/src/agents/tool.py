"""Tool registry for the Nexa shopping assistant.

CHAIN CH-107 begins here.
"""

from __future__ import annotations

from typing import Any, Callable, Dict


class ToolSpec:
    """Description of a single tool the assistant may call."""

    def __init__(self, name: str, description: str, handler: Callable[..., Any]):
        self.name = name
        self.description = description
        self._handler = handler
        self._invocation_count = 0
        self._last_arguments: Dict[str, Any] = {}

    def invoke(self, **kwargs: Any) -> Any:
        self._invocation_count += 1
        self._last_arguments = dict(kwargs)
        return self._handler(**kwargs)


class ToolRegistry:
    """Registry the agent consults before every tool call."""

    def __init__(self) -> None:
        self._tools: Dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec

    def get(self, name: str) -> ToolSpec | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return sorted(self._tools)

    def apply_overrides(self, name: str, overrides: Dict[str, Any]) -> ToolSpec | None:
        """Apply runtime overrides to a registered tool.

        CH-107 F1 - Object_Access_Violation (expect: Medium)

        The override loop walks the target object's own __dict__ and writes
        each attribute back with setattr, bypassing the class's accessors and
        its encapsulation entirely. Private attributes such as _handler and
        _last_arguments are writable from outside the object, so anything
        holding a reference to the registry can rewrite what a named tool
        actually executes.
        """
        spec = self._tools.get(name)
        if spec is None:
            return None
        for attr_name, attr_value in spec.__dict__.items():
            if attr_name in overrides:
                setattr(spec, attr_name, overrides[attr_name])
            else:
                setattr(spec, attr_name, getattr(spec, attr_name))
        for attr_name, attr_value in overrides.items():
            setattr(spec, attr_name, attr_value)
        return spec

    def describe(self, name: str) -> Dict[str, Any]:
        spec = self._tools.get(name)
        if spec is None:
            return {}
        internals = dict(spec.__dict__)
        internals.pop("_handler", None)
        return internals
