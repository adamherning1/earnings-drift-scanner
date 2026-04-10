#!/usr/bin/env python3
"""Ultra-simple mobile dashboard server"""

from flask import Flask, render_template_string
from datetime import datetime

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>MGC Trading</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
            background: #10b981;
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
        .stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 20px;
        }
        .stat-card {
            background: #374151;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #60a5fa;
        }
        .stat-label {
            font-size: 12px;
            color: #9ca3af;
            margin-top: 5px;
        }
        .footer {
            text-align: center;
            color: #6b7280;
            margin-top: 20px;
            font-size: 14px;
        }
    </style>
    <meta http-equiv="refresh" content="30">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>MGC Trading Dashboard</h1>
            <div style="margin-top: 10px; font-size: 14px;">{{ current_time }}</div>
        </div>
        
        <div class="position">
            <h2>ACTIVE POSITION</h2>
            <div class="contracts">2 LONG</div>
            <div>MGCM6 (June 2026 Gold)</div>
        </div>
        
        <div class="details">
            <div class="row">
                <span class="label">Entry Price:</span>
                <span class="value">$4,686.50</span>
            </div>
            <div class="row">
                <span class="label">Entry Time:</span>
                <span class="value">9:28 AM PT</span>
            </div>
            <div class="row">
                <span class="label">Stop Loss:</span>
                <span class="value">Active ✓</span>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">$997,687</div>
                <div class="stat-label">ACCOUNT BALANCE</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">Phase 1</div>
                <div class="stat-label">LEARNING PHASE</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">2/50</div>
                <div class="stat-label">TRADES PROGRESS</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">Active</div>
                <div class="stat-label">BOT STATUS</div>
            </div>
        </div>
        
        <div class="footer">
            <p>Bot running with auto-reconnect</p>
            <p>Trading until 5:00 PM ET daily</p>
            <p>Refreshes every 30 seconds</p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    current_time = datetime.now().strftime('%I:%M:%S %p PT')
    return render_template_string(HTML_TEMPLATE, current_time=current_time)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("MOBILE DASHBOARD STARTED")
    print("="*50)
    print("\nAccess from your phone at:")
    print("http://192.168.0.57:8080")
    print("\nOr via Cloudflare tunnel:")
    print("https://globe-interview-sympathy-probably.trycloudflare.com")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=8080, debug=False)