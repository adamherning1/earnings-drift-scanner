"""
Trade Logger - Records all trades with entry/exit details

Usage:
    from trade_logger import log_trade
    
    # Log a completed trade
    log_trade(
        symbol='MGC',
        entry_price=1850.50,
        exit_price=1855.25,
        contracts=3,
        entry_time='2026-04-05T09:30:00',
        exit_time='2026-04-05T10:15:00',
        strategy='Keltner Breakout',
        side='LONG'
    )
"""

import json
import os
from datetime import datetime

def log_trade(symbol, entry_price, exit_price, contracts, entry_time, exit_time, strategy='', side='LONG'):
    """Log a completed trade with all details
    
    Args:
        symbol (str): Contract symbol (e.g., 'MGC')
        entry_price (float): Entry price
        exit_price (float): Exit price
        contracts (int): Number of contracts
        entry_time (str/datetime): When position was entered
        exit_time (str/datetime): When position was exited
        strategy (str): Strategy name that triggered the trade
        side (str): 'LONG' or 'SHORT'
    """
    # Calculate profit
    if side == 'LONG':
        profit_per_contract = (exit_price - entry_price) * 10  # MGC = $10 per point
    else:
        profit_per_contract = (entry_price - exit_price) * 10
    
    total_profit = profit_per_contract * contracts
    
    # Create trade record
    trade = {
        'timestamp': datetime.now().isoformat(),
        'symbol': symbol,
        'entry_price': entry_price,
        'exit_price': exit_price,
        'contracts': contracts,
        'profit': total_profit,
        'entry_time': str(entry_time),
        'exit_time': str(exit_time),
        'strategy': strategy,
        'side': side,
        'duration_minutes': calculate_duration(entry_time, exit_time)
    }
    
    # Load existing log
    log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'trade_log.json')
    trades = []
    
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            trades = json.load(f)
    
    # Add new trade
    trades.append(trade)
    
    # Save updated log
    with open(log_file, 'w') as f:
        json.dump(trades, f, indent=2)
    
    # Also update the trading stats
    from update_trading_stats import update_trade_stats
    update_trade_stats(total_profit)
    
    print(f"Trade logged: {symbol} {side} - Entry: ${entry_price}, Exit: ${exit_price}")
    print(f"Profit: ${total_profit:+.2f} ({contracts} contracts)")
    
    return trade

def calculate_duration(entry_time, exit_time):
    """Calculate trade duration in minutes"""
    try:
        if isinstance(entry_time, str):
            entry_dt = datetime.fromisoformat(entry_time.replace('Z', '+00:00'))
        else:
            entry_dt = entry_time
            
        if isinstance(exit_time, str):
            exit_dt = datetime.fromisoformat(exit_time.replace('Z', '+00:00'))
        else:
            exit_dt = exit_time
            
        duration = (exit_dt - entry_dt).total_seconds() / 60
        return round(duration, 1)
    except:
        return 0

def get_recent_trades(count=20):
    """Get the most recent trades"""
    log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'trade_log.json')
    
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            trades = json.load(f)
            return trades[-count:]
    
    return []

if __name__ == "__main__":
    # Example usage
    print("Trade logger module")
    print("Example: log_trade('MGC', 1850.50, 1855.25, 3, '2026-04-05T09:30:00', '2026-04-05T10:15:00', 'Keltner', 'LONG')")