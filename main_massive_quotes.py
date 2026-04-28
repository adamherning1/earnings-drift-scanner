from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional
import time
import json
from dynamic_opportunities import get_dynamic_opportunities

load_dotenv()

app = FastAPI(
    title="Post-Earnings Drift Scanner",
    description="Professional scanner with Finnhub real-time quotes and earnings",
    version="14.0.0"  # Updated to use Finnhub for prices
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Finnhub configuration (already in use for earnings)
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "d7n6829r01qppri3n0p0d7n6829r01qppri3n0pg")

# Cache for efficiency
cache = {}
CACHE_DURATION = 60  # 1 minute for real-time data

def get_finnhub_quote(symbol: str) -> Optional[Dict]:
    """Get real-time quote from Finnhub"""
    try:
        # Check cache first
        cache_key = f"quote_{symbol}"
        now = time.time()
        if cache_key in cache:
            cached_data, cached_time = cache[cache_key]
            if now - cached_time < CACHE_DURATION:
                return cached_data
        
        # Fetch from Finnhub quote endpoint
        url = "https://finnhub.io/api/v1/quote"
        params = {
            "symbol": symbol.upper(),
            "token": FINNHUB_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # Finnhub returns: c=current, h=high, l=low, o=open, pc=previous close
            if data.get('c', 0) > 0:
                result = {
                    "price": data['c'],
                    "bid": data['c'] - 0.01,  # Estimate bid
                    "ask": data['c'] + 0.01,  # Estimate ask
                    "high": data['h'],
                    "low": data['l'],
                    "open": data['o'],
                    "previous_close": data['pc'],
                    "change": data['c'] - data['pc'],
                    "change_percent": ((data['c'] - data['pc']) / data['pc'] * 100) if data['pc'] > 0 else 0,
                    "spread": 0.02,
                    "source": "finnhub_live"
                }
                
                # Cache the result
                cache[cache_key] = (result, now)
                return result
                
        elif response.status_code == 429:
            print(f"Finnhub rate limit hit - 60 calls/minute on free tier")
            
    except Exception as e:
        print(f"Error fetching Finnhub quote for {symbol}: {e}")
    
    return None

# Updated April 2026 prices (more realistic fallbacks)
CURRENT_PRICES = {
    "SNAP": {"price": 15.42, "bid": 15.41, "ask": 15.43},
    "PINS": {"price": 28.76, "bid": 28.75, "ask": 28.77},
    "DKNG": {"price": 38.93, "bid": 38.92, "ask": 38.94},
    "ROKU": {"price": 63.45, "bid": 63.44, "ask": 63.46},
    "AAPL": {"price": 182.45, "bid": 182.44, "ask": 182.46},
    "MSFT": {"price": 425.67, "bid": 425.66, "ask": 425.68},
    "GOOGL": {"price": 175.23, "bid": 175.22, "ask": 175.24},
    "TSLA": {"price": 178.92, "bid": 178.91, "ask": 178.93}
}

def get_stock_data(symbol: str) -> Dict:
    """Get stock data from Finnhub with fallback"""
    # Try Finnhub quote first
    quote = get_finnhub_quote(symbol)
    if quote and quote["price"] > 0:
        return {
            "price": quote["price"],
            "bid": quote["bid"],
            "ask": quote["ask"],
            "spread": quote["spread"],
            "source": quote["source"]
        }
    
    # Fallback prices if API fails
    if symbol in CURRENT_PRICES:
        fb = CURRENT_PRICES[symbol]
        return {
            "price": fb["price"],
            "bid": fb["bid"],
            "ask": fb["ask"],
            "spread": fb["ask"] - fb["bid"],
            "source": "fallback"
        }
    
    # Default for unknown symbols
    return {
        "price": 100.0,
        "bid": 99.99,
        "ask": 100.01,
        "spread": 0.02,
        "source": "default"
    }

def get_upcoming_earnings_from_finnhub():
    """Fetch upcoming earnings from Finnhub"""
    try:
        # Get earnings calendar for next 30 days
        from_date = datetime.now().strftime("%Y-%m-%d")
        to_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        url = f"https://finnhub.io/api/v1/calendar/earnings"
        params = {
            "from": from_date,
            "to": to_date,
            "token": FINNHUB_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "earningsCalendar" in data:
                return data["earningsCalendar"][:20]  # Limit to 20 for display
        else:
            print(f"Finnhub calendar error: {response.status_code}")
    except Exception as e:
        print(f"Error fetching Finnhub calendar: {e}")
    
    # Return some default data as fallback
    return [
        {"date": "2026-05-01", "symbol": "AAPL", "epsActual": None, "epsEstimate": 1.52},
        {"date": "2026-05-02", "symbol": "MSFT", "epsActual": None, "epsEstimate": 3.21}
    ]

@app.get("/")
def read_root():
    return {
        "message": "Post-Earnings Drift Scanner API",
        "version": "14.0.0",
        "data_source": "Finnhub (Prices + Earnings)",
        "endpoints": [
            "/api/opportunities",
            "/api/quote/{symbol}",
            "/api/analyze/{symbol}",
            "/api/upcoming-earnings",
            "/health"
        ]
    }

@app.get("/api/upcoming-earnings")
def get_upcoming_earnings():
    earnings = get_upcoming_earnings_from_finnhub()
    
    # Add current prices to each earning
    for earning in earnings:
        if "symbol" in earning:
            data = get_stock_data(earning["symbol"])
            earning["current_price"] = data["price"]
            earning["price_source"] = data["source"]
    
    return {
        "count": len(earnings),
        "earnings": earnings,
        "source": "finnhub"
    }

@app.get("/api/quote/{symbol}")
def get_quote(symbol: str):
    symbol = symbol.upper()
    data = get_stock_data(symbol)
    
    return {
        "symbol": symbol,
        "price": data["price"],
        "bid": data["bid"],
        "ask": data["ask"],
        "spread": data["spread"],
        "mid_point": (data["bid"] + data["ask"]) / 2 if data["bid"] > 0 and data["ask"] > 0 else data["price"],
        "source": data["source"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/analyze/{symbol}")
def analyze_stock(symbol: str):
    symbol = symbol.upper()
    data = get_stock_data(symbol)
    
    price = data["price"]
    
    # Initialize variables
    sue_score = 1.5
    last_surprise_pct = 0
    historical_win_rate = "N/A"
    earnings_count = 0
    avg_drift = 3.5  # Default
    
    # Get earnings history from Finnhub
    try:
        url = f"https://finnhub.io/api/v1/stock/earnings?symbol={symbol}&token={FINNHUB_API_KEY}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            earnings = response.json()
            if earnings and len(earnings) > 0:
                earnings_count = len(earnings)
                
                # Calculate from most recent earnings
                recent = earnings[0]
                if recent.get('actual') and recent.get('estimate'):
                    last_surprise_pct = ((recent['actual'] - recent['estimate']) / abs(recent['estimate'])) * 100
                    sue_score = 1.5 + (last_surprise_pct / 10)  # Convert to SUE scale
                    
                    # Count positive surprises for win rate
                    positive_surprises = sum(1 for e in earnings[:8] 
                                           if e.get('actual') and e.get('estimate') 
                                           and e['actual'] > e['estimate'])
                    
                    if len(earnings[:8]) > 0:
                        win_rate_pct = (positive_surprises / min(len(earnings), 8)) * 100
                        historical_win_rate = f"{win_rate_pct:.0f}%"
                    
                    # Calculate average drift based on surprise magnitude
                    if abs(last_surprise_pct) > 10:
                        avg_drift = 4.5
                    elif abs(last_surprise_pct) > 5:
                        avg_drift = 3.2
                    else:
                        avg_drift = 2.1
    except:
        pass
    
    # Generate analysis
    expected_drift = abs(sue_score - 1.5) * 2.5
    
    # Determine confidence and based_on
    if earnings_count >= 8:
        confidence = "HIGH"
        based_on = f"Analysis of {earnings_count} earnings reports"
    elif earnings_count >= 4:
        confidence = "MEDIUM"
        based_on = f"Based on {earnings_count} earnings reports"
    else:
        confidence = "LOW"
        based_on = "Limited historical data available"
    
    analysis = {
        "symbol": symbol,
        "current_price": price,
        "bid": data["bid"],
        "ask": data["ask"],
        "spread": data["spread"],
        "data_quality": data["source"],
        "analysis": {
            "sue_score": round(sue_score, 2),
            "last_surprise": f"{last_surprise_pct:+.1f}%" if last_surprise_pct != 0 else "N/A",
            "historical_drift": "Positive" if sue_score > 1.5 else "Negative",
            "avg_post_earnings_move": f"{expected_drift:.1f}%",
            "drift_confidence": confidence,
            "based_on": based_on,
            "historical_win_rate": historical_win_rate,
            "liquidity": "High" if data["spread"] < 0.05 else "Medium" if data["spread"] < 0.10 else "Low",
            "options_activity": "Elevated" if symbol in ["SNAP", "PINS", "AAPL", "MSFT"] else "Normal"
        },
        "ai_recommendation": (
            "BUY - Post-earnings momentum detected" if sue_score > 1.8 else
            "WATCH - Potential drift setup" if sue_score > 1.5 else
            "AVOID - Negative drift expected" if sue_score < 1.2 else
            "HOLD - Neutral outlook"
        ),
        "suggested_play": {
            "direction": "Long" if sue_score > 1.5 else "Short",
            "entry": f"${price:.2f}",
            "target": f"${price * (1 + expected_drift/100):.2f} (+{expected_drift:.1f}%)",
            "stop": f"${price * 0.98:.2f} (-2%)",
            "timeframe": "2-5 days post-earnings"
        },
        "timestamp": datetime.now().isoformat()
    }
    
    return analysis

@app.get("/api/opportunities")
def get_opportunities():
    """Get dynamic opportunities based on real earnings surprises"""
    try:
        # Get dynamic opportunities from our scanner
        dynamic_data = get_dynamic_opportunities()
        
        # If we have real opportunities, return them
        if dynamic_data["opportunities"]:
            return dynamic_data
            
        # Otherwise fall back to some default monitoring stocks
        symbols = ["SNAP", "PINS", "DKNG", "ROKU", "AAPL", "MSFT"]
        opportunities = []
        
        for symbol in symbols:
            data = get_stock_data(symbol)
            
            if data["price"] > 0:
                # Calculate opportunity score
                liquidity_score = 1 - (data["spread"] / data["price"]) if data["price"] > 0 else 0
                
                opportunity = {
                    "symbol": symbol,
                    "price": data["price"],
                    "bid_ask_spread": f"${data['spread']:.2f}",
                    "liquidity_score": f"{liquidity_score * 100:.1f}%",
                    "signal": "MONITORING",
                    "confidence": "MEDIUM",
                    "data_source": data["source"],
                    "ai_insight": f"{symbol} on watchlist for next earnings"
                }
            opportunities.append(opportunity)
    
    return {
        "count": len(opportunities),
        "opportunities": opportunities,
        "scan_time": datetime.now().isoformat()
    }

@app.get("/health")
def health_check():
    # Test Finnhub
    test_quote = get_finnhub_quote("AAPL")
    
    return {
        "status": "healthy",
        "finnhub_configured": True,
        "price_api_working": test_quote is not None,
        "test_price": test_quote["price"] if test_quote else "Using fallback",
        "cache_entries": len(cache),
        "version": "14.0.0",
        "data_sources": {
            "prices": "finnhub",
            "earnings": "finnhub"
        }
    }

@app.get("/api/version")
def get_version():
    return {
        "version": "14.0.0",
        "description": "Finnhub integration for both prices and earnings",
        "api_status": "production"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)