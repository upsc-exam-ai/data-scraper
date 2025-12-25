"""
Base interface for news sources.
"""
from abc import ABC, abstractmethod
from typing import List
from datetime import datetime
from ..models.article import Article


class NewsSource(ABC):
    """Abstract base class for news sources."""
    
    def __init__(self, source_name: str):
        """
        Initialize news source.
        
        Args:
            source_name: Name identifier for this source
        """
        self.source_name = source_name
    
    @abstractmethod
    def fetch_articles(self, days_back: int = 7) -> List[Article]:
        """
        Fetch articles from this source.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            List of Article objects
        """
        pass
    
    @abstractmethod
    def parse_article(self, raw_data: dict) -> Article:
        """
        Parse raw article data into Article object.
        
        Args:
            raw_data: Raw article data from source
            
        Returns:
            Article object
        """
        pass
    
    def validate_article(self, article: Article) -> bool:
        """
        Validate article data.
        
        Args:
            article: Article to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if not article.title or len(article.title) < 10:
                return False
            if not article.url:
                return False
            if not article.raw_text or len(article.raw_text) < 50:
                return False
            return True
        except Exception:
            return False

