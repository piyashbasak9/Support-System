"""
Shared constants used across both servers.
"""

# Embedding model configuration
EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSION = 3072  # gemini-embedding-001 returns 3072-dimensional embeddings

# Chunking configuration
DEFAULT_CHUNK_SIZE = 500   # tokens - optimized for Gemini embeddings
DEFAULT_CHUNK_OVERLAP = 50

# LLM configuration
LLM_MODEL = "gemini-2.5-flash"  # Latest stable Gemini model
LLM_TEMPERATURE = 0.3

# Search configuration
DEFAULT_TOP_K = 5

# File upload limits
MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png']

# Ticket status
TICKET_STATUS_PENDING = "pending"
TICKET_STATUS_RESOLVED = "resolved"