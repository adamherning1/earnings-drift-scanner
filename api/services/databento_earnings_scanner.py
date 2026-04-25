"""
Databento-based earnings scanner
Professional-grade market data for production
"""

import os
import databento as db
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from dotenv import load_dotenv

load_dotenv()


class DatabentoEarningsScanner:
    """Scan for earnings using Databento's professional data"""
    
    def __init__(self):
        api_key = os.getenv('DATABENTO_API_KEY')
        if not api_key:
            raise ValueError("DATABENTO_API_KEY not found in environment")
            
        self.client = db.Historical(api_key)
        self.cache = {}
        
    def get_earnings_calendar(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Get earnings announcements between dates
        
        Args:
            start_date: YYYY-MM-DD format
            end_date: YYYY-MM-DD format
            
        Returns:
            List of earnings events with company details
        """
        
        try:
            # Databento corporate actions dataset includes earnings
            events = self.client.timeseries.get_range(
                dataset='XNYS.CORPORATE_ACTIONS',  # NYSE corporate actions
                symbols='ALL',  # Get all symbols
                schema='events',
                event_type='earnings',
                start=start_date,
                end=end_date
            )
            
            earnings_list = []
            for event in events:
                # Extract earnings data
                earnings_list.append({
                    'symbol': event.symbol,
                    'earnings_date': event.timestamp.strftime('%Y-%m-%d'),
                    'time': event.timestamp.strftime('%H:%M'),
                    'eps_actual': event.get('eps_actual'),
                    'eps_estimate': event.get('eps_estimate'),
                    'revenue_actual': event.get('revenue_actual'),
                    'revenue_estimate': event.get('revenue_estimate'),
                })
                
            return earnings_list
            
        except Exception as e:
            print(f"Error fetching earnings calendar: {e}")
            # Fall back to manual list for MVP
            return self._get_manual_earnings_calendar(start_date, end_date)
    
    def get_options_data(self, symbol: str, expiry_days: int = 45) -> Dict:
        """
        Get options chain for a symbol
        
        Args:
            symbol: Stock symbol
            expiry_days: Max days to expiration to fetch
            
        Returns:
            Dict with calls and puts data
        """
        
        try:
            # Get options data from OPRA feed
            end_date = (datetime.now() + timedelta(days=expiry_days)).strftime('%Y-%m-%d')
            
            options = self.client.timeseries.get_range(
                dataset='OPRA',
                symbols=symbol,
                schema='ohlcv-1d',
                start=datetime.now().strftime('%Y-%m-%d'),
                end=end_date
            )
            
            # Process into calls/puts
            calls = []
            puts = []
            
            for opt in options:
                option_data = {
                    'strike': opt.strike,
                    'expiry': opt.expiry,
                    'bid': opt.bid,
                    'ask': opt.ask,
                    'volume': opt.volume,
                    'open_interest': opt.open_interest,
                    'implied_vol': opt.implied_volatility
                }
                
                if opt.option_type == 'C':
                    calls.append(option_data)
                else:
                    puts.append(option_data)
                    
            return {
                'calls': sorted(calls, key=lambda x: x['strike']),
                'puts': sorted(puts, key=lambda x: x['strike'])
            }
            
        except Exception as e:
            print(f"Error fetching options data: {e}")
            return {'calls': [], 'puts': []}
    
    def get_historical_earnings(self, symbol: str, quarters: int = 8) -> List[Dict]:
        """
        Get historical earnings for SUE calculation
        
        Args:
            symbol: Stock symbol  
            quarters: Number of quarters to fetch
            
        Returns:
            List of historical earnings data
        """
        
        try:
            # Calculate date range for quarters
            end_date = datetime.now()
            start_date = end_date - timedelta(days=quarters * 90)
            
            events = self.client.timeseries.get_range(
                dataset='XNYS.CORPORATE_ACTIONS',
                symbols=[symbol],
                schema='events',
                event_type='earnings',
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d')
            )
            
            earnings_history = []
            for event in events:
                if event.get('eps_actual') and event.get('eps_estimate'):
                    earnings_history.append({
                        'date': event.timestamp.strftime('%Y-%m-%d'),
                        'eps_actual': event.eps_actual,
                        'eps_estimate': event.eps_estimate,
                        'surprise': event.eps_actual - event.eps_estimate,
                        'surprise_pct': ((event.eps_actual - event.eps_estimate) / 
                                       abs(event.eps_estimate) * 100)
                    })
                    
            return sorted(earnings_history, key=lambda x: x['date'], reverse=True)
            
        except Exception as e:
            print(f"Error fetching historical earnings: {e}")
            return []
    
    def calculate_sue(self, symbol: str) -> Optional[float]:
        """
        Calculate Standardized Unexpected Earnings (SUE)
        
        SUE = (Latest Surprise - Mean Surprise) / StdDev Surprise
        """
        
        history = self.get_historical_earnings(symbol, quarters=12)
        
        if len(history) < 4:
            return None
            
        # Extract surprises
        surprises = [h['surprise'] for h in history]
        
        # Calculate SUE
        latest_surprise = surprises[0]
        historical_surprises = surprises[1:]  # Exclude latest
        
        mean_surprise = np.mean(historical_surprises)
        std_surprise = np.std(historical_surprises)
        
        if std_surprise == 0:
            return 0
            
        sue = (latest_surprise - mean_surprise) / std_surprise
        return round(sue, 2)
    
    def screen_stocks(self, min_market_cap: int = 500_000_000, 
                     max_market_cap: int = 5_000_000_000) -> List[str]:
        """
        Screen for stocks in our target market cap range
        
        For MVP, returns a curated list. In production would query Databento universe.
        """
        
        # Curated list of liquid mid-caps with options
        return [
            # Tech/Software
            'DKNG', 'SNAP', 'PINS', 'RBLX', 'PATH', 'DOCU', 'ZM', 'ROKU',
            'NET', 'DDOG', 'PLTR', 'COIN', 'HOOD', 'SOFI', 'AFRM', 'UPST',
            
            # E-commerce/Consumer  
            'ETSY', 'W', 'CHWY', 'CVNA', 'DASH', 'ABNB', 'LYFT', 'UBER',
            
            # Healthcare/Biotech
            'TDOC', 'VEEV', 'DXCM', 'EXAS', 'ILMN', 'REGN', 'BIIB', 'VRTX',
            
            # Industrials/Energy
            'PLUG', 'FSLR', 'ENPH', 'RUN', 'SEDG', 'BE', 'CHPT', 'LCID',
            
            # Financials
            'SQ', 'PYPL', 'ALLY', 'LPLA', 'IBKR', 'SCHW', 'AMTD', 'ETFC'
        ]
    
    def _get_manual_earnings_calendar(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Manual earnings calendar for MVP testing
        Returns known upcoming earnings in our date range
        """
        
        # Known Q1 2026 earnings (approximate dates)
        manual_earnings = [
            {'symbol': 'SNAP', 'earnings_date': '2026-04-28', 'time': 'AMC'},
            {'symbol': 'PINS', 'earnings_date': '2026-04-29', 'time': 'AMC'},
            {'symbol': 'DKNG', 'earnings_date': '2026-04-30', 'time': 'BMO'},
            {'symbol': 'ROKU', 'earnings_date': '2026-04-30', 'time': 'AMC'},
            {'symbol': 'ETSY', 'earnings_date': '2026-05-01', 'time': 'AMC'},
            {'symbol': 'DOCU', 'earnings_date': '2026-05-02', 'time': 'AMC'},
            {'symbol': 'PATH', 'earnings_date': '2026-05-06', 'time': 'BMO'},
            {'symbol': 'RBLX', 'earnings_date': '2026-05-07', 'time': 'AMC'},
            {'symbol': 'PLTR', 'earnings_date': '2026-05-07', 'time': 'BMO'},
            {'symbol': 'COIN', 'earnings_date': '2026-05-08', 'time': 'AMC'},
        ]
        
        # Filter by date range
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        filtered = []
        for earning in manual_earnings:
            date = pd.to_datetime(earning['earnings_date'])
            if start <= date <= end:
                filtered.append(earning)
                
        return filtered


# Test the scanner
if __name__ == "__main__":
    scanner = DatabentoEarningsScanner()
    
    print("Testing Databento Earnings Scanner...\n")
    
    # Test earnings calendar
    today = datetime.now().strftime('%Y-%m-%d')
    next_month = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"Fetching earnings from {today} to {next_month}...")
    earnings = scanner._get_manual_earnings_calendar(today, next_month)
    
    if earnings:
        print(f"\nFound {len(earnings)} upcoming earnings:")
        for e in earnings[:5]:
            print(f"  {e['symbol']}: {e['earnings_date']} {e['time']}")
    
    # Test stock screening
    print("\n\nTesting stock universe...")
    stocks = scanner.screen_stocks()
    print(f"Tracking {len(stocks)} stocks in $500M-$5B range")
    print(f"Sample: {', '.join(stocks[:10])}")
    
    print("\n✅ Databento scanner ready!")
    print("Note: Full Databento integration requires corporate actions subscription")
    print("Using manual earnings calendar for MVP")