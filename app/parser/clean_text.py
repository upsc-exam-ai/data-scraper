"""
Text cleaning and normalization utilities.
"""
import re
from typing import Optional
import html


def clean_text(text: str) -> str:
    """
    Clean and normalize article text.
    
    Args:
        text: Raw HTML or text content
        
    Returns:
        Cleaned text string
    """
    if not text:
        return ""
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Remove HTML tags (basic cleanup)
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_paragraphs(text: str, min_length: int = 50) -> list[str]:
    """
    Extract meaningful paragraphs from text.
    
    Args:
        text: Cleaned text
        min_length: Minimum paragraph length
        
    Returns:
        List of paragraph strings
    """
    # Split by newlines and filter short paragraphs
    paragraphs = [p.strip() for p in text.split('\n') if len(p.strip()) >= min_length]
    return paragraphs


def remove_boilerplate(text: str) -> str:
    """
    Remove common boilerplate text from news articles.
    
    Args:
        text: Article text
        
    Returns:
        Text with boilerplate removed
    """
    # Common patterns to remove
    patterns = [
        r'Share this article.*?$',
        r'Subscribe to.*?$',
        r'Follow us on.*?$',
        r'Copyright \d{4}.*?$',
        r'All rights reserved.*?$',
    ]
    
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
    
    return text.strip()


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.
    
    Args:
        text: Input text
        
    Returns:
        Text with normalized whitespace
    """
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    
    # Replace multiple newlines with double newline
    text = re.sub(r'\n\n+', '\n\n', text)
    
    return text.strip()


def clean_article_text(raw_text: str) -> str:
    """
    Full pipeline for cleaning article text.
    
    Args:
        raw_text: Raw article text/HTML
        
    Returns:
        Cleaned and normalized text
    """
    text = clean_text(raw_text)
    text = remove_boilerplate(text)
    text = normalize_whitespace(text)
    return text

