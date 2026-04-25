import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('FMP_API_KEY')
print(f"Testing API key: {api_key[:10]}...\n")

# Test different endpoints
endpoints = [
    ("Available Symbols", f"https://financialmodelingprep.com/api/v3/available-traded/list?apikey={api_key}"),
    ("Market Hours", f"https://financialmodelingprep.com/api/v3/market-hours?apikey={api_key}"),
    ("Sectors Performance", f"https://financialmodelingprep.com/api/v3/sectors-performance?apikey={api_key}"),
    ("Quote (AAPL)", f"https://financialmodelingprep.com/api/v3/quote/AAPL?apikey={api_key}"),
    ("Search", f"https://financialmodelingprep.com/api/v3/search?query=apple&apikey={api_key}"),
]

for name, url in endpoints:
    try:
        print(f"Testing {name}...")
        response = requests.get(url, timeout=5)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data:
                print(f"  Success! Got {len(data) if isinstance(data, list) else 'data'}")
            else:
                print("  Empty response")
        else:
            print(f"  Response: {response.text[:200]}")
        print()
    except Exception as e:
        print(f"  Error: {e}\n")