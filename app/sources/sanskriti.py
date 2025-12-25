"""
Sanskriti IAS news source.
Fetches current affairs articles from Sanskriti IAS website.
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import time

logger = logging.getLogger(__name__)


class SanskritiIASSource:
    """Sanskriti IAS current affairs source."""
    
    def __init__(self):
        """Initialize Sanskriti IAS source."""
        self.source_name = "Sanskriti IAS"
        self.base_url = "https://www.sanskritiias.com/current-affairs/date/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def generate_date_url(self, date: datetime) -> str:
        """
        Generate URL for a specific date.
        
        Args:
            date: Date to fetch articles for
            
        Returns:
            URL string
        """
        # Format: https://www.sanskritiias.com/current-affairs/date/20-December-2025
        # Remove leading zero from day (cross-platform compatible)
        day = str(date.day)  # No leading zero
        month = date.strftime('%B')  # Full month name
        year = date.strftime('%Y')  # Year
        return f"{self.base_url}{day}-{month}-{year}"
    
    def fetch_articles_for_date(self, date: datetime) -> List[Dict]:
        """
        Fetch all articles for a specific date.
        
        Args:
            date: Date to fetch articles for
            
        Returns:
            List of article dictionaries in standardized format
        """
        url = self.generate_date_url(date)
        logger.info(f"Fetching articles from: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Find all article containers
            article_divs = soup.find_all('div', class_='blog')
            
            if not article_divs:
                logger.warning(f"No articles found for date: {date.strftime('%Y-%m-%d')}")
                return []
            
            logger.info(f"Found {len(article_divs)} articles for {date.strftime('%Y-%m-%d')}")
            
            articles = []
            for article_div in article_divs:
                try:
                    article_data = self._extract_article(article_div, date)
                    if article_data:
                        articles.append(article_data)
                except Exception as e:
                    logger.error(f"Failed to extract article: {e}")
                    continue
            
            return articles
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch page for {date.strftime('%Y-%m-%d')}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error processing date {date.strftime('%Y-%m-%d')}: {e}")
            return []
    
    def _extract_article(self, article_div, date: datetime) -> Optional[Dict]:
        """
        Extract a single article from HTML.
        
        Args:
            article_div: BeautifulSoup div element
            date: Publication date
            
        Returns:
            Article dictionary in standardized format or None
        """
        # Extract title and URL
        h4 = article_div.find('h4')
        if not h4:
            return None
        
        title_link = h4.find('a', class_='text-danger')
        if not title_link:
            return None
        
        title = title_link.text.strip()
        article_url = title_link.get('href', '')
        
        if not title or not article_url:
            return None
        
        # Extract metadata (Prelims/Mains tags)
        metadata = self._extract_metadata(article_div)
        
        # Extract content sections
        content = self._extract_content(article_div)
        
        # Extract FAQs
        faqs = self._extract_faqs(article_div)
        
        # Extract images
        images = self._extract_images(article_div)
        
        # Build standardized article JSON
        article_json = {
            "title": title,
            "source": self.source_name,
            "metadata": metadata,
            "content": content,
            "faqs": faqs,
            "images": images,
            "extracted_at": datetime.now().isoformat()
        }
        
        return {
            "published_date": date.strftime('%Y-%m-%d'),
            "source_url": article_url,
            "article": article_json,
            "attachments": {"images": images} if images else None
        }
    
    def _extract_metadata(self, article_div) -> Dict:
        """Extract Prelims/Mains metadata."""
        metadata = {
            "prelims": None,
            "mains": None,
            "tags": []
        }
        
        # Find metadata table
        table = article_div.find('table', class_='table-bordered')
        if table:
            td = table.find('td')
            if td:
                text = td.get_text(separator='\n', strip=True)
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                
                for line in lines:
                    if line.startswith('Prelims:'):
                        metadata['prelims'] = line.replace('Prelims:', '').strip()
                    elif 'Mains' in line and (':' in line or ',' in line):
                        # Handle both "Mains:" and "Mains,"
                        metadata['mains'] = line.replace('Mains:', '').replace('Mains,', '').strip()
        
        return metadata
    
    def _extract_content(self, article_div) -> List[Dict]:
        """Extract content sections."""
        content = []
        
        # Find all H2 tags (main sections)
        h2_tags = article_div.find_all('h2')
        
        for h2 in h2_tags:
            section_heading = h2.get_text(strip=True)
            
            # Skip FAQs section (handled separately)
            if section_heading.upper() == 'FAQS':
                continue
            
            # Collect content until next H2 or H4
            section_content = []
            current_subheading = None
            
            current = h2.find_next_sibling()
            while current and current.name not in ['h2', 'h4']:
                if current.name == 'h3':
                    # New subsection
                    if section_content:
                        # Save previous subsection
                        content.append({
                            "heading": section_heading,
                            "subheading": current_subheading,
                            "content": '\n\n'.join(section_content)
                        })
                        section_content = []
                    current_subheading = current.get_text(strip=True)
                
                elif current.name == 'p':
                    text = current.get_text(strip=True)
                    if text:
                        section_content.append(text)
                
                elif current.name in ['ul', 'ol']:
                    # Convert list to text with bullets
                    items = []
                    for li in current.find_all('li', recursive=False):
                        item_text = li.get_text(strip=True)
                        if item_text:
                            items.append(f"• {item_text}")
                    if items:
                        section_content.append('\n'.join(items))
                
                current = current.find_next_sibling()
            
            # Add the last subsection/section
            if section_content:
                content.append({
                    "heading": section_heading,
                    "subheading": current_subheading,
                    "content": '\n\n'.join(section_content)
                })
        
        return content
    
    def _extract_faqs(self, article_div) -> List[Dict]:
        """Extract FAQ section."""
        faqs = []
        
        # Find FAQ H2
        faq_h2 = None
        for h2 in article_div.find_all('h2'):
            if h2.get_text(strip=True).upper() == 'FAQS':
                faq_h2 = h2
                break
        
        if not faq_h2:
            return faqs
        
        # Extract Q&A pairs
        current = faq_h2.find_next_sibling()
        current_question = None
        current_answer = []
        
        while current and current.name not in ['h2', 'h4']:
            if current.name == 'p':
                text = current.get_text(strip=True)
                # Check if it's a question
                strong = current.find('strong')
                if strong and ('Q' in text[:5] or 'Q.' in text[:5]):
                    # Save previous Q&A
                    if current_question:
                        faqs.append({
                            "question": current_question,
                            "answer": ' '.join(current_answer)
                        })
                    current_question = text
                    current_answer = []
                else:
                    # It's an answer
                    if text:
                        current_answer.append(text)
            
            current = current.find_next_sibling()
        
        # Add last Q&A
        if current_question:
            faqs.append({
                "question": current_question,
                "answer": ' '.join(current_answer)
            })
        
        return faqs
    
    def _extract_images(self, article_div) -> List[Dict]:
        """Extract images from article."""
        images = []
        
        img_tags = article_div.find_all('img', class_='img-fluid')
        for img in img_tags:
            img_src = img.get('src', '')
            # Only include content images
            if 'uploaded_files/images' in img_src:
                img_data = {
                    "url": img_src,
                    "alt": img.get('alt', ''),
                    "caption": ""
                }
                
                # Try to get caption from parent link
                parent_link = img.find_parent('a')
                if parent_link:
                    img_data['caption'] = parent_link.get('title', '')
                
                images.append(img_data)
        
        return images
    
    def fetch_articles(self, days_back: int = 30) -> List[Dict]:
        """
        Fetch articles for the last N days.
        
        Args:
            days_back: Number of days to fetch (default 30 for 1 month)
            
        Returns:
            List of article dictionaries
        """
        all_articles = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        logger.info(f"Fetching articles from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        current_date = start_date
        while current_date <= end_date:
            logger.info(f"Processing date: {current_date.strftime('%Y-%m-%d')}")
            
            articles = self.fetch_articles_for_date(current_date)
            all_articles.extend(articles)
            
            # Be nice to the server
            time.sleep(1)
            
            current_date += timedelta(days=1)
        
        logger.info(f"Total articles fetched: {len(all_articles)}")
        return all_articles

