"""
Trading Stats Updater - Call this after each trade completes

Usage:
    from update_trading_stats import update_trade_stats
    
    # After a winning trade:
    update_trade_stats(profit_amount=250.00)
    
    # After a losing trade:
    update_trade_stats(profit_amount=-125.00)
"""

import json
import os

def update_trade_stats(profit_amount):
    """Update trading statistics after a trade completes
    
    Args:
        profit_amount (float): Positive for wins, negative for losses
    """
    # Load existing stats
    stats = {
        "winning_trades": 0,
        "losing_trades": 0,
        "total_profit": 0,
        "total_loss": 0,
        "profit_factor": 0
    }
    
    stats_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'trading_stats.json')
    
    if os.path.exists(stats_file):
        with open(stats_file, 'r') as f:
            stats = json.load(f)
    
    # Update stats based on trade result
    if profit_amount > 0:
        stats['winning_trades'] += 1
        stats['total_profit'] += profit_amount
    else:
        stats['losing_trades'] += 1
        stats['total_loss'] += abs(profit_amount)
    
    # Calculate profit factor
    if stats['total_loss'] > 0:
        stats['profit_factor'] = stats['total_profit'] / stats['total_loss']
    else:
        stats['profit_factor'] = stats['total_profit'] if stats['total_profit'] > 0 else 0
    
    # Save updated stats
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    # Print summary
    total_trades = stats['winning_trades'] + stats['losing_trades']
    win_rate = (stats['winning_trades'] / total_trades * 100) if total_trades > 0 else 0
    
    print(f"Trade recorded: ${profit_amount:+.2f}")
    print(f"Total trades: {total_trades} (W: {stats['winning_trades']}, L: {stats['losing_trades']})")
    print(f"Win rate: {win_rate:.1f}%")
    print(f"Profit factor: {stats['profit_factor']:.2f}")
    
    return stats

if __name__ == "__main__":
    # Example usage
    print("This module should be imported by the trading bot")
    print("Example: update_trade_stats(250.00) for a $250 winning trade")