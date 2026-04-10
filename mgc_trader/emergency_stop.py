from ib_insync import *
import math

# Connect to IB
ib = IB()
ib.connect('192.168.0.58', 4002, clientId=102)

# Get contract
contract = Future('MGC', '20260626', 'COMEX')
ib.qualifyContracts(contract)

# Get current positions
positions = ib.positions()
mgc_position = None
for pos in positions:
    if pos.contract.localSymbol == 'MGCM6':
        mgc_position = pos
        print(f"Found position: {pos.position} contracts @ avg cost ${pos.avgCost/10:.2f}")
        break

if mgc_position and mgc_position.position < 0:  # Short position
    # Calculate stop loss (round UP to nearest 10 cents for shorts)
    # Original plan was $4682.47, let's round to $4682.50
    stop_price = 4682.50
    
    # Place stop order
    stop_order = StopOrder(
        action='BUY',  # Buy to cover short
        totalQuantity=abs(mgc_position.position),
        stopPrice=stop_price
    )
    
    trade = ib.placeOrder(contract, stop_order)
    print(f"\nPlaced STOP order at ${stop_price:.2f}")
    print(f"Risk per contract: ${(stop_price - 4673.90) * 10:.2f}")
    print(f"Total risk: ${(stop_price - 4673.90) * 10 * abs(mgc_position.position):.2f}")
    
    ib.sleep(2)
    print(f"\nOrder status: {trade.orderStatus.status}")
    
    if trade.orderStatus.status in ['PreSubmitted', 'Submitted']:
        print("✅ Stop loss successfully placed!")
    else:
        print(f"⚠️ Order issue: {trade.orderStatus}")
else:
    print("No short position found!")

ib.disconnect()