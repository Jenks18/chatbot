"""
Rate limiting middleware for API protection
"""
import time
from collections import defaultdict
from typing import Dict, Tuple
from datetime import datetime, timedelta


class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        burst_size: int = 10
    ):
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.token_fill_rate = requests_per_minute / 60.0  # tokens per second
        
        # Storage: {identifier: (tokens, last_update_time)}
        self.buckets: Dict[str, Tuple[float, float]] = defaultdict(
            lambda: (self.burst_size, time.time())
        )
    
    def is_allowed(self, identifier: str) -> Tuple[bool, Dict[str, any]]:
        """
        Check if request is allowed under rate limit
        
        Args:
            identifier: IP address or session ID
            
        Returns:
            (is_allowed, rate_limit_info)
        """
        current_time = time.time()
        tokens, last_update = self.buckets[identifier]
        
        # Calculate tokens to add based on time passed
        time_passed = current_time - last_update
        tokens_to_add = time_passed * self.token_fill_rate
        tokens = min(self.burst_size, tokens + tokens_to_add)
        
        rate_limit_info = {
            'limit': self.requests_per_minute,
            'remaining': int(tokens),
            'reset': int(current_time + (self.burst_size - tokens) / self.token_fill_rate)
        }
        
        if tokens >= 1.0:
            # Request allowed
            tokens -= 1.0
            self.buckets[identifier] = (tokens, current_time)
            return True, rate_limit_info
        else:
            # Rate limit exceeded
            self.buckets[identifier] = (tokens, current_time)
            return False, rate_limit_info
    
    def reset(self, identifier: str):
        """Reset rate limit for an identifier"""
        if identifier in self.buckets:
            del self.buckets[identifier]
    
    def cleanup_old_entries(self, max_age_minutes: int = 60):
        """Remove old entries to prevent memory leak"""
        current_time = time.time()
        cutoff_time = current_time - (max_age_minutes * 60)
        
        identifiers_to_remove = [
            identifier
            for identifier, (_, last_update) in self.buckets.items()
            if last_update < cutoff_time
        ]
        
        for identifier in identifiers_to_remove:
            del self.buckets[identifier]


# Global rate limiter instances
chat_rate_limiter = RateLimiter(requests_per_minute=30, burst_size=5)
api_rate_limiter = RateLimiter(requests_per_minute=60, burst_size=10)
