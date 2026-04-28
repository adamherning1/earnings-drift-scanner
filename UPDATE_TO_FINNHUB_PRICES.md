# Update Backend to Use Finnhub for Prices

## Why Switch to Finnhub
- Already using it for earnings data
- One API = simpler operations
- Free tier sufficient for basic use
- No need for Polygon/Massive subscription

## Changes Needed in main_massive_quotes.py

### 1. Replace Massive/Polygon Functions
Replace all the `get_massive_quote()` and related functions with:

```python
def get_finnhub_quote(symbol: str) -> Optional[Dict]:
    """Get real-time quote from Finnhub"""
    try:
        # Check cache first
        cache_key = f"quote_{symbol}"
        now = time.time()
        if cache_key in cache:
            cached_data, cached_time = cache[cache_key]
            if now - cached_time < CACHE_DURATION:
                return cached_data
        
        # Finnhub configuration
        FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "d7n6829r01qppri3n0p0d7n6829r01qppri3n0pg")
        
        # Fetch from Finnhub quote endpoint
        url = "https://finnhub.io/api/v1/quote"
        params = {
            "symbol": symbol.upper(),
            "token": FINNHUB_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # Finnhub returns: c=current, h=high, l=low, o=open, pc=previous close
            if data.get('c', 0) > 0:
                result = {
                    "price": data['c'],
                    "bid": data['c'] - 0.01,  # Estimate
                    "ask": data['c'] + 0.01,  # Estimate
                    "high": data['h'],
                    "low": data['l'],
                    "open": data['o'],
                    "previous_close": data['pc'],
                    "spread": 0.02,
                    "source": "finnhub"
                }
                
                # Cache the result
                cache[cache_key] = (result, now)
                return result
                
    except Exception as e:
        print(f"Error fetching Finnhub quote for {symbol}: {e}")
    
    return None
```

### 2. Update get_stock_data Function
```python
def get_stock_data(symbol: str) -> Dict:
    """Get stock data from Finnhub with fallback"""
    # Try Finnhub quote
    quote = get_finnhub_quote(symbol)
    if quote and quote["price"] > 0:
        return {
            "price": quote["price"],
            "bid": quote["bid"],
            "ask": quote["ask"],
            "spread": quote["spread"],
            "source": quote["source"]
        }
    
    # Use existing fallback
    if symbol in CURRENT_PRICES:
        fb = CURRENT_PRICES[symbol]
        return {
            "price": fb["price"],
            "bid": fb["bid"],
            "ask": fb["ask"],
            "spread": fb["ask"] - fb["bid"],
            "source": "fallback"
        }
    
    # Default
    return {
        "price": 100.0,
        "bid": 99.99,
        "ask": 100.01,
        "spread": 0.02,
        "source": "default"
    }
```

### 3. Remove Massive/Polygon Code
- Delete `get_massive_last_quote()`
- Delete `get_massive_daily_bar()`
- Remove `MASSIVE_API_KEY` configuration
- Remove `MASSIVE_BASE_URL`

### 4. Update Health Check
```python
@app.get("/health")
def health_check():
    # Test Finnhub
    test_quote = get_finnhub_quote("AAPL")
    
    return {
        "status": "healthy",
        "finnhub_configured": True,
        "price_api_working": test_quote is not None,
        "test_price": test_quote["price"] if test_quote else "Using fallback",
        "cache_entries": len(cache),
        "version": "14.0.0"  # Finnhub prices
    }
```

## Deployment Steps

1. **Update the backend code** with Finnhub price functions
2. **Push to GitHub** - Render will auto-deploy
3. **No new environment variables needed** - Already have FINNHUB_API_KEY
4. **Test endpoints**:
   - https://post-earnings-scanner-v2.onrender.com/health
   - https://post-earnings-scanner-v2.onrender.com/api/quote/AAPL

## Rate Limit Management

### Free Tier (60 calls/min):
- Cache quotes for 60 seconds minimum
- Scan 60 stocks max without rotation
- Perfect for focused scanner

### Need More?
- Finnhub Growth: $49/mo = 300 calls/min
- Finnhub Pro: $199/mo = unlimited
- Or use WebSocket for streaming

## Benefits
✅ One API for everything
✅ Already configured
✅ Simpler error handling
✅ Consistent data source
✅ Lower operational complexity