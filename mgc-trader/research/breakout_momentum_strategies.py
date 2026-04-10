"""
Breakout Momentum Adaptations for MGC 5-min Intraday
=====================================================
These strategies adapt the proven 4H Breakout Momentum concept for intraday use.
Designed to plug into the existing MGC bot architecture (strategies.py).

Add to config.STRATEGIES and strat_map in create_strategies() to enable.
"""

import logging
from datetime import datetime, time as dtime, timedelta
from collections import deque
from indicators import ATR, EMA, RSI

logger = logging.getLogger("mgc-trader.strategy")


class Signal:
    """Trade signal (imported from strategies.py in production)."""
    def __init__(self, strategy, action, price, stop, target, reason="", partial_tp_at_1r=False):
        self.strategy = strategy
        self.action = action
        self.price = price
        self.stop = stop
        self.target = target
        self.reason = reason
        self.partial_tp_at_1r = partial_tp_at_1r
        self.timestamp = datetime.now()

    @property
    def risk_points(self):
        return abs(self.price - self.stop)

    @property
    def reward_points(self):
        return abs(self.target - self.price)

    @property
    def rr_ratio(self):
        return self.reward_points / self.risk_points if self.risk_points > 0 else 0


# =============================================================================
# ADAPTATION 1: Higher Timeframe Bias Filter
# =============================================================================
# This isn't a standalone strategy — it's a bias module that other strategies
# query to determine if they should take long/short/both directions.
#
# Usage in trader.py:
#   self.htf_bias = HigherTimeframeBias(config)
#   # Feed it 4H bars (from IB historical data)
#   # Then in _handle_signal(): if signal.action != self.htf_bias.direction: skip

class HigherTimeframeBias:
    """
    Computes daily directional bias from 4H Breakout Momentum logic.
    
    Feed this 4H bars. It tells you: should today be LONG, SHORT, or NEUTRAL?
    
    Logic: If the last 4H close broke above the 20-bar highest high → LONG bias.
           If below 20-bar lowest low → SHORT bias (if you want shorts).
           Otherwise → NEUTRAL (no trades, or allow both).
    """
    
    def __init__(self, lookback=20):
        self.lookback = lookback
        self.highs = deque(maxlen=lookback)
        self.lows = deque(maxlen=lookback)
        self.direction = None  # "BUY", "SELL", or None
        self.breakout_level = None
        self._last_close = None
    
    def update(self, high, low, close):
        """Feed a 4H bar. Call after each 4H bar completes."""
        self.highs.append(high)
        self.lows.append(low)
        self._last_close = close
        
        if len(self.highs) < self.lookback:
            self.direction = None
            return self.direction
        
        highest_high = max(self.highs)
        lowest_low = min(self.lows)
        
        if close > highest_high:
            self.direction = "BUY"
            self.breakout_level = highest_high
        elif close < lowest_low:
            self.direction = "SELL"
            self.breakout_level = lowest_low
        # Once set, bias persists until opposite signal or new day
        
        return self.direction
    
    def allows(self, action):
        """Check if a given action is allowed by the current bias."""
        if self.direction is None:
            return True  # No bias = allow everything (or change to False for strict)
        return action == self.direction
    
    def reset(self):
        """Reset bias (e.g., at start of new day if desired)."""
        self.direction = None
        self.breakout_level = None


# =============================================================================
# ADAPTATION 2: Session Breakout Strategy
# =============================================================================
# Uses meaningful intraday levels instead of arbitrary N-bar lookback.
# Breakout of: prior day high, overnight high, first-hour high.

class SessionBreakoutStrategy:
    """
    Session-Aware Breakout Strategy for 5-min MGC.
    
    Levels monitored (in priority order):
    1. Prior day high/low — strongest level
    2. Overnight session high/low (6PM-8:20AM ET)
    3. First hour high/low (8:20-9:20 ET)
    
    Entry: Close breaks above/below level with confirmation bar
    Stop: Below the breakout level minus ATR buffer
    Target: 2:1 R:R (or trail with wider ATR multiplier)
    
    Key differences from raw Donchian on 5min:
    - Levels are structurally meaningful (traders watch them)
    - Volume confirmation filters false breakouts
    - Wider stops survive intraday noise
    """
    NAME = "Session Breakout"
    
    def __init__(self, params):
        self.params = params
        self.atr = ATR(params.get("atr_period", 14))
        self.trades_today = 0
        
        # Level tracking
        self.prior_day_high = None
        self.prior_day_low = None
        self.overnight_high = None
        self.overnight_low = None
        self.first_hour_high = None
        self.first_hour_low = None
        
        # Internal state
        self._today_high = None
        self._today_low = None
        self._current_date = None
        self._overnight_tracking = False
        self._first_hour_tracking = False
        self._first_hour_end = None
        self._prev_close = None
        self._avg_volume = None
        self._vol_buffer = deque(maxlen=20)
        
        # Track which levels have been broken (don't re-enter same level)
        self._broken_levels = set()
    
    def on_new_day(self):
        self.trades_today = 0
        self._broken_levels.clear()
        self.first_hour_high = None
        self.first_hour_low = None
        self._first_hour_tracking = False
        self._first_hour_end = None
        self._prev_close = None
    
    def on_session_open(self, time):
        """Called at COMEX open (8:20 ET). Start tracking first hour."""
        self._first_hour_tracking = True
        self._first_hour_end = time + timedelta(minutes=self.params.get("first_hour_minutes", 60))
        self.first_hour_high = None
        self.first_hour_low = None
        
        # Freeze overnight levels
        if self._today_high is not None:
            self.overnight_high = self._today_high
            self.overnight_low = self._today_low
            logger.info(f"Session Breakout: ON H={self.overnight_high:.2f} L={self.overnight_low:.2f}")
    
    def evaluate(self, time, open_, high, low, close, volume):
        """Evaluate 5-min bar for session breakout signals."""
        self.atr.update(high, low, close)
        
        # Track volume for confirmation
        if volume > 0:
            self._vol_buffer.append(volume)
            if len(self._vol_buffer) >= 10:
                self._avg_volume = sum(self._vol_buffer) / len(self._vol_buffer)
        
        # Track daily H/L for next day's levels
        date = time.date() if hasattr(time, 'date') else time
        if self._current_date is None:
            self._current_date = date
            self._today_high = high
            self._today_low = low
        elif hasattr(date, '__eq__') and date != self._current_date:
            self.prior_day_high = self._today_high
            self.prior_day_low = self._today_low
            self._current_date = date
            self._today_high = high
            self._today_low = low
            logger.info(f"Session Breakout: PDH={self.prior_day_high:.2f} PDL={self.prior_day_low:.2f}")
        else:
            self._today_high = max(self._today_high, high)
            self._today_low = min(self._today_low, low)
        
        # Track first hour range
        if self._first_hour_tracking and self._first_hour_end:
            if time <= self._first_hour_end:
                if self.first_hour_high is None:
                    self.first_hour_high = high
                    self.first_hour_low = low
                else:
                    self.first_hour_high = max(self.first_hour_high, high)
                    self.first_hour_low = min(self.first_hour_low, low)
            else:
                if self._first_hour_tracking:
                    self._first_hour_tracking = False
                    logger.info(f"Session Breakout: 1H H={self.first_hour_high:.2f} L={self.first_hour_low:.2f}")
        
        # Need ATR and at least one set of levels
        if not self.atr.ready:
            self._prev_close = close
            return None
        
        if self.trades_today >= self.params.get("max_trades", 2):
            self._prev_close = close
            return None
        
        signal = self._check_breakout(time, close, high, low, volume)
        self._prev_close = close
        return signal
    
    def _check_breakout(self, time, close, high, low, volume):
        """Check for confirmed breakout of session levels."""
        if self._prev_close is None:
            return None
        
        atr_val = self.atr.value
        stop_mult = self.params.get("atr_stop_mult", 2.0)
        tp_mult = self.params.get("profit_target_mult", 2.0)
        require_volume = self.params.get("require_volume_confirm", True)
        vol_threshold = self.params.get("volume_mult", 1.3)
        
        # Volume confirmation check
        volume_ok = True
        if require_volume and self._avg_volume and self._avg_volume > 0:
            volume_ok = volume >= self._avg_volume * vol_threshold
        
        # Build list of levels to check (priority order)
        levels = []
        if self.prior_day_high and "pdh" not in self._broken_levels:
            levels.append(("PDH", self.prior_day_high, "BUY"))
        if self.prior_day_low and "pdl" not in self._broken_levels:
            levels.append(("PDL", self.prior_day_low, "SELL"))
        if self.overnight_high and "onh" not in self._broken_levels:
            levels.append(("ONH", self.overnight_high, "BUY"))
        if self.overnight_low and "onl" not in self._broken_levels:
            levels.append(("ONL", self.overnight_low, "SELL"))
        if self.first_hour_high and not self._first_hour_tracking and "1hh" not in self._broken_levels:
            levels.append(("1HH", self.first_hour_high, "BUY"))
        if self.first_hour_low and not self._first_hour_tracking and "1hl" not in self._broken_levels:
            levels.append(("1HL", self.first_hour_low, "SELL"))
        
        for level_name, level_price, direction in levels:
            if direction == "BUY":
                # Confirmed breakout: prev close above level AND current close above
                if self._prev_close > level_price and close > level_price:
                    if not volume_ok:
                        continue
                    
                    stop = level_price - atr_val * stop_mult
                    risk = close - stop
                    target = close + risk * tp_mult
                    
                    self._broken_levels.add(level_name.lower())
                    self.trades_today += 1
                    
                    return Signal(
                        self.NAME, "BUY", close, stop, target,
                        f"Breakout above {level_name} ({level_price:.2f})",
                        partial_tp_at_1r=True,
                    )
            
            elif direction == "SELL":
                if self._prev_close < level_price and close < level_price:
                    if not volume_ok:
                        continue
                    
                    stop = level_price + atr_val * stop_mult
                    risk = stop - close
                    target = close - risk * tp_mult
                    
                    self._broken_levels.add(level_name.lower())
                    self.trades_today += 1
                    
                    return Signal(
                        self.NAME, "SELL", close, stop, target,
                        f"Breakdown below {level_name} ({level_price:.2f})",
                        partial_tp_at_1r=True,
                    )
        
        return None


# =============================================================================
# ADAPTATION 3: Donchian Breakout on 15-min (MTF)
# =============================================================================
# Uses the existing MTF infrastructure. 20-bar Donchian on 15min = 5 hours.

class DonchianBreakoutMTF:
    """
    Donchian Channel Breakout on 15-min bars, executed on 5-min.
    
    This is the closest direct adaptation of the 4H strategy:
    - 20-bar highest high on 15min = 5 hours of intraday data  
    - Wider ATR multiplier (2.5-3.0×) for 5min noise
    - Trail stop instead of fixed TP (like the 4H version)
    
    Set timeframe="mtf" in config to use with trader.py's MTF aggregation.
    """
    NAME = "Donchian MTF"
    
    def __init__(self, params):
        self.params = params
        self.atr = ATR(params.get("atr_period", 14))
        self.lookback = params.get("donchian_period", 20)
        self.highs = deque(maxlen=self.lookback)
        self.lows = deque(maxlen=self.lookback)
        self.trades_today = 0
        self._prev_close = None
        self._in_trade = False  # Simple state to avoid re-entry on same breakout
    
    def on_new_day(self):
        self.trades_today = 0
        self._in_trade = False
        # Don't clear highs/lows — we want continuity across sessions for channel
    
    def evaluate(self, time, open_, high, low, close, volume):
        """Evaluate a 15-min bar (fed by MTF aggregation in trader.py)."""
        self.atr.update(high, low, close)
        self.highs.append(high)
        self.lows.append(low)
        
        if len(self.highs) < self.lookback or not self.atr.ready:
            self._prev_close = close
            return None
        
        if self.trades_today >= self.params.get("max_trades", 2):
            self._prev_close = close
            return None
        
        signal = self._check_breakout(close)
        self._prev_close = close
        return signal
    
    def _check_breakout(self, close):
        if self._prev_close is None:
            return None
        
        # Donchian channel (exclude current bar)
        channel_highs = list(self.highs)[:-1]  # all except current
        channel_lows = list(self.lows)[:-1]
        
        if len(channel_highs) < self.lookback - 1:
            return None
        
        upper = max(channel_highs)
        lower = min(channel_lows)
        
        atr_val = self.atr.value
        stop_mult = self.params.get("atr_stop_mult", 2.5)
        tp_mult = self.params.get("profit_target_mult", 2.5)
        
        # Breakout above upper channel
        if close > upper and self._prev_close <= upper:
            stop = close - atr_val * stop_mult
            risk = close - stop
            target = close + risk * tp_mult
            self.trades_today += 1
            self._in_trade = True
            return Signal(
                self.NAME, "BUY", close, stop, target,
                f"Donchian breakout above {upper:.2f} (15m {self.lookback}-bar)",
                partial_tp_at_1r=True,
            )
        
        # Breakdown below lower channel
        if close < lower and self._prev_close >= lower:
            stop = close + atr_val * stop_mult
            risk = stop - close
            target = close - risk * tp_mult
            self.trades_today += 1
            self._in_trade = True
            return Signal(
                self.NAME, "SELL", close, stop, target,
                f"Donchian breakdown below {lower:.2f} (15m {self.lookback}-bar)",
                partial_tp_at_1r=True,
            )
        
        return None


# =============================================================================
# CONFIG ENTRIES (add to config.py STRATEGIES dict)
# =============================================================================
"""
Add these to config.py:

STRATEGIES = {
    # ... existing strategies ...
    
    "session_breakout": {
        "enabled": True,
        "timeframe": "5m",          # Evaluates on raw 5-min bars
        "atr_period": 14,
        "atr_stop_mult": 2.0,       # Wider than ORB to survive noise
        "profit_target_mult": 2.0,   # 2:1 R:R
        "first_hour_minutes": 60,    # Track first 60 min of COMEX RTH
        "require_volume_confirm": True,
        "volume_mult": 1.3,          # Breakout bar volume must be 1.3× avg
        "max_trades": 2,             # Max 2 session breakout trades/day
    },
    
    "donchian_mtf": {
        "enabled": True,
        "timeframe": "mtf",          # Uses 15-min aggregation from trader.py
        "donchian_period": 20,        # 20 bars × 15min = 5 hours
        "atr_period": 14,
        "atr_stop_mult": 2.5,        # Wide to survive 5min execution noise
        "profit_target_mult": 2.5,    # 2.5:1 R:R
        "max_trades": 1,              # Max 1 Donchian trade/day (it's a trend signal)
    },
}

# Add to strat_map in create_strategies():
strat_map = {
    # ... existing ...
    "session_breakout": SessionBreakoutStrategy,
    "donchian_mtf": DonchianBreakoutMTF,
}
"""


# =============================================================================
# INTEGRATION: How to add 4H Bias to trader.py
# =============================================================================
"""
In trader.py __init__:
    self._htf_bias = HigherTimeframeBias(lookback=20)

In _warmup() — fetch 4H bars separately:
    bars_4h = self.ib.get_historical_bars(duration="30 D", bar_size="4 hours")
    for bar in bars_4h:
        self._htf_bias.update(bar.high, bar.low, bar.close)
    logger.info(f"4H Bias: {self._htf_bias.direction} (level={self._htf_bias.breakout_level})")

In _handle_signal() — add bias filter before risk check:
    # 4H Bias Filter
    if self._htf_bias.direction and not self._htf_bias.allows(signal.action):
        logger.info(f"Signal blocked: {signal.action} against 4H bias ({self._htf_bias.direction})")
        return

Refresh bias every 4 hours (add counter in _process_bar):
    self._bars_since_bias_refresh += 1
    if self._bars_since_bias_refresh >= 48:  # 48 × 5min = 4 hours
        bars_4h = self.ib.get_historical_bars(duration="30 D", bar_size="4 hours")
        for bar in bars_4h[-5:]:  # just refresh recent
            self._htf_bias.update(bar.high, bar.low, bar.close)
        self._bars_since_bias_refresh = 0
"""
