"""
AI AGENT #2 — OpenAI GPT-4o-mini (classification helper)

AI-BOM detection target: model "gpt-4o-mini" from supplier "OpenAI"
"""

from __future__ import annotations

from openai import OpenAI

from llm_workflow.credentials import OPENAI_API_KEY
from llm_workflow.prompt_loader import load_prompt_template

MODEL_NAME = "gpt-4o-mini"


def classify(text: str) -> str:
    client = OpenAI(api_key=OPENAI_API_KEY)
    system_prompt = load_prompt_template("classifier_prompt.txt")
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content or ""
