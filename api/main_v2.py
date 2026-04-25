"""
FastAPI Main Application V2
Using Hybrid Data Sources (Yahoo + Manual Calendar)
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import os
import asyncio

# Import our hybrid scanner
from services.hybrid_earnings_scanner import HybridEarningsScanner
from services.playbook_generator import PlaybookGenerator
from services.paper_trader import PaperTrader

# Initialize services
scanner = HybridEarningsScanner()
playbook_gen = PlaybookGenerator()
paper_trader = PaperTrader()

app = FastAPI(
    title="Post-Earnings Drift Scanner V2",
    description="Playbook generation for systematic earnings traders",
    version="2.0.0"
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

class ScannerResponse(BaseModel):
    scan_time: str
    opportunities: Dict
    upcoming_total: int
    recent_total: int

# Routes
@app.get("/")
async def root():
    return {
        "service": "Post-Earnings Drift Scanner",
        "version": "2.0.0",
        "status": "operational",
        "data_sources": ["Yahoo Finance", "Manual Calendar", "Databento (optional)"]
    }

@app.get("/api/opportunities", response_model=ScannerResponse)
async def get_opportunities():
    """Get current scanner opportunities"""
    try:
        return scanner.get_scanner_opportunities()
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
        sue_data = scanner.calculate_sue(symbol.upper())
        return {
            "symbol": symbol.upper(),
            "sue_data": sue_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/playbook")
async def generate_playbook(request: PlaybookRequest):
    """Generate trading playbook for a symbol"""
    try:
        # Get stock data
        upcoming = scanner.get_upcoming_earnings(days_ahead=30)
        stock_data = next((s for s in upcoming if s['symbol'] == request.symbol.upper()), None)
        
        if not stock_data:
            # Try to get basic data
            enriched = scanner._enrich_with_yahoo({
                'symbol': request.symbol.upper(),
                'date': 'TBD'
            })
            stock_data = enriched
        
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

@app.post("/api/paper-trade/{trade_id}/update")
async def update_paper_trade(trade_id: str, exit_price: float):
    """Update a paper trade with exit"""
    try:
        paper_trader.close_trade(trade_id, exit_price)
        return {"status": "updated", "trade_id": trade_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Background scanner
async def continuous_scan():
    """Background task to scan for opportunities"""
    while True:
        try:
            # Scan every 30 minutes
            opportunities = scanner.get_scanner_opportunities()
            print(f"Scanner found {opportunities['upcoming_total']} upcoming earnings")
            
            # In production, would send alerts here
            
            await asyncio.sleep(1800)  # 30 minutes
        except Exception as e:
            print(f"Scanner error: {e}")
            await asyncio.sleep(300)  # Retry in 5 min

@app.post("/api/start-scanner")
async def start_scanner(background_tasks: BackgroundTasks):
    """Start the background scanner"""
    background_tasks.add_task(continuous_scan)
    return {"status": "scanner started"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "scanner": "operational",
            "playbook_generator": "operational",
            "paper_trader": "operational"
        }
    }

# Test endpoint for development
@app.get("/api/test")
async def test_endpoint():
    """Test data sources"""
    try:
        # Test Yahoo
        import yfinance as yf
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        
        return {
            "yahoo_finance": "connected",
            "test_symbol": "AAPL",
            "current_price": info.get('regularMarketPrice', 'N/A'),
            "manual_earnings": len(scanner.manual_earnings),
            "databento": "optional"
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)