"""
Test Massive's Benzinga earnings endpoint
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MASSIVE_API_KEY", "W9yf_4m5NsX89ZNS5jGSfYkVorDBPiGfN")
BASE_URL = "https://api.massive.com"

def test_benzinga_earnings(ticker="AAPL"):
    """Test pulling earnings from Benzinga endpoint"""
    print(f"\nTesting Benzinga earnings for {ticker}...")
    
    response = requests.get(
        f"{BASE_URL}/v1/partners/benzinga/earnings",
        params={
            "ticker": ticker,
            "limit": 50000,
            "sort": "date.desc"
        },
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        earnings = response.json()
        
        # Handle different response formats
        if isinstance(earnings, list):
            print(f"Found {len(earnings)} earnings events")
            
            # Show first 3
            for i, earning in enumerate(earnings[:3]):
                print(f"\nEvent {i+1}:")
                print(json.dumps(earning, indent=2))
                
        elif isinstance(earnings, dict):
            if "data" in earnings:
                print(f"Found {len(earnings['data'])} earnings events")
                for i, earning in enumerate(earnings['data'][:3]):
                    print(f"\nEvent {i+1}:")
                    print(json.dumps(earning, indent=2))
            else:
                print("Response format:")
                print(json.dumps(earnings, indent=2))
                
        # Calculate total earnings analyzed
        total_events = len(earnings) if isinstance(earnings, list) else len(earnings.get("data", []))
        print(f"\n✅ Total earnings events available: {total_events}")
        
    else:
        print(f"Error: {response.text[:200]}")
        
    return response

# Test multiple tickers
if __name__ == "__main__":
    print("Testing Massive Benzinga Earnings Endpoint")
    print("=" * 50)
    
    # Test a few tickers
    for ticker in ["AAPL", "SNAP", "PINS"]:
        test_benzinga_earnings(ticker)
        print("\n" + "=" * 50)