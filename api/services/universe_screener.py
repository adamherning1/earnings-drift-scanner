"""
Universe Screener for Post-Earnings Drift Strategy
Filters stocks to the sweet spot: $500M-$5B with liquid options
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
from dataclasses import dataclass

@dataclass
class StockCandidate:
    """Represents a stock that passes our filters"""
    symbol: str
    market_cap: float
    avg_volume: int
    avg_options_volume: int
    sector: str
    has_weekly_options: bool
    recent_earnings_date: Optional[str]
    
class UniverseScreener:
    """
    Screen for stocks in the optimal range for post-earnings drift.
    
    Academic research shows PEAD works best in:
    - $500M - $5B market cap (less arbitraged than large caps)
    - Sufficient options liquidity (>5,000 daily contracts)
    - Recent earnings (within last 5 days)
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://financialmodelingprep.com/api/v3"
        
        # Optimal universe constraints
        self.MIN_MARKET_CAP = 500_000_000      # $500M
        self.MAX_MARKET_CAP = 5_000_000_000    # $5B
        self.MIN_AVG_VOLUME = 500_000          # 500K shares daily
        self.MIN_OPTIONS_VOLUME = 5_000        # 5K contracts daily
        self.MAX_DAYS_SINCE_EARNINGS = 5       # Trade within 5 days
        
    def get_market_cap_range_stocks(self) -> List[Dict]:
        """
        Get all stocks within our market cap range.
        """
        # FMP endpoint for stock screener
        url = f"{self.base_url}/stock-screener"
        params = {
            'marketCapMoreThan': self.MIN_MARKET_CAP,
            'marketCapLowerThan': self.MAX_MARKET_CAP,
            'volumeMoreThan': self.MIN_AVG_VOLUME,
            'exchange': 'NYSE,NASDAQ',
            'isActivelyTrading': True,
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching stocks: {e}")
            return []
    
    def check_options_liquidity(self, symbol: str) -> Dict[str, any]:
        """
        Check if stock has sufficient options liquidity.
        
        Note: Real implementation would use Polygon or ORATS for actual options volume.
        This is a placeholder that estimates based on stock volume.
        """
        # TODO: Replace with real options data provider
        # For now, estimate options volume as % of stock volume
        
        # Rough heuristic: liquid stocks have options volume ~10% of share volume
        # This is a VERY rough estimate and should be replaced with real data
        
        stock_data = self.get_stock_quote(symbol)
        if not stock_data:
            return {'has_liquid_options': False, 'avg_options_volume': 0}
        
        avg_volume = stock_data.get('avgVolume', 0)
        estimated_options_volume = avg_volume * 0.1  # 10% estimate
        
        # Check if weekly options exist (another liquidity indicator)
        has_weekly = symbol in self.get_weekly_options_list()
        
        return {
            'has_liquid_options': estimated_options_volume > self.MIN_OPTIONS_VOLUME,
            'avg_options_volume': int(estimated_options_volume),
            'has_weekly_options': has_weekly
        }
    
    def get_recent_earnings(self, days_back: int = 5) -> List[Dict]:
        """
        Get stocks that reported earnings in last N days.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        url = f"{self.base_url}/earning_calendar"
        params = {
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d'),
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching earnings calendar: {e}")
            return []
    
    def get_stock_quote(self, symbol: str) -> Dict:
        """Get current quote and market cap for a symbol."""
        url = f"{self.base_url}/quote/{symbol}"
        params = {'apikey': self.api_key}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data[0] if data else {}
        except:
            return {}
    
    def get_weekly_options_list(self) -> List[str]:
        """
        Get list of stocks with weekly options (high liquidity indicator).
        This is a static list of known weekly options stocks.
        """
        # Top stocks known to have weekly options
        # In production, fetch this from CBOE or options data provider
        return [
            'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'TSLA', 'NVDA',
            'AMD', 'NFLX', 'DIS', 'BA', 'GS', 'JPM', 'XOM', 'CVX',
            'WMT', 'HD', 'NKE', 'MCD', 'SBUX', 'TGT', 'F', 'GM'
        ]
    
    def screen_universe(self) -> List[StockCandidate]:
        """
        Main screening function - returns list of tradeable candidates.
        """
        print("Screening universe for post-earnings drift candidates...")
        
        # Step 1: Get recent earnings
        recent_earnings = self.get_recent_earnings(self.MAX_DAYS_SINCE_EARNINGS)
        earnings_symbols = {e['symbol']: e['date'] for e in recent_earnings if e.get('symbol')}
        print(f"Found {len(earnings_symbols)} recent earnings reports")
        
        # Step 2: Get stocks in our market cap range  
        stocks_in_range = self.get_market_cap_range_stocks()
        print(f"Found {len(stocks_in_range)} stocks in ${self.MIN_MARKET_CAP/1e9:.1f}B-${self.MAX_MARKET_CAP/1e9:.1f}B range")
        
        # Step 3: Find intersection - stocks with recent earnings in our range
        candidates = []
        
        for stock in stocks_in_range:
            symbol = stock.get('symbol')
            if symbol not in earnings_symbols:
                continue
                
            # Check options liquidity
            options_data = self.check_options_liquidity(symbol)
            if not options_data['has_liquid_options']:
                continue
            
            # Create candidate
            candidate = StockCandidate(
                symbol=symbol,
                market_cap=stock.get('marketCap', 0),
                avg_volume=stock.get('avgVolume', 0),
                avg_options_volume=options_data['avg_options_volume'],
                sector=stock.get('sector', 'Unknown'),
                has_weekly_options=options_data['has_weekly_options'],
                recent_earnings_date=earnings_symbols[symbol]
            )
            
            candidates.append(candidate)
        
        print(f"Found {len(candidates)} tradeable candidates")
        return candidates
    
    def to_dataframe(self, candidates: List[StockCandidate]) -> pd.DataFrame:
        """Convert candidates to pandas DataFrame for analysis."""
        data = []
        for c in candidates:
            data.append({
                'symbol': c.symbol,
                'market_cap_b': round(c.market_cap / 1e9, 2),
                'avg_volume_m': round(c.avg_volume / 1e6, 2),
                'est_options_vol_k': round(c.avg_options_volume / 1e3, 1),
                'sector': c.sector,
                'weekly_options': c.has_weekly_options,
                'earnings_date': c.recent_earnings_date
            })
        
        df = pd.DataFrame(data)
        return df.sort_values('market_cap_b', ascending=False)


# Example usage
if __name__ == "__main__":
    # Note: Replace with your actual FMP API key
    API_KEY = "your_fmp_api_key"
    
    screener = UniverseScreener(API_KEY)
    
    # Screen universe
    candidates = screener.screen_universe()
    
    # Convert to DataFrame for display
    df = screener.to_dataframe(candidates)
    print("\nTradeable Universe:")
    print(df.to_string())
    
    # Show summary stats
    if len(df) > 0:
        print(f"\nSummary:")
        print(f"Total candidates: {len(df)}")
        print(f"Avg market cap: ${df['market_cap_b'].mean():.1f}B")
        print(f"With weekly options: {df['weekly_options'].sum()}/{len(df)}")
        print(f"Sectors: {df['sector'].value_counts().to_dict()}")