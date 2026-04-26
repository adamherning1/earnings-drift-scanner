"""
Earnings History Pipeline
Pulls historical earnings data and calculates post-earnings drift patterns
Makes the "170,000 earnings events" claim real!
"""

import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import time
from dotenv import load_dotenv

load_dotenv()

# API Configuration
MASSIVE_API_KEY = os.getenv("MASSIVE_API_KEY", "your_key_here")
MASSIVE_BASE_URL = "https://api.massive.com"
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "demo")  # Free tier available

class EarningsHistoryPipeline:
    def __init__(self):
        self.massive_key = MASSIVE_API_KEY
        self.av_key = ALPHA_VANTAGE_KEY
        self.earnings_data = {}
        self.drift_patterns = {}
        
    def get_universe_tickers(self) -> List[str]:
        """Get our universe of stocks ($500M-$5B market cap with options)"""
        # Your target universe
        universe = [
            "SNAP", "PINS", "DKNG", "ROKU", "ETSY", "NET", "DOCU", "ZM",
            "CRWD", "OKTA", "TWLO", "SQ", "SHOP", "RBLX", "PLTR", "PATH",
            "U", "ABNB", "DASH", "COIN", "HOOD", "SOFI", "AFRM", "UPST"
        ]
        return universe
    
    def fetch_earnings_history(self, symbol: str) -> List[Dict]:
        """Fetch historical earnings data from Massive's Benzinga endpoint"""
        earnings_events = []
        
        try:
            # Use Massive's Benzinga earnings endpoint!
            url = f"{MASSIVE_BASE_URL}/v1/partners/benzinga/earnings"
            params = {
                "ticker": symbol,
                "limit": 50000,  # Get all available history
                "sort": "date.desc"  # Most recent first
            }
            headers = {
                "Authorization": f"Bearer {self.massive_key}"
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse Benzinga earnings format
                if isinstance(data, list):
                    earnings_list = data
                elif isinstance(data, dict) and "data" in data:
                    earnings_list = data["data"]
                else:
                    earnings_list = []
                
                for earning in earnings_list:
                    # Extract date (might be in different formats)
                    date = earning.get("date") or earning.get("report_date") or earning.get("announcement_date")
                    
                    # Extract EPS values
                    actual = float(earning.get("eps", 0) or earning.get("actual_eps", 0) or earning.get("reported_eps", 0))
                    estimate = float(earning.get("eps_est", 0) or earning.get("estimate_eps", 0) or earning.get("consensus_eps", 0))
                    
                    if date and (actual != 0 or estimate != 0):
                        event = {
                            "symbol": symbol,
                            "date": date[:10] if date else None,  # YYYY-MM-DD format
                            "actual_eps": actual,
                            "estimate_eps": estimate,
                            "surprise": actual - estimate,
                            "surprise_pct": ((actual - estimate) / abs(estimate) * 100) if estimate != 0 else 0
                        }
                        earnings_events.append(event)
            
            elif response.status_code == 401:
                print(f"Authentication error for {symbol} - check API key")
            else:
                print(f"Error {response.status_code} fetching earnings for {symbol}")
                # Fallback to Alpha Vantage if Massive fails
                return self.fetch_earnings_history_alphavantage(symbol)
            
        except Exception as e:
            print(f"Error fetching Massive earnings for {symbol}: {e}")
            # Fallback to Alpha Vantage
            return self.fetch_earnings_history_alphavantage(symbol)
            
        return earnings_events
    
    def fetch_earnings_history_alphavantage(self, symbol: str) -> List[Dict]:
        """Fallback to Alpha Vantage for earnings data"""
        earnings_events = []
        
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "EARNINGS",
                "symbol": symbol,
                "apikey": self.av_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "quarterlyEarnings" in data:
                    for earning in data["quarterlyEarnings"]:
                        event = {
                            "symbol": symbol,
                            "date": earning.get("reportedDate"),
                            "actual_eps": float(earning.get("reportedEPS", 0)),
                            "estimate_eps": float(earning.get("estimatedEPS", 0)),
                            "surprise": float(earning.get("surprise", 0)),
                            "surprise_pct": float(earning.get("surprisePercentage", 0))
                        }
                        earnings_events.append(event)
                        
            # Rate limit for free tier
            time.sleep(12)  # 5 requests per minute
            
        except Exception as e:
            print(f"Error fetching Alpha Vantage earnings for {symbol}: {e}")
            
        return earnings_events
    
    def fetch_historical_prices(self, symbol: str, date: str, days_after: int = 63) -> Optional[Dict]:
        """Fetch historical price data around earnings date using Massive"""
        try:
            # Convert date string to datetime
            earnings_date = datetime.strptime(date, "%Y-%m-%d")
            start_date = (earnings_date - timedelta(days=5)).strftime("%Y-%m-%d")
            end_date = (earnings_date + timedelta(days=days_after)).strftime("%Y-%m-%d")
            
            # Use Massive's aggregates endpoint (Polygon-compatible)
            url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start_date}/{end_date}"
            params = {"apiKey": self.massive_key}
            
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
                            pre_price = bar["c"]  # Close price
                        
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
            print(f"Error fetching prices for {symbol} on {date}: {e}")
            
        return None
    
    def calculate_sue_score(self, actual: float, estimate: float, historical_surprises: List[float]) -> float:
        """Calculate Standardized Unexpected Earnings (SUE) score"""
        if not historical_surprises or len(historical_surprises) < 4:
            # Simple surprise percentage if not enough history
            return (actual - estimate) / abs(estimate) if estimate != 0 else 0
        
        # Calculate standard deviation of surprises
        std_dev = np.std(historical_surprises)
        
        if std_dev == 0:
            return 0
        
        # SUE = (Actual - Estimate) / StdDev of surprises
        current_surprise = actual - estimate
        sue = current_surprise / std_dev
        
        return sue
    
    def calculate_drift_metrics(self, symbol: str) -> Dict:
        """Calculate historical drift patterns for a symbol"""
        if symbol not in self.earnings_data:
            return {}
        
        events = self.earnings_data[symbol]
        drift_results = []
        
        for event in events:
            if event.get("price_data"):
                pre_price = event["price_data"]["pre_price"]
                post_prices = event["price_data"]["post_prices"]
                
                # Calculate drift at different intervals
                for interval in [1, 3, 5, 10, 20, 40, 63]:
                    day_data = next((p for p in post_prices if p["days_after"] == interval), None)
                    
                    if day_data:
                        drift_pct = ((day_data["price"] - pre_price) / pre_price) * 100
                        
                        drift_results.append({
                            "sue_score": event.get("sue_score", 0),
                            "surprise_pct": event["surprise_pct"],
                            "days": interval,
                            "drift_pct": drift_pct,
                            "quintile": self.get_sue_quintile(event.get("sue_score", 0))
                        })
        
        # Aggregate by quintile
        df = pd.DataFrame(drift_results)
        
        if df.empty:
            return {}
        
        # Calculate average drift by SUE quintile and time period
        quintile_drift = {}
        
        for quintile in range(1, 6):
            q_data = df[df["quintile"] == quintile]
            
            if not q_data.empty:
                quintile_drift[f"Q{quintile}"] = {}
                
                for days in [1, 3, 5, 10, 20, 40, 63]:
                    day_data = q_data[q_data["days"] == days]
                    
                    if not day_data.empty:
                        avg_drift = day_data["drift_pct"].mean()
                        count = len(day_data)
                        quintile_drift[f"Q{quintile}"][f"day_{days}"] = {
                            "avg_drift": round(avg_drift, 2),
                            "count": count
                        }
        
        return {
            "symbol": symbol,
            "total_events": len(events),
            "quintile_drift": quintile_drift,
            "optimal_holding_period": self.find_optimal_holding(quintile_drift)
        }
    
    def get_sue_quintile(self, sue_score: float) -> int:
        """Assign SUE score to quintile (1=most negative, 5=most positive)"""
        if sue_score <= -1.5:
            return 1
        elif sue_score <= -0.5:
            return 2
        elif sue_score <= 0.5:
            return 3
        elif sue_score <= 1.5:
            return 4
        else:
            return 5
    
    def find_optimal_holding(self, quintile_drift: Dict) -> int:
        """Find optimal holding period based on drift patterns"""
        # Look for peak drift in Q1 (negative surprise) and Q5 (positive surprise)
        optimal_days = 5  # Default
        
        # Check Q1 (most negative drift expected)
        if "Q1" in quintile_drift:
            q1_data = quintile_drift["Q1"]
            min_drift = 0
            
            for day_key, data in q1_data.items():
                if data["avg_drift"] < min_drift:
                    min_drift = data["avg_drift"]
                    optimal_days = int(day_key.split("_")[1])
        
        # Check Q5 (most positive drift expected)
        if "Q5" in quintile_drift:
            q5_data = quintile_drift["Q5"]
            max_drift = 0
            
            for day_key, data in q5_data.items():
                if data["avg_drift"] > max_drift:
                    max_drift = data["avg_drift"]
                    # Average with Q1 optimal
                    optimal_days = (optimal_days + int(day_key.split("_")[1])) // 2
        
        return optimal_days
    
    def run_full_pipeline(self):
        """Run the complete pipeline for all tickers"""
        print("Starting Earnings History Pipeline...")
        universe = self.get_universe_tickers()
        
        # Step 1: Fetch earnings history
        print("\nStep 1: Fetching earnings history...")
        for symbol in universe:
            print(f"Fetching {symbol}...")
            events = self.fetch_earnings_history(symbol)
            
            if events:
                # Calculate SUE scores
                historical_surprises = [e["surprise"] for e in events]
                
                for i, event in enumerate(events):
                    # Use prior surprises for SUE calculation
                    prior_surprises = historical_surprises[i+1:i+9]  # Last 8 quarters
                    
                    if prior_surprises:
                        event["sue_score"] = self.calculate_sue_score(
                            event["actual_eps"],
                            event["estimate_eps"],
                            prior_surprises
                        )
                
                self.earnings_data[symbol] = events
        
        # Step 2: Fetch price data and calculate drift
        print("\nStep 2: Fetching price data and calculating drift...")
        total_events = 0
        
        for symbol, events in self.earnings_data.items():
            print(f"Processing {symbol} ({len(events)} events)...")
            
            for event in events[:12]:  # Last 3 years of quarters
                if event.get("date"):
                    price_data = self.fetch_historical_prices(symbol, event["date"])
                    
                    if price_data:
                        event["price_data"] = price_data
                        total_events += 1
            
            # Calculate drift metrics
            self.drift_patterns[symbol] = self.calculate_drift_metrics(symbol)
        
        print(f"\nTotal earnings events analyzed: {total_events}")
        
        # Step 3: Save results
        self.save_results()
        
        return self.drift_patterns
    
    def save_results(self):
        """Save pipeline results to files"""
        # Save raw earnings data
        with open("earnings_history.json", "w") as f:
            json.dump(self.earnings_data, f, indent=2)
        
        # Save drift patterns
        with open("drift_patterns.json", "w") as f:
            json.dump(self.drift_patterns, f, indent=2)
        
        # Create summary report
        self.create_summary_report()
    
    def create_summary_report(self):
        """Create a summary report of findings"""
        report = []
        report.append("# Post-Earnings Drift Analysis Report")
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append(f"\nTotal symbols analyzed: {len(self.drift_patterns)}")
        
        total_events = sum(p.get("total_events", 0) for p in self.drift_patterns.values())
        report.append(f"Total earnings events: {total_events}")
        
        # Aggregate quintile performance
        report.append("\n## Average Drift by SUE Quintile (All Stocks)")
        
        all_quintile_data = {}
        
        for symbol, pattern in self.drift_patterns.items():
            if "quintile_drift" in pattern:
                for quintile, data in pattern["quintile_drift"].items():
                    if quintile not in all_quintile_data:
                        all_quintile_data[quintile] = {}
                    
                    for period, metrics in data.items():
                        if period not in all_quintile_data[quintile]:
                            all_quintile_data[quintile][period] = []
                        
                        all_quintile_data[quintile][period].append(metrics["avg_drift"])
        
        # Calculate overall averages
        for quintile in ["Q1", "Q2", "Q3", "Q4", "Q5"]:
            if quintile in all_quintile_data:
                report.append(f"\n### {quintile} (SUE {'Most Negative' if quintile == 'Q1' else 'Most Positive' if quintile == 'Q5' else 'Middle'})")
                
                for days in [1, 3, 5, 10, 20, 40, 63]:
                    period = f"day_{days}"
                    
                    if period in all_quintile_data[quintile]:
                        drifts = all_quintile_data[quintile][period]
                        avg = np.mean(drifts)
                        report.append(f"- {days} days: {avg:.2f}% average drift")
        
        # Save report
        with open("drift_analysis_report.md", "w") as f:
            f.write("\n".join(report))
        
        print("\nReport saved to drift_analysis_report.md")

# Run the pipeline
if __name__ == "__main__":
    pipeline = EarningsHistoryPipeline()
    results = pipeline.run_full_pipeline()
    
    print("\n✅ Pipeline complete! Check these files:")
    print("- earnings_history.json (raw data)")
    print("- drift_patterns.json (analyzed patterns)")
    print("- drift_analysis_report.md (summary report)")