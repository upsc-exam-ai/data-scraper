"""
Sync orchestration - coordinates fetching and storing articles.
"""
import logging
from typing import List
from .sources.base import NewsSource
from .sources.pib import PIBSource
from .db.postgres import PostgresDB
from .db.qdrant import QdrantDB
from .models.article import Article

logger = logging.getLogger(__name__)


class SyncOrchestrator:
    """Orchestrates the syncing process across sources and databases."""
    
    def __init__(self):
        """Initialize orchestrator with sources and databases."""
        self.sources: List[NewsSource] = [
            PIBSource(),
            # Add more sources here as needed
        ]
        self.pg_db = PostgresDB()
        self.qdrant_db = QdrantDB()
    
    def sync(self, days_back: int = 7):
        """
        Main sync operation.
        
        Args:
            days_back: Number of days to look back for articles
        """
        logger.info("=" * 60)
        logger.info("Starting sync operation")
        logger.info("=" * 60)
        
        # Connect to databases
        try:
            self.pg_db.connect()
            self.pg_db.init_schema()
            
            if not self.qdrant_db.check_connection():
                logger.error("Qdrant is not available, skipping vector storage")
                qdrant_available = False
            else:
                self.qdrant_db.create_collection()
                qdrant_available = True
            
        except Exception as e:
            logger.error(f"Failed to initialize databases: {e}")
            return
        
        # Sync from each source
        total_fetched = 0
        total_inserted = 0
        
        try:
            for source in self.sources:
                logger.info(f"\n--- Syncing from {source.source_name} ---")
                
                # Fetch articles
                articles = source.fetch_articles(days_back=days_back)
                total_fetched += len(articles)
                logger.info(f"Fetched {len(articles)} articles from {source.source_name}")
                
                # Store articles
                for article in articles:
                    try:
                        # Insert into PostgreSQL
                        inserted = self.pg_db.insert_article(article.to_dict())
                        
                        if inserted:
                            total_inserted += 1
                            
                            # Insert into Qdrant (if available)
                            if qdrant_available:
                                metadata = {
                                    "source": article.source,
                                    "title": article.title,
                                    "url": article.url,
                                    "published_date": article.published_date.isoformat()
                                }
                                self.qdrant_db.insert_article(
                                    article.id,
                                    article.cleaned_text or article.raw_text,
                                    metadata
                                )
                    
                    except Exception as e:
                        logger.error(f"Failed to store article '{article.title}': {e}")
                        continue
            
            logger.info("\n" + "=" * 60)
            logger.info(f"Sync complete!")
            logger.info(f"Total fetched: {total_fetched}")
            logger.info(f"Total inserted: {total_inserted}")
            logger.info(f"Duplicates skipped: {total_fetched - total_inserted}")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Sync operation failed: {e}")
            raise
        
        finally:
            # Disconnect from databases
            self.pg_db.disconnect()
    
    def test_sources(self):
        """Test connectivity to all sources."""
        logger.info("Testing news sources...")
        
        for source in self.sources:
            try:
                articles = source.fetch_articles(days_back=1)
                logger.info(f"✓ {source.source_name}: OK ({len(articles)} articles)")
            except Exception as e:
                logger.error(f"✗ {source.source_name}: FAILED - {e}")
    
    def test_databases(self):
        """Test connectivity to databases."""
        logger.info("Testing databases...")
        
        # Test PostgreSQL
        try:
            self.pg_db.connect()
            self.pg_db.init_schema()
            self.pg_db.disconnect()
            logger.info("✓ PostgreSQL: OK")
        except Exception as e:
            logger.error(f"✗ PostgreSQL: FAILED - {e}")
        
        # Test Qdrant
        try:
            if self.qdrant_db.check_connection():
                logger.info("✓ Qdrant: OK")
            else:
                logger.error("✗ Qdrant: FAILED - Not reachable")
        except Exception as e:
            logger.error(f"✗ Qdrant: FAILED - {e}")

