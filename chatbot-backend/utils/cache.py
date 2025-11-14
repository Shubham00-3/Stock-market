"""Response caching using Redis."""
import json
import hashlib
import logging
from typing import Any, Optional
from .redis_client import redis_client

logger = logging.getLogger(__name__)


class ResponseCache:
    """Cache for API and tool responses using Redis."""
    
    def __init__(self, default_ttl: int = 300):
        """
        Initialize response cache.
        
        Args:
            default_ttl: Default TTL in seconds (default: 300 = 5 minutes)
        """
        self.default_ttl = default_ttl
        self.enabled = redis_client.is_available
        
        if not self.enabled:
            logger.warning("ResponseCache initialized but Redis is not available")
    
    def _make_key(self, prefix: str, **kwargs) -> str:
        """
        Create a consistent cache key from prefix and arguments.
        
        Args:
            prefix: Key prefix (e.g., tool name)
            **kwargs: Arguments to hash
            
        Returns:
            Cache key string
        """
        # Sort kwargs to ensure consistent ordering
        sorted_items = sorted(kwargs.items())
        
        # Create a string representation
        key_data = json.dumps(sorted_items, sort_keys=True)
        
        # Hash the data
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()[:16]
        
        # Combine prefix and hash
        return f"cache:{prefix}:{key_hash}"
    
    def get(self, prefix: str, **kwargs) -> Optional[Any]:
        """
        Get cached value.
        
        Args:
            prefix: Key prefix
            **kwargs: Arguments that were used to generate the cached value
            
        Returns:
            Cached value or None if not found
        """
        if not self.enabled:
            return None
        
        try:
            key = self._make_key(prefix, **kwargs)
            cached = redis_client.get(key)
            
            if cached:
                logger.debug(f"Cache HIT for {prefix}")
                return json.loads(cached)
            
            logger.debug(f"Cache MISS for {prefix}")
            return None
            
        except Exception as e:
            logger.error(f"Cache GET error: {str(e)}")
            return None
    
    def set(self, prefix: str, value: Any, ttl: Optional[int] = None, **kwargs) -> bool:
        """
        Set cached value.
        
        Args:
            prefix: Key prefix
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (uses default_ttl if not specified)
            **kwargs: Arguments used to generate the value
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            key = self._make_key(prefix, **kwargs)
            value_json = json.dumps(value)
            ttl = ttl or self.default_ttl
            
            success = redis_client.set(key, value_json, ex=ttl)
            
            if success:
                logger.debug(f"Cache SET for {prefix} (TTL: {ttl}s)")
            
            return success
            
        except Exception as e:
            logger.error(f"Cache SET error: {str(e)}")
            return False
    
    def delete(self, prefix: str, **kwargs) -> bool:
        """
        Delete cached value.
        
        Args:
            prefix: Key prefix
            **kwargs: Arguments used to generate the value
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            key = self._make_key(prefix, **kwargs)
            success = redis_client.delete(key)
            
            if success:
                logger.debug(f"Cache DELETE for {prefix}")
            
            return success
            
        except Exception as e:
            logger.error(f"Cache DELETE error: {str(e)}")
            return False
    
    def clear_prefix(self, prefix: str) -> bool:
        """
        Clear all cache entries with a given prefix.
        Note: This is not implemented as it requires Redis SCAN which is not
        available in the basic Upstash Redis client. Use individual deletes instead.
        
        Args:
            prefix: Key prefix to clear
            
        Returns:
            False (not implemented)
        """
        logger.warning(f"clear_prefix not implemented for prefix: {prefix}")
        return False

