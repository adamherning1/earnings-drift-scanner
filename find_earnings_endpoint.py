"""
Try to find the correct Massive earnings endpoint
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MASSIVE_API_KEY", "W9yf_4m5NsX89ZNS5jGSfYkVorDBPiGfN")

# Possible earnings endpoints to try
endpoints = [
    # Benzinga variations
    "https://api.massive.com/v1/partners/benzinga/earnings",
    "https://api.massive.com/v3/partners/benzinga/earnings",
    "https://api.massive.com/benzinga/earnings",
    
    # Generic earnings endpoints
    "https://api.massive.com/v3/earnings/{ticker}",
    "https://api.massive.com/v3/reference/earnings/{ticker}",
    "https://api.massive.com/v3/stocks/{ticker}/earnings",
    
    # Polygon-style endpoints (since Massive bought them)
    "https://api.polygon.io/vX/reference/financials",
    "https://api.polygon.io/v2/reference/financials/{ticker}",
    
    # Financial data endpoints
    "https://api.massive.com/v3/reference/financials/{ticker}",
    "https://api.massive.com/v3/financials/{ticker}"
]

def test_endpoint(url_template, ticker="AAPL"):
    """Test if an endpoint returns earnings data"""
    # Replace {ticker} in URL
    url = url_template.replace("{ticker}", ticker)
    
    print(f"\nTrying: {url}")
    
    # Try different auth methods
    auth_methods = [
        {"headers": {"Authorization": f"Bearer {API_KEY}"}},
        {"params": {"apiKey": API_KEY}},
        {"params": {"apikey": API_KEY}}
    ]
    
    for auth in auth_methods:
        try:
            if "headers" in auth:
                response = requests.get(url, headers=auth["headers"], timeout=5)
            else:
                response = requests.get(url, params=auth["params"], timeout=5)
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                # Look for earnings-related fields
                data_str = str(data)[:500]
                
                earnings_keywords = ['eps', 'earnings', 'actual', 'estimate', 'surprise', 'fiscal']
                if any(keyword in data_str.lower() for keyword in earnings_keywords):
                    print(f"  [FOUND] EARNINGS DATA!")
                    print(f"  Sample: {data_str[:200]}...")
                    return True
                else:
                    print(f"  [X] No earnings data found")
                    
            elif response.status_code == 404:
                print(f"  [X] Not found")
            elif response.status_code == 401:
                print(f"  [X] Auth failed with this method")
            else:
                print(f"  [X] Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"  [X] Failed: {str(e)}")
    
    return False

# Test all endpoints
print("Searching for Massive earnings endpoints...")
print("=" * 60)

found_any = False
for endpoint in endpoints:
    if test_endpoint(endpoint):
        found_any = True
        print(f"\n[WORKING] endpoint: {endpoint}")
        break

if not found_any:
    print("\n[WARNING] No earnings endpoints found. Checking if financials data includes earnings...")
    
    # Try the reference/financials endpoint more thoroughly
    url = "https://api.polygon.io/vX/reference/financials"
    params = {
        "ticker": "AAPL",
        "apiKey": API_KEY,
        "limit": 10
    }
    
    print(f"\nTrying comprehensive financials: {url}")
    response = requests.get(url, params=params, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("Sample response:")
        print(response.text[:1000])