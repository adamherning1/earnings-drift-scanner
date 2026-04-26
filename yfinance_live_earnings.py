"""
Use yfinance to get LIVE earnings data
"""
import yfinance as yf
import json
from datetime import datetime, timedelta

def get_live_earnings_data(symbol):
    """Get REAL earnings history from yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        
        # Get earnings history
        earnings = ticker.earnings_history
        
        if earnings is None or earnings.empty:
            return None
            
        # Analyze the data
        positive_surprises = []
        negative_surprises = []
        
        for _, row in earnings.iterrows():
            actual = row['Reported EPS']
            estimate = row['EPS Estimate']
            
            if actual and estimate:
                surprise_pct = ((actual - estimate) / abs(estimate) * 100)
                
                if surprise_pct > 10:
                    positive_surprises.append({
                        'date': row['Earnings Date'].strftime('%Y-%m-%d'),
                        'surprise': surprise_pct,
                        'actual': actual,
                        'estimate': estimate
                    })
                elif surprise_pct < -10:
                    negative_surprises.append({
                        'date': row['Earnings Date'].strftime('%Y-%m-%d'),
                        'surprise': surprise_pct,
                        'actual': actual,
                        'estimate': estimate
                    })
        
        # Calculate averages
        avg_pos = sum(s['surprise'] for s in positive_surprises) / len(positive_surprises) if positive_surprises else 0
        avg_neg = sum(s['surprise'] for s in negative_surprises) / len(negative_surprises) if negative_surprises else 0
        
        return {
            "symbol": symbol,
            "total_events": len(earnings),
            "positive_surprises": {
                "count": len(positive_surprises),
                "avg_surprise": round(avg_pos, 1),
                "events": positive_surprises[:5]  # Last 5
            },
            "negative_surprises": {
                "count": len(negative_surprises),
                "avg_surprise": round(avg_neg, 1),
                "events": negative_surprises[:5]  # Last 5
            },
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

# Test it
if __name__ == "__main__":
    symbols = ["SNAP", "PINS", "ROKU", "AAPL"]
    
    for symbol in symbols:
        print(f"\nFetching LIVE data for {symbol}...")
        data = get_live_earnings_data(symbol)
        
        if data:
            print(f"Total events: {data['total_events']}")
            print(f"Positive surprises: {data['positive_surprises']['count']} (avg: {data['positive_surprises']['avg_surprise']}%)")
            print(f"Negative surprises: {data['negative_surprises']['count']} (avg: {data['negative_surprises']['avg_surprise']}%)")