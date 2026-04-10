#!/usr/bin/env python3
"""
Record the current open trade in the database with correct schema
"""

import sqlite3
from datetime import datetime

# Trade details from the logs
trade_data = {
    'timestamp': '2026-04-07 09:28:00',
    'symbol': 'MGCM6',
    'direction': 'LONG',
    'entry_price': 4686.50,
    'exit_price': None,  # Still open
    'quantity': 2,
    'pnl': None,  # Not yet realized
    'pnl_percent': None,
    'stop_loss': None,  # Managed by bot
    'take_profit': None,  # Managed by bot
    'entry_reason': 'Adaptive Bot Signal',
    'exit_reason': None,
    'market_conditions': 'NEUTRAL/RANGE',
    'ai_score': None,
    'duration_minutes': None
}

try:
    # Connect to database
    conn = sqlite3.connect('data/trades.db')
    cursor = conn.cursor()
    
    # Insert the open trade
    cursor.execute('''
        INSERT INTO trades (
            timestamp, symbol, direction, entry_price, exit_price, 
            quantity, pnl, pnl_percent, stop_loss, take_profit, 
            entry_reason, exit_reason, market_conditions, ai_score, duration_minutes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        trade_data['timestamp'], trade_data['symbol'], trade_data['direction'],
        trade_data['entry_price'], trade_data['exit_price'], trade_data['quantity'],
        trade_data['pnl'], trade_data['pnl_percent'], trade_data['stop_loss'],
        trade_data['take_profit'], trade_data['entry_reason'], trade_data['exit_reason'],
        trade_data['market_conditions'], trade_data['ai_score'], trade_data['duration_minutes']
    ))
    
    conn.commit()
    print(f"✓ Recorded open trade: {trade_data['quantity']} {trade_data['direction']} @ ${trade_data['entry_price']}")
    print(f"  Symbol: {trade_data['symbol']}")
    print(f"  Entry Time: {trade_data['timestamp']}")
    
    # Verify it was inserted
    cursor.execute("SELECT COUNT(*) FROM trades WHERE exit_price IS NULL")
    open_trades = cursor.fetchone()[0]
    print(f"\n✓ Database now shows {open_trades} open trade(s)")
    
    conn.close()
    
except Exception as e:
    print(f"Error recording trade: {e}")

print("\nThe dashboard at https://globe-interview-sympathy-probably.trycloudflare.com should now show:")
print("- 2 LONG contracts")
print("- Entry: $4,686.50")
print("- Entry time: 9:28 AM PT")