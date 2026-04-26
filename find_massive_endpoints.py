"""
Script to discover Massive's real-time price endpoints
"""
import requests

API_KEY = "W9yf_4m5NsX89ZNS5jGSfYkVorDBPiGfN"

# Possible endpoints based on typical patterns
test_endpoints = [
    # Quotes endpoints
    "https://api.massive.com/v3/quotes/{symbol}",
    "https://api.massive.com/v3/quote/{symbol}",
    "https://api.massive.com/v3/stocks/quotes/{symbol}",
    "https://api.massive.com/v3/stocks/{symbol}/quote",
    "https://api.massive.com/v3/tickers/{symbol}/quote",
    
    # Price endpoints
    "https://api.massive.com/v3/price/{symbol}",
    "https://api.massive.com/v3/stocks/price/{symbol}",
    "https://api.massive.com/v3/stocks/{symbol}/price",
    
    # Snapshot endpoints (common for real-time)
    "https://api.massive.com/v3/snapshot/stocks/{symbol}",
    "https://api.massive.com/v3/stocks/{symbol}/snapshot",
    
    # Last trade
    "https://api.massive.com/v3/last/{symbol}",
    "https://api.massive.com/v3/stocks/{symbol}/last",
    
    # Polygon legacy endpoints (if they kept them)
    "https://api.polygon.io/v2/aggs/ticker/{symbol}/prev",
    "https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/{symbol}",
    "https://api.polygon.io/v1/last/stocks/{symbol}",
    "https://api.polygon.io/v2/last/trade/{symbol}"
]

def test_endpoint(url_template, symbol="AAPL"):
    """Test if an endpoint returns price data"""
    url = url_template.format(symbol=symbol)
    
    try:
        # Try with API key in query
        response = requests.get(url, params={"apiKey": API_KEY}, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            # Look for price-related fields
            price_fields = ['price', 'close', 'last', 'lastTrade', 'c', 'p', 'current_price']
            
            for field in price_fields:
                if field in str(data):
                    print(f"✅ FOUND! {url}")
                    print(f"   Response: {data}")
                    return True
                    
        elif response.status_code == 401:
            print(f"❌ Auth error: {url}")
        elif response.status_code == 404:
            print(f"❌ Not found: {url}")
        else:
            print(f"❌ Error {response.status_code}: {url}")
            
    except Exception as e:
        print(f"❌ Failed: {url} - {str(e)}")
    
    return False

if __name__ == "__main__":
    print("Testing Massive API endpoints for real-time prices...\n")
    
    found_any = False
    for endpoint in test_endpoints:
        if test_endpoint(endpoint):
            found_any = True
            
    if not found_any:
        print("\n⚠️  No price endpoints found. Check the documentation for the correct endpoint!")