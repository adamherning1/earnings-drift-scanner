"""
Test the CORRECT Massive earnings endpoint
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Use the massive-api-client approach
API_KEY = os.getenv("MASSIVE_API_KEY", "W9yf_4m5NsX89ZNS5jGSfYkVorDBPiGfN")

def test_earnings_endpoint():
    """Test the v2/reference/earnings endpoint"""
    
    ticker = "AAPL"
    print(f"Testing Massive v2/reference/earnings for {ticker}...")
    
    # Use the exact endpoint from the screenshot
    url = "https://api.massive.com/v2/reference/earnings"
    
    params = {
        "ticker": ticker,
        "limit": 50000,
        "sort": "date.asc"
    }
    
    # Try both auth methods
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    
    response = requests.get(url, params=params, headers=headers)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        earnings = response.json()
        
        # Check if it's the list format
        if isinstance(earnings, list):
            print(f"\nFound {len(earnings)} earnings events!")
            
            # Show first few events
            for i, e in enumerate(earnings[:3]):
                print(f"\nEvent {i+1}:")
                print(json.dumps(e, indent=2))
                
        elif isinstance(earnings, dict):
            if "results" in earnings:
                results = earnings["results"]
                print(f"\nFound {len(results)} earnings events!")
                
                for i, e in enumerate(results[:3]):
                    print(f"\nEvent {i+1}:")
                    print(json.dumps(e, indent=2))
            else:
                print("\nResponse structure:")
                print(json.dumps(earnings, indent=2))
                
    else:
        print(f"Error: {response.text}")
        
        # Also try with API key in params
        print("\nTrying with apiKey in params...")
        response = requests.get(url, params={**params, "apiKey": API_KEY})
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("Success with apiKey in params!")

# Run the test
if __name__ == "__main__":
    test_earnings_endpoint()