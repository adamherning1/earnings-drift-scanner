"""
Simplified pipeline to get REAL earnings data quickly
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

print("Fetching REAL earnings data from Yahoo Finance...")
print("=" * 60)

# Just analyze a few key stocks first
symbols = ["SNAP", "PINS", "ROKU", "DKNG", "AAPL", "MSFT"]
all_results = {}

for symbol in symbols:
    print(f"\nAnalyzing {symbol}...")
    
    try:
        ticker = yf.Ticker(symbol)
        
        # Get earnings history
        earnings = ticker.earnings_history
        if earnings is None or earnings.empty:
            print(f"  No earnings data")
            continue
            
        # Get 2 years of price data
        prices = ticker.history(period="2y")
        
        events_analyzed = 0
        drift_results = []
        
        # Analyze each earnings event
        for idx, row in earnings.head(8).iterrows():  # Last 8 quarters
            date = row['Earnings Date']
            actual = row['Reported EPS']
            estimate = row['EPS Estimate']
            
            if pd.isna(actual) or pd.isna(estimate):
                continue
                
            surprise_pct = ((actual - estimate) / abs(estimate) * 100) if estimate != 0 else 0
            
            # Find price drift
            earnings_date = pd.to_datetime(date)
            
            # Price day before
            pre_date = earnings_date - timedelta(days=1)
            pre_prices = prices[prices.index <= pre_date].tail(1)
            
            if pre_prices.empty:
                continue
                
            pre_price = pre_prices['Close'].iloc[0]
            
            # Price 5 days after
            post_date = earnings_date + timedelta(days=5)
            post_prices = prices[prices.index >= post_date].head(1)
            
            if post_prices.empty:
                continue
                
            post_price = post_prices['Close'].iloc[0]
            drift_pct = ((post_price - pre_price) / pre_price) * 100
            
            drift_results.append({
                'surprise_pct': surprise_pct,
                'drift_5day': drift_pct
            })
            events_analyzed += 1
        
        if drift_results:
            # Calculate correlation
            df = pd.DataFrame(drift_results)
            
            # Group by positive/negative surprise
            positive = df[df['surprise_pct'] > 10]
            negative = df[df['surprise_pct'] < -10]
            
            result = {
                'symbol': symbol,
                'events_analyzed': events_analyzed,
                'positive_surprises': {
                    'count': len(positive),
                    'avg_drift': positive['drift_5day'].mean() if len(positive) > 0 else 0,
                    'win_rate': (positive['drift_5day'] > 0).mean() * 100 if len(positive) > 0 else 0
                },
                'negative_surprises': {
                    'count': len(negative),
                    'avg_drift': negative['drift_5day'].mean() if len(negative) > 0 else 0,
                    'win_rate': (negative['drift_5day'] < 0).mean() * 100 if len(negative) > 0 else 0
                }
            }
            
            all_results[symbol] = result
            
            print(f"  ✓ Analyzed {events_analyzed} earnings events")
            print(f"  Positive surprise drift: {result['positive_surprises']['avg_drift']:.1f}%")
            print(f"  Negative surprise drift: {result['negative_surprises']['avg_drift']:.1f}%")
            
    except Exception as e:
        print(f"  Error: {e}")

# Calculate totals
total_events = sum(r['events_analyzed'] for r in all_results.values())

print(f"\n{'='*60}")
print(f"TOTAL REAL EARNINGS EVENTS ANALYZED: {total_events}")
print(f"{'='*60}")

# Save results
with open('real_drift_analysis.json', 'w') as f:
    json.dump(all_results, f, indent=2)

# Create summary
print("\nSUMMARY OF FINDINGS:")
print("-" * 40)

for symbol, data in all_results.items():
    pos = data['positive_surprises']
    neg = data['negative_surprises']
    
    if pos['count'] > 0 or neg['count'] > 0:
        print(f"\n{symbol}:")
        if pos['count'] > 0:
            print(f"  Positive surprises: {pos['avg_drift']:+.1f}% drift ({pos['count']} events)")
        if neg['count'] > 0:
            print(f"  Negative surprises: {neg['avg_drift']:+.1f}% drift ({neg['count']} events)")

print(f"\n✅ Your scanner now has {total_events} REAL earnings events!")
print("✅ Data saved to: real_drift_analysis.json")