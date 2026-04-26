import yfinance as yf

# Test if yfinance is working
print("Testing Yahoo Finance connection...")

try:
    # Get SNAP data
    snap = yf.Ticker("SNAP")
    
    # Get earnings history
    earnings = snap.earnings_history
    print(f"\nSNAP earnings history: {len(earnings) if earnings is not None else 0} quarters")
    
    if earnings is not None and not earnings.empty:
        print("\nLatest earnings:")
        print(earnings.head(3).to_string())
    
    # Get current price
    info = snap.info
    print(f"\nCurrent price: ${info.get('currentPrice', 'N/A')}")
    
except Exception as e:
    print(f"Error: {e}")
    print("\nMake sure yfinance is installed: pip install yfinance")