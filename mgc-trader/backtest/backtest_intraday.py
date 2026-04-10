"""
MGC (Micro Gold Futures) Intraday Backtester
=============================================
Uses 1H GC data as proxy. Results are APPROXIMATE — real validation needs 5m data.

Contract: MGC = $10/point, $0.10 tick ($1/tick)
Costs: $2.50 commission + $2.00 slippage = $4.50 round trip
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# ── Config ──────────────────────────────────────────────────────────────────
POINT_VALUE = 10.0
COMMISSION_RT = 2.50
SLIPPAGE_RT = 2.00
TOTAL_COST_RT = COMMISSION_RT + SLIPPAGE_RT
INITIAL_CAPITAL = 100_000.0
DATA_PATH = r"C:\Users\adamh\.openclaw\workspace\backtester\gc_1h_cache.csv"

@dataclass
class Trade:
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    direction: str  # 'long' or 'short'
    entry_price: float
    exit_price: float
    strategy: str
    
    @property
    def points(self):
        mult = 1 if self.direction == 'long' else -1
        return mult * (self.exit_price - self.entry_price)
    
    @property
    def pnl(self):
        return self.points * POINT_VALUE - TOTAL_COST_RT
    
    @property
    def hour(self):
        return self.entry_time.hour

# ── Load Data ───────────────────────────────────────────────────────────────
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, skiprows=3, header=None,
                     names=['Datetime','Close','High','Low','Open','Volume'])
    df['Datetime'] = pd.to_datetime(df['Datetime'], utc=True)
    df = df.sort_values('Datetime').reset_index(drop=True)
    for c in ['Open','High','Low','Close']:
        df[c] = df[c].astype(float)
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce').fillna(0)
    
    # ATR(14)
    df['TR'] = np.maximum(df['High'] - df['Low'],
                np.maximum(abs(df['High'] - df['Close'].shift(1)),
                           abs(df['Low'] - df['Close'].shift(1))))
    df['ATR14'] = df['TR'].ewm(span=14, adjust=False).mean()
    
    # EMAs
    df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
    
    # Session date (resets at 23:00 UTC)
    df['session_date'] = df['Datetime'].apply(
        lambda x: (x - pd.Timedelta(hours=23)).date() if x.hour >= 23 
        else (x - pd.Timedelta(hours=0)).date() if x.hour < 23
        else x.date()
    )
    # Simpler: session changes at 23:00 UTC
    df['session_date'] = df['Datetime'].apply(
        lambda dt: dt.date() if dt.hour >= 23 else (dt - pd.Timedelta(days=0)).date()
    )
    # Actually: 23:00 UTC starts new session, so bars 23:00 today belong to tomorrow's session
    df['session_date'] = df['Datetime'].apply(
        lambda dt: (dt + pd.Timedelta(hours=1)).date() if dt.hour >= 23 else dt.date()
    )
    
    # VWAP (reset at 23:00 UTC each day)
    df['TypicalPrice'] = (df['High'] + df['Low'] + df['Close']) / 3
    vol = df['Volume'].clip(lower=1).values
    tp = df['TypicalPrice'].values
    tpv = tp * vol
    sessions = df['session_date'].values
    
    # Vectorized cumsum with session reset
    session_starts = np.concatenate([[True], sessions[1:] != sessions[:-1]])
    # Build cumulative sums that reset at session boundaries
    cum_tpv = np.zeros(len(df))
    cum_vol = np.zeros(len(df))
    ct = 0.0
    cv = 0.0
    for i in range(len(df)):
        if session_starts[i]:
            ct = 0.0
            cv = 0.0
        ct += tpv[i]
        cv += vol[i]
        cum_tpv[i] = ct
        cum_vol[i] = cv
    df['VWAP'] = cum_tpv / cum_vol
    
    # Prior day high/low/close
    daily = df.groupby('session_date').agg(
        DayHigh=('High','max'), DayLow=('Low','min'), DayClose=('Close','last')
    ).reset_index()
    daily['PrevHigh'] = daily['DayHigh'].shift(1)
    daily['PrevLow'] = daily['DayLow'].shift(1)
    daily['PrevClose'] = daily['DayClose'].shift(1)
    df = df.merge(daily[['session_date','PrevHigh','PrevLow','PrevClose']], on='session_date', how='left')
    
    return df

# ── Strategy 1: Opening Range Breakout ──────────────────────────────────────
def strategy_orb(df: pd.DataFrame) -> List[Trade]:
    trades = []
    daily_count = defaultdict(int)
    
    for i in range(1, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i-1]
        
        # Opening range bar is the 13:00 UTC bar
        if prev['Datetime'].hour != 13:
            continue
        if row['Datetime'].hour < 13 or row['Datetime'].hour >= 19:
            continue
        
        date_key = row['session_date']
        if daily_count[date_key] >= 2:
            continue
        
        or_high = prev['High']
        or_low = prev['Low']
        atr = prev['ATR14']
        if pd.isna(atr) or atr < 0.5:
            continue
        
        # Check breakout on next bars (current bar = bar after OR)
        close = row['Close']
        
        if close > or_high:
            stop = or_low - atr
            risk = close - stop
            tp = close + 2 * risk
            # Simulate: check if TP or stop hit using bar's high/low
            # For simplicity, use the close as exit proxy, but check subsequent bars
            exit_price, exit_time = _simulate_exit(df, i, close, tp, stop, 'long', max_bars=6)
            trades.append(Trade(row['Datetime'], exit_time, 'long', close, exit_price, 'ORB'))
            daily_count[date_key] += 1
        elif close < or_low:
            stop = or_high + atr
            risk = stop - close
            tp = close - 2 * risk
            exit_price, exit_time = _simulate_exit(df, i, close, tp, stop, 'short', max_bars=6)
            trades.append(Trade(row['Datetime'], exit_time, 'short', close, exit_price, 'ORB'))
            daily_count[date_key] += 1
    
    return trades

def _simulate_exit(df, entry_idx, entry_price, tp, stop, direction, max_bars=6):
    """Simulate exit on subsequent bars. Returns (exit_price, exit_time)."""
    for j in range(entry_idx + 1, min(entry_idx + max_bars + 1, len(df))):
        bar = df.iloc[j]
        # End of session check (19:00 UTC)
        if bar['Datetime'].hour >= 19 or bar['Datetime'].hour < 13:
            return bar['Close'], bar['Datetime']
        
        if direction == 'long':
            if bar['Low'] <= stop:
                return stop, bar['Datetime']
            if bar['High'] >= tp:
                return tp, bar['Datetime']
        else:
            if bar['High'] >= stop:
                return stop, bar['Datetime']
            if bar['Low'] <= tp:
                return tp, bar['Datetime']
    
    # Max bars reached, exit at close
    j = min(entry_idx + max_bars, len(df) - 1)
    return df.iloc[j]['Close'], df.iloc[j]['Datetime']

# ── Strategy 2: VWAP Bounce ─────────────────────────────────────────────────
def strategy_vwap(df: pd.DataFrame) -> List[Trade]:
    trades = []
    daily_count = defaultdict(int)
    
    for i in range(2, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i-1]
        prev2 = df.iloc[i-2]
        
        date_key = row['session_date']
        if daily_count[date_key] >= 4:
            continue
        
        atr = row['ATR14']
        if pd.isna(atr) or atr < 0.5:
            continue
        
        vwap = row['VWAP']
        ema50 = row['EMA50']
        
        # Long: was below VWAP, now above
        if prev['Close'] < prev['VWAP'] and row['Close'] > vwap and row['Close'] > ema50:
            entry = row['Close']
            stop = vwap - atr
            risk = entry - stop
            tp = entry + 1.5 * risk
            exit_price, exit_time = _simulate_exit(df, i, entry, tp, stop, 'long', max_bars=8)
            trades.append(Trade(row['Datetime'], exit_time, 'long', entry, exit_price, 'VWAP'))
            daily_count[date_key] += 1
        # Short: was above VWAP, now below
        elif prev['Close'] > prev['VWAP'] and row['Close'] < vwap and row['Close'] < ema50:
            entry = row['Close']
            stop = vwap + atr
            risk = stop - entry
            tp = entry - 1.5 * risk
            exit_price, exit_time = _simulate_exit(df, i, entry, tp, stop, 'short', max_bars=8)
            trades.append(Trade(row['Datetime'], exit_time, 'short', entry, exit_price, 'VWAP'))
            daily_count[date_key] += 1
    
    return trades

# ── Strategy 3: EMA Momentum ────────────────────────────────────────────────
def strategy_ema(df: pd.DataFrame) -> List[Trade]:
    trades = []
    daily_count = defaultdict(int)
    
    for i in range(1, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i-1]
        
        if row['Datetime'].hour < 13 or row['Datetime'].hour >= 19:
            continue
        
        date_key = row['session_date']
        if daily_count[date_key] >= 4:
            continue
        
        atr = row['ATR14']
        if pd.isna(atr) or atr < 0.5 or pd.isna(row['EMA50']):
            continue
        
        # Long: EMA9 crosses above EMA21 AND close > EMA50
        if (prev['EMA9'] <= prev['EMA21'] and row['EMA9'] > row['EMA21'] 
            and row['Close'] > row['EMA50']):
            entry = row['Close']
            stop = entry - 1.5 * atr
            risk = entry - stop
            tp = entry + 1.5 * risk
            exit_price, exit_time = _simulate_exit(df, i, entry, tp, stop, 'long', max_bars=8)
            trades.append(Trade(row['Datetime'], exit_time, 'long', entry, exit_price, 'EMA'))
            daily_count[date_key] += 1
        # Short: EMA9 crosses below EMA21 AND close < EMA50
        elif (prev['EMA9'] >= prev['EMA21'] and row['EMA9'] < row['EMA21']
              and row['Close'] < row['EMA50']):
            entry = row['Close']
            stop = entry + 1.5 * atr
            risk = stop - entry
            tp = entry - 1.5 * risk
            exit_price, exit_time = _simulate_exit(df, i, entry, tp, stop, 'short', max_bars=8)
            trades.append(Trade(row['Datetime'], exit_time, 'short', entry, exit_price, 'EMA'))
            daily_count[date_key] += 1
    
    return trades

# ── Strategy 4: Level Scalp ─────────────────────────────────────────────────
def strategy_levels(df: pd.DataFrame) -> List[Trade]:
    trades = []
    daily_count = defaultdict(int)
    
    for i in range(1, len(df)):
        row = df.iloc[i]
        
        date_key = row['session_date']
        if daily_count[date_key] >= 6:
            continue
        
        atr = row['ATR14']
        if pd.isna(atr) or atr < 0.5:
            continue
        if pd.isna(row['PrevHigh']):
            continue
        
        # Build levels: prev high, prev low, prev close, round $10 numbers
        price = row['Close']
        levels = [row['PrevHigh'], row['PrevLow'], row['PrevClose']]
        # Round numbers near price
        base = int(price / 10) * 10
        for offset in [-20, -10, 0, 10, 20]:
            levels.append(float(base + offset))
        
        bounce_threshold = 0.5 * atr
        
        for level in levels:
            dist = price - level
            # Bounce up from support (price near level and moved away upward)
            if 0 < dist < bounce_threshold * 2 and row['Low'] <= level + bounce_threshold:
                entry = price
                stop = level - 0.75 * atr
                risk = entry - stop
                if risk <= 0:
                    continue
                tp = entry + 1.5 * risk
                exit_price, exit_time = _simulate_exit(df, i, entry, tp, stop, 'long', max_bars=6)
                trades.append(Trade(row['Datetime'], exit_time, 'long', entry, exit_price, 'Level'))
                daily_count[date_key] += 1
                break
            # Bounce down from resistance
            elif 0 > dist > -bounce_threshold * 2 and row['High'] >= level - bounce_threshold:
                entry = price
                stop = level + 0.75 * atr
                risk = stop - entry
                if risk <= 0:
                    continue
                tp = entry - 1.5 * risk
                exit_price, exit_time = _simulate_exit(df, i, entry, tp, stop, 'short', max_bars=6)
                trades.append(Trade(row['Datetime'], exit_time, 'short', entry, exit_price, 'Level'))
                daily_count[date_key] += 1
                break
    
    return trades

# ── Analytics ────────────────────────────────────────────────────────────────
def analyze(trades: List[Trade], name: str) -> dict:
    if not trades:
        return {'name': name, 'total': 0}
    
    pnls = [t.pnl for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    
    # Monthly P&L
    monthly = defaultdict(float)
    for t in trades:
        key = t.entry_time.strftime('%Y-%m')
        monthly[key] += t.pnl
    
    # Drawdown
    equity = INITIAL_CAPITAL
    peak = equity
    max_dd = 0
    max_dd_pct = 0
    for p in pnls:
        equity += p
        peak = max(peak, equity)
        dd = peak - equity
        if dd > max_dd:
            max_dd = dd
            max_dd_pct = dd / peak * 100
    
    # Sharpe
    daily_pnl = defaultdict(float)
    for t in trades:
        daily_pnl[t.entry_time.date()] += t.pnl
    daily_returns = list(daily_pnl.values())
    if len(daily_returns) > 1 and np.std(daily_returns) > 0:
        sharpe = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252)
    else:
        sharpe = 0
    
    # Trading days
    trading_days = len(set(t.entry_time.date() for t in trades))
    
    longs = [t for t in trades if t.direction == 'long']
    shorts = [t for t in trades if t.direction == 'short']
    
    gross_wins = sum(wins) if wins else 0
    gross_losses = abs(sum(losses)) if losses else 1
    
    best_month = max(monthly.items(), key=lambda x: x[1]) if monthly else ('N/A', 0)
    worst_month = min(monthly.items(), key=lambda x: x[1]) if monthly else ('N/A', 0)
    
    return {
        'name': name,
        'total': len(trades),
        'longs': len(longs),
        'shorts': len(shorts),
        'win_rate': len(wins) / len(trades) * 100,
        'avg_win': np.mean(wins) if wins else 0,
        'avg_loss': np.mean(losses) if losses else 0,
        'net_profit': sum(pnls),
        'profit_factor': gross_wins / gross_losses if gross_losses > 0 else float('inf'),
        'max_dd': max_dd,
        'max_dd_pct': max_dd_pct,
        'best_month': f"{best_month[0]} (${best_month[1]:,.2f})",
        'worst_month': f"{worst_month[0]} (${worst_month[1]:,.2f})",
        'sharpe': sharpe,
        'avg_trades_day': len(trades) / max(trading_days, 1),
        'trades': trades,
    }

def print_results(stats: dict):
    if stats['total'] == 0:
        print(f"\n{'='*60}")
        print(f"  {stats['name']}: NO TRADES")
        print(f"{'='*60}")
        return
    
    print(f"\n{'='*60}")
    print(f"  {stats['name']}")
    print(f"{'='*60}")
    print(f"  Total Trades:      {stats['total']} (Long: {stats['longs']}, Short: {stats['shorts']})")
    print(f"  Win Rate:          {stats['win_rate']:.1f}%")
    print(f"  Avg Win:           ${stats['avg_win']:,.2f}")
    print(f"  Avg Loss:          ${stats['avg_loss']:,.2f}")
    print(f"  Net Profit:        ${stats['net_profit']:,.2f}")
    print(f"  Profit Factor:     {stats['profit_factor']:.2f}")
    print(f"  Max Drawdown:      ${stats['max_dd']:,.2f} ({stats['max_dd_pct']:.1f}%)")
    print(f"  Best Month:        {stats['best_month']}")
    print(f"  Worst Month:       {stats['worst_month']}")
    print(f"  Sharpe Ratio:      {stats['sharpe']:.2f}")
    print(f"  Avg Trades/Day:    {stats['avg_trades_day']:.1f}")

def combined_analysis(all_trades: List[Trade]):
    if not all_trades:
        print("\nNo combined trades.")
        return {}
    
    all_trades.sort(key=lambda t: t.entry_time)
    stats = analyze(all_trades, "COMBINED (All 4 Strategies)")
    print_results(stats)
    
    # Per-hour analysis
    hour_pnl = defaultdict(lambda: {'pnl': 0, 'count': 0, 'wins': 0})
    for t in all_trades:
        h = t.hour
        hour_pnl[h]['pnl'] += t.pnl
        hour_pnl[h]['count'] += 1
        if t.pnl > 0:
            hour_pnl[h]['wins'] += 1
    
    print(f"\n{'='*60}")
    print(f"  PER-HOUR ANALYSIS (UTC)")
    print(f"{'='*60}")
    print(f"  {'Hour':>4}  {'Trades':>7}  {'Win%':>6}  {'Net P&L':>12}")
    print(f"  {'─'*4}  {'─'*7}  {'─'*6}  {'─'*12}")
    for h in sorted(hour_pnl.keys()):
        d = hour_pnl[h]
        wr = d['wins'] / d['count'] * 100 if d['count'] > 0 else 0
        print(f"  {h:>4}  {d['count']:>7}  {wr:>5.1f}%  ${d['pnl']:>11,.2f}")
    
    return stats

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("Loading data...")
    df = load_data()
    print(f"Loaded {len(df)} bars from {df['Datetime'].iloc[0]} to {df['Datetime'].iloc[-1]}")
    print(f"\n⚠️  APPROXIMATE RESULTS — Based on 1H bars. Real validation needs 5m data from IB.\n")
    
    print("Running Strategy 1: Opening Range Breakout...")
    orb_trades = strategy_orb(df)
    orb_stats = analyze(orb_trades, "Strategy 1: Opening Range Breakout (ORB)")
    print_results(orb_stats)
    
    print("\nRunning Strategy 2: VWAP Bounce...")
    vwap_trades = strategy_vwap(df)
    vwap_stats = analyze(vwap_trades, "Strategy 2: VWAP Bounce")
    print_results(vwap_stats)
    
    print("\nRunning Strategy 3: EMA Momentum...")
    ema_trades = strategy_ema(df)
    ema_stats = analyze(ema_trades, "Strategy 3: EMA Momentum")
    print_results(ema_stats)
    
    print("\nRunning Strategy 4: Level Scalp...")
    level_trades = strategy_levels(df)
    level_stats = analyze(level_trades, "Strategy 4: Level Scalp")
    print_results(level_stats)
    
    # Combined
    all_trades = orb_trades + vwap_trades + ema_trades + level_trades
    combined_stats = combined_analysis(all_trades)
    
    # Save results.md
    save_results(orb_stats, vwap_stats, ema_stats, level_stats, combined_stats)
    print(f"\n✅ Results saved to results.md")

def save_results(*all_stats):
    lines = ["# MGC Intraday Backtest Results\n"]
    lines.append("> ⚠️ **APPROXIMATE** — Based on 1H bars. Real validation needs 5m data from IB.\n")
    lines.append(f"> Data: ~11,446 bars, Feb 2024 – Feb 2026\n")
    lines.append(f"> Initial Capital: ${INITIAL_CAPITAL:,.0f} | Cost/trade: ${TOTAL_COST_RT:.2f}\n\n")
    
    for stats in all_stats:
        if not stats or stats.get('total', 0) == 0:
            continue
        lines.append(f"## {stats['name']}\n")
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Total Trades | {stats['total']} (L:{stats['longs']} S:{stats['shorts']}) |")
        lines.append(f"| Win Rate | {stats['win_rate']:.1f}% |")
        lines.append(f"| Avg Win | ${stats['avg_win']:,.2f} |")
        lines.append(f"| Avg Loss | ${stats['avg_loss']:,.2f} |")
        lines.append(f"| Net Profit | ${stats['net_profit']:,.2f} |")
        lines.append(f"| Profit Factor | {stats['profit_factor']:.2f} |")
        lines.append(f"| Max Drawdown | ${stats['max_dd']:,.2f} ({stats['max_dd_pct']:.1f}%) |")
        lines.append(f"| Best Month | {stats['best_month']} |")
        lines.append(f"| Worst Month | {stats['worst_month']} |")
        lines.append(f"| Sharpe Ratio | {stats['sharpe']:.2f} |")
        lines.append(f"| Avg Trades/Day | {stats['avg_trades_day']:.1f} |")
        lines.append("")
    
    with open(r"C:\Users\adamh\.openclaw\workspace\mgc-trader\backtest\results.md", 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

if __name__ == '__main__':
    main()
