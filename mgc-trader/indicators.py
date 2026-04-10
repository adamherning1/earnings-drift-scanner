"""
MGC Day Trader — Technical Indicators
Lightweight indicator calculations for real-time use.
"""

import numpy as np
from collections import deque


class EMA:
    """Exponential Moving Average — streaming."""

    def __init__(self, period):
        self.period = period
        self.alpha = 2.0 / (period + 1)
        self.value = None
        self.count = 0
        self._sum = 0.0

    def update(self, price):
        self.count += 1
        if self.value is None:
            self._sum += price
            if self.count >= self.period:
                self.value = self._sum / self.period
        else:
            self.value = self.alpha * price + (1 - self.alpha) * self.value
        return self.value

    @property
    def ready(self):
        return self.value is not None


class ATR:
    """Average True Range — streaming (Wilder's smoothing)."""

    def __init__(self, period):
        self.period = period
        self.alpha = 1.0 / period
        self.value = None
        self.prev_close = None
        self.count = 0
        self._sum = 0.0

    def update(self, high, low, close):
        if self.prev_close is not None:
            tr = max(high - low, abs(high - self.prev_close), abs(low - self.prev_close))
        else:
            tr = high - low

        self.count += 1
        self.prev_close = close

        if self.value is None:
            self._sum += tr
            if self.count >= self.period:
                self.value = self._sum / self.period
        else:
            self.value = self.alpha * tr + (1 - self.alpha) * self.value

        return self.value

    @property
    def ready(self):
        return self.value is not None


class VWAP:
    """Volume-Weighted Average Price — resets daily."""

    def __init__(self):
        self.cum_vol = 0.0
        self.cum_vp = 0.0
        self.value = None

    def update(self, typical_price, volume):
        """typical_price = (high + low + close) / 3"""
        self.cum_vol += volume
        self.cum_vp += typical_price * volume
        if self.cum_vol > 0:
            self.value = self.cum_vp / self.cum_vol
        return self.value

    def reset(self):
        """Call at session start to reset VWAP."""
        self.cum_vol = 0.0
        self.cum_vp = 0.0
        self.value = None

    @property
    def ready(self):
        return self.value is not None and self.cum_vol > 0


class RSI:
    """Relative Strength Index — streaming (Wilder's smoothing)."""

    def __init__(self, period=14):
        self.period = period
        self.alpha = 1.0 / period
        self.avg_gain = None
        self.avg_loss = None
        self.prev_close = None
        self.count = 0
        self._gains = []
        self._losses = []
        self.value = None

    def update(self, close):
        if self.prev_close is not None:
            change = close - self.prev_close
            gain = max(change, 0)
            loss = max(-change, 0)
            self.count += 1

            if self.avg_gain is None:
                self._gains.append(gain)
                self._losses.append(loss)
                if len(self._gains) >= self.period:
                    self.avg_gain = sum(self._gains) / self.period
                    self.avg_loss = sum(self._losses) / self.period
            else:
                self.avg_gain = self.alpha * gain + (1 - self.alpha) * self.avg_gain
                self.avg_loss = self.alpha * loss + (1 - self.alpha) * self.avg_loss

            if self.avg_gain is not None:
                if self.avg_loss == 0:
                    self.value = 100.0
                else:
                    rs = self.avg_gain / self.avg_loss
                    self.value = 100.0 - (100.0 / (1.0 + rs))

        self.prev_close = close
        return self.value

    @property
    def ready(self):
        return self.value is not None


class PriorDayLevels:
    """Track prior day high/low/close and overnight high/low."""

    def __init__(self):
        self.prior_high = None
        self.prior_low = None
        self.prior_close = None
        self.overnight_high = None
        self.overnight_low = None
        self._today_high = None
        self._today_low = None
        self._current_date = None

    def update(self, dt, high, low, close):
        """Call with each bar. dt should be a datetime object."""
        date = dt.date()

        if self._current_date is None:
            self._current_date = date
            self._today_high = high
            self._today_low = low

        if date != self._current_date:
            # New day — save yesterday's levels
            self.prior_high = self._today_high
            self.prior_low = self._today_low
            self.prior_close = close  # last close of prior day
            self.overnight_high = high
            self.overnight_low = low
            self._today_high = high
            self._today_low = low
            self._current_date = date
        else:
            self._today_high = max(self._today_high, high)
            self._today_low = min(self._today_low, low)
            # Update overnight levels (pre-RTH)
            if self.overnight_high is not None:
                self.overnight_high = max(self.overnight_high, high)
                self.overnight_low = min(self.overnight_low, low)

    @property
    def ready(self):
        return self.prior_high is not None


class OpeningRange:
    """Track the opening range (first N minutes of a session)."""

    def __init__(self, duration_minutes=15):
        self.duration_minutes = duration_minutes
        self.high = None
        self.low = None
        self.is_set = False
        self._start_time = None
        self._bars = []

    def start(self, time):
        """Call at session open to begin tracking."""
        self._start_time = time
        self._bars = []
        self.high = None
        self.low = None
        self.is_set = False

    def update(self, time, high, low):
        """Feed bars during the opening range period."""
        if self._start_time is None or self.is_set:
            return

        elapsed = (time - self._start_time).total_seconds() / 60
        if elapsed <= self.duration_minutes:
            if self.high is None:
                self.high = high
                self.low = low
            else:
                self.high = max(self.high, high)
                self.low = min(self.low, low)
        else:
            self.is_set = True

    @property
    def range_size(self):
        if self.high is not None and self.low is not None:
            return self.high - self.low
        return None

    @property
    def ready(self):
        return self.is_set
