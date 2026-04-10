#!/usr/bin/env python3
"""Web-based dashboard for mobile access"""

from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime
from ib_insync import IB
import threading
import time
from config import IB_HOST, IB_PORT

app = Flask(__name__)
ib = IB()

# Global data cache
dashboard_data = {
    'account': {},
    'positions': [],
    'orders': [],
    'today_trades': [],
    'daily_pnl': 0,
    'last_update': None,
    'bot_status': 'Starting...',
    '4h_bias': 'Checking...'
}

def connect_ib():
    """Connect to IB Gateway"""
    try:
        if not ib.isConnected():
            ib.connect(IB_HOST, IB_PORT, clientId=3)
        return True
    except:
        return False

def update_data():
    """Update dashboard data"""
    while True:
        try:
            if connect_ib():
                # Account info
                for av in ib.accountValues():
                    if av.tag in ['NetLiquidation', 'TotalCashValue', 'BuyingPower']:
                        dashboard_data['account'][av.tag] = float(av.value)
                
                # Positions
                positions = []
                for pos in ib.positions():
                    if 'MGC' in pos.contract.localSymbol:
                        positions.append({
                            'symbol': pos.contract.localSymbol,
                            'quantity': pos.position,
                            'avgCost': pos.avgCost,
                            'marketValue': pos.marketValue,
                            'unrealizedPnl': pos.unrealizedPnL
                        })
                dashboard_data['positions'] = positions
                
                # Open orders
                orders = []
                for trade in ib.openTrades():
                    if 'MGC' in trade.contract.localSymbol:
                        orders.append({
                            'action': trade.order.action,
                            'quantity': trade.order.totalQuantity,
                            'type': trade.order.orderType,
                            'status': trade.orderStatus.status
                        })
                dashboard_data['orders'] = orders
                
                dashboard_data['last_update'] = datetime.now().strftime('%H:%M:%S')
                dashboard_data['bot_status'] = 'Connected'
            else:
                dashboard_data['bot_status'] = 'Disconnected'
                
        except Exception as e:
            dashboard_data['bot_status'] = f'Error: {str(e)}'
        
        time.sleep(5)  # Update every 5 seconds

@app.route('/')
def index():
    """Main dashboard page"""
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>MGC Trading Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 10px;
            background: #1a1a1a;
            color: #fff;
        }
        .header {
            background: #2a2a2a;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .metric-card {
            background: #2a2a2a;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
        }
        .metric-title {
            color: #888;
            font-size: 14px;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
        }
        .positive { color: #4CAF50; }
        .negative { color: #f44336; }
        .neutral { color: #FFC107; }
        .positions, .orders {
            background: #2a2a2a;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
        }
        .position-item, .order-item {
            padding: 10px;
            border-bottom: 1px solid #444;
        }
        .status-dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status-connected { background: #4CAF50; }
        .status-disconnected { background: #f44336; }
        .refresh-btn {
            background: #2196F3;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            width: 100%;
            font-size: 16px;
            margin-top: 20px;
        }
        .bias-indicator {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: bold;
            margin-left: 10px;
        }
        .bias-long { background: #4CAF50; }
        .bias-short { background: #f44336; }
        .bias-neutral { background: #FFC107; color: #000; }
    </style>
</head>
<body>
    <div class="header">
        <h1>MGC Trading Bot</h1>
        <div>
            <span class="status-dot" id="status-dot"></span>
            <span id="status-text">Loading...</span>
            <span id="last-update" style="margin-left: 20px; color: #888;"></span>
        </div>
    </div>
    
    <div class="metric-card">
        <div class="metric-title">4H Strategy Bias</div>
        <div id="bias" class="metric-value">Checking...</div>
    </div>
    
    <div class="metric-card">
        <div class="metric-title">Net Liquidation</div>
        <div id="net-liq" class="metric-value">$0.00</div>
    </div>
    
    <div class="metric-card">
        <div class="metric-title">Daily P&L</div>
        <div id="daily-pnl" class="metric-value">$0.00</div>
    </div>
    
    <div class="positions">
        <h3>Open Positions</h3>
        <div id="positions-list">No positions</div>
    </div>
    
    <div class="orders">
        <h3>Open Orders</h3>
        <div id="orders-list">No orders</div>
    </div>
    
    <button class="refresh-btn" onclick="refreshData()">Refresh Now</button>
    
    <script>
        function updateDashboard(data) {
            // Status
            const statusDot = document.getElementById('status-dot');
            const statusText = document.getElementById('status-text');
            if (data.bot_status === 'Connected') {
                statusDot.className = 'status-dot status-connected';
                statusText.textContent = 'Connected';
            } else {
                statusDot.className = 'status-dot status-disconnected';
                statusText.textContent = data.bot_status;
            }
            
            // Last update
            document.getElementById('last-update').textContent = 
                data.last_update ? 'Updated: ' + data.last_update : '';
            
            // 4H Bias
            const biasElement = document.getElementById('bias');
            const bias = data['4h_bias'];
            biasElement.innerHTML = bias;
            if (bias.includes('LONG')) {
                biasElement.innerHTML = '<span class="bias-indicator bias-long">LONG BIAS</span>';
            } else if (bias.includes('SHORT')) {
                biasElement.innerHTML = '<span class="bias-indicator bias-short">SHORT BIAS</span>';
            } else {
                biasElement.innerHTML = '<span class="bias-indicator bias-neutral">NEUTRAL</span>';
            }
            
            // Account values
            const netLiq = data.account.NetLiquidation || 0;
            document.getElementById('net-liq').textContent = '$' + netLiq.toLocaleString('en-US', {minimumFractionDigits: 2});
            
            // Daily P&L
            const dailyPnl = data.daily_pnl || 0;
            const pnlElement = document.getElementById('daily-pnl');
            pnlElement.textContent = '$' + dailyPnl.toLocaleString('en-US', {minimumFractionDigits: 2});
            pnlElement.className = 'metric-value ' + (dailyPnl >= 0 ? 'positive' : 'negative');
            
            // Positions
            const positionsDiv = document.getElementById('positions-list');
            if (data.positions.length > 0) {
                positionsDiv.innerHTML = data.positions.map(pos => 
                    `<div class="position-item">
                        ${pos.symbol}: ${pos.quantity > 0 ? 'LONG' : 'SHORT'} ${Math.abs(pos.quantity)} @ $${pos.avgCost}
                        <br><small>P&L: $${(pos.unrealizedPnl || 0).toFixed(2)}</small>
                    </div>`
                ).join('');
            } else {
                positionsDiv.innerHTML = 'No positions';
            }
            
            // Orders
            const ordersDiv = document.getElementById('orders-list');
            if (data.orders.length > 0) {
                ordersDiv.innerHTML = data.orders.map(order => 
                    `<div class="order-item">
                        ${order.action} ${order.quantity} ${order.type} - ${order.status}
                    </div>`
                ).join('');
            } else {
                ordersDiv.innerHTML = 'No open orders';
            }
        }
        
        function refreshData() {
            fetch('/api/dashboard')
                .then(response => response.json())
                .then(data => updateDashboard(data))
                .catch(error => console.error('Error:', error));
        }
        
        // Auto-refresh every 5 seconds
        setInterval(refreshData, 5000);
        
        // Initial load
        refreshData();
    </script>
</body>
</html>
    '''

@app.route('/api/dashboard')
def api_dashboard():
    """API endpoint for dashboard data"""
    return jsonify(dashboard_data)

def run_web_server():
    """Run the web server"""
    app.run(host='0.0.0.0', port=8080, debug=False)

if __name__ == '__main__':
    # Start data updater in background
    update_thread = threading.Thread(target=update_data, daemon=True)
    update_thread.start()
    
    print("\n" + "="*50)
    print("   MOBILE DASHBOARD STARTED")
    print("="*50)
    print("\nAccess from your phone:")
    print(f"  http://192.168.0.57:8080")
    print("\nOr from this computer:")
    print(f"  http://localhost:8080")
    print("="*50 + "\n")
    
    # Run web server
    run_web_server()