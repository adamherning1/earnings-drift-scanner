"""
Background Scanner Worker
Runs continuously to detect new earnings and generate signals
"""

import os
import time
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Import our services
from services.earnings_ingestion import EarningsIngestionService
from services.sue_calculator import SUECalculator
from services.universe_screener import UniverseScreener
from services.alert_service import AlertService
from services.database import Database

# Load environment variables
load_dotenv()

class EarningsScannerWorker:
    """
    Main background worker that runs 24/7 in the cloud.
    Scans for earnings, generates signals, sends alerts.
    """
    
    def __init__(self):
        self.fmp_api_key = os.getenv('FMP_API_KEY')
        self.db = Database(os.getenv('DATABASE_URL'))
        
        # Initialize services
        self.earnings_service = EarningsIngestionService(self.fmp_api_key)
        self.sue_calculator = SUECalculator()
        self.universe_screener = UniverseScreener(self.fmp_api_key)
        self.alert_service = AlertService()
        
        print(f"Scanner Worker initialized at {datetime.now()}")
    
    async def process_new_earnings(self):
        """
        Main processing loop - runs every scan interval.
        """
        print(f"\n🔍 Scanning for new earnings at {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        try:
            # 1. Get new earnings
            new_earnings = self.earnings_service.scan_for_new_earnings()
            
            if not new_earnings:
                print("No new earnings found this scan")
                return
            
            print(f"Found {len(new_earnings)} new earnings to process")
            
            # 2. Calculate SUE for each
            sue_results = self.sue_calculator.calculate_batch(new_earnings)
            
            # 3. Filter for tradeable signals
            tradeable = sue_results[sue_results['is_tradeable'] == True]
            
            if len(tradeable) == 0:
                print("No tradeable signals (Q1/Q5) in this batch")
                return
            
            print(f"Found {len(tradeable)} tradeable signals")
            
            # 4. Check universe constraints
            universe = await self.get_valid_universe()
            
            # 5. Process each signal
            for _, signal in tradeable.iterrows():
                if signal['symbol'] not in universe:
                    print(f"Skipping {signal['symbol']} - not in valid universe")
                    continue
                
                await self.process_signal(signal)
                
        except Exception as e:
            print(f"Error in scanner: {e}")
            # Log to error tracking service (Sentry)
            # Continue running - don't crash
    
    async def process_signal(self, signal):
        """
        Process a single tradeable signal.
        """
        print(f"\n📊 Processing signal: {signal['symbol']}")
        
        # 1. Get current price
        quote = self.universe_screener.get_stock_quote(signal['symbol'])
        if not quote:
            print(f"Could not get quote for {signal['symbol']}")
            return
        
        current_price = quote.get('price', 0)
        
        # 2. Save signal to database
        signal_id = await self.db.save_signal({
            'symbol': signal['symbol'],
            'signal_date': datetime.now(),
            'sue_score': signal['sue_score'],
            'quintile': signal['quintile'],
            'direction': signal['signal_direction'],
            'entry_price': current_price,
            'surprise_pct': signal['surprise_pct'],
            'status': 'active'
        })
        
        # 3. Enter paper trade
        await self.db.enter_paper_position({
            'signal_id': signal_id,
            'symbol': signal['symbol'],
            'entry_date': datetime.now(),
            'entry_price': current_price,
            'direction': signal['signal_direction'],
            'position_size': self.calculate_position_size(current_price),
            'stop_loss': self.calculate_stop_loss(current_price, signal['signal_direction']),
            'take_profit': self.calculate_take_profit(current_price, signal['signal_direction']),
            'sue_score': signal['sue_score'],
            'quintile': signal['quintile']
        })
        
        # 4. Send alerts to subscribers
        await self.alert_service.send_new_signal_alert(signal, current_price)
        
        print(f"✅ Signal processed: {signal['symbol']} {signal['signal_direction']}")
    
    async def get_valid_universe(self):
        """
        Get current valid universe (cached for performance).
        """
        # Check cache first
        cached = await self.db.get_cached_universe()
        if cached and cached['age_minutes'] < 60:
            return set(cached['symbols'])
        
        # Refresh universe
        candidates = self.universe_screener.screen_universe()
        symbols = {c.symbol for c in candidates}
        
        # Cache for 1 hour
        await self.db.cache_universe(list(symbols))
        
        return symbols
    
    def calculate_position_size(self, price):
        """Calculate position size (for paper trading)."""
        # Risk 2% of $100k = $2000 per trade
        risk_amount = 2000
        stop_distance = 0.025  # 2.5% stop
        return int(risk_amount / (price * stop_distance))
    
    def calculate_stop_loss(self, price, direction):
        """Calculate stop loss price."""
        if direction == "LONG":
            return round(price * 0.975, 2)  # -2.5%
        else:
            return round(price * 1.025, 2)  # +2.5%
    
    def calculate_take_profit(self, price, direction):
        """Calculate take profit price."""
        if direction == "LONG":
            return round(price * 1.018, 2)  # +1.8%
        else:
            return round(price * 0.98, 2)   # -2.0%
    
    async def run_forever(self):
        """
        Main loop - runs forever with smart intervals.
        """
        print("🚀 Earnings Scanner Worker started")
        print(f"Scanning every 15 minutes (5 minutes during earnings hours)")
        
        while True:
            try:
                # Process new earnings
                await self.process_new_earnings()
                
                # Determine next scan interval
                now = datetime.now()
                hour = now.hour
                
                # Scan more frequently during typical earnings release times
                # Most earnings come out 6-9 AM or 4-6 PM ET
                if hour in [6, 7, 8, 16, 17]:
                    interval_minutes = 5
                    print(f"⚡ Earnings hour detected - next scan in 5 minutes")
                else:
                    interval_minutes = 15
                    print(f"💤 Normal hours - next scan in 15 minutes")
                
                # Sleep until next scan
                await asyncio.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\nShutting down scanner...")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                # Don't crash - wait and retry
                await asyncio.sleep(60)

# Main entry point
if __name__ == "__main__":
    scanner = EarningsScannerWorker()
    asyncio.run(scanner.run_forever())