"""
SQLAlchemy models for Staff Server.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from database import Base
from datetime import datetime
import uuid


class Ticket(Base):
    """Support ticket model."""
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(36), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    query = Column(Text, nullable=False)
    extracted_text = Column(Text, nullable=True)
    file_info = Column(Text, nullable=True)  # JSON string of file info
    status = Column(String(20), default="pending")  # pending, resolved
    answer = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(100), nullable=True)
    
    def to_dict(self):
        """Convert to dictionary (summary)."""
        return {
            "ticket_id": self.ticket_id,
            "query": self.query[:100] + ("..." if len(self.query) > 100 else ""),
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "answer": self.answer[:100] + ("..." if self.answer and len(self.answer) > 100 else "") if self.answer else None
        }
    
    def to_full_dict(self):
        """Convert to dictionary (full details)."""
        result = self.to_dict()
        result["query"] = self.query
        result["extracted_text"] = self.extracted_text
        result["file_info"] = self.file_info
        result["resolved_at"] = self.resolved_at.isoformat() if self.resolved_at else None
        result["resolved_by"] = self.resolved_by
        return result