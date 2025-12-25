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
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        
        CREATE TABLE IF NOT EXISTS ca_articles (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            published_date DATE NOT NULL,
            source_url TEXT NOT NULL UNIQUE,
            article JSONB NOT NULL,
            attachments JSONB,
            created_at TIMESTAMP DEFAULT now()
        );
        
        CREATE INDEX IF NOT EXISTS idx_ca_articles_published_date ON ca_articles(published_date);
        CREATE INDEX IF NOT EXISTS idx_ca_articles_source_url ON ca_articles(source_url);
        CREATE INDEX IF NOT EXISTS idx_ca_articles_source ON ca_articles USING GIN ((article->'source'));
        CREATE INDEX IF NOT EXISTS idx_ca_articles_title ON ca_articles USING GIN (to_tsvector('english', article->>'title'));
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
    
    def article_exists(self, source_url: str) -> bool:
        """Check if article with given source URL already exists."""
        query = "SELECT EXISTS(SELECT 1 FROM ca_articles WHERE source_url = %s)"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (source_url,))
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Failed to check article existence: {e}")
            return False
    
    def insert_article(self, published_date: str, source_url: str, article_json: Dict, attachments_json: Optional[Dict] = None) -> bool:
        """
        Insert article into database.
        
        Args:
            published_date: Date string in YYYY-MM-DD format
            source_url: Original article URL
            article_json: Article content in standardized JSON format
            attachments_json: Optional attachments (images, PDFs, etc.)
            
        Returns:
            True if inserted, False if duplicate
        """
        # Check for duplicate first
        if self.article_exists(source_url):
            logger.info(f"Article already exists: {source_url}")
            return False
        
        query = """
        INSERT INTO ca_articles (published_date, source_url, article, attachments)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (source_url) DO NOTHING
        RETURNING id
        """
        
        try:
            import json
            with self.conn.cursor() as cursor:
                cursor.execute(query, (
                    published_date,
                    source_url,
                    json.dumps(article_json),
                    json.dumps(attachments_json) if attachments_json else None
                ))
                self.conn.commit()
                result = cursor.fetchone()
                if result:
                    logger.info(f"Inserted article: {article_json.get('title', 'Unknown')}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to insert article: {e}")
            self.conn.rollback()
            return False
    
    def get_articles(self, limit: int = 10, source: Optional[str] = None) -> List[Dict]:
        """
        Retrieve recent articles.
        
        Args:
            limit: Maximum number of articles to retrieve
            source: Optional filter by source name
            
        Returns:
            List of article dictionaries
        """
        if source:
            query = """
            SELECT * FROM ca_articles 
            WHERE article->>'source' = %s
            ORDER BY published_date DESC 
            LIMIT %s
            """
            params = (source, limit)
        else:
            query = """
            SELECT * FROM ca_articles 
            ORDER BY published_date DESC 
            LIMIT %s
            """
            params = (limit,)
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
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

