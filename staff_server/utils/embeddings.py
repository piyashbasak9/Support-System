"""
Embedding utilities for Staff Server.
"""

import google.generativeai as genai
from typing import List
from config import settings
from shared.constants import EMBEDDING_MODEL

genai.configure(api_key=settings.GEMINI_API_KEY)


def get_embedding(text: str) -> List[float]:
    """Generate embedding for a single text."""
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=text,
        task_type="RETRIEVAL_DOCUMENT"
    )
    return result["embedding"]


def batch_get_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for multiple texts."""
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=texts,
        task_type="RETRIEVAL_DOCUMENT"
    )
    return result["embedding"]