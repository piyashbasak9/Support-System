"""
Ticket management utilities.
"""

import json
from sqlalchemy.orm import Session
from models import Ticket
from datetime import datetime
from typing import Optional


def create_ticket(
    db: Session,
    ticket_id: str,
    query: str,
    extracted_text: str = "",
    file_info: Optional[dict] = None
) -> Ticket:
    """Create a new ticket."""
    ticket = Ticket(
        ticket_id=ticket_id,
        query=query,
        extracted_text=extracted_text,
        file_info=json.dumps(file_info) if file_info else None,
        status="pending"
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def resolve_ticket(
    db: Session,
    ticket_id: str,
    answer: str,
    resolved_by: str = "staff"
) -> bool:
    """Resolve a ticket with the provided answer."""
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if ticket:
        ticket.status = "resolved"
        ticket.answer = answer
        ticket.resolved_at = datetime.utcnow()
        ticket.resolved_by = resolved_by
        db.commit()
        return True
    return False


def get_all_tickets(db: Session, status: Optional[str] = None):
    """Get all tickets, optionally filtered by status."""
    query = db.query(Ticket).order_by(Ticket.created_at.desc())
    if status:
        query = query.filter(Ticket.status == status)
    return query.all()


def get_ticket_by_id(db: Session, ticket_id: str):
    """Get a single ticket by ID."""
    return db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()


def delete_ticket(db: Session, ticket_id: str) -> bool:
    """Delete a ticket."""
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if ticket:
        db.delete(ticket)
        db.commit()
        return True
    return False


def get_ticket_stats(db: Session) -> dict:
    """Get ticket statistics."""
    total = db.query(Ticket).count()
    pending = db.query(Ticket).filter(Ticket.status == "pending").count()
    resolved = db.query(Ticket).filter(Ticket.status == "resolved").count()
    
    return {
        "total": total,
        "pending": pending,
        "resolved": resolved,
        "resolution_rate": (resolved / total * 100) if total > 0 else 0
    }