"""
Pinecone vector store operations.
Uses latest pinecone-client (5.0.1+) with updated API.
"""

from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Optional
import time
from user_server.config import settings
from shared.constants import EMBEDDING_DIMENSION, DEFAULT_TOP_K

# Initialize Pinecone client
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index_name = settings.PINECONE_INDEX_NAME


def ensure_index_exists() -> bool:
    """
    Check if index exists with correct dimension and create/recreate if necessary.
    Returns True if index exists with correct dimension.
    """
    try:
        if index_name in pc.list_indexes().names():
            # Check if existing index has correct dimension
            desc = pc.describe_index(index_name)
            if desc.dimension != EMBEDDING_DIMENSION:
                print(f"Index '{index_name}' has dimension {desc.dimension}, expected {EMBEDDING_DIMENSION}. Recreating...")
                pc.delete_index(index_name)
                # Wait for deletion
                while index_name in pc.list_indexes().names():
                    time.sleep(2)
            else:
                return True
        
        print(f"Creating index '{index_name}' with dimension {EMBEDDING_DIMENSION}...")
        pc.create_index(
            name=index_name,
            dimension=EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        # Wait for index to be ready
        while not pc.describe_index(index_name).status.get('ready', False):
            time.sleep(2)
        print(f"Index '{index_name}' created successfully.")
        return True
    except Exception as e:
        print(f"Error creating index: {str(e)}")
        return False


def get_index():
    """Get Pinecone index instance."""
    return pc.Index(index_name)


def upsert_vectors(vectors: List[Dict]) -> Dict:
    """
    Upsert vectors to Pinecone.
    
    Args:
        vectors: List of dicts with keys: id, values, metadata
        
    Returns:
        Upsert response
    """
    index = get_index()
    
    # Format vectors for upsert
    upsert_data = []
    for v in vectors:
        upsert_data.append({
            "id": v["id"],
            "values": v["values"],
            "metadata": v.get("metadata", {})
        })
    
    # Upsert in batches of 100 for efficiency
    batch_size = 100
    for i in range(0, len(upsert_data), batch_size):
        batch = upsert_data[i:i + batch_size]
        index.upsert(vectors=batch)
    
    return {"upserted_count": len(vectors)}


def search_similar(query_embedding: List[float], top_k: int = DEFAULT_TOP_K, filter_dict: Optional[Dict] = None) -> List[Dict]:
    """
    Search for similar vectors in Pinecone.
    
    Args:
        query_embedding: Query embedding vector
        top_k: Number of results to return
        filter_dict: Optional metadata filter
        
    Returns:
        List of matches with id, score, and metadata
    """
    index = get_index()
    
    query_params = {
        "vector": query_embedding,
        "top_k": top_k,
        "include_metadata": True
    }
    
    if filter_dict:
        query_params["filter"] = filter_dict
    
    results = index.query(**query_params)
    
    matches = []
    for match in results.matches:
        matches.append({
            "id": match.id,
            "score": match.score,
            "metadata": match.metadata,
            "text": match.metadata.get("text", "")
        })
    
    return matches


def delete_vectors(ids: List[str]) -> Dict:
    """
    Delete vectors by ID.
    
    Args:
        ids: List of vector IDs to delete
        
    Returns:
        Deletion response
    """
    index = get_index()
    index.delete(ids=ids)
    return {"deleted_count": len(ids)}


def get_index_stats() -> Dict:
    """
    Get index statistics.
    
    Returns:
        Index stats dictionary
    """
    index = get_index()
    return index.describe_index_stats()