"""
AI LIBRARY #8 — LangChain agent orchestration

AI-BOM detection target: library "LangChain" from supplier "langchain-ai"
"""

from __future__ import annotations

from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.prompts import PromptTemplate

from llm_workflow.credentials import OPENAI_API_KEY
from llm_workflow.prompt_loader import load_prompt_template


def build_agent() -> AgentExecutor:
    """Build a LangChain ReAct agent. The prompt template is loaded via
    the same vulnerable loader, so this agent inherits CH-A1's chain
    surface."""
    llm = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY)
    prompt_text = load_prompt_template("langchain_react_prompt.txt")
    prompt = PromptTemplate.from_template(prompt_text)

    tools = [
        Tool(
            name="lookup",
            func=lambda q: f"stub lookup: {q}",
            description="Look up information",
        ),
    ]
    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=False)
