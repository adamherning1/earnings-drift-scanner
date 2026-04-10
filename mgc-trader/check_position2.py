import asyncio, sys
asyncio.set_event_loop(asyncio.new_event_loop())
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
from ib_insync import IB
ib = IB()
try:
    ib.connect('127.0.0.1', 4002, clientId=99, timeout=10)
    print("CONNECTED")
    for pos in ib.positions():
        if pos.contract.symbol == 'MGC':
            print(f"POSITION: {pos.position} @ avg {pos.avgCost}")
    orders = [t for t in ib.openTrades() if t.contract.symbol == 'MGC']
    print(f"OPEN_ORDERS: {len(orders)}")
    for t in orders:
        print(f"  ORDER: {t.order.action} {t.order.totalQuantity} {t.order.orderType} stop={t.order.auxPrice} lmt={t.order.lmtPrice}")
    if not any(p.contract.symbol == 'MGC' and p.position != 0 for p in ib.positions()):
        print("NO_MGC_POSITION")
    ib.disconnect()
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
