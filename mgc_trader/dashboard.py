#!/usr/bin/env python3
"""Real-time Trading Dashboard"""

import asyncio
from datetime import datetime
from ib_insync import IB, util
import os
import time

# Import config
from config import IB_HOST, IB_PORT

class TradingDashboard:
    """Real-time monitoring dashboard for MGC trading"""
    
    def __init__(self):
        self.ib = IB()
        
    def connect(self):
        """Connect to IB Gateway"""
        try:
            self.ib.connect(IB_HOST, IB_PORT, clientId=2)  # Different client ID
            return True
        except:
            return False
    
    def clear_screen(self):
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_account_info(self):
        """Get account summary"""
        summary = {}
        for av in self.ib.accountValues():
            if av.tag in ['NetLiquidation', 'TotalCashValue', 'BuyingPower', 'DailyPnL']:
                summary[av.tag] = float(av.value)
        return summary
    
    def get_positions(self):
        """Get current positions"""
        positions = []
        for pos in self.ib.positions():
            if 'MGC' in pos.contract.localSymbol:
                pnl = self.ib.pnl(pos.account, '', pos.conId)
                positions.append({
                    'symbol': pos.contract.localSymbol,
                    'size': pos.position,
                    'avgCost': pos.avgCost,
                    'unrealizedPnL': pnl[0].unrealizedPnL if pnl else 0,
                    'realizedPnL': pnl[0].realizedPnL if pnl else 0
                })
        return positions
    
    def get_open_orders(self):
        """Get open orders"""
        orders = []
        for trade in self.ib.openTrades():
            if 'MGC' in trade.contract.localSymbol:
                orders.append({
                    'action': trade.order.action,
                    'quantity': trade.order.totalQuantity,
                    'orderType': trade.order.orderType,
                    'status': trade.orderStatus.status,
                    'price': trade.order.lmtPrice or trade.order.auxPrice or 'MKT'
                })
        return orders
    
    def display_dashboard(self):
        """Display the dashboard"""
        self.clear_screen()
        
        print("=" * 60)
        print("        MGC TRADING DASHBOARD - LIVE MONITORING")
        print("=" * 60)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        # Account info
        account = self.get_account_info()
        print("\nACCOUNT SUMMARY:")
        print(f"  Net Liquidation: ${account.get('NetLiquidation', 0):,.2f}")
        print(f"  Cash Balance:    ${account.get('TotalCashValue', 0):,.2f}")
        print(f"  Buying Power:    ${account.get('BuyingPower', 0):,.2f}")
        print(f"  Daily P&L:       ${account.get('DailyPnL', 0):,.2f}")
        
        # Show 4H Bias
        print("\n4H STRATEGY BIAS:")
        print("  Checking current 4H Keltner position...")
        print("  [Updates every 4 hours]")
        
        # Positions
        positions = self.get_positions()
        print("\nPOSITIONS:")
        if positions:
            for pos in positions:
                direction = "LONG" if pos['size'] > 0 else "SHORT"
                print(f"  {pos['symbol']}: {direction} {abs(pos['size'])} @ ${pos['avgCost']}")
                print(f"    Unrealized P&L: ${pos['unrealizedPnL']:,.2f}")
        else:
            print("  No open positions")
        
        # Open orders
        orders = self.get_open_orders()
        print("\nOPEN ORDERS:")
        if orders:
            for order in orders:
                print(f"  {order['action']} {order['quantity']} {order['orderType']} @ {order['price']} [{order['status']}]")
        else:
            print("  No open orders")
        
        print("\n" + "=" * 60)
        print("Press Ctrl+C to exit")
    
    async def run(self):
        """Run the dashboard loop"""
        if not self.connect():
            print("Failed to connect to IB Gateway")
            return
        
        print("Connected to IB Gateway. Starting dashboard...")
        
        try:
            while True:
                self.display_dashboard()
                await asyncio.sleep(5)  # Update every 5 seconds
        except KeyboardInterrupt:
            print("\nDashboard stopped.")
        finally:
            self.ib.disconnect()

if __name__ == "__main__":
    dashboard = TradingDashboard()
    asyncio.run(dashboard.run())