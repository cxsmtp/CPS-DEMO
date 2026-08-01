"""
AI AGENT #3 — Anthropic Claude 3.5 Sonnet

AI-BOM detection target: model "claude-3-5-sonnet" from supplier "Anthropic"
"""

from __future__ import annotations

import anthropic

from llm_workflow.credentials import ANTHROPIC_API_KEY
from llm_workflow.prompt_loader import load_prompt_template

MODEL_NAME = "claude-3-5-sonnet-20241022"


def chat(user_message: str) -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    system_prompt = load_prompt_template("anthropic_system.txt")
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text if response.content else ""
