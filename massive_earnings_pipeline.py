"""
Massive Earnings Pipeline - Using the correct v2/reference/earnings endpoint
"""
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List

class MassiveEarningsPipeline:
    def __init__(self):
        self.api_key = os.getenv("MASSIVE_API_KEY", "W9yf_4m5NsX89ZNS5jGSfYkVorDBPiGfN")
        self.base_url = "https://api.massive.com/v2/reference/earnings"
        self.earnings_data = {}
        self.drift_patterns = {}
        
    def get_universe_tickers(self) -> List[str]:
        """Get our universe of stocks"""
        return [
            "SNAP", "PINS", "DKNG", "ROKU", "ETSY", "NET", "DOCU", "ZM",
            "CRWD", "OKTA", "TWLO", "SQ", "SHOP", "RBLX", "PLTR", "PATH"
        ]
    
    def fetch_earnings(self, ticker: str) -> List[Dict]:
        """Fetch earnings history from Massive v2/reference/earnings"""
        print(f"Fetching earnings for {ticker}...")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        params = {
            "ticker": ticker,
            "limit": 50000,
            "sort": "date.desc"
        }
        
        try:
            response = requests.get(self.base_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle different response formats
                if isinstance(data, list):
                    earnings = data
                elif isinstance(data, dict) and "results" in data:
                    earnings = data["results"]
                else:
                    earnings = []
                
                print(f"  Found {len(earnings)} earnings events")
                return earnings
                
            else:
                print(f"  Error {response.status_code}: {response.text[:100]}")
                return []
                
        except Exception as e:
            print(f"  Exception: {e}")
            return []
    
    def fetch_price_data(self, ticker: str, date: str, days_after: int = 63) -> Dict:
        """Fetch historical prices around earnings date"""
        # Use Massive's aggregates endpoint for price data
        try:
            earnings_date = datetime.strptime(date[:10], "%Y-%m-%d")
            start_date = (earnings_date - timedelta(days=5)).strftime("%Y-%m-%d")
            end_date = (earnings_date + timedelta(days=days_after)).strftime("%Y-%m-%d")
            
            url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}"
            params = {"apiKey": self.api_key}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "OK" and data.get("results"):
                    prices = data["results"]
                    
                    # Find pre and post earnings prices
                    pre_price = None
                    post_prices = []
                    
                    for bar in prices:
                        bar_date = datetime.fromtimestamp(bar["t"] / 1000).date()
                        earnings_dt = earnings_date.date()
                        
                        # Day before earnings
                        if bar_date < earnings_dt and not pre_price:
                            pre_price = bar["c"]
                        
                        # Days after earnings
                        if bar_date >= earnings_dt:
                            days_diff = (bar_date - earnings_dt).days
                            post_prices.append({
                                "days_after": days_diff,
                                "price": bar["c"],
                                "volume": bar["v"]
                            })
                    
                    if pre_price and post_prices:
                        return {
                            "pre_price": pre_price,
                            "post_prices": post_prices
                        }
                        
        except Exception as e:
            print(f"  Price fetch error: {e}")
            
        return None
    
    def analyze_earnings_drift(self, ticker: str, earnings_list: List[Dict]) -> Dict:
        """Analyze drift patterns from earnings data"""
        analyzed_events = []
        
        for earning in earnings_list[:20]:  # Last 20 quarters
            # Extract earnings data using CORRECT Massive/Benzinga field names
            date = earning.get("date")  # YYYY-MM-DD format
            actual_eps = earning.get("actual_eps")  # reported EPS
            estimate_eps = earning.get("estimated_eps")  # analyst consensus
            
            if not all([date, actual_eps is not None, estimate_eps is not None]):
                continue
                
            # Calculate surprise
            try:
                actual = float(actual_eps)
                estimate = float(estimate_eps)
                surprise = actual - estimate
                surprise_pct = (surprise / abs(estimate) * 100) if estimate != 0 else 0
            except:
                continue
                
            # Get price movement
            price_data = self.fetch_price_data(ticker, date)
            
            if price_data:
                event = {
                    "date": date,
                    "actual_eps": actual,
                    "estimate_eps": estimate,
                    "surprise": surprise,
                    "surprise_pct": surprise_pct,
                    "pre_price": price_data["pre_price"],
                    "drift_data": []
                }
                
                # Calculate drift at various intervals
                pre_price = price_data["pre_price"]
                
                for target_days in [1, 3, 5, 10, 20]:
                    day_price = next(
                        (p for p in price_data["post_prices"] if p["days_after"] == target_days),
                        None
                    )
                    
                    if day_price:
                        drift_pct = ((day_price["price"] - pre_price) / pre_price) * 100
                        event["drift_data"].append({
                            "days": target_days,
                            "drift_pct": drift_pct
                        })
                
                if event["drift_data"]:
                    analyzed_events.append(event)
        
        # Group by surprise magnitude
        positive_surprises = [e for e in analyzed_events if e["surprise_pct"] > 10]
        negative_surprises = [e for e in analyzed_events if e["surprise_pct"] < -10]
        
        result = {
            "ticker": ticker,
            "total_events_analyzed": len(analyzed_events),
            "positive_surprises": self.calculate_drift_stats(positive_surprises),
            "negative_surprises": self.calculate_drift_stats(negative_surprises)
        }
        
        return result
    
    def calculate_drift_stats(self, events: List[Dict]) -> Dict:
        """Calculate drift statistics for a group of events"""
        if not events:
            return {"count": 0}
            
        stats = {
            "count": len(events),
            "drift_by_day": {}
        }
        
        for days in [1, 3, 5, 10, 20]:
            drifts = []
            
            for event in events:
                day_drift = next(
                    (d["drift_pct"] for d in event["drift_data"] if d["days"] == days),
                    None
                )
                if day_drift is not None:
                    drifts.append(day_drift)
            
            if drifts:
                stats["drift_by_day"][f"{days}_day"] = {
                    "avg_drift": np.mean(drifts),
                    "median_drift": np.median(drifts),
                    "win_rate": sum(1 for d in drifts if d > 0) / len(drifts) * 100
                }
        
        return stats
    
    def run_pipeline(self):
        """Run the complete pipeline"""
        print("\nMassive Earnings Pipeline")
        print("=" * 60)
        
        universe = self.get_universe_tickers()
        total_events = 0
        
        for ticker in universe:
            # Fetch earnings data
            earnings = self.fetch_earnings(ticker)
            
            if earnings:
                # Analyze drift patterns
                analysis = self.analyze_earnings_drift(ticker, earnings)
                
                if analysis["total_events_analyzed"] > 0:
                    self.drift_patterns[ticker] = analysis
                    total_events += analysis["total_events_analyzed"]
                    
                    print(f"  Analyzed {analysis['total_events_analyzed']} events")
                    
                    # Show results
                    pos = analysis["positive_surprises"]
                    neg = analysis["negative_surprises"]
                    
                    if pos.get("count", 0) > 0:
                        drift_5d = pos["drift_by_day"].get("5_day", {}).get("avg_drift", 0)
                        print(f"  Positive surprise drift: {drift_5d:+.1f}% (5-day)")
                        
                    if neg.get("count", 0) > 0:
                        drift_5d = neg["drift_by_day"].get("5_day", {}).get("avg_drift", 0)
                        print(f"  Negative surprise drift: {drift_5d:+.1f}% (5-day)")
        
        print(f"\nTotal events analyzed: {total_events}")
        
        # Save results
        self.save_results()
        
        return total_events
    
    def save_results(self):
        """Save analysis results"""
        output = {
            "_metadata": {
                "source": "Massive API v2/reference/earnings",
                "total_events": sum(p["total_events_analyzed"] for p in self.drift_patterns.values()),
                "generated": datetime.now().isoformat(),
                "tickers_analyzed": len(self.drift_patterns)
            },
            "patterns": self.drift_patterns
        }
        
        with open("massive_drift_analysis.json", "w") as f:
            json.dump(output, f, indent=2)
            
        print(f"\nResults saved to massive_drift_analysis.json")

# Run it
if __name__ == "__main__":
    pipeline = MassiveEarningsPipeline()
    total = pipeline.run_pipeline()
    
    if total > 0:
        print(f"\n✅ SUCCESS! Analyzed {total} real earnings events from Massive!")
    else:
        print("\n❌ No data retrieved. Check API key and endpoint.")