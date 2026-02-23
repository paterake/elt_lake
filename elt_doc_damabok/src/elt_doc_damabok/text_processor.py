"""Text processing utilities for DMBOK RAG system.

This module contains pure functions for PDF text extraction and chunking
that don't require chromadb or other heavy dependencies.
"""

from __future__ import annotations

import logging
from pathlib import Path

from pypdf import PdfReader

from elt_doc_damabok.constants import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE

logger = logging.getLogger(__name__)


def _extract_pages(pdf_path: Path) -> list[str]:
    """Extract text from PDF pages.
    
    Args:
        pdf_path: Path to the PDF file.
        
    Returns:
        List of text strings, one per page.
        
    Raises:
        FileNotFoundError: If PDF file does not exist.
        RuntimeError: If PDF extraction fails.
    """
    logger.info("Extracting text from PDF: %s", pdf_path)
    
    if not pdf_path.exists():
        logger.error("PDF file not found: %s", pdf_path)
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    try:
        reader = PdfReader(str(pdf_path))
        pages: list[str] = []
        
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                # Normalize whitespace
                normalized = " ".join(text.split())
                pages.append(normalized)
                logger.debug("Extracted page %d: %d characters", i, len(normalized))
        
        logger.info("Extracted %d pages from PDF", len(pages))
        return pages
        
    except Exception as e:
        logger.error("Failed to extract PDF: %s", e)
        raise RuntimeError(f"Failed to extract PDF: {e}")


def _chunk_pages(
    pages: list[str],
    max_chars: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    """Split pages into overlapping chunks.
    
    Args:
        pages: List of page text strings.
        max_chars: Maximum characters per chunk.
        overlap: Overlap between consecutive chunks.
        
    Returns:
        List of chunk strings.
        
    Raises:
        ValueError: If chunking parameters are invalid.
    """
    if overlap >= max_chars:
        raise ValueError(
            f"chunk_overlap ({overlap}) must be less than chunk_size ({max_chars})"
        )
    
    logger.info(
        "Chunking %d pages with chunk_size=%d, overlap=%d",
        len(pages),
        max_chars,
        overlap,
    )
    
    chunks: list[str] = []
    
    for page_idx, page in enumerate(pages, start=1):
        start = 0
        while start < len(page):
            end = start + max_chars
            chunk = page[start:end]
            
            if chunk.strip():
                chunks.append(chunk)
                logger.debug(
                    "Created chunk %d from page %d: %d characters",
                    len(chunks),
                    page_idx,
                    len(chunk),
                )
            
            if end >= len(page):
                break
            start = end - overlap
    
    logger.info("Created %d chunks from %d pages", len(chunks), len(pages))
    return chunks
