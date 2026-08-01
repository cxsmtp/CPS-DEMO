# Prompt Templates — CH-A1 chain participants

> **LAB-VULN-CHA1-F6**: prompt templates in this directory have no
> integrity sidecar. There is no `system_prompt.txt.sha256` file and no
> signature. The application loads templates at runtime and trusts their
> contents. An attacker who reaches the path-traversal primitive (F1) and
> the writable mount (F3 / F4) can overwrite these files; subsequent LLM
> invocations carry the attacker's instructions.
>
> What integrity verification *should* look like:
>
>   - sidecar file `system_prompt.txt.sha256` containing the SHA-256 hash
>   - loader verifies hash on read, refuses to load on mismatch
>   - or: prompts shipped via signed OCI artifact; verifier in CI/CD
>
> The chain matcher reads chains_index.json's `required_files` field
> and checks for the absence of these sidecars to establish F6.

## Files

| File | Purpose | Used by |
|---|---|---|
| `system_prompt.txt` | Default system prompt for OpenAI agents | openai_gpt4o.py, openai_gpt4o_mini.py |
| `classifier_prompt.txt` | Classification template | openai_gpt4o_mini.py |
| `anthropic_system.txt` | System prompt for Claude | anthropic_sonnet.py |
| `gemini_system.txt` | System prompt for Gemini | google_gemini.py |
| `llama_system.txt` | System prompt for Llama via Bedrock | meta_llama_bedrock.py |
| `mistral_system.txt` | System prompt for Mistral | mistral_large.py |
| `cohere_system.txt` | Preamble for Cohere | cohere_command.py |
| `langchain_react_prompt.txt` | LangChain ReAct prompt | langchain_agent.py |
| `adk_instruction.txt` | Google ADK agent instruction | google_adk_agent.py |

Every one of these files is loaded by the vulnerable `load_prompt_template`
function. Compromise of any file is a chain participant.
