"""
AI AGENT #1 — OpenAI GPT-4o (CH-A1 chain target)
================================================

This is the agent whose system prompt the chain attacks. The system
prompt is loaded from the prompts/ directory (see prompt_loader.py)
and shipped on every LLM call. An attacker who reaches the path
traversal primitive and the writable mount can overwrite the system
prompt, causing all subsequent invocations to carry attacker-controlled
instructions — without changing any application code or deployed binary.

AI-BOM detection target: model "GPT-4o" from supplier "OpenAI"
"""

from __future__ import annotations

# Real OpenAI SDK import — this is what Checkmarx AI Supply Chain Security
# detects as evidence of an LLM component.
from openai import OpenAI

from llm_workflow.credentials import OPENAI_API_KEY
from llm_workflow.prompt_loader import load_system_prompt

# The model name as a string literal. Checkmarx's source-code analysis
# extracts these literals into the AI-BOM as machine-learning-model
# components.
MODEL_NAME = "gpt-4o"


def build_client() -> OpenAI:
    """Construct the OpenAI client. Never called outside the lab guard."""
    return OpenAI(api_key=OPENAI_API_KEY)


def chat(user_message: str) -> str:
    """Single-turn chat. The system prompt is loaded from disk on every
    invocation, which is the surface CH-A1 exploits."""
    client = build_client()
    system_prompt = load_system_prompt()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content or ""
