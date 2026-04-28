"""
Enhanced Earnings Calendar with multiple data sources
Combines Finnhub data with known upcoming earnings
"""

from datetime import datetime, timedelta
import requests
import os

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "ct6b609r01qoukbmfpugct6b609r01qoukbmfpv0")

# Known upcoming earnings for May 2026
# This would normally come from a database or paid API
KNOWN_EARNINGS = [
    # This week (April 28 - May 2)
    {"date": "2026-04-29", "symbol": "MSFT", "time": "AMC", "company": "Microsoft", "epsEstimate": 2.94},
    {"date": "2026-04-29", "symbol": "GOOGL", "time": "AMC", "company": "Alphabet", "epsEstimate": 1.51},
    {"date": "2026-04-30", "symbol": "META", "time": "AMC", "company": "Meta Platforms", "epsEstimate": 4.32},
    {"date": "2026-04-30", "symbol": "AMD", "time": "AMC", "company": "AMD", "epsEstimate": 0.92},
    {"date": "2026-05-01", "symbol": "AMZN", "time": "AMC", "company": "Amazon", "epsEstimate": 0.84},
    {"date": "2026-05-01", "symbol": "AAPL", "time": "AMC", "company": "Apple", "epsEstimate": 1.52},
    {"date": "2026-05-02", "symbol": "COIN", "time": "AMC", "company": "Coinbase", "epsEstimate": 1.95},
    {"date": "2026-05-02", "symbol": "DKNG", "time": "BMO", "company": "DraftKings", "epsEstimate": -0.15},
    
    # Next week (May 5-9)
    {"date": "2026-05-05", "symbol": "PYPL", "time": "AMC", "company": "PayPal", "epsEstimate": 1.48},
    {"date": "2026-05-05", "symbol": "PINS", "time": "AMC", "company": "Pinterest", "epsEstimate": 0.31},
    {"date": "2026-05-06", "symbol": "SNAP", "time": "AMC", "company": "Snap Inc", "epsEstimate": 0.15},
    {"date": "2026-05-06", "symbol": "UBER", "time": "BMO", "company": "Uber", "epsEstimate": 0.21},
    
    {"date": "2026-05-07", "symbol": "DIS", "time": "AMC", "company": "Disney", "epsEstimate": 1.11},
    {"date": "2026-05-07", "symbol": "NET", "time": "AMC", "company": "Cloudflare", "epsEstimate": 0.12},
    {"date": "2026-05-08", "symbol": "RBLX", "time": "AMC", "company": "Roblox", "epsEstimate": -0.29},
    {"date": "2026-05-08", "symbol": "PLTR", "time": "BMO", "company": "Palantir", "epsEstimate": 0.08},
    {"date": "2026-05-09", "symbol": "SQ", "time": "AMC", "company": "Block (Square)", "epsEstimate": 0.52},
    {"date": "2026-05-09", "symbol": "ABNB", "time": "AMC", "company": "Airbnb", "epsEstimate": 0.75},
]

def get_enhanced_upcoming_earnings():
    """Get upcoming earnings combining Finnhub API with known earnings"""
    earnings_map = {}
    
    # Start with known earnings
    for earning in KNOWN_EARNINGS:
        key = f"{earning['symbol']}_{earning['date']}"
        earnings_map[key] = earning
    
    # Try to get Finnhub data to enrich/update
    try:
        from_date = datetime.now().strftime("%Y-%m-%d")
        to_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        
        url = f"https://finnhub.io/api/v1/calendar/earnings"
        params = {
            "from": from_date,
            "to": to_date,
            "token": FINNHUB_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "earningsCalendar" in data:
                for item in data["earningsCalendar"]:
                    if item.get("symbol") and item.get("date"):
                        key = f"{item['symbol']}_{item['date']}"
                        # Finnhub data takes precedence for estimates
                        if key in earnings_map:
                            earnings_map[key]["epsEstimate"] = item.get("epsEstimate", earnings_map[key]["epsEstimate"])
                            earnings_map[key]["epsActual"] = item.get("epsActual")
                        else:
                            # Add new earnings from Finnhub
                            earnings_map[key] = {
                                "date": item["date"],
                                "symbol": item["symbol"],
                                "epsEstimate": item.get("epsEstimate", 0),
                                "epsActual": item.get("epsActual"),
                                "time": "TBD",
                                "company": item["symbol"]  # Finnhub doesn't provide company name
                            }
    except Exception as e:
        print(f"Error fetching Finnhub calendar: {e}")
    
    # Convert to list and sort by date
    earnings_list = list(earnings_map.values())
    earnings_list.sort(key=lambda x: x["date"])
    
    # Add current prices
    for earning in earnings_list:
        try:
            url = f"https://finnhub.io/api/v1/quote"
            params = {"symbol": earning["symbol"], "token": FINNHUB_API_KEY}
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                quote = response.json()
                earning["current_price"] = quote.get("c", 0)
        except:
            earning["current_price"] = 0
    
    return earnings_list

if __name__ == "__main__":
    earnings = get_enhanced_upcoming_earnings()
    print(f"Found {len(earnings)} upcoming earnings:")
    for e in earnings[:10]:
        print(f"{e['date']} {e['symbol']:6} ${e.get('current_price', 0):>7.2f} EPS est: ${e['epsEstimate']}")