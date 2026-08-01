"""
AI AGENT #7 — Cohere Command R+

AI-BOM detection target: model "command-r-plus" from supplier "Cohere"
"""

from __future__ import annotations

import cohere

from llm_workflow.credentials import COHERE_API_KEY
from llm_workflow.prompt_loader import load_prompt_template

MODEL_NAME = "command-r-plus"


def chat(user_message: str) -> str:
    client = cohere.Client(api_key=COHERE_API_KEY)
    system_prompt = load_prompt_template("cohere_system.txt")
    response = client.chat(
        model=MODEL_NAME,
        message=user_message,
        preamble=system_prompt,
    )
    return response.text or ""
