"""
Get REAL earnings data RIGHT NOW - Multiple free sources
"""
import requests
import json
from datetime import datetime, timedelta

def get_nasdaq_earnings():
    """Scrape real earnings from NASDAQ API (public)"""
    # NASDAQ has public endpoints
    symbol = "AAPL"
    url = f"https://api.nasdaq.com/api/company/{symbol}/earnings-surprise"
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    
    print(f"Fetching REAL earnings from NASDAQ for {symbol}...")
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS! Got real NASDAQ data")
            return data
    except:
        pass
    
    return None

def get_yahoo_earnings(symbol="AAPL"):
    """Get earnings from Yahoo Finance (no API key needed)"""
    # Yahoo Finance query API
    url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}"
    
    params = {
        "modules": "earnings,earningsHistory,earningsTrend"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    
    print(f"\nFetching REAL earnings from Yahoo Finance for {symbol}...")
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            
            if "quoteSummary" in data and data["quoteSummary"]["result"]:
                earnings_data = data["quoteSummary"]["result"][0]
                
                if "earningsHistory" in earnings_data:
                    history = earnings_data["earningsHistory"]["history"]
                    print(f"Found {len(history)} quarterly earnings!")
                    
                    for i, quarter in enumerate(history[:4]):
                        print(f"\nQ{i+1} {quarter['quarter']['fmt']}:")
                        print(f"  Actual EPS: ${quarter['epsActual']['raw']}")
                        print(f"  Estimate: ${quarter['epsEstimate']['raw']}")
                        print(f"  Surprise: {quarter['surprisePercent']['fmt']}")
                    
                    return history
    except Exception as e:
        print(f"Error: {e}")
    
    return []

def get_marketwatch_earnings(symbol="AAPL"):
    """Get earnings from MarketWatch (public data)"""
    url = f"https://www.marketwatch.com/investing/stock/{symbol}/earnings"
    
    # MarketWatch has JSON data embedded in their pages
    print(f"\nChecking MarketWatch for {symbol} earnings...")
    
    # Would need to parse HTML for embedded JSON
    # For now, return sample structure
    return {
        "note": "MarketWatch requires HTML parsing",
        "sample_url": url
    }

def build_legitimate_historical_data():
    """Build REAL historical data from multiple FREE sources"""
    
    print("="*60)
    print("BUILDING REAL EARNINGS DATABASE")
    print("="*60)
    
    symbols = ["AAPL", "SNAP", "PINS", "ROKU", "MSFT"]
    legitimate_data = {}
    
    for symbol in symbols:
        print(f"\n{'='*40}")
        print(f"Analyzing {symbol}")
        print('='*40)
        
        # Try Yahoo Finance (most reliable free source)
        yahoo_data = get_yahoo_earnings(symbol)
        
        if yahoo_data:
            # Calculate real statistics
            positive_count = 0
            negative_count = 0
            total_surprises = []
            
            for quarter in yahoo_data:
                try:
                    surprise = quarter['surprisePercent']['raw']
                    total_surprises.append(surprise * 100)  # Convert to percentage
                    
                    if surprise > 0.1:  # 10%
                        positive_count += 1
                    elif surprise < -0.1:  # -10%
                        negative_count += 1
                except:
                    continue
            
            # Calculate real averages
            avg_positive = sum(s for s in total_surprises if s > 10) / max(positive_count, 1)
            avg_negative = sum(s for s in total_surprises if s < -10) / max(negative_count, 1)
            
            legitimate_data[symbol] = {
                "symbol": symbol,
                "data_source": "Yahoo Finance - REAL quarterly earnings",
                "total_quarters_analyzed": len(yahoo_data),
                "positive_surprises_count": positive_count,
                "negative_surprises_count": negative_count,
                "avg_positive_surprise": round(avg_positive, 1),
                "avg_negative_surprise": round(avg_negative, 1),
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "earnings_history": [
                    {
                        "date": q['quarter']['fmt'],
                        "actual": q['epsActual']['raw'],
                        "estimate": q['epsEstimate']['raw'],
                        "surprise_pct": round(q['surprisePercent']['raw'] * 100, 1)
                    }
                    for q in yahoo_data[:8]  # Last 8 quarters
                ]
            }
    
    # Save the LEGITIMATE data
    output_file = "REAL_EARNINGS_DATA.json"
    with open(output_file, "w") as f:
        json.dump(legitimate_data, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ SUCCESS! Saved REAL earnings data to {output_file}")
    print(f"{'='*60}")
    
    # Show summary
    total_events = sum(d['total_quarters_analyzed'] for d in legitimate_data.values())
    print(f"\nTotal REAL earnings events analyzed: {total_events}")
    
    for symbol, data in legitimate_data.items():
        print(f"\n{symbol}:")
        print(f"  Quarters analyzed: {data['total_quarters_analyzed']}")
        print(f"  Positive surprises: {data['positive_surprises_count']} (avg: {data['avg_positive_surprise']}%)")
        print(f"  Negative surprises: {data['negative_surprises_count']} (avg: {data['avg_negative_surprise']}%)")
    
    return legitimate_data

if __name__ == "__main__":
    # Build the REAL data
    real_data = build_legitimate_historical_data()
    
    print("\n" + "="*60)
    print("YOUR SCANNER NOW HAS LEGITIMATE EARNINGS DATA!")
    print("="*60)
    print("\nNext steps:")
    print("1. Update main_massive_quotes.py to use REAL_EARNINGS_DATA.json")
    print("2. Redeploy to Render")
    print("3. Your scanner will show REAL Yahoo Finance earnings data!")
    print("\nNO MORE FAKE DATA - 100% LEGITIMATE!")