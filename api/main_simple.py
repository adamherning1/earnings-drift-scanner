"""
Simplified FastAPI app for Render deployment
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

app = FastAPI(
    title="Earnings Scanner API",
    description="Post-earnings drift scanner",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "service": "Earnings Scanner",
        "version": "1.0.0",
        "status": "operational",
        "message": "Use /api/test to verify Yahoo Finance connection"
    }

@app.get("/api/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/test")
async def test():
    """Test Yahoo Finance is working"""
    try:
        import yfinance as yf
        # Simple test without metadata
        ticker = yf.download("AAPL", period="1d", progress=False)
        if not ticker.empty:
            latest_price = ticker['Close'].iloc[-1]
            return {
                "status": "success",
                "message": "Yahoo Finance connected",
                "test_symbol": "AAPL",
                "latest_close": float(latest_price)
            }
        else:
            return {"status": "error", "message": "No data returned"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/upcoming")
async def upcoming():
    """Get manually tracked upcoming earnings"""
    return {
        "earnings": [
            {"symbol": "SNAP", "date": "2026-04-28", "time": "AMC"},
            {"symbol": "PINS", "date": "2026-04-29", "time": "AMC"},
            {"symbol": "DKNG", "date": "2026-04-30", "time": "BMO"},
            {"symbol": "ROKU", "date": "2026-04-30", "time": "AMC"},
            {"symbol": "ETSY", "date": "2026-05-01", "time": "AMC"}
        ],
        "source": "manual_calendar"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)