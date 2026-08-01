"""
AI LIBRARY #9 — Google ADK (Agent Development Kit)

AI-BOM detection target: library "Google ADK" from supplier "Google"
"""

from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.runners import Runner

from llm_workflow.prompt_loader import load_prompt_template


def build_agent() -> LlmAgent:
    """Construct an ADK LlmAgent. Same prompt-loading surface as the
    other agents — chain participation is identical."""
    instruction = load_prompt_template("adk_instruction.txt")
    return LlmAgent(
        name="cps_lab_adk_agent",
        model="gemini-1.5-pro",
        instruction=instruction,
    )


def run(user_message: str) -> str:
    agent = build_agent()
    runner = Runner(agent=agent)
    result = runner.run(user_message)
    return str(result)
