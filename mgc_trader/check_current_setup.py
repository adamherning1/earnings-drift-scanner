from ib_insync import *
import pandas as pd
from datetime import datetime

# Connect
ib = IB()
ib.connect('192.168.0.58', 4002, clientId=101)

# Get contract
contract = Future('MGC', '20260626', 'COMEX')
ib.qualifyContracts(contract)

# Request market data
ib.reqMarketDataType(3)
ticker = ib.reqMktData(contract)
ib.sleep(2)

print(f"Current MGC Price: ${ticker.marketPrice()}")
print(f"Bid: ${ticker.bid} | Ask: ${ticker.ask}")
print("=" * 60)

# Get 5M bars
bars = ib.reqHistoricalData(
    contract, '', '1 D', '5 mins', 'TRADES', True
)

df = util.df(bars)
df['ema9'] = df['close'].ewm(span=9).mean()
df['ema20'] = df['close'].ewm(span=20).mean()

# Calculate RSI
delta = df['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
rs = gain / loss
df['rsi'] = 100 - (100 / (1 + rs))

# Recent bars
print("Last 5 bars (5-minute):")
print("-" * 60)
for i in range(-5, 0):
    row = df.iloc[i]
    print(f"{row.name.strftime('%H:%M')} | "
          f"O:{row['open']:.2f} H:{row['high']:.2f} L:{row['low']:.2f} C:{row['close']:.2f} | "
          f"EMA9:{row['ema9']:.2f} | RSI:{row['rsi']:.1f}")

print("-" * 60)
last = df.iloc[-1]
print(f"\nCurrent Setup:")
print(f"Price: ${last['close']:.2f}")
print(f"EMA9: ${last['ema9']:.2f} ({'+' if last['close'] > last['ema9'] else '-'}{abs(last['close'] - last['ema9']):.2f})")
print(f"EMA20: ${last['ema20']:.2f} ({'+' if last['close'] > last['ema20'] else '-'}{abs(last['close'] - last['ema20']):.2f})")
print(f"RSI: {last['rsi']:.1f}")
print(f"5-bar High: ${df['high'].iloc[-5:].max():.2f}")
print(f"5-bar Low: ${df['low'].iloc[-5:].min():.2f}")

ib.disconnect()