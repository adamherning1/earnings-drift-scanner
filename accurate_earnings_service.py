"""
Accurate Earnings Service using professional APIs
"""
import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
import time

class AccurateEarningsService:
    def __init__(self):
        # API Keys (set these in environment variables)
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_KEY", "demo")  # Free
        self.fmp_key = os.getenv("FMP_API_KEY")  # $14/month
        self.iex_token = os.getenv("IEX_TOKEN")  # $9/month
        self.twelve_data_key = os.getenv("TWELVE_DATA_KEY")  # Free tier
        
        self.cache = {}
        
    def get_earnings_alpha_vantage(self, symbol: str) -> Dict:
        """Get earnings from Alpha Vantage (FREE)"""
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "EARNINGS",
            "symbol": symbol,
            "apikey": self.alpha_vantage_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "quarterlyEarnings" in data:
                    earnings = data["quarterlyEarnings"]
                    
                    result = {
                        "symbol": symbol,
                        "total_events": len(earnings),
                        "earnings": []
                    }
                    
                    for earning in earnings[:20]:  # Last 20 quarters
                        result["earnings"].append({
                            "date": earning.get("fiscalDateEnding"),
                            "reportedDate": earning.get("reportedDate"),
                            "actual": float(earning.get("reportedEPS", 0)),
                            "estimate": float(earning.get("estimatedEPS", 0)),
                            "surprise": float(earning.get("surprise", 0)),
                            "surprise_pct": float(earning.get("surprisePercentage", "0").replace("%", ""))
                        })
                    
                    return result
                    
        except Exception as e:
            print(f"Alpha Vantage error for {symbol}: {e}")
            
        return None
        
    def get_earnings_fmp(self, symbol: str) -> Dict:
        """Get earnings from Financial Modeling Prep (Most Accurate)"""
        if not self.fmp_key:
            return None
            
        url = f"https://financialmodelingprep.com/api/v3/historical/earning_calendar/{symbol}"
        params = {"apikey": self.fmp_key}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                earnings = response.json()
                
                if earnings:
                    result = {
                        "symbol": symbol,
                        "total_events": len(earnings),
                        "earnings": []
                    }
                    
                    for earning in earnings[:20]:
                        actual = earning.get("eps", 0)
                        estimate = earning.get("epsEstimated", 0)
                        
                        if actual and estimate:
                            surprise_pct = ((actual - estimate) / abs(estimate) * 100) if estimate != 0 else 0
                        else:
                            surprise_pct = 0
                            
                        result["earnings"].append({
                            "date": earning.get("date"),
                            "actual": float(actual) if actual else 0,
                            "estimate": float(estimate) if estimate else 0,
                            "revenue": earning.get("revenue", 0),
                            "revenueEstimated": earning.get("revenueEstimated", 0),
                            "surprise_pct": round(surprise_pct, 1)
                        })
                    
                    return result
                    
        except Exception as e:
            print(f"FMP error for {symbol}: {e}")
            
        return None
        
    def get_earnings_iex(self, symbol: str) -> Dict:
        """Get earnings from IEX Cloud"""
        if not self.iex_token:
            return None
            
        url = f"https://cloud.iexapis.com/stable/stock/{symbol}/earnings/last/20"
        params = {"token": self.iex_token}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("earnings"):
                    earnings = data["earnings"]
                    
                    result = {
                        "symbol": symbol,
                        "total_events": len(earnings),
                        "earnings": []
                    }
                    
                    for earning in earnings:
                        actual = earning.get("actualEPS", 0)
                        estimate = earning.get("consensusEPS", 0)
                        
                        if actual and estimate:
                            surprise_pct = ((actual - estimate) / abs(estimate) * 100) if estimate != 0 else 0
                        else:
                            surprise_pct = earning.get("EPSSurprisePercent", 0) * 100
                            
                        result["earnings"].append({
                            "date": earning.get("EPSReportDate"),
                            "actual": float(actual) if actual else 0,
                            "estimate": float(estimate) if estimate else 0,
                            "surprise_pct": round(surprise_pct, 1),
                            "announceTime": earning.get("announceTime")
                        })
                    
                    return result
                    
        except Exception as e:
            print(f"IEX error for {symbol}: {e}")
            
        return None
        
    def get_accurate_earnings(self, symbol: str) -> Dict:
        """Get earnings from the most accurate source available"""
        
        # Check cache
        if symbol in self.cache:
            cached_data, cached_time = self.cache[symbol]
            if datetime.now() - cached_time < timedelta(hours=1):
                return cached_data
        
        # Try sources in order of accuracy
        result = None
        
        # 1. Try FMP (most accurate, paid)
        if self.fmp_key:
            print(f"Fetching from FMP for {symbol}...")
            result = self.get_earnings_fmp(symbol)
            if result:
                result["source"] = "Financial Modeling Prep"
        
        # 2. Try IEX (accurate, paid)
        if not result and self.iex_token:
            print(f"Fetching from IEX for {symbol}...")
            result = self.get_earnings_iex(symbol)
            if result:
                result["source"] = "IEX Cloud"
        
        # 3. Try Alpha Vantage (free)
        if not result:
            print(f"Fetching from Alpha Vantage for {symbol}...")
            result = self.get_earnings_alpha_vantage(symbol)
            if result:
                result["source"] = "Alpha Vantage"
            time.sleep(12)  # Rate limit for free tier
        
        if result:
            # Cache the result
            self.cache[symbol] = (result, datetime.now())
            
            # Calculate drift statistics
            positive_surprises = []
            negative_surprises = []
            
            for earning in result["earnings"]:
                surprise = earning.get("surprise_pct", 0)
                if surprise > 10:
                    positive_surprises.append(surprise)
                elif surprise < -10:
                    negative_surprises.append(surprise)
            
            result["positive_surprises"] = {
                "count": len(positive_surprises),
                "avg_surprise": round(sum(positive_surprises) / len(positive_surprises), 1) if positive_surprises else 0
            }
            
            result["negative_surprises"] = {
                "count": len(negative_surprises),
                "avg_surprise": round(sum(negative_surprises) / len(negative_surprises), 1) if negative_surprises else 0
            }
            
            return result
        
        # No data available
        return {
            "symbol": symbol,
            "error": "No earnings data available",
            "source": "None"
        }

# Example usage
if __name__ == "__main__":
    service = AccurateEarningsService()
    
    # Test with a symbol
    result = service.get_accurate_earnings("AAPL")
    
    print(f"\nEarnings data for {result['symbol']}:")
    print(f"Source: {result.get('source', 'Unknown')}")
    print(f"Total events: {result.get('total_events', 0)}")
    
    if result.get('earnings'):
        print(f"\nRecent earnings:")
        for e in result['earnings'][:3]:
            print(f"  {e['date']}: ${e['actual']} vs ${e['estimate']} ({e['surprise_pct']:+.1f}% surprise)")