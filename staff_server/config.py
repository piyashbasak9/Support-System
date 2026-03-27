"""
Configuration settings for Staff Server.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Staff server settings."""
    
    # Database
    DATABASE_URL: str = "sqlite:///./staff_server.db"
    
    # Pinecone
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "rag-support-index")
    
    # Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-in-production")
    
    # Application
    APP_NAME: str = "RAG Support System - Staff API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False


settings = Settings()