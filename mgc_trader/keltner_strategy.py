"""Keltner Trend Rider Strategy Implementation"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional

class KeltnerTrendRider:
    """Adam's Dual Keltner Channel Strategy with Asymmetric Management"""
    
    def __init__(self, config):
        self.config = config
        self.position = None
        self.entry_price = None
        self.stop_price = None
        self.take_profit = None
        
    def calculate_keltner_channel(self, df: pd.DataFrame, length: int, mult: float) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Keltner Channel bands"""
        # Typical price (HLC average)
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        
        # Middle line (EMA of typical price)
        middle = typical_price.ewm(span=length, adjust=False).mean()
        
        # True Range
        tr = pd.DataFrame({
            'hl': df['high'] - df['low'],
            'hc': abs(df['high'] - df['close'].shift(1)),
            'lc': abs(df['low'] - df['close'].shift(1))
        }).max(axis=1)
        
        # ATR
        atr = tr.ewm(span=length, adjust=False).mean()
        
        # Bands
        upper = middle + (mult * atr)
        lower = middle - (mult * atr)
        
        return upper, middle, lower
    
    def calculate_adx(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average Directional Index"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        # Directional movements
        plus_dm = high.diff()
        minus_dm = -low.diff()
        
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        # True Range
        tr = pd.DataFrame({
            'hl': high - low,
            'hc': abs(high - close.shift(1)),
            'lc': abs(low - close.shift(1))
        }).max(axis=1)
        
        # Smoothed values
        atr = tr.ewm(span=period, adjust=False).mean()
        plus_di = 100 * (plus_dm.ewm(span=period, adjust=False).mean() / atr)
        minus_di = 100 * (minus_dm.ewm(span=period, adjust=False).mean() / atr)
        
        # ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.ewm(span=period, adjust=False).mean()
        
        return adx
    
    def check_entry_signals(self, df: pd.DataFrame) -> Optional[str]:
        """Check for long or short entry signals"""
        # Calculate indicators
        kc_upper_long, _, kc_lower_long = self.calculate_keltner_channel(
            df, self.config.KC_LENGTH, self.config.KC_MULT_LONG
        )
        kc_upper_short, _, kc_lower_short = self.calculate_keltner_channel(
            df, self.config.KC_LENGTH_SHORT, self.config.KC_MULT_SHORT
        )
        adx = self.calculate_adx(df, self.config.ADX_PERIOD)
        
        # Latest values
        close = df['close'].iloc[-1]
        adx_value = adx.iloc[-1]
        
        # Check ADX filter
        if adx_value < self.config.ADX_THRESHOLD:
            return None
        
        # Long signal: close > long KC upper
        if close > kc_upper_long.iloc[-1]:
            return 'LONG'
        
        # Short signal: close < short KC lower  
        if close < kc_lower_short.iloc[-1]:
            return 'SHORT'
        
        return None
    
    def calculate_stops_and_targets(self, df: pd.DataFrame, signal: str, entry_price: float) -> Tuple[float, Optional[float]]:
        """Calculate stop loss and take profit levels"""
        # Calculate ATR
        tr = pd.DataFrame({
            'hl': df['high'] - df['low'],
            'hc': abs(df['high'] - df['close'].shift(1)),
            'lc': abs(df['low'] - df['close'].shift(1))
        }).max(axis=1)
        atr = tr.ewm(span=self.config.ATR_PERIOD, adjust=False).mean().iloc[-1]
        
        if signal == 'LONG':
            # Longs: wide stop, no TP (ride the trend)
            stop_loss = entry_price - (self.config.LONG_STOP_ATR * atr)
            take_profit = None
        else:  # SHORT
            # Shorts: tight stop, quick TP
            stop_loss = entry_price + (self.config.SHORT_STOP_ATR * atr)
            risk = self.config.SHORT_STOP_ATR * atr
            take_profit = entry_price - (self.config.SHORT_TP_R * risk)
        
        return stop_loss, take_profit
    
    def check_reentry_condition(self, df: pd.DataFrame, last_position: str) -> bool:
        """Check if we should re-enter after being stopped out"""
        if last_position == 'LONG':
            kc_upper, _, _ = self.calculate_keltner_channel(
                df, self.config.KC_LENGTH, self.config.KC_MULT_LONG
            )
            return df['close'].iloc[-1] > kc_upper.iloc[-1]
        
        elif last_position == 'SHORT':
            _, _, kc_lower = self.calculate_keltner_channel(
                df, self.config.KC_LENGTH_SHORT, self.config.KC_MULT_SHORT
            )
            return df['close'].iloc[-1] < kc_lower.iloc[-1]
        
        return False