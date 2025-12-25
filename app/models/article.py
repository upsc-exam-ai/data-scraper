"""
Article data model.
Represents a news article from various sources.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Article:
    """Represents a news article."""
    
    source: str
    title: str
    published_date: datetime
    url: str
    raw_text: str
    cleaned_text: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate article data."""
        if not self.source:
            raise ValueError("Source cannot be empty")
        if not self.title:
            raise ValueError("Title cannot be empty")
        if not self.url:
            raise ValueError("URL cannot be empty")
    
    def to_dict(self):
        """Convert article to dictionary for database insertion."""
        return {
            "id": self.id,
            "source": self.source,
            "title": self.title,
            "published_date": self.published_date.date(),
            "url": self.url,
            "raw_text": self.raw_text,
            "cleaned_text": self.cleaned_text,
            "created_at": self.created_at
        }

