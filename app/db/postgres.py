"""
PostgreSQL database connection and operations.
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class PostgresDB:
    """PostgreSQL database handler."""
    
    def __init__(self):
        """Initialize database connection."""
        self.conn = None
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.port = os.getenv("POSTGRES_PORT", "5432")
        self.database = os.getenv("POSTGRES_DB", "upsc_postgres")
        self.user = os.getenv("POSTGRES_USER", "upsc_db_admin")
        self.password = os.getenv("POSTGRES_PASSWORD", "upsc_sanjeet@1729")
    
    def connect(self):
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            logger.info(f"Connected to PostgreSQL at {self.host}:{self.port}/{self.database}")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    def disconnect(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Disconnected from PostgreSQL")
    
    def init_schema(self):
        """Initialize database schema."""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS news_articles (
            id UUID PRIMARY KEY,
            source TEXT NOT NULL,
            title TEXT NOT NULL,
            published_date DATE NOT NULL,
            url TEXT UNIQUE,
            raw_text TEXT,
            cleaned_text TEXT,
            created_at TIMESTAMP DEFAULT now()
        );
        
        CREATE INDEX IF NOT EXISTS idx_news_articles_source ON news_articles(source);
        CREATE INDEX IF NOT EXISTS idx_news_articles_published_date ON news_articles(published_date);
        CREATE INDEX IF NOT EXISTS idx_news_articles_url ON news_articles(url);
        """
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(schema_sql)
                self.conn.commit()
                logger.info("Database schema initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            self.conn.rollback()
            raise
    
    def article_exists(self, url: str) -> bool:
        """Check if article with given URL already exists."""
        query = "SELECT EXISTS(SELECT 1 FROM news_articles WHERE url = %s)"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (url,))
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Failed to check article existence: {e}")
            return False
    
    def insert_article(self, article_dict: Dict) -> bool:
        """
        Insert article into database.
        Returns True if inserted, False if duplicate.
        """
        # Check for duplicate first
        if self.article_exists(article_dict["url"]):
            logger.info(f"Article already exists: {article_dict['url']}")
            return False
        
        query = """
        INSERT INTO news_articles (id, source, title, published_date, url, raw_text, cleaned_text, created_at)
        VALUES (%(id)s, %(source)s, %(title)s, %(published_date)s, %(url)s, %(raw_text)s, %(cleaned_text)s, %(created_at)s)
        ON CONFLICT (url) DO NOTHING
        """
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, article_dict)
                self.conn.commit()
                logger.info(f"Inserted article: {article_dict['title']}")
                return True
        except Exception as e:
            logger.error(f"Failed to insert article: {e}")
            self.conn.rollback()
            return False
    
    def get_articles(self, limit: int = 10) -> List[Dict]:
        """Retrieve recent articles."""
        query = """
        SELECT * FROM news_articles 
        ORDER BY published_date DESC 
        LIMIT %s
        """
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, (limit,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to retrieve articles: {e}")
            return []
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

