"""
Staff Server - Main FastAPI Application
Handles PDF uploads, ticket management, and dashboard.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
import logging
import os
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional

from config import settings
from database import get_db, init_db
from models import Ticket
from utils.pdf_uploader import process_pdf_and_upload
from utils.ticket_manager import (
    create_ticket, resolve_ticket, get_all_tickets,
    get_ticket_by_id, get_ticket_stats
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="RAG Support System - Staff Admin Panel"
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

# PDF uploads directory
UPLOADS_DIR = "uploaded_pdfs"
os.makedirs(UPLOADS_DIR, exist_ok=True)


# ------------------- Helper Functions -------------------
def get_uploaded_files():
    """Get list of uploaded PDF files."""
    try:
        files = []
        if os.path.exists(UPLOADS_DIR):
            for filename in os.listdir(UPLOADS_DIR):
                filepath = os.path.join(UPLOADS_DIR, filename)
                if os.path.isfile(filepath):
                    files.append({
                        "name": filename,
                        "size": os.path.getsize(filepath),
                        "modified": datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M')
                    })
        return sorted(files, key=lambda x: x["modified"], reverse=True)
    except Exception as e:
        logger.error(f"Error getting uploaded files: {str(e)}")
        return []

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Starting Staff Server...")
    init_db()
    logger.info("Database initialized")
    logger.info("Staff Server started successfully")


# ------------------- Web Dashboard -------------------
@app.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    filter: str = "pending",
    tab: str = "tickets",
    db: Session = Depends(get_db)
):
    """
    Render the staff dashboard.
    Shows tickets and upload form.
    """
    if filter == "pending":
        tickets = [t for t in get_all_tickets(db) if t.status == "pending"]
    elif filter == "resolved":
        tickets = [t for t in get_all_tickets(db) if t.status == "resolved"]
    else:
        tickets = get_all_tickets(db)
    
    stats = get_ticket_stats(db)
    uploaded_files = get_uploaded_files()
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "tickets": tickets,
            "stats": stats,
            "filter": filter,
            "tab": tab,
            "uploaded_files": uploaded_files,
            "upload_message": None,
            "upload_status": None
        }
    )


# ------------------- API Endpoints -------------------
@app.post("/api/tickets", status_code=201)
async def api_create_ticket(
    ticket_id: str = Form(...),
    query: str = Form(...),
    extracted_text: str = Form(""),
    file_info: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Create a new ticket (called by User Server)."""
    file_info_dict = json.loads(file_info) if file_info else None
    
    ticket = create_ticket(
        db=db,
        ticket_id=ticket_id,
        query=query,
        extracted_text=extracted_text,
        file_info=file_info_dict
    )
    
    return {"status": "created", "ticket_id": ticket.ticket_id}


@app.get("/api/tickets")
async def api_list_tickets(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all tickets, optionally filtered by status."""
    tickets = get_all_tickets(db, status)
    return [t.to_dict() for t in tickets]


@app.get("/api/tickets/{ticket_id}")
async def api_get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    """Get full ticket details."""
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket.to_full_dict()


@app.post("/api/tickets/{ticket_id}/resolve")
async def api_resolve_ticket(
    ticket_id: str,
    answer: str = Form(...),
    resolved_by: str = "staff",
    db: Session = Depends(get_db)
):
    """Resolve a ticket with an answer."""
    success = resolve_ticket(db, ticket_id, answer, resolved_by)
    if not success:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Redirect back to dashboard
    return RedirectResponse(url="/", status_code=303)


@app.post("/api/upload_pdf")
async def api_upload_pdf(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload PDF to knowledge base."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Read file content
    content = await file.read()
    
    # Save file to uploads directory
    file_path = os.path.join(UPLOADS_DIR, file.filename)
    try:
        with open(file_path, 'wb') as f:
            f.write(content)
        logger.info(f"PDF saved: {file.filename}")
    except Exception as e:
        logger.error(f"Error saving PDF: {str(e)}")
    
    # Process and upload to Pinecone
    result = process_pdf_and_upload(content, file.filename)
    
    # Get data for re-rendering
    tickets = get_all_tickets(db, "pending")  # Show pending by default
    stats = get_ticket_stats(db)
    uploaded_files = get_uploaded_files()
    
    # Return dashboard with upload tab active
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "tickets": tickets,
            "stats": stats,
            "filter": "pending",
            "tab": "upload",
            "uploaded_files": uploaded_files,
            "upload_message": result.get("message", ""),
            "upload_status": "success" if result["status"] == "success" else "error"
        }
    )


@app.post("/api/delete_pdf")
async def api_delete_pdf(filename: str = Form(...)):
    """Delete a PDF file from uploads."""
    try:
        file_path = os.path.join(UPLOADS_DIR, filename)
        
        # Security check - prevent path traversal
        if not os.path.abspath(file_path).startswith(os.path.abspath(UPLOADS_DIR)):
            raise HTTPException(status_code=400, detail="Invalid file path")
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            os.remove(file_path)
            logger.info(f"PDF deleted: {filename}")
        else:
            logger.warning(f"PDF not found: {filename}")
        
        # Redirect back to upload tab
        return RedirectResponse(url="/?tab=upload", status_code=303)
    except Exception as e:
        logger.error(f"Error deleting PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")



@app.delete("/api/tickets/{ticket_id}")
async def api_delete_ticket(ticket_id: str, db: Session = Depends(get_db)):
    """Delete a ticket."""
    from utils.ticket_manager import delete_ticket
    success = delete_ticket(db, ticket_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"status": "deleted"}


@app.get("/api/stats")
async def api_stats(db: Session = Depends(get_db)):
    """Get ticket statistics."""
    return get_ticket_stats(db)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.APP_VERSION}