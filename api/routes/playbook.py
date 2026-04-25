"""
Playbook API Routes
Quick stats + AI-generated trading playbooks
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import yfinance as yf
from datetime import datetime, timedelta
from ..playbook_generator import PlaybookGenerator
import numpy as np

router = APIRouter(prefix="/api/playbook", tags=["playbook"])

# Mock historical data function (replace with real data source)
def get_historical_drift_data(symbol: str):
    """Get historical earnings drift patterns"""
    # In production, this would query your database of historical patterns
    # For now, using semi-realistic mock data
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        current_price = info.get('currentPrice', 100)
        
        # Simulate historical performance
        np.random.seed(hash(symbol) % 1000)  # Consistent per symbol
        
        quarters = []
        for i in range(12):
            drift = np.random.normal(0.015, 0.025)  # 1.5% avg, 2.5% std
            quarters.append({
                "quarter": f"Q{(i%4)+1} {2025 - i//4}",
                "drift_5d": drift,
                "earnings_move": np.random.normal(0, 0.05)
            })
        
        positive_drifts = sum(1 for q in quarters if q['drift_5d'] > 0)
        win_rate = positive_drifts / len(quarters)
        avg_move = np.mean([abs(q['drift_5d']) for q in quarters])
        best_drift = max(q['drift_5d'] for q in quarters)
        worst_drift = min(q['drift_5d'] for q in quarters)
        
        # Simulate IV rank (higher for popular earnings plays)
        iv_rank = min(95, max(20, 50 + hash(symbol) % 40))
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "historical_summary": {
                "total_quarters": 12,
                "positive_drifts": positive_drifts,
                "win_rate": win_rate,
                "avg_move": avg_move,
                "best_drift": best_drift,
                "worst_drift": worst_drift,
                "iv_rank": iv_rank
            },
            "quarterly_data": quarters
        }
    except:
        # Fallback for invalid symbols
        return None

@router.get("/{symbol}")
async def get_playbook(
    symbol: str,
    account_size: Optional[int] = Query(25000, description="Account size for position sizing")
):
    """
    Get AI-generated playbook for earnings trade
    
    Returns historical stats + 3 specific trade recommendations
    """
    
    # Validate symbol
    symbol = symbol.upper()
    
    # Get historical data
    historical = get_historical_drift_data(symbol)
    if not historical:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    
    # Get next earnings date (mock for now)
    # In production, this would query earnings calendar API
    earnings_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    # Generate playbook
    generator = PlaybookGenerator(account_size=account_size)
    
    playbook_data = {
        "win_rate": historical['historical_summary']['win_rate'],
        "avg_move": historical['historical_summary']['avg_move'],
        "current_price": historical['current_price'],
        "iv_rank": historical['historical_summary']['iv_rank']
    }
    
    playbook = generator.generate_playbook(symbol, earnings_date, playbook_data)
    
    # Format response
    return {
        "symbol": symbol,
        "current_price": f"${historical['current_price']:.2f}",
        "earnings_date": earnings_date,
        "quick_stats": {
            "Last 12 Quarters Performance": {
                "Avg 5-day drift": f"{historical['historical_summary']['avg_move']*100:+.1f}% (${historical['current_price']*historical['historical_summary']['avg_move']:+.2f})",
                "Win rate": f"{historical['historical_summary']['win_rate']*100:.0f}% ({historical['historical_summary']['positive_drifts']}/12 positive)",
                "Best drift": f"{historical['historical_summary']['best_drift']*100:+.1f}% (${historical['current_price']*historical['historical_summary']['best_drift']:+.2f})",
                "Worst drift": f"{historical['historical_summary']['worst_drift']*100:+.1f}% (${historical['current_price']*historical['historical_summary']['worst_drift']:+.2f})",
                "Current IV Rank": f"{historical['historical_summary']['iv_rank']}th percentile"
            }
        },
        "playbook": playbook['plays'],
        "confidence": playbook['historical_summary']['confidence'],
        "generated_at": datetime.now().isoformat()
    }

@router.get("/{symbol}/history")
async def get_historical_details(symbol: str):
    """Get detailed historical drift data for a symbol"""
    
    symbol = symbol.upper()
    historical = get_historical_drift_data(symbol)
    
    if not historical:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    
    return historical

@router.post("/{symbol}/track")
async def track_playbook_performance(
    symbol: str,
    play_type: str,
    entry_price: float,
    current_price: float
):
    """Track performance of an active playbook trade"""
    
    pnl = ((current_price - entry_price) / entry_price) * 100
    
    return {
        "symbol": symbol,
        "play_type": play_type,
        "entry_price": entry_price,
        "current_price": current_price,
        "pnl_percent": f"{pnl:+.1f}%",
        "status": "winning" if pnl > 0 else "losing",
        "recommendation": "hold" if abs(pnl) < 50 else "consider exit"
    }