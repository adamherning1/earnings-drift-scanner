"""
Hybrid earnings scanner combining multiple data sources
Uses manual calendar + Yahoo Finance for MVP, ready for Databento later
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np


class HybridEarningsScanner:
    """Production-ready scanner using best available data sources"""
    
    def __init__(self):
        self.manual_earnings = self._load_manual_calendar()
        
    def _load_manual_calendar(self) -> List[Dict]:
        """Known Q2 2026 earnings for our tracked universe"""
        
        return [
            # Late April
            {'symbol': 'SNAP', 'date': '2026-04-28', 'time': 'AMC', 'market_cap': 16.5e9},
            {'symbol': 'PINS', 'date': '2026-04-29', 'time': 'AMC', 'market_cap': 18.2e9},
            {'symbol': 'ENPH', 'date': '2026-04-29', 'time': 'AMC', 'market_cap': 22.1e9},
            {'symbol': 'SPOT', 'date': '2026-04-30', 'time': 'BMO', 'market_cap': 31.5e9},
            {'symbol': 'DKNG', 'date': '2026-04-30', 'time': 'BMO', 'market_cap': 19.8e9},
            {'symbol': 'ROKU', 'date': '2026-04-30', 'time': 'AMC', 'market_cap': 8.7e9},
            
            # Early May  
            {'symbol': 'ETSY', 'date': '2026-05-01', 'time': 'AMC', 'market_cap': 7.9e9},
            {'symbol': 'LYFT', 'date': '2026-05-01', 'time': 'AMC', 'market_cap': 4.2e9},
            {'symbol': 'SQ', 'date': '2026-05-02', 'time': 'AMC', 'market_cap': 38.5e9},
            {'symbol': 'DOCU', 'date': '2026-05-02', 'time': 'AMC', 'market_cap': 11.3e9},
            {'symbol': 'NET', 'date': '2026-05-02', 'time': 'AMC', 'market_cap': 25.7e9},
            {'symbol': 'TWLO', 'date': '2026-05-06', 'time': 'AMC', 'market_cap': 8.9e9},
            {'symbol': 'PATH', 'date': '2026-05-06', 'time': 'BMO', 'market_cap': 1.8e9},
            {'symbol': 'RBLX', 'date': '2026-05-07', 'time': 'AMC', 'market_cap': 22.4e9},
            {'symbol': 'PLTR', 'date': '2026-05-07', 'time': 'BMO', 'market_cap': 45.2e9},
            {'symbol': 'DASH', 'date': '2026-05-07', 'time': 'AMC', 'market_cap': 18.9e9},
            {'symbol': 'COIN', 'date': '2026-05-08', 'time': 'AMC', 'market_cap': 42.1e9},
            {'symbol': 'UPST', 'date': '2026-05-08', 'time': 'AMC', 'market_cap': 2.7e9},
            {'symbol': 'HOOD', 'date': '2026-05-08', 'time': 'AMC', 'market_cap': 11.2e9},
            {'symbol': 'SOFI', 'date': '2026-05-09', 'time': 'BMO', 'market_cap': 7.8e9},
        ]
    
    def get_upcoming_earnings(self, days_ahead: int = 7) -> List[Dict]:
        """Get earnings in next N days combining manual + Yahoo data"""
        
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)
        
        # Start with manual calendar
        upcoming = []
        for earning in self.manual_earnings:
            earning_date = pd.to_datetime(earning['date']).date()
            if today <= earning_date <= end_date:
                # Enrich with Yahoo data
                enriched = self._enrich_with_yahoo(earning.copy())
                upcoming.append(enriched)
        
        # Sort by date
        upcoming.sort(key=lambda x: x['date'])
        
        return upcoming
    
    def get_recent_earnings(self, days_back: int = 5) -> List[Dict]:
        """Get recent earnings with surprises calculated"""
        
        today = datetime.now().date()
        start_date = today - timedelta(days=days_back)
        
        recent = []
        
        # Check our tracked symbols for recent earnings
        for earning in self.manual_earnings:
            symbol = earning['symbol']
            
            try:
                ticker = yf.Ticker(symbol)
                earnings_dates = ticker.get_earnings_dates()
                
                if earnings_dates is not None and not earnings_dates.empty:
                    # Look for earnings in our date range
                    mask = (earnings_dates.index.date >= start_date) & (earnings_dates.index.date < today)
                    recent_earnings = earnings_dates[mask]
                    
                    if not recent_earnings.empty and not recent_earnings.iloc[0].isna().all():
                        latest = recent_earnings.iloc[0]
                        
                        if pd.notna(latest.get('Reported EPS')) and pd.notna(latest.get('EPS Estimate')):
                            eps_actual = float(latest['Reported EPS'])
                            eps_estimate = float(latest['EPS Estimate'])
                            surprise_pct = ((eps_actual - eps_estimate) / abs(eps_estimate) * 100) if eps_estimate != 0 else 0
                            
                            info = ticker.info
                            recent.append({
                                'symbol': symbol,
                                'date': recent_earnings.index[0].date().isoformat(),
                                'company_name': info.get('longName', symbol),
                                'market_cap': info.get('marketCap', 0),
                                'eps_actual': eps_actual,
                                'eps_estimate': eps_estimate,
                                'surprise_percent': round(surprise_pct, 2),
                                'current_price': info.get('regularMarketPrice', 0),
                                'volume': info.get('averageVolume', 0),
                                'options_volume': info.get('averageOptionsVolume', 0)
                            })
            except Exception as e:
                continue
        
        # Sort by surprise magnitude
        recent.sort(key=lambda x: abs(x.get('surprise_percent', 0)), reverse=True)
        
        return recent
    
    def calculate_sue(self, symbol: str) -> Dict:
        """Calculate SUE score with available data"""
        
        try:
            ticker = yf.Ticker(symbol)
            earnings_dates = ticker.get_earnings_dates()
            
            if earnings_dates is None or earnings_dates.empty:
                return {'sue': None, 'confidence': 'low'}
            
            # Get last 8 quarters with data
            past_earnings = earnings_dates[earnings_dates['Reported EPS'].notna()].head(8)
            
            if len(past_earnings) < 4:
                return {'sue': None, 'confidence': 'low'}
            
            # Calculate surprises
            surprises = []
            for idx, row in past_earnings.iterrows():
                if pd.notna(row['EPS Estimate']):
                    surprise = float(row['Reported EPS']) - float(row['EPS Estimate'])
                    surprises.append(surprise)
            
            if len(surprises) < 4:
                return {'sue': None, 'confidence': 'low'}
            
            # SUE calculation
            latest_surprise = surprises[0]
            historical = surprises[1:]
            
            mean_surprise = np.mean(historical)
            std_surprise = np.std(historical)
            
            if std_surprise > 0:
                sue = (latest_surprise - mean_surprise) / std_surprise
                confidence = 'high' if len(surprises) >= 6 else 'medium'
                return {
                    'sue': round(sue, 2),
                    'confidence': confidence,
                    'surprises_used': len(surprises),
                    'latest_surprise': round(latest_surprise, 4)
                }
            else:
                return {'sue': 0.0, 'confidence': 'low'}
                
        except Exception as e:
            return {'sue': None, 'confidence': 'error', 'error': str(e)}
    
    def _enrich_with_yahoo(self, earning: Dict) -> Dict:
        """Add current price, volume, and other data from Yahoo"""
        
        try:
            ticker = yf.Ticker(earning['symbol'])
            info = ticker.info
            
            earning.update({
                'company_name': info.get('longName', earning['symbol']),
                'current_price': info.get('regularMarketPrice', 0),
                'market_cap': info.get('marketCap', earning.get('market_cap', 0)),
                'volume': info.get('averageVolume', 0),
                'options_volume': info.get('averageOptionsVolume', 0),
                'sector': info.get('sector', 'Unknown'),
                'pe_ratio': info.get('trailingPE'),
                'short_interest': info.get('shortPercentOfFloat', 0) * 100 if info.get('shortPercentOfFloat') else 0
            })
            
            # Add SUE if we can calculate it
            sue_data = self.calculate_sue(earning['symbol'])
            earning['sue'] = sue_data.get('sue')
            earning['sue_confidence'] = sue_data.get('confidence')
            
        except Exception as e:
            # Keep basic data if Yahoo fails
            pass
            
        return earning
    
    def get_scanner_opportunities(self) -> Dict:
        """Main scanner method returning actionable opportunities"""
        
        # Get upcoming earnings (next 7 days)
        upcoming = self.get_upcoming_earnings(days_ahead=7)
        
        # Get recent earnings (last 5 days) 
        recent = self.get_recent_earnings(days_back=5)
        
        # Filter for best opportunities
        opportunities = {
            'upcoming_high_sue': [],
            'recent_surprises': [],
            'high_short_interest': []
        }
        
        # Find upcoming earnings with high historical SUE
        for stock in upcoming:
            if stock.get('sue') and abs(stock['sue']) > 1.5:
                opportunities['upcoming_high_sue'].append(stock)
        
        # Recent big surprises
        for stock in recent:
            if abs(stock.get('surprise_percent', 0)) > 10:
                opportunities['recent_surprises'].append(stock)
        
        # High short interest plays
        for stock in upcoming:
            if stock.get('short_interest', 0) > 20:
                opportunities['high_short_interest'].append(stock)
        
        return {
            'scan_time': datetime.now().isoformat(),
            'opportunities': opportunities,
            'upcoming_total': len(upcoming),
            'recent_total': len(recent)
        }


# Test the scanner
if __name__ == "__main__":
    scanner = HybridEarningsScanner()
    
    print("Testing Hybrid Earnings Scanner...\n")
    
    # Test upcoming earnings
    print("=== UPCOMING EARNINGS (Next 7 Days) ===")
    upcoming = scanner.get_upcoming_earnings(7)
    
    for stock in upcoming[:5]:
        print(f"\n{stock['symbol']} - {stock.get('company_name', stock['symbol'])}")
        print(f"  Date: {stock['date']} {stock['time']}")
        print(f"  Price: ${stock.get('current_price', 0):.2f}")
        print(f"  Market Cap: ${stock.get('market_cap', 0)/1e9:.1f}B")
        if stock.get('sue'):
            print(f"  SUE Score: {stock['sue']} ({stock.get('sue_confidence', 'unknown')} confidence)")
    
    # Test recent earnings
    print("\n\n=== RECENT EARNINGS SURPRISES ===")
    recent = scanner.get_recent_earnings(10)
    
    for stock in recent[:3]:
        print(f"\n{stock['symbol']} - {stock['company_name']}")
        print(f"  Surprise: {stock['surprise_percent']:.1f}%")
        print(f"  EPS: ${stock['eps_actual']:.2f} vs ${stock['eps_estimate']:.2f} est")
        print(f"  Price: ${stock['current_price']:.2f}")
    
    # Test full scan
    print("\n\n=== SCANNER OPPORTUNITIES ===")
    opps = scanner.get_scanner_opportunities()
    
    print(f"\nFound {opps['upcoming_total']} upcoming earnings")
    print(f"Found {opps['recent_total']} recent earnings")
    
    if opps['opportunities']['upcoming_high_sue']:
        print(f"\n🎯 High SUE Opportunities: {len(opps['opportunities']['upcoming_high_sue'])}")
        for stock in opps['opportunities']['upcoming_high_sue']:
            print(f"  - {stock['symbol']}: SUE {stock['sue']}")
    
    print("\n✅ Scanner ready for production!")