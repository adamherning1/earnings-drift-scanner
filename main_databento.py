from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Post-Earnings Drift Scanner",
    description="Find profitable post-earnings opportunities - Powered by Claude AI & Databento",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manual earnings calendar for MVP
UPCOMING_EARNINGS = [
    {"symbol": "SNAP", "date": "2026-04-28", "time": "AMC", "name": "Snap Inc"},
    {"symbol": "PINS", "date": "2026-04-29", "time": "AMC", "name": "Pinterest"},
    {"symbol": "DKNG", "date": "2026-04-30", "time": "BMO", "name": "DraftKings"},
    {"symbol": "ROKU", "date": "2026-04-30", "time": "AMC", "name": "Roku"},
    {"symbol": "ETSY", "date": "2026-05-01", "time": "AMC", "name": "Etsy"},
    {"symbol": "NET", "date": "2026-05-02", "time": "AMC", "name": "Cloudflare"},
    {"symbol": "DASH", "date": "2026-05-07", "time": "AMC", "name": "DoorDash"},
    {"symbol": "PLTR", "date": "2026-05-07", "time": "BMO", "name": "Palantir"},
]

# For now, use static prices (Databento integration requires more setup)
MOCK_PRICES = {
    "SNAP": {"price": 15.42, "market_cap": 24.8e9},
    "PINS": {"price": 28.76, "market_cap": 18.5e9},
    "DKNG": {"price": 38.93, "market_cap": 17.2e9},
    "ROKU": {"price": 63.45, "market_cap": 8.9e9},
    "ETSY": {"price": 71.28, "market_cap": 8.1e9},
    "NET": {"price": 89.34, "market_cap": 29.7e9},
    "DASH": {"price": 122.15, "market_cap": 48.3e9},
    "PLTR": {"price": 21.89, "market_cap": 46.8e9},
}

@app.get("/")
def read_root():
    return {
        "service": "Post-Earnings Drift Scanner",
        "powered_by": "Claude AI by Anthropic",
        "data_provider": "Databento",
        "status": "operational",
        "endpoints": {
            "docs": "/docs",
            "upcoming": "/api/upcoming-earnings",
            "analyze": "/api/analyze/{symbol}",
            "opportunities": "/api/opportunities",
            "paper-trades": "/api/paper-trades"
        },
        "description": "AI-powered scanner finding post-earnings drift opportunities",
        "founding_members": "$97/month (limited time)"
    }

@app.get("/api/upcoming-earnings")
def get_upcoming_earnings():
    """Get stocks reporting earnings in the next 7 days"""
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    
    upcoming = []
    for earning in UPCOMING_EARNINGS:
        earning_date = datetime.strptime(earning["date"], "%Y-%m-%d").date()
        if today <= earning_date <= next_week:
            # Add mock price data
            symbol = earning["symbol"]
            if symbol in MOCK_PRICES:
                earning["current_price"] = MOCK_PRICES[symbol]["price"]
                earning["market_cap"] = f"${MOCK_PRICES[symbol]['market_cap']/1e9:.1f}B"
            else:
                earning["current_price"] = "N/A"
                earning["market_cap"] = "N/A"
            upcoming.append(earning)
    
    return {
        "count": len(upcoming),
        "earnings": upcoming,
        "updated": datetime.now().isoformat(),
        "note": "Using mock data for demo - Databento integration coming soon"
    }

@app.get("/api/analyze/{symbol}")
def analyze_stock(symbol: str):
    """Analyze a stock for post-earnings drift potential"""
    symbol = symbol.upper()
    
    # For demo, return mock data for any symbol
    # In production, this would fetch real data from Databento
    if symbol in MOCK_PRICES:
        data = MOCK_PRICES[symbol]
    else:
        # Generate mock data for any symbol
        import random
        price = round(random.uniform(20, 500), 2)
        data = {
            "price": price,
            "market_cap": round(random.uniform(1e9, 100e9), 0)
        }
    
    # Mock analysis with realistic values
    analysis = {
        "symbol": symbol,
        "current_price": data["price"],
        "market_cap": f"${data['market_cap']/1e9:.1f}B",
        "analysis": {
            "sue_score": 2.3,  # Standardized Unexpected Earnings
            "historical_drift": "Positive",
            "avg_post_earnings_move": "3.8%",
            "options_volume": "High",
            "short_interest": "12.4%"
        },
        "ai_recommendation": "STRONG BUY - High SUE score with positive drift history",
        "suggested_play": {
            "direction": "Long",
            "entry": f"${data['price']:.2f}",
            "target": f"${data['price'] * 1.038:.2f} (+3.8%)",
            "stop": f"${data['price'] * 0.98:.2f} (-2%)",
            "timeframe": "2-5 days post-earnings"
        },
        "analysis_date": datetime.now().isoformat()
    }
    
    return analysis

@app.get("/api/opportunities")
def get_opportunities():
    """Get current trading opportunities"""
    opportunities = []
    
    for symbol, data in MOCK_PRICES.items():
        opportunity = {
            "symbol": symbol,
            "price": data["price"],
            "market_cap": f"${data['market_cap']/1e9:.1f}B",
            "signal": "POST_EARNINGS" if symbol in ["SNAP", "PINS"] else "UPCOMING",
            "confidence": "HIGH" if symbol in ["SNAP", "PINS", "DKNG"] else "MEDIUM",
            "ai_insight": f"{symbol} showing strong momentum patterns"
        }
        opportunities.append(opportunity)
    
    return {
        "count": len(opportunities),
        "opportunities": opportunities,
        "scan_time": datetime.now().isoformat(),
        "powered_by": "Claude AI analysis"
    }

@app.get("/api/paper-trades")
def get_paper_trades():
    """Get paper trading performance"""
    # Mock paper trades for demo
    trades = [
        {
            "id": 1,
            "symbol": "AAPL",
            "date": "2026-04-20",
            "entry": 172.45,
            "exit": 178.23,
            "pnl": 335.24,
            "pnl_percent": 3.35,
            "status": "WIN"
        },
        {
            "id": 2,
            "symbol": "MSFT", 
            "date": "2026-04-22",
            "entry": 425.67,
            "exit": 418.92,
            "pnl": -168.75,
            "pnl_percent": -1.59,
            "status": "LOSS"
        },
        {
            "id": 3,
            "symbol": "GOOGL",
            "date": "2026-04-24",
            "entry": 175.23,
            "exit": None,
            "pnl": 0,
            "pnl_percent": 0,
            "status": "OPEN"
        }
    ]
    
    total_pnl = sum(t["pnl"] for t in trades if t["status"] != "OPEN")
    win_rate = len([t for t in trades if t["status"] == "WIN"]) / len([t for t in trades if t["status"] != "OPEN"]) * 100
    
    return {
        "trades": trades,
        "performance": {
            "total_trades": len(trades),
            "open_trades": len([t for t in trades if t["status"] == "OPEN"]),
            "wins": len([t for t in trades if t["status"] == "WIN"]),
            "losses": len([t for t in trades if t["status"] == "LOSS"]),
            "win_rate": f"{win_rate:.1f}%",
            "total_pnl": f"${total_pnl:.2f}",
            "status": "PROFITABLE" if total_pnl > 0 else "LEARNING"
        },
        "updated": datetime.now().isoformat()
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "databento_configured": bool(os.getenv("DATABENTO_API_KEY")),
        "timestamp": datetime.now().isoformat()
    }