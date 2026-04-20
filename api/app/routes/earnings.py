from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta

from ..database import get_db
from ..models import EarningsEvent, DriftPattern
from ..services.earnings_data import EarningsDataService
from ..services.auth import get_current_user, User

router = APIRouter()

@router.get("/upcoming")
async def get_upcoming_earnings(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Get upcoming earnings for the next N days"""
    today = date.today()
    end_date = today + timedelta(days=days)
    
    earnings = db.query(EarningsEvent).filter(
        EarningsEvent.earnings_date >= today,
        EarningsEvent.earnings_date <= end_date
    ).order_by(EarningsEvent.earnings_date).limit(100).all()
    
    return {
        "count": len(earnings),
        "start_date": today.isoformat(),
        "end_date": end_date.isoformat(),
        "earnings": [
            {
                "symbol": e.symbol,
                "earnings_date": e.earnings_date.isoformat(),
                "reported_time": e.reported_time,
                "eps_estimate": e.eps_estimate
            } for e in earnings
        ]
    }

@router.get("/{symbol}/preview")
async def get_earnings_preview(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get free preview of earnings data (last 4 quarters)"""
    symbol = symbol.upper()
    
    # Get last 4 earnings events
    earnings = db.query(EarningsEvent).filter(
        EarningsEvent.symbol == symbol
    ).order_by(EarningsEvent.earnings_date.desc()).limit(4).all()
    
    if not earnings:
        # Try to fetch from external source
        service = EarningsDataService(db)
        earnings = await service.fetch_earnings_history(symbol, quarters=4)
    
    return {
        "symbol": symbol,
        "preview": True,
        "earnings_count": len(earnings),
        "data": [
            {
                "date": e.earnings_date.isoformat(),
                "eps_actual": e.eps_actual,
                "eps_estimate": e.eps_estimate,
                "surprise_pct": e.eps_surprise_pct,
                "revenue_surprise_pct": e.revenue_surprise_pct
            } for e in earnings
        ]
    }

@router.get("/{symbol}/analysis")
async def get_full_analysis(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get full 12-quarter analysis with drift patterns (requires subscription)"""
    symbol = symbol.upper()
    
    # Check subscription
    if current_user.subscription_tier == "free":
        raise HTTPException(status_code=403, detail="Subscription required")
    
    # Check usage limits
    tier_limits = {
        "starter": 10,
        "professional": 50,
        "institution": 999999
    }
    
    if current_user.searches_this_month >= tier_limits.get(current_user.subscription_tier, 0):
        raise HTTPException(status_code=429, detail="Monthly search limit reached")
    
    # Get earnings with drift patterns
    earnings = db.query(EarningsEvent).filter(
        EarningsEvent.symbol == symbol
    ).order_by(EarningsEvent.earnings_date.desc()).limit(12).all()
    
    if not earnings:
        service = EarningsDataService(db)
        earnings = await service.fetch_earnings_history(symbol, quarters=12)
        await service.calculate_drift_patterns(symbol)
    
    # Update usage
    current_user.searches_this_month += 1
    current_user.last_search_at = datetime.utcnow()
    db.commit()
    
    # Build response with drift patterns
    result = []
    for event in earnings:
        drift_data = db.query(DriftPattern).filter(
            DriftPattern.earnings_event_id == event.id
        ).order_by(DriftPattern.days_before).all()
        
        result.append({
            "earnings_date": event.earnings_date.isoformat(),
            "reported_time": event.reported_time,
            "eps_actual": event.eps_actual,
            "eps_estimate": event.eps_estimate,
            "eps_surprise_pct": event.eps_surprise_pct,
            "revenue_surprise_pct": event.revenue_surprise_pct,
            "drift_pattern": [
                {
                    "days_before": d.days_before,
                    "cumulative_return": d.cumulative_return,
                    "relative_to_spy": d.relative_to_spy,
                    "volume_ratio": d.volume_ratio
                } for d in drift_data
            ]
        })
    
    return {
        "symbol": symbol,
        "analysis_date": datetime.utcnow().isoformat(),
        "quarters_analyzed": len(result),
        "data": result
    }

@router.get("/{symbol}/statistics")
async def get_drift_statistics(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistical analysis of earnings drift patterns"""
    if current_user.subscription_tier not in ["professional", "institution"]:
        raise HTTPException(status_code=403, detail="Professional subscription required")
    
    symbol = symbol.upper()
    
    # Get all drift patterns for analysis
    service = EarningsDataService(db)
    stats = await service.calculate_drift_statistics(symbol)
    
    return {
        "symbol": symbol,
        "statistics": stats
    }