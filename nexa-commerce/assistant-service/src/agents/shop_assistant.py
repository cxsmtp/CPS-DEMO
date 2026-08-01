"""Nexa Commerce shopping assistant.

This module is the AI-BOM surface for the repository. The models and agent
libraries named here are what Checkmarx AI Supply Chain Security should
enumerate, and they are the ai_inventory declared for CH-107.

Declared AI components:
  - OpenAI GPT-4o            (machine-learning-model)  primary assistant
  - OpenAI GPT-4o-mini       (machine-learning-model)  intent classifier
  - Model Context Protocol   (library)                 catalogue tool transport
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

from openai import OpenAI

from agents.mcp.util import decode_envelope, summarise_tools
from agents.run_internal.session_persistence import load_turns, save_turns
from agents.run_internal.tool_actions import execute
from agents.tool import ToolRegistry, ToolSpec
from agents.tracing.provider import TraceProvider

PRIMARY_MODEL = "gpt-4o"
CLASSIFIER_MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = (
    "You are the Nexa Commerce shopping assistant. Help the customer find "
    "products in the catalogue and answer questions about their order. "
    "Use the provided tools; never invent product data."
)

CATALOGUE: List[Dict[str, Any]] = [
    {"sku": "NX-1001", "title": "Aurora Desk Lamp", "price_cents": 4900},
    {"sku": "NX-1002", "title": "Meridian Wool Throw", "price_cents": 8900},
    {"sku": "NX-1003", "title": "Halden Ceramic Mug", "price_cents": 1800},
]


def _search_catalogue(query: str = "") -> List[Dict[str, Any]]:
    needle = query.strip().lower()
    if not needle:
        return CATALOGUE
    return [p for p in CATALOGUE if needle in p["title"].lower()]


def _order_status(reference: str = "") -> Dict[str, Any]:
    return {"reference": reference, "status": "in transit", "eta_days": 3}


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(ToolSpec(
        "search_catalogue", "Search the Nexa product catalogue", _search_catalogue))
    registry.register(ToolSpec(
        "order_status", "Look up the status of an order", _order_status))
    return registry


class ShopAssistant:
    def __init__(self) -> None:
        self.registry = build_registry()
        self.tracing = TraceProvider()
        self._client = None

    def _openai(self) -> OpenAI | None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return None
        if self._client is None:
            self._client = OpenAI(api_key=api_key)
        return self._client

    def reply(self, session_id: str, message: str) -> Dict[str, Any]:
        self.tracing.span("assistant.reply", session=session_id)
        turns = load_turns(session_id)
        turns.append({"role": "user", "content": message})

        results = execute(self.registry, "search_catalogue", {"query": message})

        client = self._openai()
        if client is None:
            answer = (
                "Offline mode: I found {n} matching product(s) in the catalogue."
                .format(n=len(results))
            )
        else:
            completion = client.chat.completions.create(
                model=PRIMARY_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": message},
                ],
            )
            answer = completion.choices[0].message.content or ""

        turns.append({"role": "assistant", "content": answer})
        save_turns(session_id, turns)
        return {"answer": answer, "matches": results,
                "trace_id": self.tracing.trace_id}

    def catalogue_tools(self, envelope_json: str) -> List[str]:
        return summarise_tools(decode_envelope(envelope_json))
