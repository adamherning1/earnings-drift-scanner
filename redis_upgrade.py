"""
Redis Caching Upgrade - When you hit 50+ users

1. Add Redis to Render:
   - Add Redis addon ($7/mo for 100MB)
   - Or use Redis Cloud free tier

2. Update requirements.txt:
   redis==5.0.1

3. Replace in-memory cache with Redis
"""

import redis
import json
from datetime import timedelta
import os

# Redis connection
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
r = redis.from_url(REDIS_URL, decode_responses=True)

def get_cached_or_fetch(key: str, fetch_func, duration: int = 900):
    """Redis-backed caching"""
    # Try cache first
    cached = r.get(key)
    if cached:
        return json.loads(cached)
    
    # Fetch new data
    data = fetch_func()
    
    # Cache it
    r.setex(key, duration, json.dumps(data))
    
    return data

# Even better: Background refresh
def refresh_popular_stocks():
    """Run every hour to keep cache warm"""
    popular = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'META', 'AMZN']
    
    for symbol in popular:
        data = fetch_yahoo_data(symbol)
        r.setex(f"yahoo:{symbol}", 3600, json.dumps(data))
    
    print(f"Refreshed {len(popular)} popular stocks")