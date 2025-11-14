"""Redis client singleton for Upstash Redis connection."""
import os
import logging
from typing import Optional
from upstash_redis import Redis

logger = logging.getLogger(__name__)


class RedisClient:
    """Singleton Redis client for Upstash Redis."""
    
    _instance = None
    _redis = None
    _is_available = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Redis connection."""
        try:
            redis_url = os.getenv("UPSTASH_REDIS_REST_URL")
            redis_token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
            
            if not redis_url or not redis_token:
                logger.warning("Upstash Redis credentials not configured. Redis features disabled.")
                self._is_available = False
                return
            
            self._redis = Redis(url=redis_url, token=redis_token)
            
            # Test connection
            self._redis.ping()
            self._is_available = True
            logger.info("Successfully connected to Upstash Redis")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            self._is_available = False
    
    @property
    def is_available(self) -> bool:
        """Check if Redis is available."""
        return self._is_available
    
    def get(self, key: str) -> Optional[str]:
        """
        Get value from Redis.
        
        Args:
            key: Redis key
            
        Returns:
            Value as string or None if not found or Redis unavailable
        """
        if not self._is_available:
            return None
        
        try:
            return self._redis.get(key)
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {str(e)}")
            return None
    
    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """
        Set value in Redis.
        
        Args:
            key: Redis key
            value: Value to store
            ex: Expiration time in seconds (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._is_available:
            return False
        
        try:
            if ex:
                self._redis.setex(key, ex, value)
            else:
                self._redis.set(key, value)
            return True
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from Redis.
        
        Args:
            key: Redis key
            
        Returns:
            True if successful, False otherwise
        """
        if not self._is_available:
            return False
        
        try:
            self._redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {str(e)}")
            return False
    
    def incr(self, key: str) -> Optional[int]:
        """
        Increment value in Redis.
        
        Args:
            key: Redis key
            
        Returns:
            New value or None if error
        """
        if not self._is_available:
            return None
        
        try:
            return self._redis.incr(key)
        except Exception as e:
            logger.error(f"Redis INCR error for key {key}: {str(e)}")
            return None
    
    def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration on key.
        
        Args:
            key: Redis key
            seconds: Expiration time in seconds
            
        Returns:
            True if successful, False otherwise
        """
        if not self._is_available:
            return False
        
        try:
            self._redis.expire(key, seconds)
            return True
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key {key}: {str(e)}")
            return False
    
    def ttl(self, key: str) -> Optional[int]:
        """
        Get time to live for key.
        
        Args:
            key: Redis key
            
        Returns:
            TTL in seconds or None if error
        """
        if not self._is_available:
            return None
        
        try:
            return self._redis.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL error for key {key}: {str(e)}")
            return None


# Global singleton instance
redis_client = RedisClient()

