#!/usr/bin/env python3
"""
Quick fix to update dashboard with current position
"""

import json
from datetime import datetime
from ib_insync import IB
from config import IB_HOST, IB_PORT

def update_dashboard():
    """Update the dashboard status file with current position"""
    ib = IB()
    
    try:
        print("Connecting to IB Gateway...")
        ib.connect(IB_HOST, IB_PORT, clientId=5)  # Different client ID
        
        # Get account info
        account_values = {}
        for av in ib.accountValues():
            try:
                account_values[av.tag] = float(av.value)
            except:
                account_values[av.tag] = av.value
        net_liq = account_values.get('NetLiquidation', 0)
        
        # Get positions
        positions = ib.positions()
        mgc_position = None
        
        for pos in positions:
            if 'MGC' in pos.contract.localSymbol:
                mgc_position = pos
                break
        
        # Create dashboard data
        dashboard_data = {
            'account_balance': net_liq,
            'account_id': ib.managedAccounts()[0] if ib.managedAccounts() else 'DUP971200',
            'connection_status': 'CONNECTED',
            'last_update': datetime.now().strftime('%H:%M:%S')
        }
        
        if mgc_position:
            # Calculate entry price from average cost
            entry_price = mgc_position.avgCost / 10  # MGC multiplier is 10
            
            # Get current price
            contract = mgc_position.contract
            contract.exchange = 'COMEX'  # Set exchange
            ticker = ib.reqMktData(contract)
            ib.sleep(1)
            
            current_price = ticker.marketPrice() if ticker.marketPrice() > 0 else ticker.last
            
            dashboard_data['open_position'] = {
                'symbol': 'MGCM6',
                'contracts': int(mgc_position.position),
                'side': 'LONG' if mgc_position.position > 0 else 'SHORT',
                'entry_price': f"${entry_price:.2f}",
                'current_price': f"${current_price:.2f}",
                'unrealized_pnl': f"${getattr(mgc_position, 'unrealizedPnL', 0):.2f}"
            }
            
            print(f"\nPosition Found:")
            print(f"Symbol: MGCM6")
            print(f"Contracts: {int(mgc_position.position)}")
            print(f"Entry: ${entry_price:.2f}")
            print(f"Current: ${current_price:.2f}")
            print(f"Unrealized P&L: ${getattr(mgc_position, 'unrealizedPnL', 0):.2f}")
        else:
            dashboard_data['open_position'] = None
            print("No MGC position found")
        
        # Write to status file for dashboard
        with open('data/dashboard_status.json', 'w') as f:
            json.dump(dashboard_data, f, indent=2)
        
        print(f"\nDashboard updated at {dashboard_data['last_update']}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if ib.isConnected():
            ib.disconnect()

if __name__ == "__main__":
    update_dashboard()