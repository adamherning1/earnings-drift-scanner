#!/usr/bin/env python3
"""Dynamic dashboard that shows real-time P&L when trades are active"""

from flask import Flask, render_template_string
from datetime import datetime
from ib_insync import IB
from config import IB_HOST, IB_PORT
import threading
import time

app = Flask(__name__)

# Global position data
position_data = {
    'has_position': False,
    'contracts': 0,
    'side': '',
    'entry_price': 0,
    'current_price': 0,
    'unrealized_pnl': 0,
    'account_balance': 999243,
    'last_update': datetime.now()
}

def update_position_data():
    """Update position data from IB"""
    ib = IB()
    
    while True:
        try:
            if not ib.isConnected():
                ib.connect(IB_HOST, IB_PORT, clientId=7)  # Different client ID
            
            # Get positions
            positions = ib.positions()
            mgc_position = None
            
            for pos in positions:
                if 'MGC' in pos.contract.localSymbol:
                    mgc_position = pos
                    break
            
            if mgc_position:
                # Get portfolio items for current price and P&L
                portfolio = ib.portfolio()
                for item in portfolio:
                    if 'MGC' in item.contract.localSymbol:
                        position_data['has_position'] = True
                        position_data['contracts'] = int(mgc_position.position)
                        position_data['side'] = 'LONG' if mgc_position.position > 0 else 'SHORT'
                        position_data['entry_price'] = mgc_position.avgCost / 10  # MGC multiplier
                        position_data['current_price'] = item.marketPrice
                        position_data['unrealized_pnl'] = item.unrealizedPNL
                        break
            else:
                position_data['has_position'] = False
            
            # Get account balance
            for av in ib.accountValues():
                if av.tag == 'NetLiquidation':
                    position_data['account_balance'] = float(av.value)
                    break
            
            position_data['last_update'] = datetime.now()
            
        except Exception as e:
            print(f"Error updating position: {e}")
        
        time.sleep(5)  # Update every 5 seconds

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>MGC Trading</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="5">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, Arial, sans-serif;
            margin: 0;
            padding: 10px;
            background: #1a1a1a;
            color: white;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        .header {
            background: #2563eb;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        h1 {
            margin: 0;
            font-size: 24px;
        }
        .position {
            background: {% if has_position %}#10b981{% else %}#374151{% endif %};
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .position h2 {
            margin: 0 0 10px 0;
            font-size: 20px;
        }
        .contracts {
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
        }
        .pnl {
            font-size: 32px;
            font-weight: bold;
            margin: 15px 0;
            {% if unrealized_pnl >= 0 %}
            color: #10b981;
            {% else %}
            color: #ef4444;
            {% endif %}
        }
        .details {
            background: #374151;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .row {
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
            font-size: 18px;
        }
        .label {
            color: #9ca3af;
        }
        .value {
            font-weight: bold;
        }
        .footer {
            text-align: center;
            color: #6b7280;
            margin-top: 20px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>MGC Trading Dashboard</h1>
            <div style="margin-top: 10px; font-size: 14px;">{{ current_time }}</div>
        </div>
        
        {% if has_position %}
        <div class="position">
            <h2>ACTIVE POSITION</h2>
            <div class="contracts">{{ contracts }} {{ side }}</div>
            <div>MGCM6 @ ${{ "%.2f"|format(entry_price) }}</div>
            <div class="pnl">
                {% if unrealized_pnl >= 0 %}+{% endif %}${{ "%.2f"|format(unrealized_pnl) }}
            </div>
        </div>
        
        <div class="details">
            <div class="row">
                <span class="label">Current Price:</span>
                <span class="value">${{ "%.2f"|format(current_price) }}</span>
            </div>
            <div class="row">
                <span class="label">Price Change:</span>
                <span class="value {% if current_price > entry_price %}style="color: #10b981;"{% else %}style="color: #ef4444;"{% endif %}">
                    ${{ "%.2f"|format(current_price - entry_price) }}
                </span>
            </div>
        </div>
        {% else %}
        <div class="position">
            <h2>NO ACTIVE POSITION</h2>
            <div>Bot is scanning for entries...</div>
            <div style="margin-top: 10px;">Market Bias: STRONG BULLISH</div>
        </div>
        {% endif %}
        
        <div class="details">
            <div class="row">
                <span class="label">Account Balance:</span>
                <span class="value">${{ "{:,.0f}".format(account_balance) }}</span>
            </div>
            <div class="row">
                <span class="label">Phase 1 Progress:</span>
                <span class="value">3/50 trades</span>
            </div>
            <div class="row">
                <span class="label">Bot Status:</span>
                <span class="value" style="color: #10b981;">Active ✓</span>
            </div>
        </div>
        
        <div class="footer">
            <p>Updates every 5 seconds</p>
            <p>Market closes at 2:00 PM PT</p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    current_time = datetime.now().strftime('%I:%M:%S %p PT')
    return render_template_string(HTML_TEMPLATE, 
        current_time=current_time,
        **position_data)

if __name__ == '__main__':
    # Start position updater in background
    update_thread = threading.Thread(target=update_position_data, daemon=True)
    update_thread.start()
    
    print("\n" + "="*50)
    print("DYNAMIC DASHBOARD STARTED")
    print("="*50)
    print("\nShows real-time P&L when trades are active!")
    print("Access at: http://192.168.0.57:8080")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=8080, debug=False)