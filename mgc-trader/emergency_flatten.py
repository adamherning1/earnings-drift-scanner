"""Emergency flatten — cancel all orders and close all MGC positions."""
import asyncio
asyncio.set_event_loop(asyncio.new_event_loop())

from ib_insync import IB, Future, MarketOrder

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=99)

# Cancel ALL open orders
for trade in ib.openTrades():
    ib.cancelOrder(trade.order)
    print(f'Cancelled order {trade.order.orderId}: {trade.order.action} {trade.order.totalQuantity}')

ib.sleep(2)

# Flatten all MGC positions
for pos in ib.positions():
    if pos.contract.symbol == 'MGC' and pos.position != 0:
        action = 'SELL' if pos.position > 0 else 'BUY'
        qty = abs(pos.position)
        contract = Future(conId=706903676, symbol='MGC', exchange='COMEX',
                         currency='USD', lastTradeDateOrContractMonth='20260428',
                         multiplier='10')
        order = MarketOrder(action=action, totalQuantity=qty)
        trade = ib.placeOrder(contract, order)
        print(f'Flattening: {action} {qty} contracts')
        ib.sleep(5)
        print(f'Status: {trade.orderStatus.status}, avg fill: {trade.orderStatus.avgFillPrice}')

ib.sleep(2)

# Verify
flat = True
for pos in ib.positions():
    if pos.contract.symbol == 'MGC' and pos.position != 0:
        print(f'WARNING: Still have position: {pos.position}')
        flat = False

if flat:
    print('✅ All positions flat, all orders cancelled')

ib.disconnect()
