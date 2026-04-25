"""
FastAPI Main Application
Post-Earnings Drift Scanner API
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Dict, Optional
import os
from datetime import datetime
import asyncio

# Import our services
from services.sue_calculator import SUECalculator
from services.universe_screener import UniverseScreener
from services.earnings_ingestion import EarningsIngestionService
from services.paper_trader import PaperTrader

# Get API key from environment
FMP_API_KEY = os.getenv('FMP_API_KEY', '')

# Initialize services
sue_calculator = SUECalculator()
universe_screener = UniverseScreener(FMP_API_KEY)
earnings_service = EarningsIngestionService(FMP_API_KEY)
paper_trader = PaperTrader()

# Background task for continuous scanning
background_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Post-Earnings Drift Scanner API...")
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title="Post-Earnings Drift Scanner",
    description="Academic-grade PEAD signal generation and paper trading",
    version="0.1.0",
    lifespan=lifespan
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check and basic info."""
    return {
        "status": "running",
        "service": "Post-Earnings Drift Scanner",
        "version": "0.1.0",
        "paper_trading_active": True
    }

@app.get("/api/opportunities")
async def get_opportunities(
    days_back: int = 5,
    min_sue: float = 1.5
) -> Dict:
    """
    Get current drift opportunities based on recent earnings.
    
    Args:
        days_back: How many days back to look for earnings
        min_sue: Minimum SUE score to consider (1.5 = Q5/Q1 only)
    """
    try:
        # Get recent earnings
        earnings_data = earnings_service.scan_for_new_earnings()
        
        if not earnings_data:
            return {
                "opportunities": [],
                "message": "No new earnings found in the specified period"
            }
        
        # Calculate SUE for each
        sue_results = sue_calculator.calculate_batch(earnings_data)
        
        # Filter for tradeable signals
        tradeable = sue_results[
            (sue_results['is_tradeable'] == True) & 
            (abs(sue_results['sue_score']) >= min_sue)
        ]
        
        # Get universe filter data
        candidates = universe_screener.screen_universe()
        valid_symbols = {c.symbol for c in candidates}
        
        # Filter by universe constraints
        final_opportunities = tradeable[tradeable['symbol'].isin(valid_symbols)]
        
        # Convert to dict format
        opportunities = final_opportunities.to_dict('records')
        
        # Add confidence scores
        for opp in opportunities:
            confidence = sue_calculator.get_signal_confidence(opp['sue_score'])
            opp.update(confidence)
        
        return {
            "opportunities": opportunities,
            "total_found": len(opportunities),
            "scan_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis/{symbol}")
async def get_analysis(symbol: str) -> Dict:
    """
    Get detailed analysis for a specific symbol.
    """
    try:
        # Get historical earnings
        historical = earnings_service.get_historical_surprises(symbol, quarters=12)
        
        # Get current quote
        quote = universe_screener.get_stock_quote(symbol)
        
        if not quote:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        return {
            "symbol": symbol,
            "company": quote.get('name', ''),
            "price": quote.get('price', 0),
            "market_cap": quote.get('marketCap', 0),
            "avg_volume": quote.get('avgVolume', 0),
            "historical_surprises": historical,
            "historical_quarters": len(historical),
            "avg_surprise": sum(historical) / len(historical) if historical else 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/paper-trade")
async def execute_paper_trade(
    symbol: str,
    current_price: float,
    sue_score: float,
    quintile: int,
    direction: str
) -> Dict:
    """
    Execute a paper trade based on signal.
    """
    try:
        position = paper_trader.enter_position(
            symbol=symbol,
            current_price=current_price,
            sue_score=sue_score,
            quintile=quintile,
            direction=direction
        )
        
        return {
            "success": True,
            "position": {
                "id": position.id,
                "symbol": position.symbol,
                "entry_price": position.entry_price,
                "position_size": position.position_size,
                "stop_loss": position.stop_loss,
                "take_profit": position.take_profit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/paper-performance")
async def get_paper_performance() -> Dict:
    """
    Get current paper trading performance.
    """
    stats = paper_trader.get_performance_stats()
    report = paper_trader.generate_transparency_report()
    
    return {
        "statistics": stats,
        "report": report,
        "open_positions": [
            {
                "symbol": p.symbol,
                "direction": p.direction,
                "entry_price": p.entry_price,
                "sue_score": p.sue_score,
                "days_held": (datetime.now() - datetime.strptime(p.entry_date, '%Y-%m-%d')).days
            }
            for p in paper_trader.positions
        ]
    }

@app.post("/api/start-scanner")
async def start_scanner(background_tasks: BackgroundTasks) -> Dict:
    """
    Start the background earnings scanner.
    """
    def scan_task():
        earnings_service.continuous_scan(interval_minutes=15)
    
    background_tasks.add_task(scan_task)
    
    return {
        "status": "Scanner started",
        "scan_interval": "15 minutes (5 minutes during peak hours)"
    }

@app.get("/api/universe-stats")
async def get_universe_stats() -> Dict:
    """
    Get statistics about our tradeable universe.
    """
    try:
        candidates = universe_screener.screen_universe()
        df = universe_screener.to_dataframe(candidates)
        
        if len(df) == 0:
            return {"error": "No candidates found"}
        
        return {
            "total_candidates": len(df),
            "avg_market_cap_b": round(df['market_cap_b'].mean(), 2),
            "sectors": df['sector'].value_counts().to_dict(),
            "with_weekly_options": int(df['weekly_options'].sum()),
            "recent_earnings": len(df)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run with: uvicorn main:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)