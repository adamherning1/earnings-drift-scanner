"""
Quick script to verify we're getting real prices
"""
import yfinance as yf
import requests

print("Testing real-time price fetching...\n")

symbols = ["SNAP", "AAPL", "MSFT", "GOOGL"]

for symbol in symbols:
    print(f"\n{symbol}:")
    
    # Try yfinance
    try:
        ticker = yf.Ticker(symbol)
        data = yf.download(symbol, period="1d", progress=False)
        if not data.empty:
            price = data['Close'].iloc[-1]
            print(f"  yfinance: ${price:.2f}")
        else:
            print("  yfinance: No data")
    except Exception as e:
        print(f"  yfinance: Error - {e}")
    
    # Try CNBC
    try:
        url = f"https://quote.cnbc.com/quote-html-webservice/restQuote/symbolType/symbol?symbols={symbol}&requestMethod=itv&noform=1&partnerId=2&fund=1&exthrs=1&output=json&events=1"
        response = requests.get(url, timeout=5)
        data = response.json()
        if 'FormattedQuoteResult' in data:
            quotes = data['FormattedQuoteResult']['FormattedQuote']
            if quotes:
                price = float(quotes[0].get('last', '0').replace(',', ''))
                print(f"  CNBC: ${price:.2f}")
    except:
        print("  CNBC: Error")

print("\nUse the source that gives real prices!")