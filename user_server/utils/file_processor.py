"""
File processing utilities for PDF and images.
"""

import io
import pdfplumber
from PIL import Image
import pytesseract
from typing import Optional


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract all text from a PDF file.
    
    Args:
        file_bytes: PDF file bytes
        
    Returns:
        Extracted text as string
    """
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {str(e)}")


def extract_text_from_image(file_bytes: bytes) -> str:
    """
    Extract text from image using OCR (Tesseract).
    
    Args:
        file_bytes: Image file bytes
        
    Returns:
        Extracted text as string
    """
    try:
        image = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from image: {str(e)}")


def validate_file_size(file_bytes: bytes, max_size_mb: int = 10) -> bool:
    """
    Validate file size.
    
    Args:
        file_bytes: File bytes
        max_size_mb: Maximum allowed size in MB
        
    Returns:
        True if valid, False otherwise
    """
    size_mb = len(file_bytes) / (1024 * 1024)
    return size_mb <= max_size_mb


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.
    
    Args:
        filename: Filename string
        
    Returns:
        File extension (lowercase, with dot)
    """
    import os
    _, ext = os.path.splitext(filename)
    return ext.lower()