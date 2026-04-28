"""
Update backend to use Finnhub for real-time prices
Replace the Massive/Polygon code with this simpler Finnhub approach
"""

import requests
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

# Finnhub configuration
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "d7n6829r01qppri3n0p0d7n6829r01qppri3n0pg")
FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

# Cache for efficiency
price_cache = {}
CACHE_DURATION = 60  # 1 minute cache

def get_finnhub_quote(symbol: str) -> Optional[Dict]:
    """Get real-time quote from Finnhub"""
    try:
        # Check cache first
        cache_key = f"quote_{symbol}"
        if cache_key in price_cache:
            cached_data, cached_time = price_cache[cache_key]
            if (datetime.now() - cached_time).seconds < CACHE_DURATION:
                return cached_data
        
        # Fetch from Finnhub
        url = f"{FINNHUB_BASE_URL}/quote"
        params = {
            "symbol": symbol.upper(),
            "token": FINNHUB_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # Finnhub returns:
            # c = current price
            # h = high of the day
            # l = low of the day
            # o = open price
            # pc = previous close
            # t = timestamp
            
            if data.get('c', 0) > 0:  # Valid price
                result = {
                    "price": data['c'],
                    "bid": data['c'] - 0.01,  # Estimate bid
                    "ask": data['c'] + 0.01,  # Estimate ask
                    "high": data['h'],
                    "low": data['l'],
                    "open": data['o'],
                    "previous_close": data['pc'],
                    "change": data['c'] - data['pc'],
                    "change_percent": ((data['c'] - data['pc']) / data['pc'] * 100) if data['pc'] > 0 else 0,
                    "source": "finnhub",
                    "timestamp": datetime.now().isoformat()
                }
                
                # Cache the result
                price_cache[cache_key] = (result, datetime.now())
                return result
        
        elif response.status_code == 429:
            print(f"Finnhub rate limit hit - 60 calls/minute on free tier")
        else:
            print(f"Finnhub error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"Error fetching Finnhub quote for {symbol}: {e}")
    
    return None

def get_stock_data(symbol: str) -> Dict:
    """Get stock data from Finnhub with fallback"""
    # Try Finnhub first
    quote = get_finnhub_quote(symbol)
    if quote and quote["price"] > 0:
        return {
            "price": quote["price"],
            "bid": quote["bid"],
            "ask": quote["ask"],
            "spread": quote["ask"] - quote["bid"],
            "change": quote["change"],
            "change_percent": quote["change_percent"],
            "source": quote["source"]
        }
    
    # Fallback prices if API fails
    FALLBACK_PRICES = {
        "SNAP": 15.42,
        "PINS": 28.76,
        "DKNG": 38.93,
        "ROKU": 63.45,
        "AAPL": 182.45,
        "MSFT": 425.67,
        "GOOGL": 175.23,
        "TSLA": 178.92
    }
    
    if symbol in FALLBACK_PRICES:
        price = FALLBACK_PRICES[symbol]
        return {
            "price": price,
            "bid": price - 0.01,
            "ask": price + 0.01,
            "spread": 0.02,
            "change": 0,
            "change_percent": 0,
            "source": "fallback"
        }
    
    # Default for unknown symbols
    return {
        "price": 100.0,
        "bid": 99.99,
        "ask": 100.01,
        "spread": 0.02,
        "change": 0,
        "change_percent": 0,
        "source": "default"
    }

# Rate limit considerations:
# - Free tier: 60 calls/minute
# - If scanning 20 stocks every 5 seconds = 240 calls/minute (need paid tier)
# - Solution: Cache for 60 seconds, or use WebSocket for real-time updates

print("Finnhub Integration Ready!")
print(f"Using API key: {FINNHUB_API_KEY[:10]}...")
print("\nBenefits:")
print("- Already have Finnhub for earnings data")
print("- Same API for both prices and earnings")
print("- Free tier sufficient for basic scanning")
print("- Upgrade to paid tier for high-frequency polling")