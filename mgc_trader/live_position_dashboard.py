#!/usr/bin/env python3
"""Simple live dashboard showing current position"""

from flask import Flask, render_template_string
from datetime import datetime
import re

app = Flask(__name__)

def get_latest_position():
    """Read the latest position from log file"""
    try:
        with open('adaptive_bot.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()[-200:]  # Last 200 lines
        
        # Find latest portfolio update
        position_data = {
            'has_position': False,
            'contracts': 0,
            'side': '',
            'entry_price': 0,
            'current_price': 0,
            'unrealized_pnl': 0,
            'realized_pnl': 0
        }
        
        for line in reversed(lines):
            if 'updatePortfolio' in line and 'MGCM6' in line:
                # Extract position info
                match = re.search(r'position=([\d.]+)', line)
                if match:
                    position_data['contracts'] = int(float(match.group(1)))
                    position_data['has_position'] = position_data['contracts'] > 0
                    position_data['side'] = 'LONG' if position_data['contracts'] > 0 else 'SHORT'
                
                # Extract prices
                match = re.search(r'marketPrice=([\d.]+)', line)
                if match:
                    position_data['current_price'] = float(match.group(1))
                
                match = re.search(r'averageCost=([\d.]+)', line)
                if match:
                    position_data['entry_price'] = float(match.group(1)) / 10  # MGC multiplier
                
                # Extract P&L
                match = re.search(r'unrealizedPNL=([-\d.]+)', line)
                if match:
                    position_data['unrealized_pnl'] = float(match.group(1))
                
                match = re.search(r'realizedPNL=([-\d.]+)', line)
                if match:
                    position_data['realized_pnl'] = float(match.group(1))
                
                break
        
        # Find entry time
        for line in lines:
            if 'Placed LONG order' in line or 'Placed SHORT order' in line:
                match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                if match:
                    position_data['entry_time'] = match.group(1)
        
        return position_data
    except Exception as e:
        print(f"Error reading position: {e}")
        return None

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>MGC Live Position</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="5">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, Arial, sans-serif;
            margin: 0;
            padding: 15px;
            background: #0a0a0a;
            color: white;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #1e40af, #3730a3);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        h1 {
            margin: 0;
            font-size: 28px;
        }
        .position-card {
            background: linear-gradient(135deg, #065f46, #047857);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .no-position {
            background: #374151;
        }
        .position-size {
            font-size: 42px;
            font-weight: bold;
            margin: 15px 0;
        }
        .entry-info {
            font-size: 22px;
            margin: 10px 0;
            color: #d1fae5;
        }
        .pnl-display {
            font-size: 48px;
            font-weight: bold;
            margin: 20px 0;
        }
        .profit {
            color: #4ade80;
        }
        .loss {
            color: #ef4444;
        }
        .details {
            background: rgba(0,0,0,0.3);
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .detail-row {
            display: flex;
            justify-content: space-between;
            margin: 12px 0;
            font-size: 18px;
        }
        .label {
            color: #9ca3af;
        }
        .value {
            font-weight: bold;
        }
        .update-time {
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
            <h1>MGC Trading - Live Position</h1>
            <div style="margin-top: 10px; font-size: 16px;">{{ current_time }}</div>
        </div>
        
        {% if position and position.has_position %}
        <div class="position-card">
            <div class="position-size">
                {{ position.contracts }} {{ position.side }}
            </div>
            <div class="entry-info">
                Entry: ${{ "%.2f"|format(position.entry_price) }}
            </div>
            <div class="pnl-display {% if position.unrealized_pnl >= 0 %}profit{% else %}loss{% endif %}">
                {% if position.unrealized_pnl >= 0 %}+{% endif %}${{ "%.2f"|format(position.unrealized_pnl) }}
            </div>
            
            <div class="details">
                <div class="detail-row">
                    <span class="label">Current Price:</span>
                    <span class="value">${{ "%.2f"|format(position.current_price) }}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Move from Entry:</span>
                    <span class="value {% if position.current_price > position.entry_price %}profit{% else %}loss{% endif %}">
                        ${{ "%.2f"|format(position.current_price - position.entry_price) }}
                    </span>
                </div>
                <div class="detail-row">
                    <span class="label">Per Contract:</span>
                    <span class="value">
                        ${{ "%.2f"|format(position.unrealized_pnl / position.contracts if position.contracts > 0 else 0) }}
                    </span>
                </div>
                {% if position.realized_pnl != 0 %}
                <div class="detail-row">
                    <span class="label">Realized P&L:</span>
                    <span class="value {% if position.realized_pnl >= 0 %}profit{% else %}loss{% endif %}">
                        ${{ "%.2f"|format(position.realized_pnl) }}
                    </span>
                </div>
                {% endif %}
            </div>
        </div>
        {% else %}
        <div class="position-card no-position">
            <h2>No Active Position</h2>
            <p style="font-size: 18px;">Bot is scanning for entries...</p>
            <p style="margin-top: 15px;">Market Bias: STRONG BULLISH (5/5)</p>
        </div>
        {% endif %}
        
        <div class="update-time">
            <p>Updates every 5 seconds</p>
            <p>Dashboard: http://192.168.0.57:8080</p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    position = get_latest_position()
    current_time = datetime.now().strftime('%I:%M:%S %p PT')
    return render_template_string(HTML_TEMPLATE, 
        position=position,
        current_time=current_time)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("LIVE POSITION DASHBOARD")
    print("="*50)
    print("\nReading position data from bot logs")
    print("Access at: http://192.168.0.57:8080")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=8080, debug=False)