# CH-A1 — Prompt-Template Tampering for Persistent Backdoor

> **Chain anatomy**: SAST + IaC + AI-BOM compose into a chain whose
> terminal outcome is persistent attacker-controlled instructions in
> the LLM workflow's system prompt, taking effect on every subsequent
> invocation, without modifying application code or any deployed binary.
> Real-world anchor: prompt registry compromise / template-tampering
> attacks documented in 2024-2026 LLM security research.

## What's in this directory

```
CHA1_prompt_template_tampering/
├── README.md                         # this file
├── src/                              # Python LLM workflow — produces SAST findings
│   └── llm_workflow/
│       ├── lab_guard.py              # safety guard (env var required to start)
│       ├── main.py                   # Flask entry exposing vulnerable endpoints
│       ├── prompt_loader.py          # F1: path traversal in template loader
│       ├── credentials.py            # F2: hardcoded LLM provider keys
│       ├── prompts/                  # 9 templates, no integrity sidecars (F6)
│       └── agents/                   # 10 AI components for AI-BOM detection
│           ├── openai_gpt4o.py            # AI #1 — chain TARGET
│           ├── openai_gpt4o_mini.py       # AI #2
│           ├── anthropic_sonnet.py        # AI #3
│           ├── google_gemini.py           # AI #4
│           ├── meta_llama_bedrock.py      # AI #5
│           ├── mistral_large.py           # AI #6
│           ├── cohere_command.py          # AI #7
│           ├── langchain_agent.py         # AI #8 — library
│           ├── google_adk_agent.py        # AI #9 — library
│           └── pinecone_rag.py            # AI #10 — library
├── iac/                              # Infrastructure-as-code — produces KICS findings
│   ├── kubernetes/deployment.yaml    # F3: writable mount on /app/prompts
│   └── terraform/main.tf             # F4: S3 PutObject + IAM wildcard
└── ai_bom/
    └── ai_inventory.yaml             # declarative: 10 AI components
```

## Chain anatomy

| # | Engine | Query (intended) | Severity | Role |
|---|---|---|---|---|
| F1 | SAST | `Path_Traversal` (Python) | Low | L2 Bridge — attacker-influenceable file path |
| F2 | SAST | `Use_Of_Hardcoded_Password` | Low/Medium | L1 Signal — peripheral chain Low |
| F3 | IaC (K8s) | writable volume mount on prompt directory | Low | L3 Amplifier — enables overwrite |
| F4 | IaC (TF) | S3 PutObject without object lock + IAM wildcard | Low/Medium | L3 Amplifier — cloud equivalent of F3 |
| F5 | AI-BOM | OpenAI GPT-4o model component (chain target) | (synthetic Informational) | L2 Bridge — LLM whose behaviour is hijacked |

## AI Inventory (chain context, not chain participants)

The lab declares 9 additional AI components in addition to F5's targeted GPT-4o.
Reviewers can verify the inventory is realistic — all from major commercial
providers, all detected via standard SDK imports. The matcher reports them
as inventory context: a chain matcher run produces a section listing all 10
components, with the chain's targeted model marked.

| # | Component | Provider | Type |
|---|---|---|---|
| 1 | GPT-4o | OpenAI | machine-learning-model (TARGET) |
| 2 | GPT-4o-mini | OpenAI | machine-learning-model |
| 3 | Claude 3.5 Sonnet | Anthropic | machine-learning-model |
| 4 | Gemini 1.5 Pro | Google | machine-learning-model |
| 5 | Llama 3.1 70B | Meta (via AWS Bedrock) | machine-learning-model |
| 6 | Mistral Large | Mistral AI | machine-learning-model |
| 7 | Command R+ | Cohere | machine-learning-model |
| 8 | LangChain | langchain-ai | library |
| 9 | Google ADK | Google | library |
| 10 | Pinecone | Pinecone | library |

## How to scan

Point Checkmarx One at `chains/CHA1_prompt_template_tampering/`. Enable
SAST + IaC Security + SCA + AI Supply Chain Security. Use the Python
preset for SAST.

After completion, export TWO artifacts:

1. **Vulnerability Type comprehensive report** (JSON) — covers SAST/IaC/SCA findings
2. **AI-BOM CycloneDX export** — covers the 10 AI components

## How to interpret

```
python -m cps_engine.cli sample_data/cha1_results.json \
    --aibom sample_data/cha1_aibom.json \
    --catalog lab_app/chains_index.json --all
```

Expected output:

- 10 AI component findings synthesized from the CycloneDX export
- 4–6 SAST/IaC findings from the comprehensive report
- Chain Detection Report: CH-A1 fully assembled (or partially, with honest "missing" markers if some patterns don't trigger)
- AI Inventory section: all 10 components, with chain target marked

## Severity drift to expect

`Path_Traversal` in Python: tenant may rate Low *or* Medium depending on
whether the sink crosses a trust boundary. `Use_Of_Hardcoded_Password`:
your tenant rates Medium (per CH-001-DEMO finding); the v9.7.0 catalog
rates Low. The IAM wildcard policy: tenant rates Medium. These drifts are
already documented for CH-001 and reinforce the paper's argument.
