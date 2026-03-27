"""
Client for sending tickets to Staff Server.
"""

import requests
import logging
from typing import Optional
from user_server.config import settings

logger = logging.getLogger(__name__)


def create_ticket(ticket_id: str, query: str, extracted_text: str = "", file_info: Optional[dict] = None) -> bool:
    """
    Send ticket data to Staff Server API.
    
    Args:
        ticket_id: Unique ticket identifier
        query: User's original query
        extracted_text: Text extracted from uploaded file
        file_info: Optional file metadata
        
    Returns:
        True if successful, False otherwise
    """
    payload = {
        "ticket_id": ticket_id,
        "query": query,
        "extracted_text": extracted_text,
    }
    
    if file_info:
        payload["file_info"] = file_info
    
    try:
        response = requests.post(
            settings.STAFF_SERVER_URL,
            data=payload,
            timeout=10
        )
        
        if response.status_code == 201:
            logger.info(f"Ticket {ticket_id} created successfully")
            return True
        else:
            logger.error(f"Failed to create ticket: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("Timeout while creating ticket")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("Connection error while creating ticket")
        return False
    except Exception as e:
        logger.error(f"Unexpected error creating ticket: {str(e)}")
        return False