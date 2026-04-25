from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Test API"}

@app.get("/test-yfinance")
def test_yfinance():
    try:
        import yfinance as yf
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        return {
            "status": "success",
            "yfinance_installed": True,
            "test_symbol": "AAPL",
            "price": info.get("regularMarketPrice", "No price data")
        }
    except ImportError:
        return {
            "status": "error",
            "yfinance_installed": False,
            "message": "yfinance not installed"
        }
    except Exception as e:
        return {
            "status": "error",
            "yfinance_installed": True,
            "message": str(e)
        }