"""
Text chunking utilities using langchain-text-splitters.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from shared.constants import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP

# Initialize the text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=DEFAULT_CHUNK_SIZE,
    chunk_overlap=DEFAULT_CHUNK_OVERLAP,
    separators=["\n\n", "\n", ".", " ", ""],
    length_function=len,
)


def chunk_text(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE) -> list[str]:
    """
    Split text into chunks for embedding.
    
    Args:
        text: The input text to split
        chunk_size: Maximum size of each chunk
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    chunks = text_splitter.split_text(text)
    return chunks


def chunk_document(text: str, source: str) -> list[dict]:
    """
    Split document into chunks with metadata.
    
    Args:
        text: Document text
        source: Source identifier (e.g., filename)
        
    Returns:
        List of dicts with 'text' and 'metadata' keys
    """
    chunks = chunk_text(text)
    
    result = []
    for i, chunk in enumerate(chunks):
        result.append({
            "text": chunk,
            "metadata": {
                "source": source,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
        })
    
    return result