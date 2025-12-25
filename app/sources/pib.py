"""
PIB (Press Information Bureau) news source.
Fetches articles from PIB RSS feed.
"""
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List
import logging
from .base import NewsSource
from ..models.article import Article
from ..parser.clean_text import clean_article_text

logger = logging.getLogger(__name__)


class PIBSource(NewsSource):
    """Press Information Bureau news source."""
    
    def __init__(self):
        """Initialize PIB source."""
        super().__init__("PIB")
        self.rss_url = "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3"
        # Alternative: "https://pib.gov.in/allRss.aspx"
    
    def fetch_articles(self, days_back: int = 7) -> List[Article]:
        """
        Fetch articles from PIB RSS feed.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            List of Article objects
        """
        articles = []
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        try:
            logger.info(f"Fetching PIB articles from RSS feed...")
            response = requests.get(self.rss_url, timeout=30)
            response.raise_for_status()
            
            # Parse RSS XML
            root = ET.fromstring(response.content)
            
            # Find all item elements
            items = root.findall('.//item')
            logger.info(f"Found {len(items)} items in RSS feed")
            
            for item in items:
                try:
                    article = self._parse_rss_item(item)
                    
                    # Filter by date
                    if article.published_date >= cutoff_date:
                        if self.validate_article(article):
                            articles.append(article)
                        else:
                            logger.warning(f"Invalid article: {article.title}")
                except Exception as e:
                    logger.error(f"Failed to parse RSS item: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(articles)} valid articles from PIB")
            return articles
            
        except Exception as e:
            logger.error(f"Failed to fetch PIB articles: {e}")
            return []
    
    def _parse_rss_item(self, item: ET.Element) -> Article:
        """
        Parse RSS item into Article.
        
        Args:
            item: XML element representing an RSS item
            
        Returns:
            Article object
        """
        title = item.findtext('title', '').strip()
        link = item.findtext('link', '').strip()
        description = item.findtext('description', '').strip()
        pub_date_str = item.findtext('pubDate', '')
        
        # Parse publication date
        try:
            # RSS date format: "Wed, 18 Dec 2024 12:00:00 GMT"
            pub_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %Z')
        except Exception:
            # Fallback to current date if parsing fails
            pub_date = datetime.now()
            logger.warning(f"Failed to parse date: {pub_date_str}, using current date")
        
        # Clean the description/content
        raw_text = description
        cleaned_text = clean_article_text(raw_text)
        
        return Article(
            source=self.source_name,
            title=title,
            published_date=pub_date,
            url=link,
            raw_text=raw_text,
            cleaned_text=cleaned_text
        )
    
    def parse_article(self, raw_data: dict) -> Article:
        """
        Parse raw article data (not used for RSS, kept for interface compliance).
        
        Args:
            raw_data: Raw article data
            
        Returns:
            Article object
        """
        return Article(
            source=self.source_name,
            title=raw_data.get('title', ''),
            published_date=raw_data.get('published_date', datetime.now()),
            url=raw_data.get('url', ''),
            raw_text=raw_data.get('raw_text', ''),
            cleaned_text=raw_data.get('cleaned_text', '')
        )

