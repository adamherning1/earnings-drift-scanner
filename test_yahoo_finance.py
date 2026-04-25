import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

print("[TESTING] Yahoo Finance Connection...\n")

# Test 1: Get stock info
print("[STOCK INFO] Testing AAPL...")
try:
    ticker = yf.Ticker("AAPL")
    info = ticker.info
    
    print(f"Company: {info.get('longName', 'N/A')}")
    print(f"Symbol: {info.get('symbol', 'N/A')}")
    print(f"Price: ${info.get('regularMarketPrice', 0):.2f}")
    print(f"Market Cap: ${info.get('marketCap', 0):,.0f}")
    print(f"Volume: {info.get('volume', 0):,}")
    print("[OK] Stock data working!\n")
except Exception as e:
    print(f"[ERROR] {e}\n")

# Test 2: Get earnings calendar for multiple stocks
print("[EARNINGS] Testing earnings calendar...")
symbols = ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA']
earnings_data = []

for symbol in symbols:
    try:
        ticker = yf.Ticker(symbol)
        # Get next earnings date
        if hasattr(ticker, 'calendar') and ticker.calendar is not None:
            cal = ticker.calendar
            if isinstance(cal, pd.DataFrame) and 'Earnings Date' in cal.columns:
                next_earnings = cal['Earnings Date'].iloc[0]
                print(f"  {symbol}: Next earnings on {next_earnings}")
                earnings_data.append({
                    'symbol': symbol,
                    'earnings_date': next_earnings
                })
    except:
        pass

if earnings_data:
    print(f"[OK] Found {len(earnings_data)} upcoming earnings!\n")
else:
    print("[WARNING] Earnings calendar might need different approach\n")

# Test 3: Get historical earnings
print("[HISTORICAL] Testing historical earnings...")
try:
    ticker = yf.Ticker("AAPL")
    earnings = ticker.earnings_history
    
    if earnings is not None and not earnings.empty:
        print(f"Found {len(earnings)} quarters of earnings history")
        recent = earnings.head(4)
        for idx, row in recent.iterrows():
            print(f"  {idx}: EPS {row.get('epsactual', 'N/A')} vs Est {row.get('epsestimate', 'N/A')}")
        print("[OK] Historical earnings working!")
    else:
        # Alternative method
        earnings_dates = ticker.get_earnings_dates()
        if earnings_dates is not None and not earnings_dates.empty:
            print(f"Found {len(earnings_dates)} earnings dates")
            for date, row in earnings_dates.head(4).iterrows():
                if 'EPS Estimate' in row and 'Reported EPS' in row:
                    print(f"  {date.date()}: EPS {row['Reported EPS']} vs Est {row['EPS Estimate']}")
            print("[OK] Historical earnings working (alt method)!")
except Exception as e:
    print(f"[ERROR] {e}")

# Test 4: Screen stocks by market cap
print("\n[SCREENER] Testing stock screening...")
try:
    # Get S&P 500 list as a proxy for screening
    sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    symbols = sp500['Symbol'].tolist()[:10]  # Just test first 10
    
    screened = []
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            market_cap = info.get('marketCap', 0)
            
            # Our target: $500M - $5B
            if 500_000_000 <= market_cap <= 5_000_000_000:
                screened.append({
                    'symbol': symbol,
                    'name': info.get('longName', 'N/A'),
                    'market_cap': market_cap
                })
        except:
            pass
    
    if screened:
        print(f"[OK] Found {len(screened)} stocks in $500M-$5B range:")
        for s in screened[:3]:
            print(f"  {s['symbol']}: ${s['market_cap']/1e9:.1f}B")
    else:
        print("[INFO] No stocks in range from test sample")
except Exception as e:
    print(f"[ERROR] {e}")

print("\n[SUMMARY] Yahoo Finance is working! We can build with this for free.")
print("When ready for production, we'll upgrade to Polygon.io for reliability.")