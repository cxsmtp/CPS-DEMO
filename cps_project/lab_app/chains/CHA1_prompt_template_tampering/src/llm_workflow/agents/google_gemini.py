"""
AI AGENT #4 — Google Gemini 1.5 Pro

AI-BOM detection target: model "gemini-1.5-pro" from supplier "Google"
"""

from __future__ import annotations

import google.generativeai as genai

from llm_workflow.credentials import GOOGLE_API_KEY
from llm_workflow.prompt_loader import load_prompt_template

MODEL_NAME = "gemini-1.5-pro"


def chat(user_message: str) -> str:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(
        MODEL_NAME,
        system_instruction=load_prompt_template("gemini_system.txt"),
    )
    response = model.generate_content(user_message)
    return response.text or ""
