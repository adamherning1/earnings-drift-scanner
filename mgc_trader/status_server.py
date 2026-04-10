#!/usr/bin/env python3
"""Status server for the Cloudflare dashboard"""

from flask import Flask, jsonify
import json
import sqlite3
from datetime import datetime
from ib_insync import IB
import threading
import time
from config import IB_HOST, IB_PORT

app = Flask(__name__)

# Global status data
status_data = {
    'account_balance': 0,
    'account_id': '',
    'total_pnl': 0,
    'daily_pnl': 0,
    'active_pnl': 0,
    'open_positions': 0,
    'win_rate': 0,
    'total_trades': 0,
    'wins': 0,
    'losses': 0,
    'profit_factor': 0,
    'avg_win': 0,
    'avg_loss': 0,
    'trades': [],
    'last_update': 'Never',
    'connection_status': 'DISCONNECTED'
}

def get_trade_history():
    """Get trade history from database"""
    try:
        conn = sqlite3.connect('data/trades.db')
        cursor = conn.cursor()
        
        # Get today's trades
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT date, symbol, entry_price, exit_price, quantity, pnl
            FROM trades 
            WHERE date >= ?
            ORDER BY date DESC
            LIMIT 20
        ''', (today,))
        
        trades = []
        for row in cursor.fetchall():
            trades.append({
                'date': row[0],
                'symbol': row[1],
                'entry': f"${row[2]:.2f}" if row[2] else "N/A",
                'exit': f"${row[3]:.2f}" if row[3] else "OPEN",
                'contracts': row[4],
                'pnl': f"${row[5]:.2f}" if row[5] else "0.00"
            })
        
        conn.close()
        return trades
    except:
        return []

def update_status():
    """Update status from IB connection"""
    ib = IB()
    
    while True:
        try:
            if not ib.isConnected():
                ib.connect(IB_HOST, IB_PORT, clientId=4)  # Different client ID
                
            if ib.isConnected():
                status_data['connection_status'] = 'CONNECTED'
                
                # Account info
                account_values = {av.tag: float(av.value) for av in ib.accountValues()}
                status_data['account_balance'] = account_values.get('NetLiquidation', 0)
                status_data['account_id'] = ib.managedAccounts()[0] if ib.managedAccounts() else 'Unknown'
                
                # Daily P&L (would need to track from market open)
                status_data['daily_pnl'] = account_values.get('DailyPnL', 0)
                
                # Positions
                positions = ib.positions()
                mgc_positions = [p for p in positions if 'MGC' in p.contract.localSymbol]
                status_data['open_positions'] = len(mgc_positions)
                
                # Active P&L from open positions
                active_pnl = sum(p.unrealizedPnL for p in mgc_positions)
                status_data['active_pnl'] = active_pnl
                
                # Trade stats from database
                trades = get_trade_history()
                status_data['trades'] = trades
                
                if trades:
                    # Calculate win rate and other stats
                    pnl_values = []
                    for t in trades:
                        try:
                            pnl_str = t['pnl'].replace('$', '').replace(',', '')
                            if pnl_str and pnl_str != '0.00':
                                pnl_values.append(float(pnl_str))
                        except:
                            pass
                    
                    if pnl_values:
                        wins = [p for p in pnl_values if p > 0]
                        losses = [p for p in pnl_values if p < 0]
                        
                        status_data['total_trades'] = len(pnl_values)
                        status_data['wins'] = len(wins)
                        status_data['losses'] = len(losses)
                        status_data['win_rate'] = (len(wins) / len(pnl_values) * 100) if pnl_values else 0
                        
                        total_wins = sum(wins)
                        total_losses = abs(sum(losses))
                        status_data['profit_factor'] = (total_wins / total_losses) if total_losses > 0 else 0
                        status_data['avg_win'] = (total_wins / len(wins)) if wins else 0
                        status_data['avg_loss'] = (total_losses / len(losses)) if losses else 0
                        status_data['total_pnl'] = sum(pnl_values)
                
                status_data['last_update'] = datetime.now().strftime('%H:%M:%S')
            else:
                status_data['connection_status'] = 'DISCONNECTED'
                
        except Exception as e:
            print(f"Error updating status: {e}")
            status_data['connection_status'] = f'ERROR: {str(e)}'
        
        time.sleep(5)  # Update every 5 seconds

@app.route('/')
def index():
    """Status page HTML"""
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>MGC Trading Dashboard</title>
        <meta http-equiv="refresh" content="5">
        <style>
            body {{ font-family: Arial; background: #1a1a1a; color: white; padding: 20px; }}
            .status {{ font-size: 24px; font-weight: bold; }}
            .connected {{ color: #4CAF50; }}
            .disconnected {{ color: #f44336; }}
            .metric {{ background: #333; padding: 15px; margin: 10px 0; border-radius: 5px; }}
            .positive {{ color: #4CAF50; }}
            .negative {{ color: #f44336; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #555; }}
        </style>
    </head>
    <body>
        <h1 class="status {"connected" if status_data["connection_status"] == "CONNECTED" else "disconnected"}">
            {status_data["connection_status"]}
        </h1>
        
        <div class="metric">
            <h2>Account Balance</h2>
            <div style="font-size: 32px;">${status_data["account_balance"]:,.2f}</div>
            <div style="color: #888;">Account: {status_data["account_id"]}</div>
        </div>
        
        <div class="metric">
            <h2>Total P&L (All Time)</h2>
            <div style="font-size: 24px;" class="{"positive" if status_data["total_pnl"] >= 0 else "negative"}">
                ${status_data["total_pnl"]:,.2f}
            </div>
        </div>
        
        <div class="metric">
            <h2>Daily P&L</h2>
            <div style="font-size: 24px;" class="{"positive" if status_data["daily_pnl"] >= 0 else "negative"}">
                ${status_data["daily_pnl"]:,.2f}
            </div>
        </div>
        
        <div class="metric">
            <h2>Active P&L</h2>
            <div style="font-size: 24px;" class="{"positive" if status_data["active_pnl"] >= 0 else "negative"}">
                ${status_data["active_pnl"]:,.2f}
            </div>
            <div style="color: #888;">Open Positions: {status_data["open_positions"]}</div>
        </div>
        
        <div class="metric">
            <h2>Win Rate</h2>
            <div style="font-size: 24px;">{status_data["win_rate"]:.1f}%</div>
            <div style="color: #888;">
                Total Trades: {status_data["total_trades"]} | 
                Wins/Losses: {status_data["wins"]} / {status_data["losses"]}
            </div>
        </div>
        
        <div class="metric">
            <h2>Profit Factor</h2>
            <div style="font-size: 24px;">{status_data["profit_factor"]:.2f}</div>
            <div style="color: #888;">
                Win $ / Loss $
            </div>
        </div>
        
        <h2>Trade Log</h2>
        <table>
            <tr>
                <th>Date</th>
                <th>Symbol</th>
                <th>Entry</th>
                <th>Exit</th>
                <th>Contracts</th>
                <th>P&L</th>
            </tr>
            {"".join(f'''<tr>
                <td>{t["date"]}</td>
                <td>{t["symbol"]}</td>
                <td>{t["entry"]}</td>
                <td>{t["exit"]}</td>
                <td>{t["contracts"]}</td>
                <td class="{"positive" if float(t["pnl"].replace("$","").replace(",","")) > 0 else "negative"}">{t["pnl"]}</td>
            </tr>''' for t in status_data["trades"])}
        </table>
        
        <div style="margin-top: 20px; color: #888;">
            Last Update: {status_data["last_update"]}
        </div>
    </body>
    </html>
    '''
    return html

@app.route('/api/status')
def api_status():
    """API endpoint for status data"""
    return jsonify(status_data)

if __name__ == '__main__':
    # Start status updater in background
    update_thread = threading.Thread(target=update_status, daemon=True)
    update_thread.start()
    
    print("\n" + "="*50)
    print("   STATUS SERVER STARTED")
    print("="*50)
    print("\nServing on port 5001")
    print("="*50 + "\n")
    
    # Run on port 5001
    app.run(host='0.0.0.0', port=5001, debug=False)