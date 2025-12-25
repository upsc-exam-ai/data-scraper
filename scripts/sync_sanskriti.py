"""
Sync script for Sanskriti IAS current affairs.
Fetches articles and stores them in PostgreSQL.
"""
import logging
import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.sources.sanskriti import SanskritiIASSource
from app.db.postgres import PostgresDB

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging
log_file = LOGS_DIR / f'sanskriti_sync_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file)
    ]
)

logger = logging.getLogger(__name__)


def sync_sanskriti_ias(days_back: int = 30):
    """
    Sync Sanskriti IAS articles for the last N days.
    
    Args:
        days_back: Number of days to fetch (default 30 for 1 month)
    """
    logger.info("="*80)
    logger.info("SANSKRITI IAS SYNCER - STARTING")
    logger.info("="*80)
    logger.info(f"Fetching articles for the last {days_back} days")
    logger.info(f"Log file: {log_file}")
    
    # Initialize source
    source = SanskritiIASSource()
    
    # Initialize database
    db = PostgresDB()
    
    try:
        # Connect to database
        logger.info("Connecting to database...")
        db.connect()
        
        # Initialize schema
        logger.info("Initializing database schema...")
        db.init_schema()
        
        # Fetch articles
        logger.info("Fetching articles from Sanskriti IAS...")
        articles = source.fetch_articles(days_back=days_back)
        
        if not articles:
            logger.warning("No articles fetched!")
            return
        
        logger.info(f"Fetched {len(articles)} articles")
        
        # Insert articles into database
        logger.info("Inserting articles into database...")
        inserted_count = 0
        duplicate_count = 0
        error_count = 0
        
        for article in articles:
            try:
                success = db.insert_article(
                    published_date=article['published_date'],
                    source_url=article['source_url'],
                    article_json=article['article'],
                    attachments_json=article.get('attachments')
                )
                
                if success:
                    inserted_count += 1
                else:
                    duplicate_count += 1
                    
            except Exception as e:
                logger.error(f"Error inserting article: {e}")
                error_count += 1
        
        # Summary
        logger.info("="*80)
        logger.info("SYNC COMPLETE")
        logger.info("="*80)
        logger.info(f"Total articles processed: {len(articles)}")
        logger.info(f"Successfully inserted: {inserted_count}")
        logger.info(f"Duplicates skipped: {duplicate_count}")
        logger.info(f"Errors: {error_count}")
        logger.info("="*80)
        
        # Show sample of inserted articles
        if inserted_count > 0:
            logger.info("\nSample of inserted articles:")
            recent = db.get_articles(limit=5, source="Sanskriti IAS")
            for i, article in enumerate(recent, 1):
                logger.info(f"{i}. {article['article']['title']} - {article['published_date']}")
        
        logger.info(f"\nFull log saved to: {log_file}")
        
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.disconnect()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Sync Sanskriti IAS current affairs articles to PostgreSQL',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sync last 30 days (1 month)
  python scripts/sync_sanskriti.py --days 30
  
  # Sync last 7 days (1 week)
  python scripts/sync_sanskriti.py --days 7
  
  # Sync last 60 days (2 months)
  python scripts/sync_sanskriti.py --days 60
  
Note: Make sure PostgreSQL is running via docker-compose before running this script.
See README.md for setup instructions.
        """
    )
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days to fetch (default: 30)'
    )
    
    args = parser.parse_args()
    
    sync_sanskriti_ias(days_back=args.days)

