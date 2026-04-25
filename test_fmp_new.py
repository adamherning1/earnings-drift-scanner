import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('FMP_API_KEY')
print(f"Testing API key: {api_key[:10]}...\n")

# New FMP API requires header authorization
headers = {
    'apikey': api_key
}

# Test endpoints without API key in URL
endpoints = [
    ("Company Search", "https://financialmodelingprep.com/api/v3/search", {"query": "Apple", "limit": 3}),
    ("Stock List", "https://financialmodelingprep.com/api/v3/stock/list", {"limit": 5}),
    ("Quote", "https://financialmodelingprep.com/api/v3/quote/AAPL", {}),
    ("Earnings Calendar", "https://financialmodelingprep.com/api/v3/earnings-calendar", {"limit": 5}),
]

for name, url, params in endpoints:
    try:
        print(f"Testing {name}...")
        # Try both header auth and query param auth
        
        # Method 1: Header auth (new method)
        response = requests.get(url, headers=headers, params=params, timeout=5)
        if response.status_code != 200:
            # Method 2: Query param auth (old method)
            params['apikey'] = api_key
            response = requests.get(url, params=params, timeout=5)
        
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data:
                if isinstance(data, list):
                    print(f"  Success! Got {len(data)} results")
                    if data and len(data) > 0:
                        # Show sample data
                        first = data[0]
                        if 'symbol' in first:
                            print(f"  Sample: {first.get('symbol')} - {first.get('name', 'N/A')}")
                else:
                    print(f"  Success! Got data")
            else:
                print("  Empty response")
        else:
            print(f"  Error: {response.text[:150]}...")
        print()
    except Exception as e:
        print(f"  Error: {e}\n")

# Test specifically for earnings data which we need
print("\nTesting Earnings-Specific Endpoints:")

# Earnings calendar with date range
from datetime import datetime, timedelta
today = datetime.now().strftime('%Y-%m-%d')
next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

earnings_endpoints = [
    ("Today's Earnings", f"https://financialmodelingprep.com/api/v3/earnings-calendar?from={today}&to={today}", {}),
    ("Upcoming Earnings", f"https://financialmodelingprep.com/api/v3/earnings-calendar?from={today}&to={next_week}", {}),
    ("Historical Earnings (AAPL)", f"https://financialmodelingprep.com/api/v3/earnings/AAPL", {"limit": 4}),
]

for name, url, params in earnings_endpoints:
    try:
        print(f"\nTesting {name}...")
        params['apikey'] = api_key
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                if isinstance(data, list):
                    print(f"  Success! Got {len(data)} earnings events")
                    for item in data[:3]:
                        symbol = item.get('symbol', 'N/A')
                        date = item.get('date', 'N/A')
                        eps_est = item.get('epsEstimated', 'N/A')
                        print(f"  - {symbol}: {date} (EPS est: {eps_est})")
                else:
                    print("  Got earnings data")
        else:
            print(f"  Status: {response.status_code}")
            print(f"  Error: {response.text[:150]}...")
    except Exception as e:
        print(f"  Error: {e}")