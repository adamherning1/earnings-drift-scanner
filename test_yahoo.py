"""
Test Yahoo Finance connection to debug the $100 issue
"""
import yfinance as yf

def test_yahoo_connection():
    print("Testing Yahoo Finance connection...")
    
    test_symbols = ["AAPL", "MSFT", "SNAP", "PINS"]
    
    for symbol in test_symbols:
        print(f"\nTesting {symbol}:")
        try:
            ticker = yf.Ticker(symbol)
            
            # Method 1: Get info dict
            info = ticker.info
            print(f"  Info keys: {len(info)} keys found")
            print(f"  regularMarketPrice: {info.get('regularMarketPrice', 'NOT FOUND')}")
            print(f"  currentPrice: {info.get('currentPrice', 'NOT FOUND')}")
            print(f"  previousClose: {info.get('previousClose', 'NOT FOUND')}")
            
            # Method 2: Get history
            hist = ticker.history(period="1d")
            if not hist.empty:
                latest_price = hist['Close'].iloc[-1]
                print(f"  History close price: ${latest_price:.2f}")
            else:
                print("  History: EMPTY")
                
            # Method 3: Fast info
            fast_info = ticker.fast_info
            print(f"  Fast info price: ${fast_info.get('lastPrice', 'NOT FOUND')}")
            
        except Exception as e:
            print(f"  ERROR: {e}")

if __name__ == "__main__":
    test_yahoo_connection()