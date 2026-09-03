import json
import hashlib
from typing import Optional


class ResponseCache:
    """Redis-backed response cache for cost efficiency."""
    
    def __init__(self, redis_client, ttl_seconds=3600):
        self.redis_client = redis_client
        self.ttl = ttl_seconds
    
    def _get_cache_key(self, question: str, user_id: str = "default") -> str:
        """Generate cache key from question and user ID."""
        key_str = f"{user_id}:{question}".lower()
        return f"cache:{hashlib.md5(key_str.encode()).hexdigest()}"
    
    def get(self, question: str, user_id: str = "default") -> Optional[dict]:
        """Retrieve cached response."""
        if not self.redis_client:
            return None
        
        try:
            cache_key = self._get_cache_key(question, user_id)
            cached = self.redis_client.get(cache_key)
            return json.loads(cached) if cached else None
        except Exception as e:
            print(f"Cache retrieval error: {e}")
            return None
    
    def set(self, question: str, response: dict, user_id: str = "default") -> bool:
        """Store response in cache."""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._get_cache_key(question, user_id)
            self.redis_client.setex(
                cache_key,
                self.ttl,
                json.dumps(response)
            )
            return True
        except Exception as e:
            print(f"Cache storage error: {e}")
            return False
