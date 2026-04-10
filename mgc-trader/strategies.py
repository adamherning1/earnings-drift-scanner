"""
MGC Day Trader — Strategy Engine
Each strategy evaluates bars and emits signals.
"""

import logging
from datetime import datetime, time as dtime
from indicators import EMA, ATR, VWAP, RSI, PriorDayLevels, OpeningRange
import pytz
import config

logger = logging.getLogger("mgc-trader.strategy")


class Signal:
    """Trade signal emitted by a strategy."""
    def __init__(self, strategy, action, price, stop, target, reason="", partial_tp_at_1r=False):
        self.strategy = strategy
        self.action = action          # "BUY" or "SELL"
        self.price = price            # Expected entry price
        self.stop = stop              # Stop loss price
        self.target = target          # Take profit price
        self.reason = reason
        self.partial_tp_at_1r = partial_tp_at_1r  # Close half at 1R profit
        self.timestamp = datetime.now()

    @property
    def risk_points(self):
        return abs(self.price - self.stop)

    @property
    def reward_points(self):
        return abs(self.target - self.price)

    @property
    def rr_ratio(self):
        if self.risk_points > 0:
            return self.reward_points / self.risk_points
        return 0

    def __repr__(self):
        return (f"Signal({self.strategy} {self.action} @ {self.price:.2f}, "
                f"stop={self.stop:.2f}, tp={self.target:.2f}, R:R={self.rr_ratio:.1f})")


class ORBStrategy:
    """
    Opening Range Breakout — COMEX open.
    Trades breakout of first 15 minutes after 8:20 AM ET.
    """
    NAME = "ORB"

    def __init__(self, params):
        self.params = params
        self.atr = ATR(params["atr_period"])
        self.orb = OpeningRange(params["orb_minutes"])
        self.trades_today = 0
        self.active = False
        self._prev_close = None  # Track previous bar close for candle confirmation

    def on_new_day(self):
        self.trades_today = 0
        self.active = False
        self._prev_close = None
        self.orb = OpeningRange(self.params["orb_minutes"])

    def on_session_open(self, time):
        """Call at COMEX open (8:20 ET)."""
        self.orb.start(time)
        self.active = True

    def evaluate(self, time, open_, high, low, close, volume):
        """Evaluate a new bar. Returns Signal or None."""
        self.atr.update(high, low, close)

        if not self.active:
            self._prev_close = close
            return None

        # Still building the opening range
        if not self.orb.is_set:
            self.orb.update(time, high, low)
            self._prev_close = close
            return None

        if not self.atr.ready:
            self._prev_close = close
            return None

        if self.trades_today >= self.params["max_trades"]:
            self._prev_close = close
            return None

        atr_val = self.atr.value
        stop_mult = self.params["atr_stop_mult"]
        tp_mult = self.params["profit_target_mult"]

        # Candle close confirmation: require the PREVIOUS bar to have closed
        # above/below the ORB level, filtering out false intrabar breakouts
        prev = self._prev_close
        signal = None

        # Confirmed breakout: previous bar closed above ORB high AND current still above
        if prev is not None and prev > self.orb.high and close > self.orb.high:
            stop = self.orb.high - atr_val * stop_mult
            risk = close - stop
            target = close + risk * tp_mult
            self.trades_today += 1
            signal = Signal(self.NAME, "BUY", close, stop, target,
                            f"ORB breakout above {self.orb.high:.2f} (confirmed)",
                            partial_tp_at_1r=True)

        # Confirmed breakdown: previous bar closed below ORB low AND current still below
        elif prev is not None and prev < self.orb.low and close < self.orb.low:
            stop = self.orb.low + atr_val * stop_mult
            risk = stop - close
            target = close - risk * tp_mult
            self.trades_today += 1
            signal = Signal(self.NAME, "SELL", close, stop, target,
                            f"ORB breakdown below {self.orb.low:.2f} (confirmed)",
                            partial_tp_at_1r=True)

        self._prev_close = close
        return signal


class VWAPBounceStrategy:
    """
    VWAP Mean Reversion — buy/sell bounces off VWAP.
    Requires price to approach VWAP and bounce with trend confirmation.
    """
    NAME = "VWAP Bounce"

    def __init__(self, params):
        self.params = params
        self.vwap = VWAP()
        self.atr = ATR(params["atr_period"])
        self.ema_trend = EMA(50)  # Trend filter
        self.trades_today = 0
        self.prev_close = None
        self.near_vwap_count = 0

    def on_new_day(self):
        self.trades_today = 0
        self.vwap.reset()
        self.near_vwap_count = 0

    def evaluate(self, time, open_, high, low, close, volume):
        typical = (high + low + close) / 3
        self.vwap.update(typical, volume)
        self.atr.update(high, low, close)
        self.ema_trend.update(close)

        if not all([self.vwap.ready, self.atr.ready, self.ema_trend.ready]):
            result = None
        elif self.trades_today >= self.params["max_trades"]:
            result = None
        else:
            result = self._check_signal(close, high, low)

        self.prev_close = close
        return result

    def _check_signal(self, close, high, low):
        vwap_val = self.vwap.value
        atr_val = self.atr.value
        max_dist = self.params["max_distance_ticks"] * config.TICK_SIZE
        stop_mult = self.params["atr_stop_mult"]
        tp_mult = self.params["profit_target_mult"]

        distance = abs(close - vwap_val)

        # Track bars near VWAP
        if distance <= max_dist:
            self.near_vwap_count += 1
        else:
            self.near_vwap_count = 0

        if self.near_vwap_count < self.params["lookback_bars"]:
            return None

        if self.prev_close is None:
            return None

        # Bullish bounce: price was near VWAP and now bouncing up, trend is up
        if close > vwap_val and self.prev_close <= vwap_val and close > self.ema_trend.value:
            stop = vwap_val - atr_val * stop_mult
            risk = close - stop
            target = close + risk * tp_mult
            self.trades_today += 1
            self.near_vwap_count = 0
            return Signal(self.NAME, "BUY", close, stop, target,
                          f"VWAP bounce (VWAP={vwap_val:.2f})")

        # Bearish bounce: price was near VWAP and now bouncing down, trend is down
        if close < vwap_val and self.prev_close >= vwap_val and close < self.ema_trend.value:
            stop = vwap_val + atr_val * stop_mult
            risk = stop - close
            target = close - risk * tp_mult
            self.trades_today += 1
            self.near_vwap_count = 0
            return Signal(self.NAME, "SELL", close, stop, target,
                          f"VWAP rejection (VWAP={vwap_val:.2f})")

        return None


class EMAMomentumStrategy:
    """
    EMA Crossover Momentum — 9/21 EMA cross with 50 EMA trend filter.
    Only trades in direction of the 50 EMA trend.
    """
    NAME = "EMA Momentum"

    def __init__(self, params):
        self.params = params
        self.fast_ema = EMA(params["fast_ema"])
        self.slow_ema = EMA(params["slow_ema"])
        self.trend_ema = EMA(params["trend_ema"])
        self.atr = ATR(params["atr_period"])
        self.trades_today = 0
        self.prev_fast = None
        self.prev_slow = None
        self._comex_open_checked = False  # Flag for first-bar continuation signal

    def on_new_day(self):
        self.trades_today = 0
        self._comex_open_checked = False

    # COMEX RTH hours: 8:20 AM - 1:30 PM ET
    COMEX_RTH_START = dtime(8, 20)
    COMEX_RTH_END = dtime(13, 30)
    _ET = pytz.timezone("US/Eastern")

    def _in_comex_rth(self, bar_time):
        """Check if current time is within COMEX Regular Trading Hours."""
        try:
            if hasattr(bar_time, 'tzinfo') and bar_time.tzinfo:
                now_et = bar_time.astimezone(self._ET)
            else:
                now_et = datetime.now(self._ET)
            return self.COMEX_RTH_START <= now_et.time() <= self.COMEX_RTH_END
        except Exception:
            return True  # fail-open to avoid blocking trades on error

    def evaluate(self, time, open_, high, low, close, volume):
        fast = self.fast_ema.update(close)
        slow = self.slow_ema.update(close)
        trend = self.trend_ema.update(close)
        self.atr.update(high, low, close)

        if not all([self.fast_ema.ready, self.slow_ema.ready,
                     self.trend_ema.ready, self.atr.ready]):
            self.prev_fast = fast
            self.prev_slow = slow
            return None

        if self.trades_today >= self.params["max_trades"]:
            self.prev_fast = fast
            self.prev_slow = slow
            return None

        # Only generate signals during COMEX RTH (8:20 AM - 1:30 PM ET)
        if not self._in_comex_rth(time):
            self.prev_fast = fast
            self.prev_slow = slow
            return None

        signal = self._check_cross(close, fast, slow, trend)

        # Momentum continuation: on the first COMEX RTH bar, if EMAs are already
        # aligned (crossed during overnight/Asian session), take the entry without
        # requiring a fresh crossover. This prevents missing trending moves that
        # started before COMEX open.
        if signal is None and not self._comex_open_checked and self.trades_today == 0:
            self._comex_open_checked = True
            signal = self._check_continuation(close, fast, slow, trend)

        self.prev_fast = fast
        self.prev_slow = slow
        return signal

    def _check_continuation(self, close, fast, slow, trend):
        """First-bar momentum continuation — EMAs already aligned from overnight."""
        atr_val = self.atr.value
        stop_mult = self.params["atr_stop_mult"]
        tp_mult = self.params["profit_target_mult"]

        # Strong bullish alignment: fast > slow, price > trend
        if fast > slow and close > trend:
            stop = close - atr_val * stop_mult
            risk = close - stop
            target = close + risk * tp_mult
            self.trades_today += 1
            return Signal(self.NAME, "BUY", close, stop, target,
                          f"EMA continuation: already aligned bullish (F={fast:.2f}>S={slow:.2f}, trend={trend:.2f})")

        # Strong bearish alignment: fast < slow, price < trend
        if fast < slow and close < trend:
            stop = close + atr_val * stop_mult
            risk = stop - close
            target = close - risk * tp_mult
            self.trades_today += 1
            return Signal(self.NAME, "SELL", close, stop, target,
                          f"EMA continuation: already aligned bearish (F={fast:.2f}<S={slow:.2f}, trend={trend:.2f})")

        return None

    def _check_cross(self, close, fast, slow, trend):
        if self.prev_fast is None or self.prev_slow is None:
            return None

        atr_val = self.atr.value
        stop_mult = self.params["atr_stop_mult"]
        tp_mult = self.params["profit_target_mult"]

        # Bullish crossover + uptrend
        if self.prev_fast <= self.prev_slow and fast > slow and close > trend:
            stop = close - atr_val * stop_mult
            risk = close - stop
            target = close + risk * tp_mult
            self.trades_today += 1
            return Signal(self.NAME, "BUY", close, stop, target,
                          f"9/21 EMA cross up (trend={trend:.2f}) [COMEX RTH]")

        # Bearish crossover + downtrend
        if self.prev_fast >= self.prev_slow and fast < slow and close < trend:
            stop = close + atr_val * stop_mult
            risk = stop - close
            target = close - risk * tp_mult
            self.trades_today += 1
            return Signal(self.NAME, "SELL", close, stop, target,
                          f"9/21 EMA cross down (trend={trend:.2f}) [COMEX RTH]")

        return None


class LevelScalpStrategy:
    """
    Key Level Scalp — trade reactions at significant price levels.
    Levels: prior day H/L, round numbers, overnight H/L.
    """
    NAME = "Level Scalp"

    def __init__(self, params):
        self.params = params
        self.levels = PriorDayLevels()
        self.atr = ATR(params["atr_period"])
        self.trades_today = 0

    def on_new_day(self):
        self.trades_today = 0

    def evaluate(self, time, open_, high, low, close, volume):
        self.levels.update(time, high, low, close)
        self.atr.update(high, low, close)

        if not self.levels.ready or not self.atr.ready:
            return None

        if self.trades_today >= self.params["max_trades"]:
            return None

        return self._check_levels(close, high, low)

    def _check_levels(self, close, high, low):
        atr_val = self.atr.value
        stop_mult = self.params["atr_stop_mult"]
        tp_mult = self.params["profit_target_mult"]
        tick = config.TICK_SIZE
        proximity = atr_val * 0.15  # How close price must be to a level

        # Gather all active levels
        levels = []
        if self.params.get("use_prior_day_hl") and self.levels.prior_high:
            levels.append(("PDH", self.levels.prior_high))
            levels.append(("PDL", self.levels.prior_low))
        if self.params.get("use_overnight_hl") and self.levels.overnight_high:
            levels.append(("ONH", self.levels.overnight_high))
            levels.append(("ONL", self.levels.overnight_low))
        if self.params.get("use_round_numbers"):
            # Nearest $5 and $10 round numbers
            base = round(close / 5) * 5
            for offset in [-10, -5, 0, 5, 10]:
                levels.append(("RND", base + offset))

        for name, level in levels:
            dist = close - level

            # Bounce long off support (close just above level after touching it)
            if 0 < dist < proximity and low <= level + tick:
                stop = level - atr_val * stop_mult
                risk = close - stop
                target = close + risk * tp_mult
                self.trades_today += 1
                return Signal(self.NAME, "BUY", close, stop, target,
                              f"Bounce off {name} ({level:.2f})")

            # Rejection short off resistance (close just below level after touching it)
            if -proximity < dist < 0 and high >= level - tick:
                stop = level + atr_val * stop_mult
                risk = stop - close
                target = close - risk * tp_mult
                self.trades_today += 1
                return Signal(self.NAME, "SELL", close, stop, target,
                              f"Rejection at {name} ({level:.2f})")

        return None


class HigherTimeframeBias:
    """
    4H Breakout Momentum bias filter.
    Computes directional bias from 4H bars: if last close broke above 20-bar 
    highest high → BUY bias. Below 20-bar lowest low → SELL bias.
    Other strategies should only trade in the direction of the bias.
    """
    def __init__(self, lookback=20):
        self.lookback = lookback
        self.highs = []
        self.lows = []
        self.direction = None   # "BUY", "SELL", or None
        self.breakout_level = None
        self._last_close = None

    def update(self, high, low, close):
        """Feed a 4H bar. Call after each 4H bar completes."""
        self.highs.append(high)
        self.lows.append(low)
        # Keep only lookback+1 bars (need lookback prior bars excluding current)
        if len(self.highs) > self.lookback + 5:
            self.highs = self.highs[-(self.lookback + 5):]
            self.lows = self.lows[-(self.lookback + 5):]
        self._last_close = close

        if len(self.highs) <= self.lookback:
            return self.direction

        # Highest high of the lookback bars PRIOR to the current bar
        prior_highs = self.highs[-(self.lookback + 1):-1]
        prior_lows = self.lows[-(self.lookback + 1):-1]
        highest_high = max(prior_highs)
        lowest_low = min(prior_lows)

        if close > highest_high:
            self.direction = "BUY"
            self.breakout_level = highest_high
        elif close < lowest_low:
            self.direction = "SELL"
            self.breakout_level = lowest_low
        # Bias persists until opposite signal

        return self.direction

    def allows(self, action, current_price=None):
        """Check if an action is allowed by the current bias.
        Only BUY when bias=BUY, only SELL (short) when bias=SELL.
        Block everything when bias is neutral (no breakout detected).
        
        Proximity override: if current price is >2% away from the bias
        breakout level, treat bias as neutral and allow either direction.
        This prevents the filter from blocking obvious moves when price
        has already broken far away from the level.
        """
        if self.direction is None:
            return False  # No bias = no trades until breakout detected

        # Proximity override: if price has moved far from the breakout level,
        # the bias level is stale — allow trades in either direction
        if current_price is not None and self.breakout_level is not None and self.breakout_level > 0:
            distance_pct = abs(current_price - self.breakout_level) / self.breakout_level
            if distance_pct > 0.02:  # >2% away from bias level
                return True  # Bias is stale, allow any direction

        return action == self.direction

    @property
    def ready(self):
        return len(self.highs) > self.lookback


def create_strategies():
    """Initialize all enabled strategies from config."""
    strategies = []
    strat_map = {
        "orb": ORBStrategy,
        "vwap_bounce": VWAPBounceStrategy,
        "ema_momentum": EMAMomentumStrategy,
        "level_scalp": LevelScalpStrategy,
    }
    for name, params in config.STRATEGIES.items():
        if params.get("enabled", False) and name in strat_map:
            strat = strat_map[name](params)
            strategies.append(strat)
            logger.info(f"Loaded strategy: {strat.NAME}")
    return strategies
