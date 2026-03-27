"""
User Server - Main FastAPI Application
Handles user queries, RAG retrieval, and ticket creation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import uuid
import time
import logging
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Request
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime

from config import settings
from models import AskResponse, HealthResponse
from database import get_db, QueryLog, init_db
from utils.embeddings import get_query_embedding
from utils.llm import generate_answer_with_sources
from utils.vector_store import search_similar, ensure_index_exists
from utils.file_processor import extract_text_from_pdf, extract_text_from_image, validate_file_size, get_file_extension
from utils.ticket_client import create_ticket
from shared.constants import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="RAG Support System - User Facing API"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates
templates = Jinja2Templates(directory="templates")

# Initialize database and Pinecone on startup
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting User Server...")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Ensure Pinecone index exists
    if not ensure_index_exists():
        logger.warning("Failed to create Pinecone index. Please check configuration.")
    else:
        logger.info("Pinecone index ready")
    
    logger.info("User Server started successfully")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow()
    )


# ------------------- Frontend Routes -------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main user interface."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/ask", response_model=AskResponse)
async def ask_question(
    query: str = Form(..., min_length=1, max_length=5000, description="User's question"),
    file: UploadFile = File(None, description="Optional PDF file"),
    db: Session = Depends(get_db)
):
    """
    Process user query with RAG.
    
    - If relevant context exists, generate answer using Gemini
    - If no answer found, create support ticket
    """
    start_time = time.time()
    ticket_id = None
    response_status = "success"
    
    # Validate query is not just whitespace
    if not query or not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty. Please provide a valid question."
        )
    
    try:
        # Validate file if provided
        extracted_text = ""
        file_info = None
        
        if file:
            # Check file extension
            ext = get_file_extension(file.filename)
            if ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type. Allowed: {ALLOWED_EXTENSIONS}"
                )
            
            # Read file
            content = await file.read()
            
            # Validate file size
            if not validate_file_size(content, MAX_FILE_SIZE_MB):
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Max size: {MAX_FILE_SIZE_MB}MB"
                )
            
            # Extract text based on file type
            if ext == '.pdf':
                extracted_text = extract_text_from_pdf(content)
            elif ext in ['.jpg', '.jpeg', '.png']:
                extracted_text = extract_text_from_image(content)
            
            file_info = {
                "filename": file.filename,
                "size_bytes": len(content),
                "type": ext
            }
        
        # Combine query with extracted text
        full_text = query
        if extracted_text:
            full_text += "\n\n" + extracted_text
        
        # Generate query embedding
        query_embedding = get_query_embedding(full_text)
        
        # Search Pinecone for relevant chunks
        matches = search_similar(query_embedding, top_k=5)
        
        # If no matches found, create ticket
        if not matches:
            response_status = "ticket_created"
            ticket_id = str(uuid.uuid4())
            
            # Send ticket to staff server
            success = create_ticket(
                ticket_id=ticket_id,
                query=query,
                extracted_text=extracted_text,
                file_info=file_info
            )
            
            if not success:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create support ticket. Please try again later."
                )
            
            # Log the query
            log_entry = QueryLog(
                query=query[:500],
                response_status=response_status,
                ticket_id=ticket_id,
                latency_ms=(time.time() - start_time) * 1000
            )
            db.add(log_entry)
            db.commit()
            
            return AskResponse(
                status="ticket_created",
                ticket_id=ticket_id,
                message="I don't have enough information to answer your question. A support ticket has been created. You will be contacted shortly."
            )
        
        # Build context from matches
        chunks = []
        for match in matches:
            chunks.append({
                "id": match["id"],
                "text": match["text"],
                "score": match["score"],
                "metadata": match["metadata"]
            })
        
        # Generate answer with sources
        result = generate_answer_with_sources(full_text, chunks)
        
        # If answer not found, create ticket
        if result["answer"] == "NO_INFO":
            response_status = "ticket_created"
            ticket_id = str(uuid.uuid4())
            
            create_ticket(
                ticket_id=ticket_id,
                query=query,
                extracted_text=extracted_text,
                file_info=file_info
            )
            
            # Log the query
            log_entry = QueryLog(
                query=query[:500],
                response_status=response_status,
                ticket_id=ticket_id,
                latency_ms=(time.time() - start_time) * 1000
            )
            db.add(log_entry)
            db.commit()
            
            return AskResponse(
                status="ticket_created",
                ticket_id=ticket_id,
                message="I couldn't find a specific answer in the knowledge base. A support ticket has been created."
            )
        
        # Success - return answer with sources
        log_entry = QueryLog(
            query=query[:500],
            response_status="answered",
            latency_ms=(time.time() - start_time) * 1000
        )
        db.add(log_entry)
        db.commit()
        
        return AskResponse(
            status="success",
            answer=result["answer"],
            sources=result["sources"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error processing request: {str(e)}")
        
        # Log error
        try:
            log_entry = QueryLog(
                query=query[:500] if query else "",
                response_status="error",
                latency_ms=(time.time() - start_time) * 1000
            )
            db.add(log_entry)
            db.commit()
        except:
            pass
        
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get system statistics."""
    total_queries = db.query(QueryLog).count()
    tickets_created = db.query(QueryLog).filter(QueryLog.response_status == "ticket_created").count()
    
    return {
        "total_queries": total_queries,
        "tickets_created": tickets_created,
        "resolution_rate": (total_queries - tickets_created) / total_queries * 100 if total_queries > 0 else 0
    }