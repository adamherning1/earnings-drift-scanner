"""
Find the correct Massive earnings endpoint
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MASSIVE_API_KEY", "W9yf_4m5NsX89ZNS5jGSfYkVorDBPiGfN")

# All possible earnings endpoints to try
urls_to_try = [
    "https://api.massive.com/v2/reference/earnings",
    "https://api.massive.com/v1/partners/benzinga/earnings",
    "https://api.massive.com/v3/reference/earnings",
    # Also try Polygon legacy endpoints
    "https://api.polygon.io/v2/reference/financials",
    "https://api.polygon.io/vX/reference/financials",
    # Try with ticker in path
    "https://api.massive.com/v2/reference/earnings/AAPL",
    "https://api.massive.com/v3/reference/tickers/AAPL/earnings",
]

params = {
    "ticker": "AAPL",
    "limit": 100,
    "sort": "date.desc"
}

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

print("Searching for Massive earnings endpoint...")
print("=" * 60)

found = False

for url in urls_to_try:
    print(f"\nTrying: {url}")
    
    try:
        # For URLs with ticker in path, remove it from params
        if "AAPL" in url:
            params_to_use = {k: v for k, v in params.items() if k != "ticker"}
        else:
            params_to_use = params
        
        r = requests.get(url, params=params_to_use, headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            
            # Check if response contains earnings data
            data_str = str(data)[:500].lower()
            
            if any(keyword in data_str for keyword in ['eps', 'earnings', 'revenue', 'actual', 'estimate']):
                print("[SUCCESS] FOUND EARNINGS DATA!")
                found = True
                
                # Show sample data
                if isinstance(data, list):
                    print(f"Total records: {len(data)}")
                    if data:
                        print("\nFirst earnings event:")
                        print(json.dumps(data[0], indent=2))
                elif isinstance(data, dict):
                    if "results" in data:
                        print(f"Total records: {len(data['results'])}")
                        if data['results']:
                            print("\nFirst earnings event:")
                            print(json.dumps(data['results'][0], indent=2))
                    else:
                        print("\nResponse structure:")
                        print(json.dumps(data, indent=2)[:1000])
                
                # Save working endpoint
                with open('working_earnings_endpoint.json', 'w') as f:
                    json.dump({
                        "url": url,
                        "params": params_to_use,
                        "sample_response": data if isinstance(data, dict) else {"results": data[:3]}
                    }, f, indent=2)
                
                print(f"\n[SUCCESS] Saved working endpoint details to working_earnings_endpoint.json")
                break
            else:
                print("[X] No earnings data in response")
                
        elif r.status_code == 404:
            print("[X] Not found")
        elif r.status_code == 401:
            print("[X] Authentication failed")
        else:
            print(f"[X] Error: {r.text[:100]}")
            
    except Exception as e:
        print(f"[X] Exception: {str(e)}")

if not found:
    print("\n[WARNING] No working earnings endpoint found")
    print("\nTrying alternative: Query params instead of Bearer token...")
    
    # Try with API key in params
    for url in urls_to_try[:3]:
        print(f"\nTrying {url} with apiKey param...")
        
        alt_params = {**params, "apiKey": API_KEY}
        r = requests.get(url, params=alt_params)
        
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print("[SUCCESS] Success with apiKey in params!")
            break

print("\n" + "=" * 60)
print("Search complete!")

if found:
    print("\n[NEXT] Update the pipeline to use the working endpoint")