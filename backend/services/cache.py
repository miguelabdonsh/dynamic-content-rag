"""
Redis Cache System - Simple and efficient
"""

import json
import hashlib
from typing import Optional, Dict, Any, List
import redis
from backend.config.settings import settings

class RAGCache:
    """Simple Redis cache for RAG operations"""
    
    def __init__(self):
        self.redis_client = redis.from_url(
            settings.REDIS_URL, 
            decode_responses=True,
            socket_timeout=settings.REDIS_TIMEOUT
        )
    
    def _generate_key(self, prefix: str, content: str) -> str:
        """Generate cache key"""
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        return f"{prefix}:{content_hash}"
    
    def cache_query_result(self, query: str, result: Dict[str, Any]) -> None:
        """Cache complete query result"""
        try:
            key = self._generate_key("query", query)
            self.redis_client.setex(
                key, 
                settings.CACHE_TTL, 
                json.dumps(result)
            )
        except Exception:
            pass
    
    def get_cached_query_result(self, query: str) -> Optional[Dict[str, Any]]:
        """Get cached query result"""
        try:
            key = self._generate_key("query", query)
            cached = self.redis_client.get(key)
            if cached:
                return json.loads(cached)
        except Exception:
            pass
        return None
    
    def cache_embedding(self, text: str, embedding: List[float]) -> None:
        """Cache text embedding"""
        try:
            key = self._generate_key("embedding", text)
            self.redis_client.setex(
                key,
                86400,  # 24 hours
                json.dumps(embedding)
            )
        except Exception:
            pass
    
    def get_cached_embedding(self, text: str) -> Optional[List[float]]:
        """Get cached embedding"""
        try:
            key = self._generate_key("embedding", text)
            cached = self.redis_client.get(key)
            if cached:
                return json.loads(cached)
        except Exception:
            pass
        return None
    
    def is_connected(self) -> bool:
        """Check Redis connection"""
        try:
            self.redis_client.ping()
            return True
        except Exception:
            return False

# Global cache instance
cache = RAGCache() 