#!/usr/bin/env python3
"""
Phase 2: Adaptive Position Sizing for MGC Trading Bot
Adjusts position size based on recent performance
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

class AdaptivePositionSizer:
    """
    Conservative position sizing based on win streaks
    Increases size after consecutive wins, resets on any loss
    """
    
    def __init__(self, base_size: int = 2, max_size: int = 4):
        self.base_size = base_size
        self.max_size = max_size
        self.current_size = base_size
        
        # Streak tracking
        self.current_streak = 0
        self.is_win_streak = True
        
        # Performance tracking
        self.recent_trades = []
        self.daily_contracts_used = 0
        self.daily_pnl = 0.0
        self.last_trade_date = None
        
        # Thresholds for size increases
        self.size_thresholds = {
            3: 5,   # 3 contracts after 5 consecutive wins
            4: 8    # 4 contracts after 8 consecutive wins
        }
        
        # Safety parameters
        self.daily_loss_limit = 300  # Reduce size if daily loss exceeds this
        self.max_daily_contracts = 12  # Maximum contracts per day
        
        # Load state if exists
        self.load_state()
    
    def get_position_size(self, current_balance: float = None) -> int:
        """
        Get the position size for the next trade
        
        Args:
            current_balance: Current account balance (for risk management)
            
        Returns:
            Number of contracts to trade
        """
        # Check if it's a new day and reset daily counters
        self._check_new_day()
        
        # Safety check: Reduce size if daily loss is too high
        if self.daily_pnl < -self.daily_loss_limit:
            logger.warning(f"Daily loss ${self.daily_pnl:.2f} exceeds limit. Using base size.")
            return self.base_size
        
        # Safety check: Don't exceed daily contract limit
        if self.daily_contracts_used >= self.max_daily_contracts:
            logger.warning(f"Daily contract limit reached ({self.max_daily_contracts})")
            return 0  # No more trades today
        
        # Determine size based on win streak
        if not self.is_win_streak or self.current_streak == 0:
            size = self.base_size
        else:
            size = self._calculate_streak_size()
        
        # Never exceed max size
        size = min(size, self.max_size)
        
        # Optional: Reduce size if balance is low
        if current_balance and current_balance < 50000:
            size = min(size, 2)  # Conservative when balance is low
        
        logger.info(f"Position size: {size} contracts (streak: {self.current_streak})")
        self.current_size = size
        return size
    
    def record_trade(self, is_win: bool, pnl: float, contracts: int):
        """
        Record a completed trade and update streak
        
        Args:
            is_win: True if trade was profitable
            pnl: Profit/loss from the trade
            contracts: Number of contracts traded
        """
        trade = {
            'timestamp': datetime.now().isoformat(),
            'is_win': is_win,
            'pnl': pnl,
            'contracts': contracts,
            'streak_at_entry': self.current_streak
        }
        
        self.recent_trades.append(trade)
        
        # Keep only last 100 trades
        if len(self.recent_trades) > 100:
            self.recent_trades.pop(0)
        
        # Update daily counters
        self.daily_pnl += pnl
        self.daily_contracts_used += contracts
        
        # Update streak
        if is_win:
            if self.is_win_streak:
                self.current_streak += 1
            else:
                self.is_win_streak = True
                self.current_streak = 1
        else:
            if not self.is_win_streak:
                self.current_streak += 1
            else:
                self.is_win_streak = False
                self.current_streak = 1
        
        logger.info(f"Trade recorded: {'WIN' if is_win else 'LOSS'} ${pnl:.2f}")
        logger.info(f"Current streak: {self.current_streak} {'wins' if self.is_win_streak else 'losses'}")
        
        # Save state after each trade
        self.save_state()
    
    def _calculate_streak_size(self) -> int:
        """Calculate position size based on win streak"""
        if self.current_streak >= 8:
            return 4
        elif self.current_streak >= 5:
            return 3
        else:
            return self.base_size
    
    def _check_new_day(self):
        """Reset daily counters if it's a new trading day"""
        today = datetime.now().date()
        
        if self.last_trade_date != today:
            logger.info(f"New trading day. Resetting daily counters.")
            self.daily_contracts_used = 0
            self.daily_pnl = 0.0
            self.last_trade_date = today
    
    def get_stats(self) -> Dict:
        """Get current statistics"""
        total_trades = len(self.recent_trades)
        wins = sum(1 for t in self.recent_trades if t['is_win'])
        
        stats = {
            'current_size': self.current_size,
            'current_streak': self.current_streak,
            'streak_type': 'wins' if self.is_win_streak else 'losses',
            'daily_pnl': self.daily_pnl,
            'daily_contracts': self.daily_contracts_used,
            'total_recent_trades': total_trades,
            'recent_win_rate': (wins / total_trades * 100) if total_trades > 0 else 0,
            'position_sizes_available': {
                2: 'Base size (default)',
                3: 'After 5 consecutive wins',
                4: 'After 8 consecutive wins'
            }
        }
        
        return stats
    
    def save_state(self):
        """Save current state to file"""
        state = {
            'current_streak': self.current_streak,
            'is_win_streak': self.is_win_streak,
            'recent_trades': self.recent_trades[-20:],  # Keep last 20 for state
            'daily_contracts_used': self.daily_contracts_used,
            'daily_pnl': self.daily_pnl,
            'last_trade_date': self.last_trade_date.isoformat() if self.last_trade_date else None
        }
        
        try:
            with open('adaptive_sizing_state.json', 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def load_state(self):
        """Load previous state from file"""
        try:
            with open('adaptive_sizing_state.json', 'r') as f:
                state = json.load(f)
                
            self.current_streak = state.get('current_streak', 0)
            self.is_win_streak = state.get('is_win_streak', True)
            self.recent_trades = state.get('recent_trades', [])
            self.daily_contracts_used = state.get('daily_contracts_used', 0)
            self.daily_pnl = state.get('daily_pnl', 0.0)
            
            if state.get('last_trade_date'):
                self.last_trade_date = datetime.fromisoformat(state['last_trade_date']).date()
            
            logger.info(f"Loaded state: {self.current_streak} streak")
            
        except FileNotFoundError:
            logger.info("No previous state found. Starting fresh.")
        except Exception as e:
            logger.error(f"Failed to load state: {e}")


# Integration helper for the main bot
def integrate_with_bot(bot_instance):
    """
    Integration function to add adaptive sizing to existing bot
    
    Usage in adaptive_trading_bot.py:
    
    # In __init__:
    self.position_sizer = AdaptivePositionSizer(base_size=2, max_size=4)
    
    # When placing order:
    position_size = self.position_sizer.get_position_size(current_balance)
    
    # After trade completes:
    self.position_sizer.record_trade(is_win, pnl, contracts)
    """
    pass


if __name__ == "__main__":
    # Test the position sizer
    sizer = AdaptivePositionSizer()
    
    print("Adaptive Position Sizing Test")
    print("=" * 50)
    
    # Simulate some trades
    trades = [
        (True, 150),   # Win
        (True, 200),   # Win
        (True, 180),   # Win
        (True, 220),   # Win
        (True, 190),   # Win - should increase size
        (True, 300),   # Win
        (False, -150), # Loss - should reset to base
        (True, 160),   # Win
    ]
    
    for i, (is_win, pnl) in enumerate(trades, 1):
        size = sizer.get_position_size()
        print(f"\nTrade {i}: Size = {size} contracts")
        
        sizer.record_trade(is_win, pnl, size)
        print(f"Result: {'WIN' if is_win else 'LOSS'} ${pnl}")
        
        stats = sizer.get_stats()
        print(f"Streak: {stats['current_streak']} {stats['streak_type']}")
        print(f"Daily P&L: ${stats['daily_pnl']:.2f}")