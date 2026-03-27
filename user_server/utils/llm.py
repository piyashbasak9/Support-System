"""
Gemini LLM utilities for answer generation.
"""

import google.generativeai as genai
from typing import Optional
from user_server.config import settings
from shared.constants import LLM_MODEL, LLM_TEMPERATURE

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


def generate_answer(query: str, context: str, temperature: float = LLM_TEMPERATURE) -> str:
    """
    Generate answer using Gemini based on retrieved context.
    Returns 'NO_INFO' if answer cannot be found in context.
    
    Args:
        query: User's question
        context: Retrieved relevant text chunks
        temperature: Controls randomness (0=deterministic, 1=creative)
        
    Returns:
        Generated answer or 'NO_INFO'
    """
    prompt = f"""
You are a helpful assistant. Answer the user's question based ONLY on the provided context.
If the answer cannot be found in the context, respond exactly with: NO_INFO

Context:
{context}

Question: {query}

Answer:"""
    
    try:
        model = genai.GenerativeModel(
            model_name=LLM_MODEL,
            generation_config={
                "temperature": temperature,
                "top_p": 0.95,
                "top_k": 40,
            }
        )
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        raise RuntimeError(f"Failed to generate answer: {str(e)}")


def generate_answer_with_sources(query: str, chunks: list) -> dict:
    """
    Generate answer and track which sources were used.
    
    Args:
        query: User's question
        chunks: List of retrieved chunks with metadata
        
    Returns:
        Dictionary with answer and source information
    """
    context = "\n\n".join([chunk["text"] for chunk in chunks])
    answer = generate_answer(query, context)
    
    if answer == "NO_INFO":
        return {
            "answer": answer,
            "sources": []
        }
    
    return {
        "answer": answer,
        "sources": [
            {
                "chunk_id": chunk.get("id", f"chunk_{i}"),
                "text": chunk["text"][:200] + "...",
                "score": chunk.get("score", 0),
                "metadata": chunk.get("metadata", {})
            }
            for i, chunk in enumerate(chunks)
        ]
    }