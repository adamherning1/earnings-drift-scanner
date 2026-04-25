#!/usr/bin/env python3
"""Test FMP API connection"""

import os
import sys
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Fix Windows emoji encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

def test_fmp_connection():
    api_key = os.getenv('FMP_API_KEY')
    
    if not api_key or api_key == 'your_key_here':
        print("[ERROR] Please set your FMP_API_KEY in .env file")
        return False
    
    print(f"[KEY] Found API key: {api_key[:10]}...")
    
    # Test endpoint - use v4 API for company overview
    test_url = f"https://financialmodelingprep.com/api/v4/company-outlook?symbol=AAPL&apikey={api_key}"
    
    try:
        print("[TEST] Testing connection to FMP...")
        response = requests.get(test_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                print("[OK] Success! Connection working!")
                if isinstance(data, dict) and 'profile' in data:
                    profile = data['profile']
                    print(f"[DATA] Test data: {profile['companyName']} (${profile['symbol']})")
                    print(f"[PRICE] Current: ${profile.get('price', 'N/A')}")
                    print(f"[MARKET CAP] ${float(profile.get('mktCap', 0)):,.0f}")
                else:
                    print("[DATA] Connection successful, API key is valid!")
                return True
            else:
                print("[ERROR] Empty response from API")
        elif response.status_code == 401:
            print("[ERROR] Invalid API key")
        elif response.status_code == 429:
            print("[WARNING] Rate limit reached (but key is valid!)")
            return True
        else:
            print(f"[ERROR] HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Connection error: {e}")
    
    return False

if __name__ == "__main__":
    print("[TESTING] FMP API Connection...\n")
    
    if test_fmp_connection():
        print("\n[SUCCESS] Ready to deploy! Your API key is working!")
        
        # Show next earnings for testing
        print("\n[EARNINGS] Bonus test - checking upcoming earnings...")
        api_key = os.getenv('FMP_API_KEY')
        # Try the stock screener endpoint instead
        print("\n[SCREENER] Testing stock screener endpoint...")
        screener_url = f"https://financialmodelingprep.com/api/v3/stock-screener?marketCapMoreThan=500000000&marketCapLowerThan=5000000000&limit=5&apikey={api_key}"
        
        try:
            response = requests.get(screener_url, timeout=10)
            if response.status_code == 200:
                stocks = response.json()
                if stocks:
                    print(f"[STOCKS] Found {len(stocks)} stocks in our target range:")
                    for s in stocks[:3]:
                        print(f"  - {s.get('symbol', 'N/A')}: ${s.get('marketCap', 0)/1e9:.1f}B market cap")
            elif response.status_code == 403:
                print("[NOTE] Stock screener requires paid plan")
        except Exception as e:
            print(f"[NOTE] Screener test failed: {e}")
    else:
        print("\n[ERROR] Please check your API key and try again")