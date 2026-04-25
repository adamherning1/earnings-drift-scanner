"""
Earnings Data Ingestion Service
Fetches and processes earnings data from FMP API
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
import json
import time
from dataclasses import dataclass

@dataclass
class EarningsEvent:
    """Standardized earnings event"""
    symbol: str
    report_date: str
    actual_eps: float
    estimated_eps: float
    revenue_actual: Optional[float] = None
    revenue_estimated: Optional[float] = None
    period: Optional[str] = None
    
class EarningsIngestionService:
    """
    Fetches earnings data and calculates surprises.
    Runs continuously to catch new earnings as they're reported.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://financialmodelingprep.com/api/v3"
        self.cache_file = "earnings_cache.json"
        self.processed_file = "processed_earnings.json"
        self.load_processed()
        
    def load_processed(self):
        """Load list of already processed earnings to avoid duplicates."""
        if os.path.exists(self.processed_file):
            with open(self.processed_file, 'r') as f:
                self.processed = set(json.load(f))
        else:
            self.processed = set()
    
    def save_processed(self):
        """Save processed earnings list."""
        with open(self.processed_file, 'w') as f:
            json.dump(list(self.processed), f)
    
    def fetch_earnings_calendar(self, days_back: int = 5, days_forward: int = 1) -> List[Dict]:
        """
        Fetch earnings calendar for recent and upcoming earnings.
        
        Args:
            days_back: Number of days to look back
            days_forward: Number of days to look forward
        """
        end_date = datetime.now() + timedelta(days=days_forward)
        start_date = datetime.now() - timedelta(days=days_back)
        
        url = f"{self.base_url}/earning_calendar"
        params = {
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d'),
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            print(f"Fetched {len(data)} earnings events")
            return data
        except Exception as e:
            print(f"Error fetching earnings calendar: {e}")
            return []
    
    def get_historical_surprises(self, symbol: str, quarters: int = 8) -> List[float]:
        """
        Get historical earnings surprises for SUE calculation.
        """
        url = f"{self.base_url}/historical/earning_calendar/{symbol}"
        params = {
            'limit': quarters,
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            surprises = []
            for earnings in data:
                if earnings.get('eps') and earnings.get('epsEstimated'):
                    surprise = earnings['eps'] - earnings['epsEstimated']
                    surprises.append(surprise)
            
            return surprises
        except:
            return []
    
    def process_earnings_event(self, event: Dict) -> Optional[EarningsEvent]:
        """
        Process raw earnings event into standardized format.
        """
        # Skip if no actual EPS reported yet
        if not event.get('eps') or not event.get('epsEstimated'):
            return None
            
        # Skip if we already processed this
        event_id = f"{event.get('symbol')}_{event.get('date')}"
        if event_id in self.processed:
            return None
        
        try:
            earnings = EarningsEvent(
                symbol=event['symbol'],
                report_date=event['date'],
                actual_eps=float(event['eps']),
                estimated_eps=float(event['epsEstimated']),
                revenue_actual=event.get('revenue'),
                revenue_estimated=event.get('revenueEstimated'),
                period=event.get('period')
            )
            
            # Mark as processed
            self.processed.add(event_id)
            self.save_processed()
            
            return earnings
        except Exception as e:
            print(f"Error processing event for {event.get('symbol')}: {e}")
            return None
    
    def scan_for_new_earnings(self) -> List[Dict]:
        """
        Main function to scan for new earnings with complete data.
        Returns list of earnings ready for SUE analysis.
        """
        print(f"\nScanning for earnings at {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Get recent earnings
        calendar_events = self.fetch_earnings_calendar(days_back=5)
        
        new_earnings = []
        
        for event in calendar_events:
            # Process event
            earnings = self.process_earnings_event(event)
            if not earnings:
                continue
                
            # Get historical surprises for SUE calculation
            historical = self.get_historical_surprises(earnings.symbol)
            
            # Create analysis-ready data
            analysis_data = {
                'symbol': earnings.symbol,
                'report_date': earnings.report_date,
                'actual_eps': earnings.actual_eps,
                'estimated_eps': earnings.estimated_eps,
                'historical_surprises': historical,
                'revenue_actual': earnings.revenue_actual,
                'revenue_estimated': earnings.revenue_estimated,
                'period': earnings.period
            }
            
            new_earnings.append(analysis_data)
            
            print(f"New earnings: {earnings.symbol} - "
                  f"EPS: ${earnings.actual_eps:.2f} vs ${earnings.estimated_eps:.2f} "
                  f"({(earnings.actual_eps/earnings.estimated_eps - 1)*100:+.1f}%)")
        
        print(f"Found {len(new_earnings)} new earnings events to analyze")
        return new_earnings
    
    def continuous_scan(self, interval_minutes: int = 15):
        """
        Run continuous scanning during market hours.
        """
        print(f"Starting continuous earnings scan (every {interval_minutes} minutes)")
        
        while True:
            try:
                # Check if market hours (roughly)
                now = datetime.now()
                if now.weekday() < 5:  # Monday-Friday
                    hour = now.hour
                    
                    # Scan more frequently around typical earnings release times
                    # Most earnings come out before market open or after close
                    if hour in [6, 7, 8, 15, 16, 17]:  # Eastern time
                        interval_minutes = 5  # Scan every 5 min during peak times
                    else:
                        interval_minutes = 15  # Normal interval
                    
                    # Scan for new earnings
                    new_earnings = self.scan_for_new_earnings()
                    
                    # Cache results
                    if new_earnings:
                        with open(self.cache_file, 'w') as f:
                            json.dump({
                                'timestamp': now.isoformat(),
                                'earnings': new_earnings
                            }, f, indent=2)
                
                # Sleep until next scan
                print(f"Next scan in {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\nStopping earnings scanner")
                break
            except Exception as e:
                print(f"Error in continuous scan: {e}")
                time.sleep(60)  # Wait 1 minute on error


# Test the service
if __name__ == "__main__":
    # Note: Replace with actual API key
    API_KEY = os.getenv('FMP_API_KEY', 'your_api_key')
    
    service = EarningsIngestionService(API_KEY)
    
    # Do one scan
    new_earnings = service.scan_for_new_earnings()
    
    # Show what we found
    if new_earnings:
        print("\nReady for SUE analysis:")
        for e in new_earnings[:5]:  # Show first 5
            surprise_pct = (e['actual_eps'] / e['estimated_eps'] - 1) * 100
            print(f"{e['symbol']}: {surprise_pct:+.1f}% surprise on {e['report_date']}")
    
    # Uncomment to run continuous scanning
    # service.continuous_scan()