"""
Quick test script to verify Sanskriti IAS scraper works.
Tests with just 2 days of data.
"""
import logging
import sys
from datetime import datetime
from app.sources.sanskriti import SanskritiIASSource

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


def test_sanskriti_source():
    """Test the Sanskriti IAS source."""
    logger.info("="*80)
    logger.info("TESTING SANSKRITI IAS SOURCE")
    logger.info("="*80)
    
    source = SanskritiIASSource()
    
    # Test URL generation
    test_date = datetime(2025, 12, 20)
    url = source.generate_date_url(test_date)
    logger.info(f"Test URL: {url}")
    
    # Fetch articles for 2 days
    logger.info("\nFetching articles for last 2 days...")
    articles = source.fetch_articles(days_back=2)
    
    logger.info(f"\nTotal articles fetched: {len(articles)}")
    
    if articles:
        logger.info("\nFirst article sample:")
        article = articles[0]
        logger.info(f"Published Date: {article['published_date']}")
        logger.info(f"Source URL: {article['source_url']}")
        logger.info(f"Title: {article['article']['title']}")
        logger.info(f"Source: {article['article']['source']}")
        logger.info(f"Content sections: {len(article['article']['content'])}")
        logger.info(f"FAQs: {len(article['article']['faqs'])}")
        logger.info(f"Images: {len(article['article']['images'])}")
        
        if article['article']['metadata']:
            logger.info(f"\nMetadata:")
            logger.info(f"  Prelims: {article['article']['metadata'].get('prelims')}")
            logger.info(f"  Mains: {article['article']['metadata'].get('mains')}")
        
        if article['article']['content']:
            logger.info(f"\nFirst section:")
            first_section = article['article']['content'][0]
            logger.info(f"  Heading: {first_section['heading']}")
            logger.info(f"  Subheading: {first_section['subheading']}")
            logger.info(f"  Content preview: {first_section['content'][:150]}...")
    
    logger.info("\n" + "="*80)
    logger.info("TEST COMPLETE")
    logger.info("="*80)


if __name__ == "__main__":
    test_sanskriti_source()

