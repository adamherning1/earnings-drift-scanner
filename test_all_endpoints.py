"""
Test all possible Massive earnings endpoints
"""
import requests
import os

API_KEY = "W9yf_4m5NsX89ZNS5jGSfYkVorDBPiGfN"

# All possible endpoints based on the screenshot
test_urls = [
    # v2 endpoints
    "https://api.massive.com/v2/reference/earnings",
    "https://api.massive.com/v2/reference/earnings/AAPL",
    "https://api.massive.com/v2/reference/tickers/AAPL/earnings",
    
    # v3 endpoints  
    "https://api.massive.com/v3/reference/earnings",
    "https://api.massive.com/v3/reference/earnings/AAPL",
    "https://api.massive.com/v3/reference/tickers/AAPL/earnings",
    
    # Polygon legacy
    "https://api.polygon.io/v2/reference/financials/AAPL",
    "https://api.polygon.io/vX/reference/financials",
    
    # Benzinga partner
    "https://api.massive.com/v1/partners/benzinga/earnings/AAPL",
]

def test_endpoint(url):
    print(f"\nTesting: {url}")
    
    # Try different auth and param combinations
    tests = [
        {"name": "Bearer + ticker param", "headers": {"Authorization": f"Bearer {API_KEY}"}, "params": {"ticker": "AAPL", "limit": 5}},
        {"name": "apiKey param only", "headers": {}, "params": {"ticker": "AAPL", "limit": 5, "apiKey": API_KEY}},
        {"name": "Bearer no ticker", "headers": {"Authorization": f"Bearer {API_KEY}"}, "params": {"limit": 5}},
        {"name": "apiKey no ticker", "headers": {}, "params": {"limit": 5, "apiKey": API_KEY}},
    ]
    
    for test in tests:
        try:
            r = requests.get(url, headers=test["headers"], params=test["params"], timeout=5)
            
            if r.status_code == 200:
                print(f"  SUCCESS with {test['name']}!")
                print(f"  Response preview: {str(r.text[:200])}")
                return True
            elif r.status_code == 404:
                pass  # Silent on 404s
            else:
                print(f"  {test['name']}: {r.status_code}")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    return False

# Run all tests
print("Testing all possible Massive earnings endpoints...")
print("=" * 60)

found = False
for url in test_urls:
    if test_endpoint(url):
        found = True
        print(f"\n*** WORKING ENDPOINT: {url} ***")
        break

if not found:
    print("\nNo working endpoints found. The API might require:")
    print("1. Different authentication method")
    print("2. Different endpoint path")
    print("3. MCP server for discovery")