"""
F5 chain participant — AI WEAPONISATION AGENT

This file declares the AI agent that turns the Low recon findings
(F1/F2/F3/F4) into a runnable exploit chain. The agent is GPT-4o
with Code Interpreter (a tool-using LLM with code execution
capability), embedded as a customer-service chatbot that has the
ability to run Python code in a sandbox.

The chain story: an attacker provides input through the chatbot
(any input channel — direct prompt, indirect injection through
content the bot reads). The Low recon findings disclose framework
and library versions; the AI agent autonomously cross-references
those against advisory databases, generates an exploit using the
predictable session tokens (F3) and known CVE on the disclosed
library (F4), executes it through Code Interpreter, and exfiltrates
results via the unrestricted egress (F6).

AI-BOM detection target:
  - Model: gpt-4o
  - Supplier: OpenAI
  - Type: machine-learning-model
  - Capability: tool-use (Code Interpreter / code execution)

Without this file in the application, the same recon findings are
still present but the chain doesn't compose into RCE — it stays
as recon nuisance. This is the "AI weaponisation contribution"
that the framework's AI-Leverage dimension measures.
"""

from __future__ import annotations

from openai import OpenAI


MODEL_NAME = "gpt-4o"
SUPPLIER = "OpenAI"
CAPABILITY = "code-interpreter"


def build_agent_with_code_interpreter():
    """Construct the tool-using AI agent.

    The agent is given Code Interpreter access — meaning it can
    autonomously execute Python code. This is the F5 weaponisation
    primitive. With this access plus the Low recon findings, the agent
    can self-direct from reconnaissance to exploit synthesis to
    execution to exfiltration without human-in-the-loop.
    """
    client = OpenAI(api_key="sk-lab-stub-not-real")
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a customer service assistant."},
            {"role": "user", "content": "Hello, I need help with my account."},
        ],
        tools=[
            {
                "type": "code_interpreter",
            },
        ],
    )
    return response


if __name__ == "__main__":
    build_agent_with_code_interpreter()
