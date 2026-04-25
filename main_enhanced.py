from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import List, Dict
import yfinance as yf

app = FastAPI(
    title="Post-Earnings Drift Scanner",
    description="Find profitable post-earnings opportunities",
    version="2.0.0"
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

@app.get("/")
def read_root():
    return {
        "service": "Post-Earnings Drift Scanner",
        "status": "operational",
        "endpoints": {
            "docs": "/docs",
            "upcoming": "/api/upcoming-earnings",
            "analyze": "/api/analyze/{symbol}",
            "opportunities": "/api/opportunities"
        }
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
            # Add current price from Yahoo
            try:
                ticker = yf.Ticker(earning["symbol"])
                info = ticker.info
                earning["current_price"] = info.get("regularMarketPrice", 0)
                earning["market_cap"] = info.get("marketCap", 0)
            except:
                earning["current_price"] = "N/A"
                earning["market_cap"] = "N/A"
            upcoming.append(earning)
    
    return {
        "count": len(upcoming),
        "earnings": upcoming,
        "updated": datetime.now().isoformat()
    }

@app.get("/api/analyze/{symbol}")
def analyze_stock(symbol: str):
    """Analyze a stock for post-earnings drift potential"""
    symbol = symbol.upper()
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Get recent price history
        hist = ticker.history(period="1mo")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        # Calculate basic metrics
        current_price = info.get("regularMarketPrice", hist['Close'].iloc[-1])
        avg_volume = info.get("averageVolume", hist['Volume'].mean())
        
        # Simple volatility measure
        price_volatility = (hist['High'] - hist['Low']).mean() / hist['Close'].mean() * 100
        
        return {
            "symbol": symbol,
            "name": info.get("longName", symbol),
            "current_price": current_price,
            "market_cap": info.get("marketCap", 0),
            "avg_volume": avg_volume,
            "volatility": round(price_volatility, 2),
            "recommendation": "Monitor" if price_volatility > 3 else "Skip",
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/opportunities")
def get_opportunities():
    """Get current trading opportunities"""
    opportunities = []
    
    # Check our tracked symbols
    symbols = ["SNAP", "PINS", "DKNG", "ROKU", "ETSY"]
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Simple opportunity scoring
            opportunity = {
                "symbol": symbol,
                "name": info.get("longName", symbol),
                "price": info.get("regularMarketPrice", 0),
                "change_pct": info.get("regularMarketChangePercent", 0),
                "volume": info.get("volume", 0),
                "avg_volume": info.get("averageVolume", 0),
                "volume_ratio": info.get("volume", 0) / info.get("averageVolume", 1) if info.get("averageVolume", 0) > 0 else 0
            }
            
            # Flag high volume (potential post-earnings move)
            if opportunity["volume_ratio"] > 2:
                opportunity["signal"] = "HIGH_VOLUME"
            elif abs(opportunity["change_pct"]) > 5:
                opportunity["signal"] = "BIG_MOVE"
            else:
                opportunity["signal"] = "NORMAL"
                
            opportunities.append(opportunity)
            
        except:
            continue
    
    # Sort by volume ratio (highest activity first)
    opportunities.sort(key=lambda x: x["volume_ratio"], reverse=True)
    
    return {
        "count": len(opportunities),
        "opportunities": opportunities,
        "scan_time": datetime.now().isoformat()
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}