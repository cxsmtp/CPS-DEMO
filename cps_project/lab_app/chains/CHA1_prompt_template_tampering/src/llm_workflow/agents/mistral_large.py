"""
AI AGENT #6 — Mistral Large

AI-BOM detection target: model "mistral-large" from supplier "Mistral AI"
"""

from __future__ import annotations

from mistralai import Mistral

from llm_workflow.credentials import MISTRAL_API_KEY
from llm_workflow.prompt_loader import load_prompt_template

MODEL_NAME = "mistral-large-latest"


def chat(user_message: str) -> str:
    client = Mistral(api_key=MISTRAL_API_KEY)
    system_prompt = load_prompt_template("mistral_system.txt")
    response = client.chat.complete(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content or ""
