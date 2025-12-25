"""
Qdrant vector database connection and operations.
"""
import os
import requests
import logging
from typing import List, Dict, Optional
import numpy as np

logger = logging.getLogger(__name__)


class QdrantDB:
    """Qdrant vector database handler."""
    
    def __init__(self):
        """Initialize Qdrant connection."""
        self.host = os.getenv("QDRANT_HOST", "localhost")
        self.port = os.getenv("QDRANT_PORT", "6333")
        self.base_url = f"http://{self.host}:{self.port}"
        self.collection_name = "current_affairs"
        self.vector_size = 768
    
    def check_connection(self) -> bool:
        """Check if Qdrant is accessible."""
        try:
            response = requests.get(f"{self.base_url}/readyz", timeout=5)
            is_ready = response.status_code == 200
            if is_ready:
                logger.info(f"Connected to Qdrant at {self.base_url}")
            return is_ready
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            return False
    
    def create_collection(self):
        """Create the current_affairs collection if it doesn't exist."""
        # Check if collection exists
        try:
            response = requests.get(
                f"{self.base_url}/collections/{self.collection_name}",
                timeout=5
            )
            if response.status_code == 200:
                logger.info(f"Collection '{self.collection_name}' already exists")
                return True
        except Exception:
            pass
        
        # Create collection
        payload = {
            "vectors": {
                "size": self.vector_size,
                "distance": "Cosine"
            }
        }
        
        try:
            response = requests.put(
                f"{self.base_url}/collections/{self.collection_name}",
                json=payload,
                timeout=10
            )
            if response.status_code in [200, 201]:
                logger.info(f"Created collection '{self.collection_name}'")
                return True
            else:
                logger.error(f"Failed to create collection: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return False
    
    def mock_embedding(self, text: str) -> List[float]:
        """
        Generate a mock embedding vector.
        In production, this would use a real embedding model.
        """
        # Simple deterministic mock based on text hash
        np.random.seed(hash(text) % (2**32))
        embedding = np.random.randn(self.vector_size).tolist()
        return embedding
    
    def insert_article(self, article_id: str, text: str, metadata: Dict) -> bool:
        """
        Insert article embedding into Qdrant.
        Uses mock embeddings for now.
        """
        embedding = self.mock_embedding(text)
        
        payload = {
            "points": [
                {
                    "id": article_id,
                    "vector": embedding,
                    "payload": metadata
                }
            ]
        }
        
        try:
            response = requests.put(
                f"{self.base_url}/collections/{self.collection_name}/points",
                json=payload,
                timeout=10
            )
            if response.status_code in [200, 201]:
                logger.info(f"Inserted embedding for article: {article_id}")
                return True
            else:
                logger.error(f"Failed to insert embedding: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Failed to insert embedding: {e}")
            return False
    
    def search_similar(self, query_text: str, limit: int = 5) -> List[Dict]:
        """
        Search for similar articles.
        Uses mock embeddings for now.
        """
        query_vector = self.mock_embedding(query_text)
        
        payload = {
            "vector": query_vector,
            "limit": limit,
            "with_payload": True
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/collections/{self.collection_name}/points/search",
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get("result", [])
            else:
                logger.error(f"Failed to search: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Failed to search: {e}")
            return []

