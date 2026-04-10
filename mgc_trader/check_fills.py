from ib_insync import *
from datetime import datetime

ib = IB()
ib.connect('192.168.0.58', 4002, clientId=105)

fills = ib.fills()
print(f"Total fills today: {len(fills)}\n")

# Group by time to see trades
trades = []
current_trade = []

for fill in fills:
    print(f"{fill.time}: {fill.execution.side} {fill.execution.shares} @ ${fill.execution.price:.2f}")
    print(f"  Commission: ${fill.commissionReport.commission:.2f}")
    
    if fill.execution.side == 'SLD':
        current_trade.append(fill)
    elif fill.execution.side == 'BOT' and current_trade:
        current_trade.append(fill)
        trades.append(current_trade)
        current_trade = []

print("\n" + "="*60)
print("TRADE SUMMARY:")
print("="*60)

# Calculate P&L for the complete trade
if trades:
    for i, trade in enumerate(trades):
        # Get entry and exit info
        entries = [f for f in trade if f.execution.side == 'SLD']
        exits = [f for f in trade if f.execution.side == 'BOT']
        
        if entries and exits:
            # Calculate average prices
            entry_qty = sum(f.execution.shares for f in entries)
            entry_total = sum(f.execution.shares * f.execution.price for f in entries)
            entry_avg = entry_total / entry_qty
            
            exit_qty = sum(f.execution.shares for f in exits)
            exit_total = sum(f.execution.shares * f.execution.price for f in exits)
            exit_avg = exit_total / exit_qty
            
            # P&L calculation (SHORT trade)
            gross_pnl = (entry_avg - exit_avg) * exit_qty * 10  # MGC multiplier is 10
            commissions = sum(f.commissionReport.commission for f in trade)
            net_pnl = gross_pnl - commissions
            
            print(f"\nTrade #{i+1}:")
            print(f"  Entry: SHORT {entry_qty} @ ${entry_avg:.2f}")
            print(f"  Exit:  COVER {exit_qty} @ ${exit_avg:.2f}")
            print(f"  Price difference: ${exit_avg - entry_avg:.2f}")
            print(f"  Gross P&L: ${gross_pnl:,.2f}")
            print(f"  Commissions: ${commissions:.2f}")
            print(f"  Net P&L: ${net_pnl:,.2f}")

# Get account status
print("\n" + "="*60)
print("ACCOUNT STATUS:")
print("="*60)
for av in ib.accountValues():
    if av.tag in ['NetLiquidation', 'DailyPnL', 'RealizedPnL']:
        print(f"{av.tag}: ${float(av.value):,.2f}")

ib.disconnect()