#!/usr/bin/env python3
"""
Record the current open trade in the database
"""

import sqlite3
from datetime import datetime

# Trade details from the logs
trade_data = {
    'date': '2026-04-07 09:28:00',
    'symbol': 'MGCM6',
    'entry_price': 4686.50,
    'exit_price': None,  # Still open
    'quantity': 2,
    'pnl': None,  # Not yet realized
    'strategy': 'Adaptive Bot',
    'entry_time': '09:28:00',
    'exit_time': None
}

try:
    # Connect to database
    conn = sqlite3.connect('data/trades.db')
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            symbol TEXT,
            entry_price REAL,
            exit_price REAL,
            quantity INTEGER,
            pnl REAL,
            strategy TEXT,
            entry_time TEXT,
            exit_time TEXT
        )
    ''')
    
    # Insert the open trade
    cursor.execute('''
        INSERT INTO trades (date, symbol, entry_price, exit_price, quantity, pnl, strategy, entry_time, exit_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (trade_data['date'], trade_data['symbol'], trade_data['entry_price'], 
          trade_data['exit_price'], trade_data['quantity'], trade_data['pnl'],
          trade_data['strategy'], trade_data['entry_time'], trade_data['exit_time']))
    
    conn.commit()
    print(f"✓ Recorded open trade: {trade_data['quantity']} contracts @ ${trade_data['entry_price']}")
    
    conn.close()
    
except Exception as e:
    print(f"Error recording trade: {e}")

print("\nDashboard should now show the open position!")