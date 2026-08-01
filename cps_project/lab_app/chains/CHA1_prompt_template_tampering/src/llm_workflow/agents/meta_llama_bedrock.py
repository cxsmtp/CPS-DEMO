"""
AI AGENT #5 — Meta Llama 3.1 70B Instruct via AWS Bedrock

AI-BOM detection target: model "Llama 3.1 70B Instruct" from supplier "Meta"
                         (accessed via AWS Bedrock)
"""

from __future__ import annotations

import json

import boto3

from llm_workflow.prompt_loader import load_prompt_template

MODEL_NAME = "meta.llama3-1-70b-instruct-v1:0"
BEDROCK_REGION = "us-east-1"


def chat(user_message: str) -> str:
    client = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
    system_prompt = load_prompt_template("llama_system.txt")
    body = {
        "prompt": f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>",
        "max_gen_len": 1024,
    }
    response = client.invoke_model(
        modelId=MODEL_NAME,
        body=json.dumps(body),
    )
    payload = json.loads(response["body"].read())
    return payload.get("generation", "")
