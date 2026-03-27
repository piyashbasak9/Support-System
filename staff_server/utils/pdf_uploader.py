"""
PDF processing and upload to Pinecone.
"""

import io
import pdfplumber
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone
from config import settings
from utils.embeddings import batch_get_embeddings
from shared.constants import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP

# Initialize text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=DEFAULT_CHUNK_SIZE,
    chunk_overlap=DEFAULT_CHUNK_OVERLAP,
    separators=["\n\n", "\n", ".", " ", ""],
    length_function=len,
)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract all text from PDF."""
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def chunk_text(text: str) -> List[str]:
    """Split text into chunks."""
    if not text:
        return []
    return text_splitter.split_text(text)


def process_pdf_and_upload(file_bytes: bytes, filename: str) -> Dict:
    """
    Process PDF: extract text, chunk, embed, and upsert to Pinecone.
    
    Returns:
        Dict with status and number of chunks added
    """
    # Extract text
    text = extract_text_from_pdf(file_bytes)
    
    if not text:
        return {"status": "error", "message": "No text could be extracted from PDF", "chunks": 0}
    
    # Chunk the text
    chunks = chunk_text(text)
    
    if not chunks:
        return {"status": "error", "message": "No chunks created from text", "chunks": 0}
    
    # Generate embeddings
    try:
        embeddings = batch_get_embeddings(chunks)
    except Exception as e:
        return {"status": "error", "message": f"Failed to generate embeddings: {str(e)}", "chunks": 0}
    
    # Prepare vectors for Pinecone
    vectors = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        vectors.append({
            "id": f"{filename}_{i}_{hash(chunk) % 10000}",
            "values": embedding,
            "metadata": {
                "text": chunk,
                "source": filename,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
        })
    
    # Connect to Pinecone and upsert
    try:
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        index = pc.Index(settings.PINECONE_INDEX_NAME)
        
        # Upsert in batches
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            index.upsert(vectors=batch)
        
        return {"status": "success", "message": f"Uploaded {len(chunks)} chunks", "chunks": len(chunks)}
        
    except Exception as e:
        return {"status": "error", "message": f"Failed to upload to Pinecone: {str(e)}", "chunks": 0}