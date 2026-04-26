"""
Test Finnhub API with your key
"""
import requests

API_KEY = "d7n6829r01qppri3n0p0d7n6829r01qppri3n0pg"

# Test earnings endpoint
print("Testing Finnhub API...")
print("=" * 50)

# Test 1: Get earnings for AAPL
url = "https://finnhub.io/api/v1/stock/earnings"
params = {
    "symbol": "AAPL",
    "token": API_KEY
}

response = requests.get(url, params=params)
print(f"\n1. Earnings for AAPL - Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"   Found {len(data)} earnings events")
    
    if data:
        latest = data[0]
        print(f"   Latest: {latest.get('period')} - Actual: ${latest.get('actual')} vs Estimate: ${latest.get('estimate')}")
        surprise_pct = ((latest['actual'] - latest['estimate']) / abs(latest['estimate']) * 100) if latest.get('estimate') else 0
        print(f"   Surprise: {surprise_pct:+.1f}%")

# Test 2: Earnings calendar
print("\n2. Testing earnings calendar...")
from datetime import datetime, timedelta

today = datetime.now().strftime("%Y-%m-%d")
next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

url = "https://finnhub.io/api/v1/calendar/earnings"
params = {
    "from": today,
    "to": next_week,
    "token": API_KEY
}

response = requests.get(url, params=params)
print(f"   Calendar status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    calendar = data.get('earningsCalendar', [])
    print(f"   Found {len(calendar)} upcoming earnings")
    
    # Show first 5
    for event in calendar[:5]:
        print(f"   - {event.get('symbol')} on {event.get('date')}")

print("\n✅ Finnhub API is working!")