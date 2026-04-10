"""
MGC 4H Strategy Backtester
Tests multiple strategies against the Keltner Breakout benchmark.
"""

import csv
import json
import math
from datetime import datetime, timedelta
from pathlib import Path
from itertools import product

DATA_DIR = Path(__file__).parent / "data" / "history"
OUTPUT_DIR = Path(__file__).parent

# Constants
POINT_VALUE = 10.0       # $10 per point for MGC
COMMISSION_RT = 1.24     # Round trip commission
SLIPPAGE_PTS = 0.5       # Slippage in points per trade
SLIPPAGE_COST = SLIPPAGE_PTS * POINT_VALUE


def load_data(filepath):
    """Load CSV into list of dicts with proper types."""
    rows = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                'datetime': r['datetime'],
                'open': float(r['open']),
                'high': float(r['high']),
                'low': float(r['low']),
                'close': float(r['close']),
                'volume': float(r.get('volume', 0)),
            })
    return rows


# ── Indicator helpers ────────────────────────────────────────────────────────

def ema(values, period):
    """Compute EMA series (same length, NaN-padded)."""
    result = [None] * len(values)
    if len(values) < period:
        return result
    k = 2.0 / (period + 1)
    # Seed with SMA
    s = sum(values[:period]) / period
    result[period - 1] = s
    for i in range(period, len(values)):
        s = values[i] * k + s * (1 - k)
        result[i] = s
    return result


def sma(values, period):
    result = [None] * len(values)
    for i in range(period - 1, len(values)):
        result[i] = sum(values[i - period + 1:i + 1]) / period
    return result


def true_range(bars):
    """Compute true range series."""
    tr = [None]
    for i in range(1, len(bars)):
        h = bars[i]['high']
        l = bars[i]['low']
        pc = bars[i - 1]['close']
        tr.append(max(h - l, abs(h - pc), abs(l - pc)))
    return tr


def atr(bars, period=14):
    """ATR using EMA of true range."""
    tr = true_range(bars)
    # Replace None at index 0
    tr_vals = [t if t is not None else 0 for t in tr]
    return ema(tr_vals, period)


def adx(bars, period=14):
    """Simplified ADX calculation."""
    result = [None] * len(bars)
    if len(bars) < period * 2:
        return result
    
    plus_dm = []
    minus_dm = []
    tr_list = []
    
    for i in range(1, len(bars)):
        h = bars[i]['high']
        l = bars[i]['low']
        ph = bars[i-1]['high']
        pl = bars[i-1]['low']
        pc = bars[i-1]['close']
        
        up = h - ph
        down = pl - l
        plus_dm.append(up if up > down and up > 0 else 0)
        minus_dm.append(down if down > up and down > 0 else 0)
        tr_list.append(max(h - l, abs(h - pc), abs(l - pc)))
    
    # Smooth with EMA
    k = 1.0 / period
    if len(plus_dm) < period:
        return result
    
    atr_s = sum(tr_list[:period])
    plus_s = sum(plus_dm[:period])
    minus_s = sum(minus_dm[:period])
    
    dx_list = []
    for i in range(period, len(plus_dm)):
        atr_s = atr_s - atr_s / period + tr_list[i]
        plus_s = plus_s - plus_s / period + plus_dm[i]
        minus_s = minus_s - minus_s / period + minus_dm[i]
        
        if atr_s == 0:
            dx_list.append(0)
            continue
        plus_di = 100 * plus_s / atr_s
        minus_di = 100 * minus_s / atr_s
        denom = plus_di + minus_di
        if denom == 0:
            dx_list.append(0)
        else:
            dx_list.append(100 * abs(plus_di - minus_di) / denom)
    
    # ADX = smoothed DX
    if len(dx_list) < period:
        return result
    
    adx_val = sum(dx_list[:period]) / period
    offset = 1 + period + period  # index into bars
    if offset - 1 < len(result):
        result[offset - 1] = adx_val
    for i in range(period, len(dx_list)):
        adx_val = (adx_val * (period - 1) + dx_list[i]) / period
        idx = 1 + period + i
        if idx < len(result):
            result[idx] = adx_val
    
    return result


def keltner_channels(bars, kc_len=10, kc_mult=1.25):
    """Compute Keltner Channel (EMA basis, ATR bands)."""
    closes = [b['close'] for b in bars]
    basis = ema(closes, kc_len)
    atr_vals = atr(bars, kc_len)
    
    upper = [None] * len(bars)
    lower = [None] * len(bars)
    for i in range(len(bars)):
        if basis[i] is not None and atr_vals[i] is not None:
            upper[i] = basis[i] + kc_mult * atr_vals[i]
            lower[i] = basis[i] - kc_mult * atr_vals[i]
    
    return basis, upper, lower, atr_vals


def macd_histogram(bars, fast=12, slow=26, signal=9):
    """MACD histogram."""
    closes = [b['close'] for b in bars]
    fast_ema = ema(closes, fast)
    slow_ema = ema(closes, slow)
    
    macd_line = [None] * len(bars)
    for i in range(len(bars)):
        if fast_ema[i] is not None and slow_ema[i] is not None:
            macd_line[i] = fast_ema[i] - slow_ema[i]
    
    macd_vals = [v if v is not None else 0 for v in macd_line]
    sig = ema(macd_vals, signal)
    
    hist = [None] * len(bars)
    for i in range(len(bars)):
        if macd_line[i] is not None and sig[i] is not None:
            hist[i] = macd_line[i] - sig[i]
    return hist


def donchian(bars, period=20):
    """Donchian channel high/low."""
    upper = [None] * len(bars)
    lower = [None] * len(bars)
    for i in range(period - 1, len(bars)):
        upper[i] = max(b['high'] for b in bars[i - period + 1:i + 1])
        lower[i] = min(b['low'] for b in bars[i - period + 1:i + 1])
    return upper, lower


def atr_percentile(atr_vals, lookback=100):
    """ATR percentile rank over lookback window."""
    result = [None] * len(atr_vals)
    for i in range(lookback, len(atr_vals)):
        if atr_vals[i] is None:
            continue
        window = [v for v in atr_vals[i - lookback:i] if v is not None]
        if not window:
            continue
        rank = sum(1 for v in window if v <= atr_vals[i]) / len(window)
        result[i] = rank
    return result


def get_hour_et(dt_str):
    """Extract hour from datetime string. Assumes ET."""
    try:
        # Format: "2025-01-15 08:00:00" or similar
        parts = dt_str.split(' ')
        if len(parts) >= 2:
            time_parts = parts[1].split(':')
            return int(time_parts[0])
    except:
        pass
    return 12  # default


def resample_daily(bars):
    """Resample 4H bars to daily OHLC."""
    daily = {}
    for b in bars:
        date = b['datetime'][:10]
        if date not in daily:
            daily[date] = {'open': b['open'], 'high': b['high'], 'low': b['low'], 'close': b['close']}
        else:
            d = daily[date]
            d['high'] = max(d['high'], b['high'])
            d['low'] = min(d['low'], b['low'])
            d['close'] = b['close']
    return daily


# ── Trade tracking ───────────────────────────────────────────────────────────

class Trade:
    def __init__(self, entry_price, entry_bar, stop_loss, take_profit=None, trail_mult=3.0, atr_val=1.0, breakeven_r=1.0):
        self.entry_price = entry_price
        self.entry_bar = entry_bar
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.trail_mult = trail_mult
        self.atr_val = atr_val
        self.breakeven_r = breakeven_r
        self.highest = entry_price
        self.risk = entry_price - stop_loss
        self.exit_price = None
        self.exit_bar = None
        self.pnl = None
        self.breakeven_moved = False
    
    def update(self, bar):
        """Update trade with new bar. Returns True if trade is closed."""
        h = bar['high']
        l = bar['low']
        c = bar['close']
        
        # Check stop loss first (hit on low)
        if l <= self.stop_loss:
            self.exit_price = self.stop_loss
            self.exit_bar = bar
            self._calc_pnl()
            return True
        
        # Check take profit (hit on high)
        if self.take_profit and h >= self.take_profit:
            self.exit_price = self.take_profit
            self.exit_bar = bar
            self._calc_pnl()
            return True
        
        # Update trailing stop and breakeven
        if h > self.highest:
            self.highest = h
            # Trailing stop
            new_stop = self.highest - self.trail_mult * self.atr_val
            if new_stop > self.stop_loss:
                self.stop_loss = new_stop
        
        # Move to breakeven after 1R move
        if not self.breakeven_moved and self.risk > 0:
            if c >= self.entry_price + self.breakeven_r * self.risk:
                self.stop_loss = max(self.stop_loss, self.entry_price)
                self.breakeven_moved = True
        
        return False
    
    def _calc_pnl(self):
        pts = self.exit_price - self.entry_price
        self.pnl = pts * POINT_VALUE - COMMISSION_RT - SLIPPAGE_COST


def calc_stats(trades, bars):
    """Calculate strategy statistics from trade list."""
    if not trades:
        return {
            'total_pnl': 0, 'num_trades': 0, 'win_rate': 0, 'profit_factor': 0,
            'max_drawdown_pct': 0, 'sharpe': 0, 'avg_duration_bars': 0
        }
    
    total_pnl = sum(t.pnl for t in trades)
    wins = [t for t in trades if t.pnl > 0]
    losses = [t for t in trades if t.pnl <= 0]
    win_rate = len(wins) / len(trades) * 100 if trades else 0
    
    gross_profit = sum(t.pnl for t in wins) if wins else 0
    gross_loss = abs(sum(t.pnl for t in losses)) if losses else 0.001
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 999
    
    # Max drawdown
    equity = 0
    peak = 0
    max_dd = 0
    for t in trades:
        equity += t.pnl
        peak = max(peak, equity)
        dd = peak - equity
        max_dd = max(max_dd, dd)
    
    initial_capital = 100000
    max_dd_pct = max_dd / initial_capital * 100 if initial_capital > 0 else 0
    
    # Sharpe (annualized, using trade returns)
    if len(trades) > 1:
        returns = [t.pnl for t in trades]
        avg_r = sum(returns) / len(returns)
        std_r = (sum((r - avg_r) ** 2 for r in returns) / (len(returns) - 1)) ** 0.5
        # Approx: 6 trades/month * 12 = 72/year for 4H
        trades_per_year = len(trades) / max(1, (len(bars) / (6 * 252)))
        sharpe = (avg_r / std_r) * (trades_per_year ** 0.5) if std_r > 0 else 0
    else:
        sharpe = 0
    
    # Avg duration
    durations = []
    for t in trades:
        if t.exit_bar and t.entry_bar:
            try:
                entry_idx = bars.index(t.entry_bar) if isinstance(t.entry_bar, dict) else 0
                exit_idx = bars.index(t.exit_bar) if isinstance(t.exit_bar, dict) else 0
                durations.append(exit_idx - entry_idx)
            except (ValueError, IndexError):
                durations.append(0)
    avg_dur = sum(durations) / len(durations) if durations else 0
    
    return {
        'total_pnl': round(total_pnl, 2),
        'num_trades': len(trades),
        'win_rate': round(win_rate, 2),
        'profit_factor': round(profit_factor, 3),
        'max_drawdown_pct': round(max_dd_pct, 2),
        'sharpe': round(sharpe, 2),
        'avg_duration_bars': round(avg_dur, 1),
    }


# ── Strategies ───────────────────────────────────────────────────────────────

def run_keltner_breakout(bars, kc_len=10, kc_mult=1.25, trail_mult=3.0, tp_r=0.5, be_r=1.0, adx_thresh=10, 
                          reentry=False, max_reentries=0,
                          momentum_filter=False, session_filter=False, 
                          adaptive=False, dual_tf=False, inside_bar=False):
    """
    Unified Keltner breakout engine with optional filters.
    """
    basis, upper, lower, atr_vals = keltner_channels(bars, kc_len, kc_mult)
    adx_vals = adx(bars, 14)
    
    # Optional indicators
    macd_hist = macd_histogram(bars) if momentum_filter else None
    daily = resample_daily(bars) if dual_tf else None
    daily_dates = sorted(daily.keys()) if daily else []
    daily_ema_vals = {}
    if dual_tf and daily:
        daily_closes = [daily[d]['close'] for d in daily_dates]
        daily_ema_raw = ema(daily_closes, 20)
        for i, d in enumerate(daily_dates):
            daily_ema_vals[d] = daily_ema_raw[i]
    
    if adaptive:
        atr_pct = atr_percentile(atr_vals)
    
    trades = []
    active_trade = None
    last_stopped = False  # For reentry logic
    last_stop_bar = -1
    reentry_count = 0
    
    for i in range(1, len(bars)):
        bar = bars[i]
        prev = bars[i - 1]
        
        # Update active trade
        if active_trade:
            closed = active_trade.update(bar)
            if closed:
                trades.append(active_trade)
                if active_trade.pnl <= 0:
                    last_stopped = True
                    last_stop_bar = i
                else:
                    last_stopped = False
                active_trade = None
                continue
        
        # Entry logic
        if active_trade is None:
            if upper[i] is None or atr_vals[i] is None or atr_vals[i] <= 0:
                continue
            if adx_vals[i] is None or adx_vals[i] < adx_thresh:
                continue
            
            # Adaptive multiplier
            actual_mult = kc_mult
            if adaptive and atr_pct[i] is not None:
                # High vol = wider, low vol = tighter
                actual_mult = kc_mult * (0.8 + 0.4 * atr_pct[i])
                actual_upper = basis[i] + actual_mult * atr_vals[i]
            else:
                actual_upper = upper[i]
            
            # Base signal: close above upper KC
            signal = prev['close'] > actual_upper
            
            # Reentry: also enter if we just got stopped but price still above KC
            if reentry and not signal and last_stopped and (i - last_stop_bar) <= 2:
                if prev['close'] > actual_upper and reentry_count < max_reentries:
                    signal = True
                    reentry_count += 1
                else:
                    reentry_count = 0
            elif signal:
                reentry_count = 0
            
            if not signal:
                continue
            
            # Momentum filter
            if momentum_filter and macd_hist[i] is not None and macd_hist[i] <= 0:
                continue
            
            # Session filter - skip Asia session (22:00-03:00 ET roughly)
            if session_filter:
                hour = get_hour_et(bar['datetime'])
                if hour >= 22 or hour < 3:
                    continue
            
            # Dual timeframe filter
            if dual_tf:
                date = bar['datetime'][:10]
                # Find previous day's EMA
                prev_dates = [d for d in daily_dates if d < date]
                if prev_dates:
                    prev_d = prev_dates[-1]
                    if daily_ema_vals.get(prev_d) is not None:
                        if daily[prev_d]['close'] < daily_ema_vals[prev_d]:
                            continue  # Daily trend is down, skip
                
            # Inside bar filter
            if inside_bar:
                if not (prev['high'] < bars[i-2]['high'] and prev['low'] > bars[i-2]['low']):
                    continue  # Not an inside bar
            
            entry_price = bar['open'] + SLIPPAGE_PTS
            risk_atr = atr_vals[i]
            stop_loss = entry_price - trail_mult * risk_atr
            take_profit = entry_price + tp_r * (trail_mult * risk_atr) if tp_r > 0 else None
            
            active_trade = Trade(
                entry_price=entry_price,
                entry_bar=bar,
                stop_loss=stop_loss,
                take_profit=take_profit,
                trail_mult=trail_mult,
                atr_val=risk_atr,
                breakeven_r=be_r,
            )
    
    # Close any remaining trade at last bar
    if active_trade:
        active_trade.exit_price = bars[-1]['close']
        active_trade.exit_bar = bars[-1]
        active_trade._calc_pnl()
        trades.append(active_trade)
    
    return trades


def run_donchian_breakout(bars, period=20, trail_mult=3.0, adx_thresh=10):
    """Donchian channel breakout with ATR trailing stop."""
    dc_upper, dc_lower = donchian(bars, period)
    atr_vals = atr(bars, 14)
    adx_vals = adx(bars, 14)
    
    trades = []
    active_trade = None
    
    for i in range(1, len(bars)):
        bar = bars[i]
        prev = bars[i - 1]
        
        if active_trade:
            closed = active_trade.update(bar)
            if closed:
                trades.append(active_trade)
                active_trade = None
                continue
        
        if active_trade is None:
            if dc_upper[i] is None or atr_vals[i] is None or atr_vals[i] <= 0:
                continue
            if adx_vals[i] is not None and adx_vals[i] < adx_thresh:
                continue
            
            # Breakout: close above previous Donchian upper
            if dc_upper[i-1] is not None and prev['close'] > dc_upper[i-1]:
                entry_price = bar['open'] + SLIPPAGE_PTS
                risk_atr = atr_vals[i]
                stop_loss = entry_price - trail_mult * risk_atr
                
                active_trade = Trade(
                    entry_price=entry_price,
                    entry_bar=bar,
                    stop_loss=stop_loss,
                    take_profit=entry_price + 0.5 * trail_mult * risk_atr,
                    trail_mult=trail_mult,
                    atr_val=risk_atr,
                    breakeven_r=1.0,
                )
    
    if active_trade:
        active_trade.exit_price = bars[-1]['close']
        active_trade.exit_bar = bars[-1]
        active_trade._calc_pnl()
        trades.append(active_trade)
    
    return trades


def run_ema_momentum(bars, fast=12, slow=26, adx_thresh=10, trail_mult=2.5):
    """EMA crossover with ADX filter."""
    closes = [b['close'] for b in bars]
    fast_ema = ema(closes, fast)
    slow_ema = ema(closes, slow)
    adx_vals = adx(bars, 14)
    atr_vals = atr(bars, 14)
    
    trades = []
    active_trade = None
    
    for i in range(1, len(bars)):
        bar = bars[i]
        
        if active_trade:
            closed = active_trade.update(bar)
            if closed:
                trades.append(active_trade)
                active_trade = None
                continue
        
        if active_trade is None:
            if fast_ema[i] is None or slow_ema[i] is None or atr_vals[i] is None or atr_vals[i] <= 0:
                continue
            if fast_ema[i-1] is None or slow_ema[i-1] is None:
                continue
            if adx_vals[i] is not None and adx_vals[i] < adx_thresh:
                continue
            
            # EMA crossover: fast crosses above slow
            if fast_ema[i-1] <= slow_ema[i-1] and fast_ema[i] > slow_ema[i]:
                entry_price = bar['open'] + SLIPPAGE_PTS
                risk_atr = atr_vals[i]
                stop_loss = entry_price - trail_mult * risk_atr
                
                active_trade = Trade(
                    entry_price=entry_price,
                    entry_bar=bar,
                    stop_loss=stop_loss,
                    take_profit=entry_price + 0.5 * trail_mult * risk_atr,
                    trail_mult=trail_mult,
                    atr_val=risk_atr,
                    breakeven_r=1.0,
                )
    
    if active_trade:
        active_trade.exit_price = bars[-1]['close']
        active_trade.exit_bar = bars[-1]
        active_trade._calc_pnl()
        trades.append(active_trade)
    
    return trades


def run_optimized_keltner(bars):
    """Grid search over Keltner parameters."""
    best = None
    best_stats = None
    
    kc_lengths = [8, 10, 12, 15, 20]
    kc_mults = [1.0, 1.25, 1.5, 1.75, 2.0]
    trail_mults = [2.0, 2.5, 3.0, 3.5, 4.0]
    tp_rs = [0.3, 0.5, 0.7, 1.0]
    
    print("  Running grid search (500 combinations)...")
    count = 0
    for kc_len, kc_m, trail_m, tp_r in product(kc_lengths, kc_mults, trail_mults, tp_rs):
        trades = run_keltner_breakout(bars, kc_len=kc_len, kc_mult=kc_m, trail_mult=trail_m, tp_r=tp_r)
        stats = calc_stats(trades, bars)
        count += 1
        
        if stats['num_trades'] >= 20:  # Minimum trade count
            if best is None or stats['total_pnl'] > best_stats['total_pnl']:
                best = {'kc_len': kc_len, 'kc_mult': kc_m, 'trail_mult': trail_m, 'tp_r': tp_r}
                best_stats = stats
    
    print(f"  Searched {count} combinations")
    if best:
        print(f"  Best params: KC({best['kc_len']}, {best['kc_mult']}), trail={best['trail_mult']}, TP={best['tp_r']}R")
    
    return best, best_stats


def main():
    # Load data
    csv_path = DATA_DIR / "mgc_continuous_4hours.csv"
    if not csv_path.exists():
        print(f"ERROR: {csv_path} not found. Run download_history.py first.")
        return
    
    bars = load_data(csv_path)
    print(f"Loaded {len(bars)} 4H bars from {bars[0]['datetime']} to {bars[-1]['datetime']}")
    print(f"Price range: {min(b['low'] for b in bars):.1f} - {max(b['high'] for b in bars):.1f}")
    print()
    
    results = {}
    
    # a. Keltner Breakout (benchmark)
    print("1. Keltner Breakout (benchmark)...")
    trades = run_keltner_breakout(bars, kc_len=10, kc_mult=1.25, trail_mult=3.0, tp_r=0.5, be_r=1.0)
    results['Keltner Breakout'] = calc_stats(trades, bars)
    
    # b. Keltner Reentry
    print("2. Keltner Reentry x1...")
    trades = run_keltner_breakout(bars, kc_len=10, kc_mult=1.25, trail_mult=3.0, tp_r=0.5, be_r=1.0, 
                                   reentry=True, max_reentries=1)
    results['Keltner Reentry x1'] = calc_stats(trades, bars)
    
    # c. Donchian Breakout
    print("3. Donchian Breakout...")
    trades = run_donchian_breakout(bars, period=20, trail_mult=3.0)
    results['Donchian Breakout'] = calc_stats(trades, bars)
    
    # d. EMA Momentum
    print("4. EMA Momentum...")
    trades = run_ema_momentum(bars, fast=12, slow=26, trail_mult=2.5)
    results['EMA Momentum'] = calc_stats(trades, bars)
    
    # e. Keltner + Momentum Filter
    print("5. Keltner + Momentum...")
    trades = run_keltner_breakout(bars, kc_len=10, kc_mult=1.25, trail_mult=3.0, tp_r=0.5, be_r=1.0,
                                   momentum_filter=True)
    results['Keltner + Momentum'] = calc_stats(trades, bars)
    
    # f. Adaptive Keltner
    print("6. Adaptive Keltner...")
    trades = run_keltner_breakout(bars, kc_len=10, kc_mult=1.25, trail_mult=3.0, tp_r=0.5, be_r=1.0,
                                   adaptive=True)
    results['Adaptive Keltner'] = calc_stats(trades, bars)
    
    # g. Keltner + Session Filter
    print("7. Keltner + Session Filter...")
    trades = run_keltner_breakout(bars, kc_len=10, kc_mult=1.25, trail_mult=3.0, tp_r=0.5, be_r=1.0,
                                   session_filter=True)
    results['Keltner + Session'] = calc_stats(trades, bars)
    
    # h. Dual Timeframe Keltner
    print("8. Dual Timeframe Keltner...")
    trades = run_keltner_breakout(bars, kc_len=10, kc_mult=1.25, trail_mult=3.0, tp_r=0.5, be_r=1.0,
                                   dual_tf=True)
    results['Dual TF Keltner'] = calc_stats(trades, bars)
    
    # i. Inside Bar + Keltner
    print("9. Inside Bar + Keltner...")
    trades = run_keltner_breakout(bars, kc_len=10, kc_mult=1.25, trail_mult=3.0, tp_r=0.5, be_r=1.0,
                                   inside_bar=True)
    results['Inside Bar + Keltner'] = calc_stats(trades, bars)
    
    # j. Optimized Keltner
    print("10. Optimized Keltner (grid search)...")
    opt_params, opt_stats = run_optimized_keltner(bars)
    if opt_stats:
        results['Optimized Keltner'] = opt_stats
        results['Optimized Keltner']['params'] = opt_params
    
    # Print results table
    print()
    print("=" * 120)
    print(f"{'Strategy':<25} {'P&L ($)':>10} {'Trades':>8} {'Win%':>8} {'PF':>8} {'MaxDD%':>8} {'Sharpe':>8} {'AvgBars':>8}")
    print("=" * 120)
    
    # Sort by P&L
    sorted_results = sorted(results.items(), key=lambda x: x[1]['total_pnl'], reverse=True)
    
    for name, stats in sorted_results:
        print(f"{name:<25} {stats['total_pnl']:>10,.2f} {stats['num_trades']:>8} {stats['win_rate']:>7.1f}% "
              f"{stats['profit_factor']:>8.3f} {stats['max_drawdown_pct']:>7.2f}% {stats['sharpe']:>8.2f} "
              f"{stats['avg_duration_bars']:>8.1f}")
    
    print("=" * 120)
    print()
    print("BENCHMARK (TradingView): Keltner Breakout = $16,926 | 115 trades | 82.61% WR | PF 2.509 | DD 14.49%")
    print("BENCHMARK (TradingView): Keltner Reentry  = $21,448 | trades | 81% WR | PF 2.29 | DD 17.95%")
    print()
    print("NOTE: Python backtest results will differ from TradingView due to data differences,")
    print("      indicator calculation methods, and execution assumptions.")
    
    # Save results
    json_results = {}
    for name, stats in results.items():
        json_results[name] = stats
    
    with open(OUTPUT_DIR / "backtest_4h_results.json", 'w') as f:
        json.dump(json_results, f, indent=2)
    print(f"\nDetailed results saved to backtest_4h_results.json")
    
    # Save summary
    with open(OUTPUT_DIR / "backtest_4h_summary.txt", 'w') as f:
        f.write("MGC 4H Strategy Backtest Summary\n")
        f.write(f"Data: {bars[0]['datetime']} to {bars[-1]['datetime']} ({len(bars)} bars)\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"{'Strategy':<25} {'P&L ($)':>10} {'Trades':>8} {'Win%':>8} {'PF':>8} {'MaxDD%':>8} {'Sharpe':>8}\n")
        f.write("-" * 85 + "\n")
        for name, stats in sorted_results:
            f.write(f"{name:<25} {stats['total_pnl']:>10,.2f} {stats['num_trades']:>8} {stats['win_rate']:>7.1f}% "
                    f"{stats['profit_factor']:>8.3f} {stats['max_drawdown_pct']:>7.2f}% {stats['sharpe']:>8.2f}\n")
        f.write("\n")
        if opt_params:
            f.write(f"Optimized params: KC({opt_params['kc_len']}, {opt_params['kc_mult']}), "
                    f"trail={opt_params['trail_mult']}, TP={opt_params['tp_r']}R\n")
    print(f"Summary saved to backtest_4h_summary.txt")
    
    # Generate Pine Scripts for top strategies
    generate_pine_scripts(sorted_results, opt_params)
    
    return sorted_results


def generate_pine_scripts(sorted_results, opt_params=None):
    """Generate Pine Script v5 for top strategies."""
    
    # Always generate for Keltner Reentry (the known best variant)
    pine_reentry = '''//@version=5
strategy("MGC Keltner Reentry x1", overlay=true, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, commission_type=strategy.commission.cash_per_order, commission_value=0.62, slippage=1)

// Inputs
kcLen = input.int(10, "KC Length")
kcMult = input.float(1.25, "KC Multiplier")
adxThresh = input.float(10, "ADX Threshold")
trailMult = input.float(3.0, "Trail ATR Mult")
tpR = input.float(0.5, "Take Profit (R)")
beR = input.float(1.0, "Breakeven (R)")
maxReentries = input.int(1, "Max Re-entries")

// Keltner Channel
basis = ta.ema(close, kcLen)
atrVal = ta.atr(kcLen)
upper = basis + kcMult * atrVal
lower = basis - kcMult * atrVal

// ADX
[diPlus, diMinus, adxVal] = ta.dmi(14, 14)

// Plots
plot(basis, "Basis", color.gray)
p1 = plot(upper, "Upper", color.blue)
p2 = plot(lower, "Lower", color.blue)
fill(p1, p2, color=color.new(color.blue, 90))

// State
var int reentryCount = 0
var bool lastWasStopped = false

// Entry
longSignal = close[1] > upper[1] and adxVal > adxThresh
reentrySignal = lastWasStopped and close[1] > upper[1] and reentryCount < maxReentries

if (longSignal or reentrySignal) and strategy.position_size == 0
    risk = trailMult * atrVal
    sl = close - risk
    tp = close + tpR * risk
    strategy.entry("Long", strategy.long)
    strategy.exit("Exit", "Long", stop=sl, limit=tp, trail_points=risk / syminfo.mintick, trail_offset=risk / syminfo.mintick)
    if reentrySignal
        reentryCount += 1
    else
        reentryCount := 0

// Track stops
if strategy.position_size == 0 and strategy.position_size[1] > 0
    lastWasStopped := strategy.closedtrades.profit(strategy.closedtrades.size - 1) <= 0
'''
    
    with open(OUTPUT_DIR / "keltner_reentry_4h.pine", 'w') as f:
        f.write(pine_reentry)
    print("Saved keltner_reentry_4h.pine")
    
    # Generate for optimized if params exist
    if opt_params:
        pine_opt = f'''//@version=5
strategy("MGC Optimized Keltner", overlay=true, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, commission_type=strategy.commission.cash_per_order, commission_value=0.62, slippage=1)

// Optimized Parameters
kcLen = input.int({opt_params['kc_len']}, "KC Length")
kcMult = input.float({opt_params['kc_mult']}, "KC Multiplier")
adxThresh = input.float(10, "ADX Threshold")
trailMult = input.float({opt_params['trail_mult']}, "Trail ATR Mult")
tpR = input.float({opt_params['tp_r']}, "Take Profit (R)")
beR = input.float(1.0, "Breakeven (R)")

// Keltner Channel
basis = ta.ema(close, kcLen)
atrVal = ta.atr(kcLen)
upper = basis + kcMult * atrVal
lower = basis - kcMult * atrVal

// ADX
[diPlus, diMinus, adxVal] = ta.dmi(14, 14)

// Plots
plot(basis, "Basis", color.gray)
p1 = plot(upper, "Upper", color.orange)
p2 = plot(lower, "Lower", color.orange)
fill(p1, p2, color=color.new(color.orange, 90))

// Entry
longSignal = close[1] > upper[1] and adxVal > adxThresh

if longSignal and strategy.position_size == 0
    risk = trailMult * atrVal
    sl = close - risk
    tp = close + tpR * risk
    strategy.entry("Long", strategy.long)
    strategy.exit("Exit", "Long", stop=sl, limit=tp, trail_points=risk / syminfo.mintick, trail_offset=risk / syminfo.mintick)
'''
        with open(OUTPUT_DIR / "keltner_optimized_4h.pine", 'w') as f:
            f.write(pine_opt)
        print("Saved keltner_optimized_4h.pine")


if __name__ == "__main__":
    main()
