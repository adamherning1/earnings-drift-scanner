"""
Yahoo Finance based earnings scanner
Free alternative to FMP for development/testing
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np


class YahooEarningsScanner:
    """Scan for earnings using Yahoo Finance"""
    
    def __init__(self):
        self.cache = {}
        
    def get_upcoming_earnings(self, days_ahead: int = 7) -> List[Dict]:
        """Get stocks reporting earnings in next N days"""
        
        # For Yahoo Finance, we'll scan popular stocks
        # In production, we'd use a proper API
        earnings_stocks = []
        
        # Popular stocks to check (in production, scan broader universe)
        universe = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 
            'JPM', 'V', 'JNJ', 'WMT', 'PG', 'UNH', 'HD', 'MA', 'DIS',
            'NFLX', 'ADBE', 'CRM', 'PYPL', 'INTC', 'CSCO', 'PEP', 'COST',
            'AMD', 'QCOM', 'TXN', 'AVGO', 'ORCL', 'IBM', 'GS', 'MS'
        ]
        
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)
        
        for symbol in universe:
            try:
                ticker = yf.Ticker(symbol)
                
                # Try to get earnings dates
                earnings_dates = ticker.get_earnings_dates()
                if earnings_dates is not None and not earnings_dates.empty:
                    # Get next earnings date
                    future_earnings = earnings_dates[earnings_dates.index.date >= today]
                    if not future_earnings.empty:
                        next_earnings = future_earnings.index[0].date()
                        
                        if today <= next_earnings <= end_date:
                            info = ticker.info
                            earnings_stocks.append({
                                'symbol': symbol,
                                'earnings_date': next_earnings.isoformat(),
                                'company_name': info.get('longName', symbol),
                                'market_cap': info.get('marketCap', 0),
                                'eps_estimate': future_earnings.iloc[0].get('EPS Estimate', None)
                            })
            except Exception as e:
                continue
                
        return earnings_stocks
    
    def get_recent_earnings(self, days_back: int = 5) -> List[Dict]:
        """Get stocks that recently reported earnings"""
        
        recent_earnings = []
        universe = self._get_mid_cap_universe()
        
        today = datetime.now().date()
        start_date = today - timedelta(days=days_back)
        
        for symbol in universe[:50]:  # Limit for performance
            try:
                ticker = yf.Ticker(symbol)
                earnings_dates = ticker.get_earnings_dates()
                
                if earnings_dates is not None and not earnings_dates.empty:
                    # Get recent past earnings
                    past_earnings = earnings_dates[
                        (earnings_dates.index.date >= start_date) & 
                        (earnings_dates.index.date < today)
                    ]
                    
                    if not past_earnings.empty:
                        latest = past_earnings.iloc[0]
                        if pd.notna(latest.get('Reported EPS')) and pd.notna(latest.get('EPS Estimate')):
                            
                            # Calculate surprise
                            actual = latest['Reported EPS']
                            estimate = latest['EPS Estimate']
                            surprise_pct = ((actual - estimate) / abs(estimate) * 100) if estimate != 0 else 0
                            
                            info = ticker.info
                            market_cap = info.get('marketCap', 0)
                            
                            # Filter for our target market cap range
                            if 500_000_000 <= market_cap <= 5_000_000_000:
                                recent_earnings.append({
                                    'symbol': symbol,
                                    'earnings_date': past_earnings.index[0].date().isoformat(),
                                    'company_name': info.get('longName', symbol),
                                    'market_cap': market_cap,
                                    'eps_actual': actual,
                                    'eps_estimate': estimate,
                                    'surprise_percent': round(surprise_pct, 2),
                                    'current_price': info.get('regularMarketPrice', 0),
                                    'volume': info.get('averageVolume', 0)
                                })
                                
            except Exception as e:
                continue
                
        # Sort by surprise magnitude
        recent_earnings.sort(key=lambda x: abs(x['surprise_percent']), reverse=True)
        
        return recent_earnings
    
    def calculate_sue(self, symbol: str) -> Optional[float]:
        """Calculate Standardized Unexpected Earnings (SUE) score"""
        
        try:
            ticker = yf.Ticker(symbol)
            earnings_dates = ticker.get_earnings_dates()
            
            if earnings_dates is None or earnings_dates.empty:
                return None
                
            # Get last 8 quarters of earnings
            past_earnings = earnings_dates[earnings_dates['Reported EPS'].notna()].head(8)
            
            if len(past_earnings) < 4:
                return None
                
            # Calculate surprises
            surprises = []
            for idx, row in past_earnings.iterrows():
                if pd.notna(row['EPS Estimate']):
                    surprise = row['Reported EPS'] - row['EPS Estimate']
                    surprises.append(surprise)
                    
            if len(surprises) < 4:
                return None
                
            # SUE = (Latest Surprise - Mean) / Std Dev
            latest_surprise = surprises[0]
            mean_surprise = np.mean(surprises[1:])  # Exclude latest
            std_surprise = np.std(surprises[1:])
            
            if std_surprise > 0:
                sue = (latest_surprise - mean_surprise) / std_surprise
                return round(sue, 2)
            else:
                return 0.0
                
        except Exception as e:
            return None
    
    def _get_mid_cap_universe(self) -> List[str]:
        """Get a universe of mid-cap stocks"""
        
        # In production, we'd have a proper universe
        # For now, use a curated list of mid-caps
        return [
            'DKNG', 'SNAP', 'PINS', 'RBLX', 'PATH', 'DOCU', 'ZM', 'ROKU',
            'SQ', 'TWLO', 'NET', 'DDOG', 'SNOW', 'U', 'PLTR', 'COIN',
            'HOOD', 'SOFI', 'AFRM', 'UPST', 'BILL', 'HUBS', 'TEAM', 'MDB',
            'OKTA', 'CRWD', 'ZS', 'PANW', 'FTNT', 'S', 'ESTC', 'SUMO',
            'FSLY', 'FROG', 'APPS', 'PUBM', 'MGNI', 'TTD', 'ROKU', 'SPOT',
            'W', 'ETSY', 'MELI', 'SHOP', 'CHWY', 'CVNA', 'OSTK', 'FTCH'
        ]


# Example usage
if __name__ == "__main__":
    scanner = YahooEarningsScanner()
    
    print("Scanning for recent earnings surprises...\n")
    recent = scanner.get_recent_earnings(days_back=10)
    
    if recent:
        print(f"Found {len(recent)} stocks with recent earnings:\n")
        for stock in recent[:5]:
            print(f"{stock['symbol']} ({stock['company_name']})")
            print(f"  Market Cap: ${stock['market_cap']/1e9:.1f}B")
            print(f"  Surprise: {stock['surprise_percent']}%")
            print(f"  Price: ${stock['current_price']}")
            print(f"  Volume: {stock['volume']:,}\n")
    else:
        print("No recent earnings found in target range")
        
    print("\nChecking upcoming earnings...")
    upcoming = scanner.get_upcoming_earnings(days_ahead=30)
    if upcoming:
        print(f"\nFound {len(upcoming)} upcoming earnings:")
        for stock in upcoming[:5]:
            print(f"  {stock['symbol']}: {stock['earnings_date']}")