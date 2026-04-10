import asyncio
asyncio.set_event_loop(asyncio.new_event_loop())
from ib_insync import IB

ib = IB()
try:
    ib.connect('127.0.0.1', 4002, clientId=99)
    print("Connected to IB Gateway")
    for pos in ib.positions():
        if pos.contract.symbol == 'MGC':
            print(f"Position: {pos.position} contracts, avg cost: {pos.avgCost}")
    orders = [t for t in ib.openTrades() if t.contract.symbol == 'MGC']
    print(f"Open MGC orders: {len(orders)}")
    for t in orders:
        print(f"  {t.order.action} {t.order.totalQuantity} {t.order.orderType} @ {t.order.auxPrice or t.order.lmtPrice}")
    ib.disconnect()
except Exception as e:
    print(f"Cannot connect: {e}")
