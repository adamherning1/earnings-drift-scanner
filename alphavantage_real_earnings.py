"""
Alpha Vantage - FREE Real Earnings Data
"""
import requests
import json
import time

# Alpha Vantage offers free API keys
AV_API_KEY = "demo"  # Replace with your free key from https://www.alphavantage.co/support/#api-key

def get_earnings_calendar():
    """Get real earnings calendar from Alpha Vantage"""
    url = "https://www.alphavantage.co/query"
    
    params = {
        "function": "EARNINGS_CALENDAR",
        "horizon": "3month",
        "apikey": AV_API_KEY
    }
    
    print("Fetching REAL earnings calendar from Alpha Vantage...")
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        # Alpha Vantage returns CSV, need to parse
        print("Calendar data received!")
        return response.text
    else:
        print(f"Error: {response.status_code}")
        return None

def get_company_earnings(symbol):
    """Get real historical earnings for a company"""
    url = "https://www.alphavantage.co/query"
    
    params = {
        "function": "EARNINGS",
        "symbol": symbol,
        "apikey": AV_API_KEY
    }
    
    print(f"\nFetching REAL earnings history for {symbol}...")
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        if "quarterlyEarnings" in data:
            earnings = data["quarterlyEarnings"]
            print(f"Found {len(earnings)} quarterly earnings reports!")
            
            # Show recent earnings
            for i, earning in enumerate(earnings[:5]):
                print(f"\n{earning['fiscalDateEnding']}:")
                print(f"  Reported EPS: ${earning.get('reportedEPS', 'N/A')}")
                print(f"  Estimated EPS: ${earning.get('estimatedEPS', 'N/A')}")
                print(f"  Surprise: ${earning.get('surprise', 'N/A')}")
                print(f"  Surprise %: {earning.get('surprisePercentage', 'N/A')}%")
                
            return earnings
    
    return []

def build_real_historical_data():
    """Build REAL historical data from Alpha Vantage"""
    
    symbols = ["AAPL", "MSFT", "GOOGL", "SNAP", "PINS", "ROKU"]
    real_data = {}
    
    for symbol in symbols:
        earnings = get_company_earnings(symbol)
        
        if earnings:
            # Analyze the earnings
            positive_surprises = []
            negative_surprises = []
            
            for earning in earnings[:20]:  # Last 20 quarters
                try:
                    surprise_pct = float(earning.get('surprisePercentage', '0').replace('%', ''))
                    
                    if surprise_pct > 10:
                        positive_surprises.append(surprise_pct)
                    elif surprise_pct < -10:
                        negative_surprises.append(surprise_pct)
                except:
                    continue
            
            real_data[symbol] = {
                "symbol": symbol,
                "company": symbol,  # Would lookup real name
                "total_events": len(earnings),
                "events_analyzed": len(earnings[:20]),
                "positive_surprise_count": len(positive_surprises),
                "negative_surprise_count": len(negative_surprises),
                "avg_positive_surprise": sum(positive_surprises)/len(positive_surprises) if positive_surprises else 0,
                "avg_negative_surprise": sum(negative_surprises)/len(negative_surprises) if negative_surprises else 0,
                "data_source": "Alpha Vantage - REAL quarterly earnings",
                "last_updated": earnings[0]['fiscalDateEnding'] if earnings else None
            }
        
        # Rate limit: 5 calls per minute on free tier
        time.sleep(12)
    
    # Save the real data
    with open("alphavantage_real_data.json", "w") as f:
        json.dump(real_data, f, indent=2)
        
    print(f"\n✅ Saved REAL earnings data for {len(real_data)} companies!")
    return real_data

if __name__ == "__main__":
    print("=== Alpha Vantage - FREE Real Earnings Data ===\n")
    
    # Build real historical data
    real_data = build_real_historical_data()
    
    print("\n" + "="*60)
    print("REAL EARNINGS DATA SUMMARY:")
    print("="*60)
    
    for symbol, data in real_data.items():
        print(f"\n{symbol}:")
        print(f"  Total earnings reports: {data['total_events']}")
        print(f"  Positive surprises (>10%): {data['positive_surprise_count']}")
        print(f"  Negative surprises (<-10%): {data['negative_surprise_count']}")
        print(f"  Last earnings: {data['last_updated']}")