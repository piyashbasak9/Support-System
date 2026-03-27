"""
Gemini 2.0 embedding utilities.
Uses text-embedding-004 model with task_type parameter for optimal retrieval.
"""

import google.generativeai as genai
from typing import List, Union
from user_server.config import settings
from shared.constants import EMBEDDING_MODEL

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


def get_embedding(text: Union[str, List[str]], task_type: str = "RETRIEVAL_DOCUMENT") -> List[float]:
    """
    Generate embeddings for text using Gemini 2.0.
    
    Args:
        text: Single string or list of strings to embed
        task_type: Type of task - "RETRIEVAL_DOCUMENT" or "RETRIEVAL_QUERY"
        
    Returns:
        Embedding vector(s) as list of floats
    """
    try:
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=text,
            task_type=task_type,
        )
        
        # Return single embedding or list based on input
        if isinstance(text, str):
            return result["embedding"]
        return result["embedding"]
        
    except Exception as e:
        raise RuntimeError(f"Failed to generate embedding: {str(e)}")


def get_query_embedding(query: str) -> List[float]:
    """
    Generate embedding for a search query.
    Uses RETRIEVAL_QUERY task type for better matching with stored documents.
    
    Args:
        query: User's search query
        
    Returns:
        Query embedding vector
    """
    return get_embedding(query, task_type="RETRIEVAL_QUERY")


def get_document_embedding(text: str) -> List[float]:
    """
    Generate embedding for a document chunk.
    Uses RETRIEVAL_DOCUMENT task type for storage.
    
    Args:
        text: Document chunk text
        
    Returns:
        Document embedding vector
    """
    return get_embedding(text, task_type="RETRIEVAL_DOCUMENT")


def batch_get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in one API call.
    
    Args:
        texts: List of text strings
        
    Returns:
        List of embedding vectors
    """
    return get_embedding(texts, task_type="RETRIEVAL_DOCUMENT")