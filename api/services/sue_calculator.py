"""
Standardized Unexpected Earnings (SUE) Calculator
Core signal for post-earnings drift strategy
"""

import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import pandas as pd

class SUECalculator:
    """
    Calculate Standardized Unexpected Earnings (SUE) - the academic standard
    for measuring earnings surprises.
    
    SUE = (Actual EPS - Expected EPS) / Standard Deviation of Surprises
    """
    
    def __init__(self, lookback_quarters: int = 8):
        """
        Args:
            lookback_quarters: Number of quarters to calculate std dev (default 8)
        """
        self.lookback_quarters = lookback_quarters
        
    def calculate_sue(
        self, 
        actual_eps: float, 
        estimated_eps: float,
        historical_surprises: List[float]
    ) -> float:
        """
        Calculate SUE for a single earnings event.
        
        Args:
            actual_eps: Reported EPS
            estimated_eps: Consensus estimate
            historical_surprises: List of prior (actual - estimate) values
            
        Returns:
            SUE score (typically -3 to +3, extreme values beyond)
        """
        # Calculate raw surprise
        surprise = actual_eps - estimated_eps
        
        # Avoid division by zero
        if not historical_surprises or len(historical_surprises) < 2:
            # Fallback: use percentage surprise
            if abs(estimated_eps) < 0.01:
                return 0.0
            return surprise / abs(estimated_eps)
        
        # Calculate standard deviation of historical surprises
        try:
            std_dev = statistics.stdev(historical_surprises)
            if std_dev < 0.01:  # Avoid near-zero division
                std_dev = 0.01
        except:
            std_dev = 0.01
            
        # Standardized surprise
        sue = surprise / std_dev
        
        return round(sue, 3)
    
    def calculate_surprise_percentage(
        self, 
        actual_eps: float, 
        estimated_eps: float
    ) -> float:
        """
        Simple percentage surprise for comparison.
        """
        if abs(estimated_eps) < 0.01:
            return 0.0
        return round((actual_eps - estimated_eps) / abs(estimated_eps) * 100, 2)
    
    def assign_quintile(self, sue_score: float) -> int:
        """
        Assign SUE score to quintile (1-5).
        
        Based on empirical distribution of SUE scores:
        Q1: < -1.5 (big misses)
        Q2: -1.5 to -0.5
        Q3: -0.5 to +0.5 (near consensus)
        Q4: +0.5 to +1.5
        Q5: > +1.5 (big beats)
        """
        if sue_score < -1.5:
            return 1
        elif sue_score < -0.5:
            return 2
        elif sue_score < 0.5:
            return 3
        elif sue_score < 1.5:
            return 4
        else:
            return 5
    
    def is_tradeable_surprise(
        self, 
        sue_score: float,
        min_surprise_pct: float = 5.0
    ) -> Tuple[bool, str]:
        """
        Determine if surprise is large enough to trade.
        
        Returns:
            (is_tradeable, direction)
        """
        quintile = self.assign_quintile(sue_score)
        
        # Only trade extreme quintiles
        if quintile == 5 and sue_score > 1.5:
            return True, "LONG"
        elif quintile == 1 and sue_score < -1.5:
            return True, "SHORT"
        else:
            return False, "NEUTRAL"
    
    def calculate_batch(
        self,
        earnings_data: List[Dict]
    ) -> pd.DataFrame:
        """
        Calculate SUE for multiple stocks.
        
        Args:
            earnings_data: List of dicts with keys:
                - symbol
                - actual_eps
                - estimated_eps
                - historical_surprises
                - report_date
                
        Returns:
            DataFrame with SUE calculations
        """
        results = []
        
        for data in earnings_data:
            sue = self.calculate_sue(
                data['actual_eps'],
                data['estimated_eps'],
                data.get('historical_surprises', [])
            )
            
            surprise_pct = self.calculate_surprise_percentage(
                data['actual_eps'],
                data['estimated_eps']
            )
            
            quintile = self.assign_quintile(sue)
            is_tradeable, direction = self.is_tradeable_surprise(sue)
            
            results.append({
                'symbol': data['symbol'],
                'report_date': data['report_date'],
                'actual_eps': data['actual_eps'],
                'estimated_eps': data['estimated_eps'],
                'surprise_pct': surprise_pct,
                'sue_score': sue,
                'quintile': quintile,
                'is_tradeable': is_tradeable,
                'signal_direction': direction
            })
        
        return pd.DataFrame(results)
    
    def get_signal_confidence(
        self,
        sue_score: float,
        historical_win_rate: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Estimate confidence in the signal based on SUE magnitude.
        """
        # Base confidence from SUE magnitude
        if abs(sue_score) > 3.0:
            base_confidence = 0.75
        elif abs(sue_score) > 2.0:
            base_confidence = 0.65
        elif abs(sue_score) > 1.5:
            base_confidence = 0.55
        else:
            base_confidence = 0.45
            
        # Adjust for historical win rate if available
        if historical_win_rate:
            confidence = (base_confidence + historical_win_rate) / 2
        else:
            confidence = base_confidence
            
        return {
            'confidence': round(confidence, 2),
            'expected_drift_pct': round(abs(sue_score) * 0.8, 2),  # Empirical
            'suggested_hold_days': 3 if abs(sue_score) < 2 else 5
        }


# Example usage and testing
if __name__ == "__main__":
    calculator = SUECalculator()
    
    # Test data
    test_earnings = [
        {
            'symbol': 'AAPL',
            'actual_eps': 2.18,
            'estimated_eps': 2.10,
            'historical_surprises': [0.05, 0.08, 0.03, -0.02, 0.07, 0.04, 0.06, 0.09],
            'report_date': '2026-04-20'
        },
        {
            'symbol': 'NFLX',
            'actual_eps': 3.95,
            'estimated_eps': 4.52,
            'historical_surprises': [0.20, -0.15, 0.30, -0.10, 0.25, -0.30, 0.15, -0.25],
            'report_date': '2026-04-20'
        }
    ]
    
    results = calculator.calculate_batch(test_earnings)
    print("\nSUE Analysis Results:")
    print(results.to_string())
    
    # Get detailed signal for AAPL
    aapl_sue = results[results['symbol'] == 'AAPL']['sue_score'].values[0]
    confidence = calculator.get_signal_confidence(aapl_sue)
    print(f"\nAAPL Signal Confidence: {confidence}")