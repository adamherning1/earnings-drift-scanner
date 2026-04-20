import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from ..models import EarningsEvent, DriftPattern

class EarningsDataService:
    def __init__(self, db: Session):
        self.db = db
    
    async def fetch_earnings_history(self, symbol: str, quarters: int = 12) -> List[EarningsEvent]:
        """Fetch earnings history from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            earnings_dates = ticker.earnings_dates
            
            if earnings_dates is None or earnings_dates.empty:
                return []
            
            # Get last N quarters
            earnings_dates = earnings_dates.head(quarters)
            
            events = []
            for date_idx, row in earnings_dates.iterrows():
                # Check if already exists
                existing = self.db.query(EarningsEvent).filter(
                    EarningsEvent.symbol == symbol,
                    EarningsEvent.earnings_date == date_idx.date()
                ).first()
                
                if not existing:
                    event = EarningsEvent(
                        symbol=symbol,
                        earnings_date=date_idx.date(),
                        reported_time="AMC" if date_idx.hour > 12 else "BMO",
                        eps_actual=row.get('Reported EPS'),
                        eps_estimate=row.get('Estimated EPS'),
                        eps_surprise=row.get('Surprise'),
                        eps_surprise_pct=row.get('Surprise %')
                    )
                    self.db.add(event)
                    events.append(event)
                else:
                    events.append(existing)
            
            self.db.commit()
            return events
            
        except Exception as e:
            print(f"Error fetching earnings for {symbol}: {e}")
            return []
    
    async def calculate_drift_patterns(self, symbol: str):
        """Calculate pre-earnings drift patterns"""
        # Get all earnings events
        events = self.db.query(EarningsEvent).filter(
            EarningsEvent.symbol == symbol
        ).order_by(EarningsEvent.earnings_date.desc()).all()
        
        if not events:
            return
        
        # Get price data
        ticker = yf.Ticker(symbol)
        
        # Get SPY for relative performance
        spy = yf.Ticker("SPY")
        
        for event in events:
            # Skip if patterns already calculated
            existing_patterns = self.db.query(DriftPattern).filter(
                DriftPattern.earnings_event_id == event.id
            ).count()
            
            if existing_patterns >= 5:
                continue
            
            # Get price data for 10 days before earnings
            start_date = event.earnings_date - timedelta(days=15)
            end_date = event.earnings_date + timedelta(days=1)
            
            try:
                price_data = ticker.history(start=start_date, end=end_date)
                spy_data = spy.history(start=start_date, end=end_date)
                
                if price_data.empty:
                    continue
                
                # Calculate patterns for -5 to 0 days
                base_price = None
                cumulative_return = 0
                
                for days_before in range(-5, 1):
                    target_date = event.earnings_date + timedelta(days=days_before)
                    
                    # Find closest trading day
                    mask = price_data.index.date <= target_date.date()
                    if not mask.any():
                        continue
                    
                    idx = price_data[mask].index[-1]
                    
                    if idx in price_data.index:
                        row = price_data.loc[idx]
                        
                        if base_price is None:
                            base_price = row['Close']
                        
                        daily_return = (row['Close'] / row['Open'] - 1) * 100
                        cumulative_return = (row['Close'] / base_price - 1) * 100
                        
                        # SPY relative
                        spy_return = 0
                        if idx in spy_data.index:
                            spy_base = spy_data[spy_data.index.date <= (event.earnings_date - timedelta(days=5)).date()].iloc[-1]['Close']
                            spy_return = (spy_data.loc[idx]['Close'] / spy_base - 1) * 100
                        
                        pattern = DriftPattern(
                            earnings_event_id=event.id,
                            days_before=days_before,
                            open_price=row['Open'],
                            close_price=row['Close'],
                            high_price=row['High'],
                            low_price=row['Low'],
                            volume=int(row['Volume']),
                            daily_return=daily_return,
                            cumulative_return=cumulative_return,
                            relative_to_spy=cumulative_return - spy_return
                        )
                        
                        self.db.add(pattern)
                
                self.db.commit()
                
            except Exception as e:
                print(f"Error calculating drift for {symbol} on {event.earnings_date}: {e}")
                continue
    
    async def calculate_drift_statistics(self, symbol: str) -> Dict:
        """Calculate statistical measures of drift patterns"""
        # Get all events with positive surprises
        positive_surprises = self.db.query(EarningsEvent).filter(
            EarningsEvent.symbol == symbol,
            EarningsEvent.eps_surprise_pct > 0
        ).all()
        
        # Get all events with negative surprises
        negative_surprises = self.db.query(EarningsEvent).filter(
            EarningsEvent.symbol == symbol,
            EarningsEvent.eps_surprise_pct < 0
        ).all()
        
        def get_pattern_stats(events):
            if not events:
                return None
            
            # Collect all -5 to -1 day returns
            returns = []
            for event in events:
                pattern = self.db.query(DriftPattern).filter(
                    DriftPattern.earnings_event_id == event.id,
                    DriftPattern.days_before == -1
                ).first()
                
                if pattern:
                    returns.append(pattern.cumulative_return)
            
            if not returns:
                return None
            
            returns = np.array(returns)
            return {
                "mean_drift": np.mean(returns),
                "median_drift": np.median(returns),
                "std_drift": np.std(returns),
                "positive_drift_pct": (returns > 0).sum() / len(returns) * 100,
                "avg_positive_drift": np.mean(returns[returns > 0]) if (returns > 0).any() else 0,
                "avg_negative_drift": np.mean(returns[returns < 0]) if (returns < 0).any() else 0,
                "sample_size": len(returns)
            }
        
        return {
            "positive_surprises": get_pattern_stats(positive_surprises),
            "negative_surprises": get_pattern_stats(negative_surprises),
            "all_events": get_pattern_stats(positive_surprises + negative_surprises)
        }