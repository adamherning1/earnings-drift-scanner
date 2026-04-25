"""
AI Playbook Generator for Earnings Trades
Generates specific, actionable options trades based on historical patterns
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random  # Will replace with real AI integration

class PlaybookGenerator:
    def __init__(self, account_size: int = 25000):
        self.account_size = account_size
        self.risk_per_trade = 0.05  # 5% max risk per trade
        
    def generate_playbook(self, symbol: str, earnings_date: str, 
                         historical_data: Dict) -> Dict:
        """Generate complete trading playbook for a symbol"""
        
        # Extract key metrics
        win_rate = historical_data.get('win_rate', 0.5)
        avg_move = historical_data.get('avg_move', 0.02)
        current_price = historical_data.get('current_price', 100)
        iv_rank = historical_data.get('iv_rank', 50)
        
        # Generate 3 plays: Aggressive, Conservative, Hedge
        plays = []
        
        # Play 1: Aggressive directional
        if win_rate > 0.6:  # Bullish bias
            plays.append(self._generate_call_play(symbol, current_price, 
                                                  win_rate, avg_move))
        else:  # More neutral
            plays.append(self._generate_straddle_play(symbol, current_price,
                                                     iv_rank))
        
        # Play 2: Conservative spread
        plays.append(self._generate_spread_play(symbol, current_price,
                                               win_rate, avg_move))
        
        # Play 3: Hedge/Protection
        plays.append(self._generate_hedge_play(symbol, current_price))
        
        return {
            "symbol": symbol,
            "earnings_date": earnings_date,
            "generated_at": datetime.now().isoformat(),
            "account_size": self.account_size,
            "historical_summary": {
                "win_rate": f"{win_rate*100:.0f}%",
                "avg_move": f"{avg_move*100:.1f}%", 
                "iv_rank": f"{iv_rank}th percentile",
                "confidence": self._calculate_confidence(win_rate, iv_rank)
            },
            "plays": plays
        }
    
    def _generate_call_play(self, symbol: str, price: float, 
                           win_rate: float, avg_move: float) -> Dict:
        """Generate aggressive call buying play"""
        
        # Calculate strikes
        atm_strike = round(price / 5) * 5  # Round to $5 increments
        strike = atm_strike if win_rate > 0.65 else atm_strike + 5
        
        # Position sizing
        option_price = price * 0.03  # Rough estimate, 3% of stock price
        max_contracts = int((self.account_size * self.risk_per_trade) / 
                           (option_price * 100))
        contracts = min(max_contracts, 20)  # Cap at 20 contracts
        
        return {
            "type": "Aggressive",
            "action": f"Buy {symbol} May 2 ${strike} Calls",
            "entry": "Monday 9:45 AM ET",
            "exit": "Wednesday 3:30 PM ET", 
            "position_size": "5% of account",
            "confidence": f"{win_rate * 100:.0f}%",
            "reasoning": f"Expecting >{avg_move*100:.1f}% move based on history",
            "notes": "Check current price in your broker"
        }
    
    def _generate_spread_play(self, symbol: str, price: float,
                             win_rate: float, avg_move: float) -> Dict:
        """Generate conservative spread play"""
        
        atm_strike = round(price / 5) * 5
        spread_width = 10 if price > 100 else 5
        
        # Bull call spread if bullish, bear put spread if bearish
        if win_rate > 0.5:
            play_type = "Call Spread"
            long_strike = atm_strike
            short_strike = atm_strike + spread_width
        else:
            play_type = "Put Spread" 
            long_strike = atm_strike
            short_strike = atm_strike - spread_width
            
        spread_cost = spread_width * 0.4  # 40% of width
        max_contracts = int((self.account_size * self.risk_per_trade * 0.7) / 
                           (spread_cost * 100))
        contracts = min(max_contracts, 30)
        
        return {
            "type": "Conservative",
            "action": f"BUY {contracts}x {symbol} ${long_strike}/{short_strike} {play_type} @ ${spread_cost:.2f}",
            "entry": "Monday open",
            "exit": "Wednesday close",
            "risk": f"${contracts * spread_cost * 100:,.0f}",
            "target": f"${contracts * spread_cost * 100 * 1.5:,.0f} (+50%)",
            "confidence": f"{min(win_rate * 100 + 10, 85):.0f}%",
            "notes": "Lower risk, capped profit"
        }
    
    def _generate_straddle_play(self, symbol: str, price: float,
                               iv_rank: int) -> Dict:
        """Generate straddle for high IV plays"""
        
        atm_strike = round(price / 5) * 5
        straddle_price = price * 0.06  # ~6% for weekly straddle
        
        max_contracts = int((self.account_size * self.risk_per_trade) / 
                           (straddle_price * 100))
        contracts = min(max_contracts, 10)  # Smaller size for straddles
        
        return {
            "type": "Volatility Play",
            "action": f"BUY {contracts}x {symbol} May 2 ${atm_strike} Straddle @ ${straddle_price:.2f}",
            "entry": "Monday 9:45 AM ET",
            "exit": "Wednesday 3:30 PM ET",
            "risk": f"${contracts * straddle_price * 100:,.0f}",
            "target": f"${contracts * straddle_price * 100 * 1.4:,.0f} (+40%)",
            "confidence": "60%",
            "notes": "Profits from movement in either direction"
        }
    
    def _generate_hedge_play(self, symbol: str, price: float) -> Dict:
        """Generate hedge recommendation"""
        
        # 3% OTM puts
        put_strike = round(price * 0.97 / 5) * 5
        put_price = price * 0.01  # ~1% for OTM puts
        
        # Small hedge, 20% of main position
        contracts = max(2, int(self.risk_per_trade * self.account_size * 0.2 / 
                              (put_price * 100)))
        
        return {
            "type": "Hedge",
            "action": f"ADD {contracts}x {symbol} ${put_strike} Puts @ ${put_price:.2f}",
            "entry": "With main position",
            "exit": "With main position",
            "risk": f"${contracts * put_price * 100:,.0f}",
            "target": "Protection only",
            "confidence": "N/A",
            "notes": "Protects against -3% gap down"
        }
    
    def _calculate_confidence(self, win_rate: float, iv_rank: int) -> str:
        """Calculate overall trade confidence"""
        # Higher win rate and moderate IV = higher confidence
        if win_rate > 0.7 and 40 <= iv_rank <= 70:
            return "HIGH"
        elif win_rate > 0.6 or iv_rank > 80:
            return "MEDIUM"
        else:
            return "LOW"


# Example usage
if __name__ == "__main__":
    generator = PlaybookGenerator(account_size=25000)
    
    # Mock historical data
    historical_data = {
        "win_rate": 0.67,
        "avg_move": 0.032,
        "current_price": 250,
        "iv_rank": 78
    }
    
    playbook = generator.generate_playbook("AMZN", "2026-04-29", historical_data)
    print(json.dumps(playbook, indent=2))