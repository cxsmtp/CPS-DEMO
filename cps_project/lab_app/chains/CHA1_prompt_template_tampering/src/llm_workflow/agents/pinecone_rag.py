"""
AI LIBRARY #10 — Pinecone vector database client

AI-BOM detection target: library "Pinecone" from supplier "Pinecone"
"""

from __future__ import annotations

import os

from pinecone import Pinecone

PINECONE_INDEX_NAME = "cps-lab-index"


def query_index(vector: list[float], top_k: int = 5):
    """Stub retrieval — used by the LangChain and ADK agents as a
    RAG tool. The Pinecone import is what AI-BOM detects."""
    pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY", "lab-stub-key"))
    index = pc.Index(PINECONE_INDEX_NAME)
    return index.query(vector=vector, top_k=top_k, include_metadata=True)
