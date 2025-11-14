"""Rate limiting using token bucket algorithm with Redis."""
import time
import logging
from typing import Tuple
from .redis_client import redis_client

logger = logging.getLogger(__name__)


class RateLimitPresets:
    """Predefined rate limit configurations."""
    
    NORMAL = {
        "requests_per_minute": 10,
        "burst": 5
    }
    
    STREAMING = {
        "requests_per_minute": 5,
        "burst": 2
    }
    
    GENEROUS = {
        "requests_per_minute": 30,
        "burst": 10
    }


class TokenBucketRateLimiter:
    """Token bucket rate limiter using Redis."""
    
    def __init__(self, requests_per_minute: int = 10, burst: int = 5):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Number of requests allowed per minute
            burst: Additional burst capacity
        """
        self.requests_per_minute = requests_per_minute
        self.burst = burst
        self.capacity = requests_per_minute + burst
        self.refill_rate = requests_per_minute / 60.0  # tokens per second
        self.enabled = redis_client.is_available
        
        if not self.enabled:
            logger.warning("Rate limiter initialized but Redis is not available")
    
    def _get_key(self, identifier: str, endpoint: str) -> str:
        """
        Get Redis key for rate limit bucket.
        
        Args:
            identifier: User/session identifier
            endpoint: API endpoint
            
        Returns:
            Redis key
        """
        return f"ratelimit:{endpoint}:{identifier}"
    
    def check_rate_limit(self, identifier: str, endpoint: str) -> Tuple[bool, dict]:
        """
        Check if request is within rate limit.
        
        Args:
            identifier: User/session identifier
            endpoint: API endpoint
            
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        if not self.enabled:
            # If Redis is not available, allow all requests
            return True, {
                "allowed": True,
                "remaining": self.capacity,
                "reset_in": 0
            }
        
        try:
            key = self._get_key(identifier, endpoint)
            current_time = time.time()
            
            # Get current bucket state
            bucket_data = redis_client.get(key)
            
            if bucket_data:
                import json
                bucket = json.loads(bucket_data)
                tokens = bucket["tokens"]
                last_refill = bucket["last_refill"]
            else:
                # Initialize new bucket
                tokens = self.capacity
                last_refill = current_time
            
            # Refill tokens based on time elapsed
            time_elapsed = current_time - last_refill
            tokens_to_add = time_elapsed * self.refill_rate
            tokens = min(self.capacity, tokens + tokens_to_add)
            
            # Check if we have tokens available
            if tokens >= 1:
                # Consume one token
                tokens -= 1
                allowed = True
            else:
                allowed = False
            
            # Calculate reset time
            if tokens < self.capacity:
                tokens_needed = 1 - tokens if not allowed else 0
                reset_in = int(tokens_needed / self.refill_rate) + 1
            else:
                reset_in = 0
            
            # Save bucket state
            import json
            bucket_data = json.dumps({
                "tokens": tokens,
                "last_refill": current_time
            })
            redis_client.set(key, bucket_data, ex=300)  # 5 minute TTL
            
            rate_limit_info = {
                "allowed": allowed,
                "remaining": int(tokens),
                "reset_in": reset_in,
                "limit": self.requests_per_minute
            }
            
            if not allowed:
                logger.warning(f"Rate limit exceeded for {identifier} on {endpoint}")
            
            return allowed, rate_limit_info
            
        except Exception as e:
            logger.error(f"Rate limit check error: {str(e)}")
            # On error, allow the request
            return True, {
                "allowed": True,
                "remaining": self.capacity,
                "reset_in": 0,
                "error": str(e)
            }
    
    def reset(self, identifier: str, endpoint: str) -> bool:
        """
        Reset rate limit for an identifier.
        
        Args:
            identifier: User/session identifier
            endpoint: API endpoint
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            key = self._get_key(identifier, endpoint)
            return redis_client.delete(key)
        except Exception as e:
            logger.error(f"Rate limit reset error: {str(e)}")
            return False

