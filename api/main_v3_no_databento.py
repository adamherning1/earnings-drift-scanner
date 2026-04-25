"""
FastAPI Main Application V3 - Yahoo Finance Only
No Databento dependency for clean deployment
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import os
import asyncio

# Import our Yahoo-only scanner
from services.yahoo_earnings_scanner import YahooEarningsScanner
from services.playbook_generator import PlaybookGenerator
from services.paper_trader import PaperTrader

# Initialize services
scanner = YahooEarningsScanner()
playbook_gen = PlaybookGenerator()
paper_trader = PaperTrader()

app = FastAPI(
    title="Post-Earnings Drift Scanner V3",
    description="Yahoo Finance powered earnings scanner",
    version="3.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class PlaybookRequest(BaseModel):
    symbol: str
    account_size: float = 25000
    risk_per_trade: float = 0.05

# Routes
@app.get("/")
async def root():
    return {
        "service": "Post-Earnings Drift Scanner",
        "version": "3.0.0",
        "status": "operational",
        "data_source": "Yahoo Finance"
    }

@app.get("/api/opportunities")
async def get_opportunities():
    """Get current scanner opportunities"""
    try:
        upcoming = scanner.get_upcoming_earnings(days_ahead=7)
        recent = scanner.get_recent_earnings(days_back=5)
        
        return {
            "scan_time": datetime.now().isoformat(),
            "upcoming_earnings": upcoming[:10],
            "recent_surprises": recent[:5],
            "total_upcoming": len(upcoming),
            "total_recent": len(recent)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/upcoming-earnings")
async def get_upcoming_earnings(days: int = 7):
    """Get earnings announcements in next N days"""
    try:
        earnings = scanner.get_upcoming_earnings(days_ahead=days)
        return {
            "count": len(earnings),
            "earnings": earnings,
            "days_ahead": days
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/recent-surprises")
async def get_recent_surprises(days: int = 5):
    """Get recent earnings surprises"""
    try:
        surprises = scanner.get_recent_earnings(days_back=days)
        return {
            "count": len(surprises),
            "surprises": surprises,
            "days_back": days
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sue/{symbol}")
async def calculate_sue(symbol: str):
    """Calculate SUE score for a symbol"""
    try:
        sue_score = scanner.calculate_sue(symbol.upper())
        return {
            "symbol": symbol.upper(),
            "sue": sue_score,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/playbook")
async def generate_playbook(request: PlaybookRequest):
    """Generate trading playbook for a symbol"""
    try:
        # Get basic stock data from Yahoo
        import yfinance as yf
        ticker = yf.Ticker(request.symbol.upper())
        info = ticker.info
        
        stock_data = {
            'symbol': request.symbol.upper(),
            'company_name': info.get('longName', request.symbol),
            'current_price': info.get('regularMarketPrice', 0),
            'market_cap': info.get('marketCap', 0),
            'volume': info.get('averageVolume', 0)
        }
        
        # Generate playbook
        playbook = playbook_gen.generate_playbook(
            stock_data,
            request.account_size,
            request.risk_per_trade
        )
        
        return playbook
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/paper-trades")
async def get_paper_trades():
    """Get all paper trading results"""
    try:
        return {
            "trades": paper_trader.get_all_trades(),
            "performance": paper_trader.get_performance_summary()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_source": "Yahoo Finance"
    }

@app.get("/api/test")
async def test_endpoint():
    """Test Yahoo Finance connection"""
    try:
        import yfinance as yf
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        
        return {
            "status": "connected",
            "test_symbol": "AAPL",
            "current_price": info.get('regularMarketPrice', 'N/A'),
            "data_source": "Yahoo Finance"
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)