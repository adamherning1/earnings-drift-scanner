import asyncio, sys
asyncio.set_event_loop(asyncio.new_event_loop())
sys.stdout.reconfigure(encoding='utf-8')
from ib_insync import IB
ib = IB()
ib.connect('127.0.0.1', 4002, clientId=99, timeout=10)
for item in ib.accountSummary():
    if item.tag in ('NetLiquidation', 'TotalCashValue', 'UnrealizedPnL', 'RealizedPnL'):
        print(f"{item.tag}: {item.value} {item.currency}")
ib.disconnect()
