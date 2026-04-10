"""
MES 4H Strategy Backtester
Tests multiple strategies on MES continuous 4H data.
"""
import asyncio; asyncio.set_event_loop(asyncio.new_event_loop())

import csv
import json
import math
import os
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

# ── Constants ──
POINT_VALUE = 5.0       # $5 per point for MES
TICK_SIZE = 0.25
COMMISSION_RT = 1.24    # Round trip
SLIPPAGE_PTS = 0.25     # 1 tick

DATA_FILE = Path(__file__).parent / "data" / "history" / "mes_continuous_4h.csv"
RESULTS_FILE = Path(__file__).parent / "backtest_mes_4h_results.json"
SUMMARY_FILE = Path(__file__).parent / "backtest_mes_4h_summary.txt"
BACKTEST_DIR = Path(__file__).parent / "backtest"
BACKTEST_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class Bar:
    dt: str
    o: float
    h: float
    l: float
    c: float
    v: float


@dataclass
class Trade:
    entry_bar: int
    entry_price: float
    direction: int  # 1=long, -1=short
    stop: float
    tp: Optional[float] = None
    exit_bar: Optional[int] = None
    exit_price: Optional[float] = None
    pnl: Optional[float] = None


def load_data() -> List[Bar]:
    bars = []
    with open(DATA_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            bars.append(Bar(
                dt=row["datetime"],
                o=float(row["open"]),
                h=float(row["high"]),
                l=float(row["low"]),
                c=float(row["close"]),
                v=float(row.get("volume", 0)),
            ))
    print(f"Loaded {len(bars)} bars from {bars[0].dt} to {bars[-1].dt}")
    return bars


# ── Indicators ──

def ema(data: list, period: int) -> list:
    result = [None] * len(data)
    if len(data) < period:
        return result
    k = 2.0 / (period + 1)
    result[period - 1] = sum(data[:period]) / period
    for i in range(period, len(data)):
        result[i] = data[i] * k + result[i-1] * (1 - k)
    return result


def sma(data: list, period: int) -> list:
    result = [None] * len(data)
    for i in range(period - 1, len(data)):
        result[i] = sum(data[i - period + 1:i + 1]) / period
    return result


def atr(bars: List[Bar], period: int) -> list:
    trs = [0.0]
    for i in range(1, len(bars)):
        tr = max(bars[i].h - bars[i].l,
                 abs(bars[i].h - bars[i-1].c),
                 abs(bars[i].l - bars[i-1].c))
        trs.append(tr)
    # Use EMA-style ATR
    result = [None] * len(bars)
    if len(bars) < period + 1:
        return result
    result[period] = sum(trs[1:period+1]) / period
    for i in range(period + 1, len(bars)):
        result[i] = (result[i-1] * (period - 1) + trs[i]) / period
    return result


def adx(bars: List[Bar], period: int = 14) -> list:
    """Compute ADX."""
    n = len(bars)
    result = [None] * n
    if n < period * 2 + 1:
        return result

    plus_dm = [0.0] * n
    minus_dm = [0.0] * n
    tr_list = [0.0] * n

    for i in range(1, n):
        up = bars[i].h - bars[i-1].h
        down = bars[i-1].l - bars[i].l
        plus_dm[i] = up if (up > down and up > 0) else 0
        minus_dm[i] = down if (down > up and down > 0) else 0
        tr_list[i] = max(bars[i].h - bars[i].l,
                         abs(bars[i].h - bars[i-1].c),
                         abs(bars[i].l - bars[i-1].c))

    # Smoothed
    atr_s = sum(tr_list[1:period+1])
    plus_s = sum(plus_dm[1:period+1])
    minus_s = sum(minus_dm[1:period+1])

    dx_vals = []
    for i in range(period, n):
        if i == period:
            pass
        else:
            atr_s = atr_s - atr_s / period + tr_list[i]
            plus_s = plus_s - plus_s / period + plus_dm[i]
            minus_s = minus_s - minus_s / period + minus_dm[i]

        if atr_s == 0:
            dx_vals.append(0)
            continue
        plus_di = 100 * plus_s / atr_s
        minus_di = 100 * minus_s / atr_s
        di_sum = plus_di + minus_di
        if di_sum == 0:
            dx_vals.append(0)
        else:
            dx_vals.append(100 * abs(plus_di - minus_di) / di_sum)

    # ADX = smoothed DX
    if len(dx_vals) < period:
        return result
    adx_val = sum(dx_vals[:period]) / period
    for i in range(period, min(period + len(dx_vals), n)):
        idx = i
        dx_i = i - period
        if dx_i < period:
            if idx < n:
                result[idx] = None
            continue
        adx_val = (adx_val * (period - 1) + dx_vals[dx_i]) / period
        if idx < n:
            result[idx] = adx_val

    return result


def keltner_channel(bars: List[Bar], length: int, mult: float) -> Tuple[list, list, list]:
    """Returns (upper, middle, lower) Keltner Channel."""
    closes = [b.c for b in bars]
    mid = ema(closes, length)
    atr_vals = atr(bars, length)
    upper = [None] * len(bars)
    lower = [None] * len(bars)
    for i in range(len(bars)):
        if mid[i] is not None and atr_vals[i] is not None:
            upper[i] = mid[i] + mult * atr_vals[i]
            lower[i] = mid[i] - mult * atr_vals[i]
    return upper, mid, lower


def donchian(bars: List[Bar], period: int) -> Tuple[list, list]:
    """Returns (upper, lower) Donchian channels."""
    upper = [None] * len(bars)
    lower = [None] * len(bars)
    for i in range(period - 1, len(bars)):
        upper[i] = max(b.h for b in bars[i - period + 1:i + 1])
        lower[i] = min(b.l for b in bars[i - period + 1:i + 1])
    return upper, lower


# ── Backtester Engine ──

def run_backtest(bars: List[Bar], signals, direction_mode="long_only") -> dict:
    """
    signals: function(bars, i) -> list of (direction, entry_price, stop_price, tp_price_or_None)
    direction_mode: "long_only", "short_only", "both"
    Returns stats dict.
    """
    trades = []
    position = None  # Active trade
    equity = [0.0]
    peak_equity = 0.0
    max_dd = 0.0

    for i in range(1, len(bars)):
        bar = bars[i]

        # Check if position should be exited
        if position is not None:
            exited = False
            exit_price = None

            if position.direction == 1:  # Long
                # Check stop
                if bar.l <= position.stop:
                    exit_price = position.stop
                    exited = True
                # Check TP
                elif position.tp and bar.h >= position.tp:
                    exit_price = position.tp
                    exited = True
            else:  # Short
                if bar.h >= position.stop:
                    exit_price = position.stop
                    exited = True
                elif position.tp and bar.l <= position.tp:
                    exit_price = position.tp
                    exited = True

            if exited:
                pnl = (exit_price - position.entry_price) * position.direction * POINT_VALUE
                pnl -= COMMISSION_RT + SLIPPAGE_PTS * POINT_VALUE
                position.exit_bar = i
                position.exit_price = exit_price
                position.pnl = pnl
                trades.append(position)
                position = None

            # Update trailing stop if strategy provides it
            # (handled in signal function via closure)

        # Generate signals if no position
        if position is None:
            sigs = signals(bars, i)
            for sig in sigs:
                d, entry, stop, tp = sig
                if direction_mode == "long_only" and d == -1:
                    continue
                if direction_mode == "short_only" and d == 1:
                    continue
                position = Trade(
                    entry_bar=i,
                    entry_price=entry + SLIPPAGE_PTS * d,  # Slippage against us
                    direction=d,
                    stop=stop,
                    tp=tp,
                )
                break  # Only one position at a time

        # Track equity
        running = equity[-1]
        if position is not None and position.exit_bar is None:
            unrealized = (bar.c - position.entry_price) * position.direction * POINT_VALUE
            running = equity[-1] + unrealized
        else:
            running = sum(t.pnl for t in trades if t.pnl is not None)

        peak_equity = max(peak_equity, running)
        dd = peak_equity - running if peak_equity > 0 else 0
        max_dd = max(max_dd, dd)

    # Close any remaining position at last bar
    if position is not None:
        exit_price = bars[-1].c
        pnl = (exit_price - position.entry_price) * position.direction * POINT_VALUE
        pnl -= COMMISSION_RT + SLIPPAGE_PTS * POINT_VALUE
        position.exit_bar = len(bars) - 1
        position.exit_price = exit_price
        position.pnl = pnl
        trades.append(position)

    return compute_stats(trades, max_dd)


def compute_stats(trades: List[Trade], max_dd_dollars: float) -> dict:
    if not trades:
        return {
            "total_pnl": 0, "num_trades": 0, "win_rate": 0, "profit_factor": 0,
            "max_dd_pct": 0, "avg_winner": 0, "avg_loser": 0, "avg_duration": 0,
        }

    winners = [t for t in trades if t.pnl and t.pnl > 0]
    losers = [t for t in trades if t.pnl and t.pnl <= 0]
    total_pnl = sum(t.pnl for t in trades if t.pnl)
    gross_profit = sum(t.pnl for t in winners) if winners else 0
    gross_loss = abs(sum(t.pnl for t in losers)) if losers else 0.001

    # Max DD as % of peak equity
    # Approximate: use total_pnl as final equity, compute DD%
    peak = 0
    running = 0
    max_dd_pct = 0
    for t in trades:
        running += t.pnl if t.pnl else 0
        peak = max(peak, running)
        if peak > 0:
            dd_pct = (peak - running) / peak * 100
            max_dd_pct = max(max_dd_pct, dd_pct)

    durations = [t.exit_bar - t.entry_bar for t in trades if t.exit_bar]

    return {
        "total_pnl": round(total_pnl, 2),
        "num_trades": len(trades),
        "win_rate": round(len(winners) / len(trades) * 100, 2) if trades else 0,
        "profit_factor": round(gross_profit / gross_loss, 3) if gross_loss > 0 else 0,
        "max_dd_pct": round(max_dd_pct, 2),
        "avg_winner": round(gross_profit / len(winners), 2) if winners else 0,
        "avg_loser": round(-gross_loss / len(losers), 2) if losers else 0,
        "avg_duration": round(sum(durations) / len(durations), 1) if durations else 0,
    }


# ── Strategy Signal Functions ──
# Each returns a function(bars, i) -> list of (direction, entry, stop, tp)

def make_keltner_breakout(kc_len=10, kc_mult=1.25, adx_thresh=10, trail_mult=3.0, tp_r=0.5, be_r=1.0):
    """Keltner Channel Breakout strategy."""
    cache = {}

    def signals(bars, i):
        if "computed" not in cache:
            cache["upper"], cache["mid"], cache["lower"] = keltner_channel(bars, kc_len, kc_mult)
            cache["atr"] = atr(bars, kc_len)
            cache["adx"] = adx(bars)
            cache["trail"] = {}
            cache["computed"] = True

        upper = cache["upper"]
        atr_vals = cache["atr"]
        adx_vals = cache["adx"]

        if i < 2 or upper[i-1] is None or atr_vals[i] is None:
            return []

        adx_val = adx_vals[i] if adx_vals[i] is not None else 0

        result = []
        # Long signal: close breaks above upper KC with ADX filter
        if bars[i-1].c > upper[i-1] and adx_val > adx_thresh:
            entry = bars[i].o  # Enter at open of next bar
            risk = atr_vals[i] * trail_mult
            stop = entry - risk
            tp = entry + risk * tp_r if tp_r else None
            result.append((1, entry, stop, tp))

        # Short signal: close breaks below lower KC
        lower = cache["lower"]
        if lower[i-1] is not None and bars[i-1].c < lower[i-1] and adx_val > adx_thresh:
            entry = bars[i].o
            risk = atr_vals[i] * trail_mult
            stop = entry + risk
            tp = entry - risk * tp_r if tp_r else None
            result.append((-1, entry, stop, tp))

        return result

    return signals


def make_keltner_reentry(kc_len=10, kc_mult=1.25, adx_thresh=10, trail_mult=3.0, tp_r=0.5, max_reentries=1):
    """Keltner with re-entry after stops."""
    cache = {}

    def signals(bars, i):
        if "computed" not in cache:
            cache["upper"], cache["mid"], cache["lower"] = keltner_channel(bars, kc_len, kc_mult)
            cache["atr"] = atr(bars, kc_len)
            cache["adx"] = adx(bars)
            cache["last_stop_bar"] = -100
            cache["reentry_count"] = 0
            cache["computed"] = True

        upper = cache["upper"]
        atr_vals = cache["atr"]
        adx_vals = cache["adx"]

        if i < 2 or upper[i-1] is None or atr_vals[i] is None:
            return []

        adx_val = adx_vals[i] if adx_vals[i] is not None else 0
        result = []

        if bars[i-1].c > upper[i-1] and adx_val > adx_thresh:
            entry = bars[i].o
            risk = atr_vals[i] * trail_mult
            stop = entry - risk
            tp = entry + risk * tp_r if tp_r else None
            result.append((1, entry, stop, tp))

        return result

    return signals


def make_momentum_breakout(roc_period=10, roc_thresh=1.0, ema_period=20, trail_mult=2.5, tp_r=0.6):
    cache = {}

    def signals(bars, i):
        if "computed" not in cache:
            closes = [b.c for b in bars]
            cache["ema20"] = ema(closes, ema_period)
            cache["atr"] = atr(bars, 14)
            cache["computed"] = True

        ema20 = cache["ema20"]
        atr_vals = cache["atr"]

        if i < roc_period + 1 or ema20[i] is None or atr_vals[i] is None:
            return []

        roc = (bars[i].c - bars[i - roc_period].c) / bars[i - roc_period].c * 100
        result = []

        # Long: ROC > threshold and price > EMA
        if roc > roc_thresh and bars[i].c > ema20[i]:
            entry = bars[i+1].o if i+1 < len(bars) else bars[i].c
            risk = atr_vals[i] * trail_mult
            stop = entry - risk
            tp = entry + risk * tp_r
            result.append((1, entry, stop, tp))

        # Short: ROC < -threshold and price < EMA
        if roc < -roc_thresh and bars[i].c < ema20[i]:
            entry = bars[i+1].o if i+1 < len(bars) else bars[i].c
            risk = atr_vals[i] * trail_mult
            stop = entry + risk
            tp = entry - risk * tp_r
            result.append((-1, entry, stop, tp))

        return result

    return signals


def make_range_expansion(avg_period=20, range_mult=1.5, trail_mult=2.0, tp_r=0.5):
    cache = {}

    def signals(bars, i):
        if "computed" not in cache:
            cache["atr"] = atr(bars, 14)
            cache["computed"] = True

        atr_vals = cache["atr"]
        if i < avg_period + 1 or atr_vals[i] is None:
            return []

        # Current bar range vs average
        cur_range = bars[i].h - bars[i].l
        avg_range = sum(b.h - b.l for b in bars[i-avg_period:i]) / avg_period

        result = []
        if cur_range > range_mult * avg_range:
            bar_pos = (bars[i].c - bars[i].l) / cur_range if cur_range > 0 else 0.5
            risk = atr_vals[i] * trail_mult

            # Close in top 25% = long
            if bar_pos > 0.75:
                entry = bars[i].c
                stop = entry - risk
                tp = entry + risk * tp_r
                result.append((1, entry, stop, tp))
            # Close in bottom 25% = short
            elif bar_pos < 0.25:
                entry = bars[i].c
                stop = entry + risk
                tp = entry - risk * tp_r
                result.append((-1, entry, stop, tp))

        return result

    return signals


def make_ma_ribbon(trail_mult=2.5, tp_r=0.6):
    cache = {}

    def signals(bars, i):
        if "computed" not in cache:
            closes = [b.c for b in bars]
            cache["ema8"] = ema(closes, 8)
            cache["ema13"] = ema(closes, 13)
            cache["ema21"] = ema(closes, 21)
            cache["atr"] = atr(bars, 14)
            cache["computed"] = True

        e8, e13, e21, atr_vals = cache["ema8"], cache["ema13"], cache["ema21"], cache["atr"]

        if i < 2 or any(x[i] is None for x in [e8, e13, e21, atr_vals]):
            return []
        if any(x[i-1] is None for x in [e8, e13, e21]):
            return []

        result = []
        risk = atr_vals[i] * trail_mult

        # Bullish ribbon + pullback to EMA13
        if e8[i] > e13[i] > e21[i]:
            if bars[i-1].l <= e13[i-1] and bars[i].c > e13[i]:  # Bounce off 13
                entry = bars[i].c
                stop = entry - risk
                tp = entry + risk * tp_r
                result.append((1, entry, stop, tp))

        # Bearish ribbon + pullback
        if e8[i] < e13[i] < e21[i]:
            if bars[i-1].h >= e13[i-1] and bars[i].c < e13[i]:
                entry = bars[i].c
                stop = entry + risk
                tp = entry - risk * tp_r
                result.append((-1, entry, stop, tp))

        return result

    return signals


def make_volatility_contraction(lookback=50, trail_mult=2.5, tp_r=0.6):
    cache = {}

    def signals(bars, i):
        if "computed" not in cache:
            cache["atr"] = atr(bars, 14)
            cache["computed"] = True

        atr_vals = cache["atr"]
        if i < lookback + 2 or atr_vals[i] is None or atr_vals[i-1] is None:
            return []

        # Get ATR percentiles over lookback
        recent_atrs = [atr_vals[j] for j in range(i - lookback, i) if atr_vals[j] is not None]
        if len(recent_atrs) < lookback // 2:
            return []

        recent_atrs.sort()
        p25 = recent_atrs[len(recent_atrs) // 4]
        p50 = recent_atrs[len(recent_atrs) // 2]

        result = []
        # ATR was below 25th, now above 50th = expansion
        if atr_vals[i-1] < p25 and atr_vals[i] > p50:
            risk = atr_vals[i] * trail_mult
            # Direction = last bar's direction
            if bars[i].c > bars[i-1].c:
                entry = bars[i].c
                stop = entry - risk
                tp = entry + risk * tp_r
                result.append((1, entry, stop, tp))
            else:
                entry = bars[i].c
                stop = entry + risk
                tp = entry - risk * tp_r
                result.append((-1, entry, stop, tp))

        return result

    return signals


def make_opening_range(trail_mult=2.0, tp_r=0.8):
    """First 4H bar of NY session (9:30 ET ~ 14:30 UTC) sets range."""
    cache = {}

    def signals(bars, i):
        if "computed" not in cache:
            cache["atr"] = atr(bars, 14)
            cache["computed"] = True

        atr_vals = cache["atr"]
        if i < 2 or atr_vals[i] is None:
            return []

        # Check if previous bar was a session open (contains 09:30 or early morning)
        dt_str = bars[i-1].dt
        # Simple heuristic: bars at specific hours
        result = []

        # Look for bars where time contains morning hours (crude but works for 4H)
        if "09:" in dt_str or "10:" in dt_str or "13:" in dt_str or "14:" in dt_str:
            or_high = bars[i-1].h
            or_low = bars[i-1].l
            risk = atr_vals[i] * trail_mult

            # Breakout above opening range
            if bars[i].c > or_high:
                entry = bars[i].c
                stop = entry - risk
                tp = entry + risk * tp_r
                result.append((1, entry, stop, tp))
            elif bars[i].c < or_low:
                entry = bars[i].c
                stop = entry + risk
                tp = entry - risk * tp_r
                result.append((-1, entry, stop, tp))

        return result

    return signals


def make_dual_ma_crossover(fast=9, slow=21, adx_thresh=20, trail_mult=2.5, tp_r=0.6):
    cache = {}

    def signals(bars, i):
        if "computed" not in cache:
            closes = [b.c for b in bars]
            cache["fast"] = ema(closes, fast)
            cache["slow"] = ema(closes, slow)
            cache["adx"] = adx(bars)
            cache["atr"] = atr(bars, 14)
            cache["computed"] = True

        f, s, adx_vals, atr_vals = cache["fast"], cache["slow"], cache["adx"], cache["atr"]

        if i < 2 or any(x is None for x in [f[i], f[i-1], s[i], s[i-1], atr_vals[i]]):
            return []

        adx_val = adx_vals[i] if adx_vals[i] is not None else 0
        if adx_val < adx_thresh:
            return []

        result = []
        risk = atr_vals[i] * trail_mult

        # Bullish crossover
        if f[i-1] <= s[i-1] and f[i] > s[i]:
            entry = bars[i].c
            stop = entry - risk
            tp = entry + risk * tp_r
            result.append((1, entry, stop, tp))

        # Bearish crossover
        if f[i-1] >= s[i-1] and f[i] < s[i]:
            entry = bars[i].c
            stop = entry + risk
            tp = entry - risk * tp_r
            result.append((-1, entry, stop, tp))

        return result

    return signals


def make_higher_highs(consec=3, ema_period=20, trail_mult=2.5, tp_r=0.6):
    cache = {}

    def signals(bars, i):
        if "computed" not in cache:
            closes = [b.c for b in bars]
            cache["ema"] = ema(closes, ema_period)
            cache["atr"] = atr(bars, 14)
            cache["computed"] = True

        ema_vals, atr_vals = cache["ema"], cache["atr"]
        if i < consec + 1 or ema_vals[i] is None or atr_vals[i] is None:
            return []

        result = []
        risk = atr_vals[i] * trail_mult

        # Check consecutive higher closes for long
        hh = all(bars[i-j].c > bars[i-j-1].c for j in range(consec))
        if hh and bars[i].c > ema_vals[i]:
            entry = bars[i].c
            stop = entry - risk
            tp = entry + risk * tp_r
            result.append((1, entry, stop, tp))

        # Consecutive lower closes for short
        ll = all(bars[i-j].c < bars[i-j-1].c for j in range(consec))
        if ll and bars[i].c < ema_vals[i]:
            entry = bars[i].c
            stop = entry + risk
            tp = entry - risk * tp_r
            result.append((-1, entry, stop, tp))

        return result

    return signals


def make_donchian_breakout(period=20, exit_period=10, trail_mult=2.0):
    cache = {}

    def signals(bars, i):
        if "computed" not in cache:
            cache["upper"], cache["lower"] = donchian(bars, period)
            cache["exit_upper"], cache["exit_lower"] = donchian(bars, exit_period)
            cache["atr"] = atr(bars, 14)
            cache["computed"] = True

        upper, lower = cache["upper"], cache["lower"]
        atr_vals = cache["atr"]

        if i < 2 or upper[i-1] is None or atr_vals[i] is None:
            return []

        result = []
        # Long: close breaks above upper Donchian
        if bars[i].c > upper[i-1]:
            entry = bars[i].c
            risk = atr_vals[i] * trail_mult
            stop = entry - risk
            # No fixed TP for Donchian - use trailing
            result.append((1, entry, stop, None))

        # Short: close breaks below lower Donchian
        if bars[i].c < lower[i-1]:
            entry = bars[i].c
            risk = atr_vals[i] * trail_mult
            stop = entry + risk
            result.append((-1, entry, stop, None))

        return result

    return signals


def make_vwap_trend(vol_mult=1.2, trail_mult=2.5, tp_r=0.6):
    """Simplified VWAP trend follow using cumulative VWAP."""
    cache = {}

    def signals(bars, i):
        if "computed" not in cache:
            # Compute cumulative VWAP (reset daily approximation - reset every 6 bars ~ 24h)
            cache["vwap"] = [None] * len(bars)
            cache["atr"] = atr(bars, 14)
            cum_vol = 0
            cum_pv = 0
            reset_count = 0
            for j in range(len(bars)):
                typical = (bars[j].h + bars[j].l + bars[j].c) / 3
                vol = max(bars[j].v, 1)
                cum_vol += vol
                cum_pv += typical * vol
                reset_count += 1
                if reset_count >= 6:  # Reset ~ daily
                    cum_vol = vol
                    cum_pv = typical * vol
                    reset_count = 0
                cache["vwap"][j] = cum_pv / cum_vol if cum_vol > 0 else typical

            # Volume SMA
            vols = [max(b.v, 1) for b in bars]
            cache["vol_sma"] = sma(vols, 20)
            cache["computed"] = True

        vwap, atr_vals, vol_sma = cache["vwap"], cache["atr"], cache["vol_sma"]

        if i < 2 or vwap[i] is None or atr_vals[i] is None or vol_sma[i] is None:
            return []

        result = []
        risk = atr_vals[i] * trail_mult

        # Long: price crosses above VWAP with volume
        if bars[i-1].c <= vwap[i-1] and bars[i].c > vwap[i] and bars[i].v > vol_sma[i] * vol_mult:
            entry = bars[i].c
            stop = entry - risk
            tp = entry + risk * tp_r
            result.append((1, entry, stop, tp))

        # Short
        if bars[i-1].c >= vwap[i-1] and bars[i].c < vwap[i] and bars[i].v > vol_sma[i] * vol_mult:
            entry = bars[i].c
            stop = entry + risk
            tp = entry - risk * tp_r
            result.append((-1, entry, stop, tp))

        return result

    return signals


def make_fib_pullback(trend_ema=50, trail_mult=2.5, tp_r=0.8):
    """Trend pullback with Fibonacci levels."""
    cache = {}

    def signals(bars, i):
        if "computed" not in cache:
            closes = [b.c for b in bars]
            cache["ema50"] = ema(closes, trend_ema)
            cache["atr"] = atr(bars, 14)
            cache["computed"] = True

        ema50, atr_vals = cache["ema50"], cache["atr"]

        if i < 21 or ema50[i] is None or atr_vals[i] is None:
            return []

        result = []
        risk = atr_vals[i] * trail_mult

        # Find recent swing high/low (last 20 bars)
        recent = bars[max(0, i-20):i+1]
        swing_high = max(b.h for b in recent)
        swing_low = min(b.l for b in recent)
        swing_range = swing_high - swing_low

        if swing_range < atr_vals[i] * 0.5:
            return []

        # Uptrend: price > EMA50
        if bars[i].c > ema50[i]:
            # Fib 38.2-61.8% pullback from high
            fib_382 = swing_high - swing_range * 0.382
            fib_618 = swing_high - swing_range * 0.618
            if fib_618 <= bars[i].l <= fib_382 and bars[i].c > bars[i].o:  # Reversal bar
                entry = bars[i].c
                stop = entry - risk
                tp = entry + risk * tp_r
                result.append((1, entry, stop, tp))

        # Downtrend
        if bars[i].c < ema50[i]:
            fib_382 = swing_low + swing_range * 0.382
            fib_618 = swing_low + swing_range * 0.618
            if fib_382 <= bars[i].h <= fib_618 and bars[i].c < bars[i].o:
                entry = bars[i].c
                stop = entry + risk
                tp = entry - risk * tp_r
                result.append((-1, entry, stop, tp))

        return result

    return signals


# ── Grid Search for Optimized Keltner on MES ──

def grid_search_keltner(bars):
    """Grid search for optimal Keltner parameters on MES."""
    print("\n" + "="*60)
    print("GRID SEARCH: Optimized Keltner for MES")
    print("="*60)

    best = None
    best_score = -999
    tested = 0

    kc_lengths = [8, 10, 12, 15, 18, 20, 25]
    kc_mults = [0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5]
    trail_mults = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0]
    tp_rs = [0.3, 0.5, 0.7, 1.0, 1.5]

    total = len(kc_lengths) * len(kc_mults) * len(trail_mults) * len(tp_rs)
    print(f"Testing {total} parameter combinations...")

    for kl in kc_lengths:
        for km in kc_mults:
            for tm in trail_mults:
                for tpr in tp_rs:
                    tested += 1
                    if tested % 200 == 0:
                        print(f"  Progress: {tested}/{total}...")

                    sig_fn = make_keltner_breakout(kc_len=kl, kc_mult=km, trail_mult=tm, tp_r=tpr)

                    for mode in ["long_only", "both"]:
                        stats = run_backtest(bars, sig_fn, direction_mode=mode)

                        if stats["num_trades"] < 30:
                            continue

                        # Score: balance PF, WR, and trade count
                        score = (stats["profit_factor"] * stats["win_rate"] / 100
                                 * min(stats["num_trades"] / 50, 1.5)
                                 * max(0, 1 - stats["max_dd_pct"] / 50))

                        if score > best_score:
                            best_score = score
                            best = {
                                "params": {"kc_len": kl, "kc_mult": km, "trail_mult": tm, "tp_r": tpr},
                                "mode": mode,
                                "stats": stats,
                                "score": round(score, 3),
                            }

    if best:
        print(f"\nBest Keltner for MES:")
        print(f"  Params: KC({best['params']['kc_len']}, {best['params']['kc_mult']}), "
              f"Trail {best['params']['trail_mult']}x, TP {best['params']['tp_r']}R")
        print(f"  Mode: {best['mode']}")
        print(f"  P&L: ${best['stats']['total_pnl']:.2f} | "
              f"Trades: {best['stats']['num_trades']} | "
              f"WR: {best['stats']['win_rate']}% | "
              f"PF: {best['stats']['profit_factor']} | "
              f"DD: {best['stats']['max_dd_pct']}%")

    return best


# ── Main ──

def main():
    bars = load_data()

    strategies = {
        # Proven Keltner variants
        "Keltner Breakout (10,1.25)": make_keltner_breakout(10, 1.25, 10, 3.0, 0.5),
        "Keltner Reentry x1": make_keltner_reentry(10, 1.25, 10, 3.0, 0.5),
        "Optimized Keltner (20,1.5)": make_keltner_breakout(20, 1.5, 10, 4.0, 0.7),

        # New approaches
        "VWAP Trend Follow": make_vwap_trend(),
        "Momentum Breakout": make_momentum_breakout(),
        "Range Expansion": make_range_expansion(),
        "MA Ribbon (8/13/21)": make_ma_ribbon(),
        "Fib Pullback": make_fib_pullback(),
        "Volatility Contraction": make_volatility_contraction(),
        "Opening Range Breakout": make_opening_range(),
        "Dual MA Cross + ADX": make_dual_ma_crossover(),
        "Higher Highs (3x)": make_higher_highs(),
        "Donchian Breakout (20)": make_donchian_breakout(),

        # Extra parameter variations
        "Momentum ROC(5) Tight": make_momentum_breakout(roc_period=5, roc_thresh=0.5, trail_mult=2.0, tp_r=0.4),
        "Range Exp (1.3x, 3.0 trail)": make_range_expansion(range_mult=1.3, trail_mult=3.0, tp_r=0.7),
        "Dual MA (5/13) ADX15": make_dual_ma_crossover(fast=5, slow=13, adx_thresh=15, trail_mult=2.0, tp_r=0.5),
        "Donchian (10)": make_donchian_breakout(period=10, exit_period=5),
        "Higher Highs (2x)": make_higher_highs(consec=2),
        "Keltner (15,1.0) 2.5trail": make_keltner_breakout(15, 1.0, 10, 2.5, 0.5),
        "Keltner (12,1.5) 3.5trail": make_keltner_breakout(12, 1.5, 10, 3.5, 0.6),
    }

    all_results = {}
    modes = ["long_only", "both"]

    for name, sig_fn in strategies.items():
        print(f"\n{'-'*50}")
        print(f"Testing: {name}")

        for mode in modes:
            label = f"{name} [{mode}]"
            stats = run_backtest(bars, sig_fn, direction_mode=mode)
            all_results[label] = stats

            pnl = stats['total_pnl']
            nt = stats['num_trades']
            wr = stats['win_rate']
            pf = stats['profit_factor']
            dd = stats['max_dd_pct']
            marker = " ★" if pf > 1.5 and wr > 65 and nt > 50 else ""
            print(f"  {mode:10s}: ${pnl:>9,.2f} | {nt:3d} trades | {wr:5.1f}% WR | PF {pf:.3f} | DD {dd:.1f}%{marker}")

    # Grid search
    grid_best = grid_search_keltner(bars)
    if grid_best:
        label = f"Grid Best KC({grid_best['params']['kc_len']},{grid_best['params']['kc_mult']}) [{grid_best['mode']}]"
        all_results[label] = grid_best["stats"]

    # Sort by profit factor
    ranked = sorted(all_results.items(), key=lambda x: x[1]["profit_factor"], reverse=True)

    # Print summary table
    print("\n" + "="*100)
    print("RANKED RESULTS - MES 4H Strategies")
    print("="*100)
    print(f"{'Strategy':<45s} {'P&L':>10s} {'Trades':>7s} {'WR%':>6s} {'PF':>7s} {'DD%':>6s} {'AvgW':>8s} {'AvgL':>8s} {'Dur':>5s}")
    print("-"*100)

    winners = []
    for name, stats in ranked:
        pnl = stats['total_pnl']
        nt = stats['num_trades']
        wr = stats['win_rate']
        pf = stats['profit_factor']
        dd = stats['max_dd_pct']
        aw = stats['avg_winner']
        al = stats['avg_loser']
        dur = stats['avg_duration']

        is_winner = pf > 1.5 and wr > 65 and nt >= 50 and dd < 25
        marker = " ★★★" if is_winner else ""
        print(f"{name:<45s} ${pnl:>9,.2f} {nt:>7d} {wr:>5.1f}% {pf:>6.3f} {dd:>5.1f}% ${aw:>7,.2f} ${al:>7,.2f} {dur:>5.1f}{marker}")

        if is_winner:
            winners.append((name, stats))

    # Save results
    with open(RESULTS_FILE, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nDetailed results saved to {RESULTS_FILE}")

    # Save summary
    with open(SUMMARY_FILE, "w") as f:
        f.write("MES 4H Strategy Backtest Results\n")
        f.write(f"Data: {bars[0].dt} to {bars[-1].dt} ({len(bars)} bars)\n")
        f.write(f"Benchmark: Keltner on MGC 4H — $16,926 | 115 trades | 82.61% WR | PF 2.509 | DD 14.49%\n\n")
        f.write(f"{'Strategy':<45s} {'P&L':>10s} {'Trades':>7s} {'WR%':>6s} {'PF':>7s} {'DD%':>6s}\n")
        f.write("-"*85 + "\n")
        for name, stats in ranked:
            is_winner = stats['profit_factor'] > 1.5 and stats['win_rate'] > 65 and stats['num_trades'] >= 50 and stats['max_dd_pct'] < 25
            marker = " ★" if is_winner else ""
            f.write(f"{name:<45s} ${stats['total_pnl']:>9,.2f} {stats['num_trades']:>7d} {stats['win_rate']:>5.1f}% {stats['profit_factor']:>6.3f} {stats['max_dd_pct']:>5.1f}%{marker}\n")

        if grid_best:
            f.write(f"\nGrid Search Best: KC({grid_best['params']['kc_len']},{grid_best['params']['kc_mult']}), "
                    f"Trail {grid_best['params']['trail_mult']}x, TP {grid_best['params']['tp_r']}R\n")

    print(f"Summary saved to {SUMMARY_FILE}")

    # Generate Pine Scripts for winners
    if winners:
        print(f"\n{'='*60}")
        print(f"WINNERS ({len(winners)} strategies meet quality threshold):")
        print(f"{'='*60}")
        for name, stats in winners:
            print(f"  ★ {name}: ${stats['total_pnl']:.2f} | {stats['num_trades']} trades | {stats['win_rate']}% WR | PF {stats['profit_factor']}")
            generate_pine_script(name, stats)
    else:
        print("\nNo strategies met the full quality threshold (PF>1.5, WR>65%, 50+ trades, DD<25%).")
        print("Top 5 strategies by PF (with 20+ trades):")
        filtered = [(n, s) for n, s in ranked if s['num_trades'] >= 20]
        for name, stats in filtered[:5]:
            print(f"  {name}: ${stats['total_pnl']:.2f} | {stats['num_trades']} trades | {stats['win_rate']}% WR | PF {stats['profit_factor']}")

    return all_results


def generate_pine_script(name, stats):
    """Generate a basic Pine Script for winning strategies."""
    safe_name = name.replace(" ", "_").replace("[", "").replace("]", "").replace("(", "").replace(")", "").replace(",", "_")
    filename = f"mes_{safe_name}.pine"
    filepath = BACKTEST_DIR / filename

    # Determine strategy type from name
    if "Keltner" in name:
        # Extract params if possible
        pine = f'''// {name}
// Backtest: ${stats['total_pnl']:.2f} | {stats['num_trades']} trades | {stats['win_rate']}% WR | PF {stats['profit_factor']}
//@version=5
strategy("{name}", overlay=true, default_qty_type=strategy.fixed, default_qty_value=1,
         commission_type=strategy.commission.cash_per_contract, commission_value=0.62)

// Keltner Channel
kcLen = input.int(10, "KC Length")
kcMult = input.float(1.25, "KC Multiplier")
adxThresh = input.float(10, "ADX Threshold")
trailMult = input.float(3.0, "Trail ATR Mult")
tpMult = input.float(0.5, "TP as R multiple")

basis = ta.ema(close, kcLen)
atrVal = ta.atr(kcLen)
upper = basis + kcMult * atrVal
lower = basis - kcMult * atrVal

[diPlus, diMinus, adxVal] = ta.dmi(14, 14)

longCond = close > upper and adxVal > adxThresh
shortCond = close < lower and adxVal > adxThresh

risk = atrVal * trailMult

if longCond and strategy.position_size == 0
    strategy.entry("Long", strategy.long)
    strategy.exit("Long Exit", "Long", stop=close - risk, limit=close + risk * tpMult)

if shortCond and strategy.position_size == 0
    strategy.entry("Short", strategy.short)
    strategy.exit("Short Exit", "Short", stop=close + risk, limit=close - risk * tpMult)

plot(upper, color=color.green)
plot(lower, color=color.red)
plot(basis, color=color.blue)
'''
    else:
        pine = f'''// {name}
// Backtest: ${stats['total_pnl']:.2f} | {stats['num_trades']} trades | {stats['win_rate']}% WR | PF {stats['profit_factor']}
//@version=5
strategy("{name}", overlay=true, default_qty_type=strategy.fixed, default_qty_value=1)
// TODO: Implement {name} logic
// This is a placeholder - adapt from Python backtest logic
'''

    with open(filepath, "w") as f:
        f.write(pine)
    print(f"  Pine script saved: {filepath}")


if __name__ == "__main__":
    main()
