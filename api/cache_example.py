import redis
import json
from datetime import timedelta

# Redis cache setup
cache = redis.Redis(host='localhost', port=6379, decode_responses=True)

def get_stock_analysis(symbol: str):
    # Check cache first
    cached = cache.get(f"analysis:{symbol}")
    if cached:
        return json.loads(cached)
    
    # If not cached, fetch data (expensive call)
    analysis = fetch_expensive_data(symbol)  # Databento/Yahoo
    
    # Cache for 15 minutes
    cache.setex(
        f"analysis:{symbol}", 
        timedelta(minutes=15), 
        json.dumps(analysis)
    )
    
    return analysis

# Even better: Daily batch updates
def update_popular_stocks():
    """Run once per day at market close"""
    popular = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
    for symbol in popular:
        data = fetch_expensive_data(symbol)
        cache.setex(f"analysis:{symbol}", timedelta(hours=16), json.dumps(data))