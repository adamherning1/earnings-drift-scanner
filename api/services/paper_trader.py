"""
Paper Trading Engine for Post-Earnings Drift
Tracks signals and performance transparently
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
from dataclasses import dataclass, asdict
import os

@dataclass
class PaperPosition:
    """Represents a paper trading position"""
    id: str
    symbol: str
    entry_date: str
    entry_price: float
    position_size: int  # Number of shares
    sue_score: float
    quintile: int
    direction: str  # LONG or SHORT
    stop_loss: float
    take_profit: float
    status: str  # OPEN, CLOSED, STOPPED
    exit_date: Optional[str] = None
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    
class PaperTrader:
    """
    Paper trading engine that tracks post-earnings drift signals.
    Full transparency - every trade logged and tracked.
    """
    
    def __init__(self, starting_capital: float = 100_000):
        self.starting_capital = starting_capital
        self.current_capital = starting_capital
        self.positions = []
        self.closed_positions = []
        self.trade_log_file = "paper_trades.json"
        self.load_existing_trades()
        
    def load_existing_trades(self):
        """Load existing paper trades from file."""
        if os.path.exists(self.trade_log_file):
            with open(self.trade_log_file, 'r') as f:
                data = json.load(f)
                self.positions = [PaperPosition(**p) for p in data.get('open_positions', [])]
                self.closed_positions = [PaperPosition(**p) for p in data.get('closed_positions', [])]
                self.current_capital = data.get('current_capital', self.starting_capital)
    
    def save_trades(self):
        """Save all trades to file for transparency."""
        data = {
            'open_positions': [asdict(p) for p in self.positions],
            'closed_positions': [asdict(p) for p in self.closed_positions],
            'current_capital': self.current_capital,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.trade_log_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def enter_position(
        self,
        symbol: str,
        current_price: float,
        sue_score: float,
        quintile: int,
        direction: str
    ) -> PaperPosition:
        """
        Enter a new paper position based on SUE signal.
        
        Position sizing: Risk 2% of capital per trade
        Stop loss: 2.5% for longs, 2.5% for shorts
        Take profit: Based on expected drift (1.8% for Q5, 2.0% for Q1)
        """
        # Position sizing - risk 2% of capital
        risk_amount = self.current_capital * 0.02
        stop_distance = 0.025  # 2.5% stop
        
        position_size = int(risk_amount / (current_price * stop_distance))
        
        # Set stops and targets
        if direction == "LONG":
            stop_loss = current_price * (1 - stop_distance)
            take_profit = current_price * 1.018  # 1.8% target
        else:  # SHORT
            stop_loss = current_price * (1 + stop_distance)
            take_profit = current_price * 0.98   # 2.0% target
            
        position = PaperPosition(
            id=f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            symbol=symbol,
            entry_date=datetime.now().strftime('%Y-%m-%d'),
            entry_price=current_price,
            position_size=position_size,
            sue_score=sue_score,
            quintile=quintile,
            direction=direction,
            stop_loss=round(stop_loss, 2),
            take_profit=round(take_profit, 2),
            status="OPEN"
        )
        
        self.positions.append(position)
        self.save_trades()
        
        print(f"\n📈 NEW PAPER TRADE:")
        print(f"Symbol: {symbol}")
        print(f"Direction: {direction}")
        print(f"Entry: ${current_price:.2f}")
        print(f"Size: {position_size} shares")
        print(f"Stop: ${stop_loss:.2f}")
        print(f"Target: ${take_profit:.2f}")
        print(f"SUE Score: {sue_score:.2f} (Q{quintile})")
        
        return position
    
    def update_positions(self, current_prices: Dict[str, float]):
        """
        Update all open positions with current prices.
        Close positions that hit stops or targets.
        """
        for position in self.positions[:]:  # Copy list to modify during iteration
            if position.status != "OPEN":
                continue
                
            symbol = position.symbol
            if symbol not in current_prices:
                continue
                
            current_price = current_prices[symbol]
            
            # Check stop loss
            if position.direction == "LONG":
                if current_price <= position.stop_loss:
                    self.close_position(position, current_price, "STOPPED")
                elif current_price >= position.take_profit:
                    self.close_position(position, current_price, "TARGET")
            else:  # SHORT
                if current_price >= position.stop_loss:
                    self.close_position(position, current_price, "STOPPED")
                elif current_price <= position.take_profit:
                    self.close_position(position, current_price, "TARGET")
    
    def close_position(self, position: PaperPosition, exit_price: float, reason: str):
        """Close a position and calculate P&L."""
        position.exit_date = datetime.now().strftime('%Y-%m-%d')
        position.exit_price = exit_price
        position.status = reason
        
        # Calculate P&L
        if position.direction == "LONG":
            position.pnl = (exit_price - position.entry_price) * position.position_size
        else:  # SHORT
            position.pnl = (position.entry_price - exit_price) * position.position_size
            
        position.pnl_percent = position.pnl / (position.entry_price * position.position_size) * 100
        
        # Update capital
        self.current_capital += position.pnl
        
        # Move to closed positions
        self.positions.remove(position)
        self.closed_positions.append(position)
        self.save_trades()
        
        emoji = "✅" if position.pnl > 0 else "❌"
        print(f"\n{emoji} POSITION CLOSED:")
        print(f"Symbol: {position.symbol}")
        print(f"Exit: ${exit_price:.2f} ({reason})")
        print(f"P&L: ${position.pnl:.2f} ({position.pnl_percent:+.2f}%)")
    
    def get_performance_stats(self) -> Dict:
        """Calculate performance statistics for transparency."""
        if not self.closed_positions:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'total_pnl': 0,
                'return_pct': 0
            }
        
        wins = [p for p in self.closed_positions if p.pnl > 0]
        losses = [p for p in self.closed_positions if p.pnl <= 0]
        
        total_pnl = sum(p.pnl for p in self.closed_positions)
        
        return {
            'total_trades': len(self.closed_positions),
            'win_rate': len(wins) / len(self.closed_positions) * 100,
            'avg_win': sum(p.pnl_percent for p in wins) / len(wins) if wins else 0,
            'avg_loss': sum(p.pnl_percent for p in losses) / len(losses) if losses else 0,
            'total_pnl': total_pnl,
            'return_pct': (self.current_capital - self.starting_capital) / self.starting_capital * 100,
            'current_capital': self.current_capital,
            'open_positions': len(self.positions)
        }
    
    def generate_transparency_report(self) -> str:
        """Generate a report for public transparency."""
        stats = self.get_performance_stats()
        
        report = f"""
# Paper Trading Performance Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Overall Statistics
- Total Trades: {stats['total_trades']}
- Win Rate: {stats['win_rate']:.1f}%
- Average Win: +{stats['avg_win']:.2f}%
- Average Loss: {stats['avg_loss']:.2f}%
- Total P&L: ${stats['total_pnl']:,.2f}
- Return: {stats['return_pct']:+.2f}%
- Current Capital: ${stats['current_capital']:,.2f}

## Open Positions ({stats['open_positions']})
"""
        
        if self.positions:
            for p in self.positions:
                report += f"\n- {p.symbol}: {p.direction} @ ${p.entry_price:.2f} (SUE: {p.sue_score:.2f})"
        
        report += "\n\n## Recent Closed Trades\n"
        
        # Show last 10 trades
        for p in self.closed_positions[-10:]:
            emoji = "✅" if p.pnl > 0 else "❌"
            report += f"\n{emoji} {p.symbol}: {p.pnl_percent:+.2f}% ({p.entry_date} → {p.exit_date})"
        
        return report


# Example usage
if __name__ == "__main__":
    trader = PaperTrader()
    
    # Example: Enter a position based on SUE signal
    trader.enter_position(
        symbol="AAPL",
        current_price=175.50,
        sue_score=2.1,
        quintile=5,
        direction="LONG"
    )
    
    # Simulate price movement
    current_prices = {"AAPL": 178.20}  # Hit target
    trader.update_positions(current_prices)
    
    # Generate report
    print(trader.generate_transparency_report())