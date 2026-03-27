"""
Configuration settings for User Server.
Loads environment variables and provides settings object.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """User server settings."""
    
    # Pinecone settings
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "rag-support-index")
    
    # Gemini settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Staff server URL
    STAFF_SERVER_URL: str = os.getenv("STAFF_SERVER_URL", "http://localhost:8001/api/tickets")
    
    # Application settings
    APP_NAME: str = "RAG Support System - User API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # Validation
    def validate(self):
        """Validate required settings."""
        if not self.PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY is not set")
        if not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set")


settings = Settings()