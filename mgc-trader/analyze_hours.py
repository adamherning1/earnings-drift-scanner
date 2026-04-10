"""Analyze MGC trading hours to determine if overnight is worth trading."""
import asyncio; asyncio.set_event_loop(asyncio.new_event_loop())
from ib_insync import IB, Future
import pandas as pd
import numpy as np

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=94, timeout=15)

mgc = Future('MGC', '20260428', exchange='COMEX')
ib.qualifyContracts(mgc)

bars = ib.reqHistoricalData(mgc, endDateTime='', durationStr='7 D',
                            barSizeSetting='5 mins', whatToShow='TRADES',
                            useRTH=False, formatDate=1)
print(f'Got {len(bars)} bars over 7 days')

data = [{'date': b.date, 'o': b.open, 'h': b.high, 'l': b.low, 'c': b.close, 'v': b.volume} for b in bars]
df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])

if df['date'].dt.tz is not None:
    df['date_et'] = df['date'].dt.tz_convert('America/New_York')
else:
    df['date_et'] = df['date'].dt.tz_localize('UTC').dt.tz_convert('America/New_York')

df['hour_et'] = df['date_et'].dt.hour
df['range'] = df['h'] - df['l']
df['body'] = abs(df['c'] - df['o'])
df['move'] = df['c'] - df['o']
df['direction'] = np.where(df['c'] > df['o'], 1, np.where(df['c'] < df['o'], -1, 0))

# EMA cross signal simulation per session
def simulate_ema_cross(sdf):
    """Simple EMA 9/21 cross momentum - count profitable signals."""
    if len(sdf) < 25:
        return 0, 0, 0
    close = sdf['c'].values
    ema9 = pd.Series(close).ewm(span=9, adjust=False).mean().values
    ema21 = pd.Series(close).ewm(span=21, adjust=False).mean().values
    
    trades = 0
    wins = 0
    total_pnl = 0
    for i in range(22, len(close)):
        # Cross up
        if ema9[i] > ema21[i] and ema9[i-1] <= ema21[i-1]:
            # Hold for 3 bars
            exit_i = min(i + 3, len(close) - 1)
            pnl = close[exit_i] - close[i]
            trades += 1
            total_pnl += pnl
            if pnl > 0: wins += 1
        # Cross down
        elif ema9[i] < ema21[i] and ema9[i-1] >= ema21[i-1]:
            exit_i = min(i + 3, len(close) - 1)
            pnl = close[i] - close[exit_i]
            trades += 1
            total_pnl += pnl
            if pnl > 0: wins += 1
    return trades, wins, total_pnl

print('\n=== HOURLY ANALYSIS (ET) ===')
print(f'{"Hour":>6} {"Bars":>6} {"AvgRange":>10} {"AvgVol":>10} {"Avg|Move|":>10} {"Trend%":>8}')
print('-' * 55)

for hour in sorted(df['hour_et'].unique()):
    hdf = df[df['hour_et'] == hour]
    avg_range = hdf['range'].mean()
    avg_vol = hdf['v'].mean()
    avg_move = hdf['body'].mean()
    trend_pct = (hdf['direction'].abs().sum() / len(hdf)) * 100
    print(f'{hour:>6} {len(hdf):>6} {avg_range:>10.2f} {avg_vol:>10.0f} {avg_move:>10.2f} {trend_pct:>7.1f}%')

print('\n=== SESSION BREAKDOWN ===')
sessions = {
    'Asia (18-02 ET)': df[df['hour_et'].isin([18,19,20,21,22,23,0,1])],
    'London (03-07 ET)': df[df['hour_et'].isin([3,4,5,6,7])],
    'NY Pre (08-09 ET)': df[df['hour_et'].isin([8,9])],
    'COMEX (10-13 ET)': df[df['hour_et'].isin([10,11,12,13])],
    'Afternoon (14-17 ET)': df[df['hour_et'].isin([14,15,16,17])],
}

print(f'{"Session":>20} {"Bars":>6} {"AvgRange":>10} {"AvgVol":>10} {"Avg|Move|":>10}')
print('-' * 60)
for name, sdf in sessions.items():
    if len(sdf) > 0:
        print(f'{name:>20} {len(sdf):>6} {sdf["range"].mean():>10.2f} {sdf["v"].mean():>10.0f} {sdf["body"].mean():>10.2f}')

print('\n=== EMA CROSS SIMULATION BY SESSION ===')
for name, sdf in sessions.items():
    if len(sdf) > 0:
        trades, wins, pnl = simulate_ema_cross(sdf.reset_index(drop=True))
        wr = (wins/trades*100) if trades > 0 else 0
        pnl_dollar = pnl * 10  # $10/point MGC
        print(f'{name:>20}: {trades:>3} trades, WR={wr:>5.1f}%, PnL={pnl:>7.1f} pts (${pnl_dollar:>8.0f})')

print('\n=== VERDICT ===')
asia = df[df['hour_et'].isin([18,19,20,21,22,23,0,1])]
ny = df[df['hour_et'].isin([8,9,10,11,12,13])]
vol_ratio = asia['v'].mean() / ny['v'].mean() if ny['v'].mean() > 0 else 0
range_ratio = asia['range'].mean() / ny['range'].mean() if ny['range'].mean() > 0 else 0
print(f'Asia vs NY volume ratio: {vol_ratio:.2f}x')
print(f'Asia vs NY range ratio: {range_ratio:.2f}x')
if vol_ratio < 0.3:
    print('SKIP overnight - volume too thin for reliable signals')
elif range_ratio < 0.5:
    print('SKIP overnight - range too tight, likely to get chopped')
else:
    print('OVERNIGHT TRADEABLE - decent volume and range')

ib.disconnect()
