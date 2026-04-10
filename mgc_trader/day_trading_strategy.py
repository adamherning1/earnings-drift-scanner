"""Day Trading Strategy for MGC - 5M/15M Timeframes"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional, Dict
from datetime import datetime

class DayTradingStrategy:
    """Multi-timeframe day trading strategy for MGC"""
    
    def __init__(self, config):
        self.config = config
        self.position = None
        self.trades_today = 0
        self.last_trade_time = None
        self.daily_stats = {'wins': 0, 'losses': 0}
        self.config.MAX_TRADES_PER_DAY = getattr(config, 'MAX_TRADES_PER_DAY', 10)
        
    def calculate_ema(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return df['close'].ewm(span=period, adjust=False).mean()
    
    def calculate_keltner_channel(self, df: pd.DataFrame, length: int, mult: float) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Keltner Channel bands"""
        # Typical price
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        
        # Middle line (EMA)
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
    
    def calculate_vwap(self, df: pd.DataFrame) -> pd.Series:
        """Calculate VWAP for the day"""
        # Reset at market open
        df['date'] = pd.to_datetime(df.index).date
        
        vwap_values = []
        for date in df['date'].unique():
            day_data = df[df['date'] == date]
            
            # Calculate VWAP
            typical_price = (day_data['high'] + day_data['low'] + day_data['close']) / 3
            cumulative_tpv = (typical_price * day_data['volume']).cumsum()
            cumulative_volume = day_data['volume'].cumsum()
            
            day_vwap = cumulative_tpv / cumulative_volume
            vwap_values.extend(day_vwap.values)
        
        return pd.Series(vwap_values, index=df.index)
    
    def get_4h_bias(self, df_4h: pd.DataFrame) -> Tuple[str, float]:
        """Get directional bias from proven 4H Keltner strategy"""
        # Use original proven parameters
        kc_length_long = 15
        kc_mult_long = 0.75
        kc_length_short = 20
        kc_mult_short = 1.75
        
        # Calculate long KC
        kc_upper_long, _, _ = self.calculate_keltner_channel(
            df_4h, kc_length_long, kc_mult_long
        )
        
        # Calculate short KC
        _, _, kc_lower_short = self.calculate_keltner_channel(
            df_4h, kc_length_short, kc_mult_short
        )
        
        current_price = df_4h['close'].iloc[-1]
        
        # Check bias using proven logic
        if current_price > kc_upper_long.iloc[-1]:
            return 'LONG', 0.9  # Strong long bias
        elif current_price < kc_lower_short.iloc[-1]:
            return 'SHORT', 0.9  # Strong short bias
        else:
            return 'NEUTRAL', 0.5  # No clear bias
    
    def check_entry_signals(self, df_5m: pd.DataFrame, df_15m: pd.DataFrame, df_4h: pd.DataFrame) -> Optional[Dict]:
        """Check for day trading entry signals using 4H bias"""
        
        # Check if we've hit max trades
        if self.trades_today >= self.config.MAX_TRADES_PER_DAY:
            return None
        
        # Get 4H directional bias from PROVEN strategy
        bias_4h, bias_strength = self.get_4h_bias(df_4h)
        
        if bias_4h == 'NEUTRAL':
            return None  # No trades without clear 4H bias
        
        # 5M entry signals
        kc_upper_5m, kc_middle_5m, kc_lower_5m = self.calculate_keltner_channel(
            df_5m, self.config.KC_LENGTH, self.config.KC_MULT_LONG
        )
        
        # Calculate indicators
        ema_fast = self.calculate_ema(df_5m, 9)
        ema_slow = self.calculate_ema(df_5m, 21)
        vwap = self.calculate_vwap(df_5m)
        
        current_price = df_5m['close'].iloc[-1]
        
        # Volume confirmation
        avg_volume = df_5m['volume'].rolling(20).mean().iloc[-1]
        current_volume = df_5m['volume'].iloc[-1]
        volume_surge = current_volume > avg_volume * 1.5
        
        # 15M momentum check
        ema_15m_fast = self.calculate_ema(df_15m, 9)
        ema_15m_slow = self.calculate_ema(df_15m, 21)
        momentum_15m = 'BULLISH' if ema_15m_fast.iloc[-1] > ema_15m_slow.iloc[-1] else 'BEARISH'
        
        # Only take longs if 4H bias is LONG
        if bias_4h == 'LONG' and momentum_15m == 'BULLISH':
            # Breakout above KC upper band
            if (current_price > kc_upper_5m.iloc[-1] and 
                ema_fast.iloc[-1] > ema_slow.iloc[-1] and
                current_price > vwap.iloc[-1] and
                volume_surge):
                
                return {
                    'signal': 'LONG',
                    'reason': 'KC breakout with 4H long bias',
                    'strength': bias_strength * 0.8
                }
            
            # Bounce from KC middle (mean reversion in trend)
            elif (abs(current_price - kc_middle_5m.iloc[-1]) < current_price * 0.001 and
                  df_5m['close'].iloc[-2] < kc_middle_5m.iloc[-2] and
                  current_price > kc_middle_5m.iloc[-1]):
                
                return {
                    'signal': 'LONG',
                    'reason': 'KC bounce with 4H long bias',
                    'strength': bias_strength * 0.7
                }
        
        # Only take shorts if 4H bias is SHORT
        elif bias_4h == 'SHORT' and momentum_15m == 'BEARISH':
            # Breakdown below KC lower band
            if (current_price < kc_lower_5m.iloc[-1] and
                ema_fast.iloc[-1] < ema_slow.iloc[-1] and
                current_price < vwap.iloc[-1] and
                volume_surge):
                
                return {
                    'signal': 'SHORT',
                    'reason': 'KC breakdown with 4H short bias',
                    'strength': bias_strength * 0.8
                }
            
            # Rejection from KC middle
            elif (abs(current_price - kc_middle_5m.iloc[-1]) < current_price * 0.001 and
                  df_5m['close'].iloc[-2] > kc_middle_5m.iloc[-2] and
                  current_price < kc_middle_5m.iloc[-1]):
                
                return {
                    'signal': 'SHORT',
                    'reason': 'KC rejection with 4H short bias',
                    'strength': bias_strength * 0.7
                }
        
        return None
    
    def calculate_stops_and_targets(self, df: pd.DataFrame, signal: str, entry_price: float) -> Tuple[float, float]:
        """Calculate stop loss and take profit for day trades"""
        # Calculate ATR
        tr = pd.DataFrame({
            'hl': df['high'] - df['low'],
            'hc': abs(df['high'] - df['close'].shift(1)),
            'lc': abs(df['low'] - df['close'].shift(1))
        }).max(axis=1)
        atr = tr.ewm(span=self.config.ATR_PERIOD, adjust=False).mean().iloc[-1]
        
        if signal == 'LONG':
            stop_loss = entry_price - (self.config.LONG_STOP_ATR * atr)
            take_profit = entry_price + (self.config.LONG_TP_R * self.config.LONG_STOP_ATR * atr)
        else:  # SHORT
            stop_loss = entry_price + (self.config.SHORT_STOP_ATR * atr)
            take_profit = entry_price - (self.config.SHORT_TP_R * self.config.SHORT_STOP_ATR * atr)
        
        return stop_loss, take_profit
    
    def should_exit_time_based(self, entry_time: datetime) -> bool:
        """Check if we should exit based on time (avoid overnight)"""
        current_time = datetime.now()
        
        # Exit all positions 15 minutes before market close
        if current_time.hour == 16 and current_time.minute >= 45:
            return True
        
        # Exit if position held too long (2 hours for day trades)
        if (current_time - entry_time).seconds > 7200:
            return True
        
        return False
    
    def update_daily_stats(self, pnl: float):
        """Update daily statistics"""
        if pnl > 0:
            self.daily_stats['wins'] += 1
        else:
            self.daily_stats['losses'] += 1
        
        self.trades_today += 1
        self.last_trade_time = datetime.now()
    
    def reset_daily_stats(self):
        """Reset stats at start of new day"""
        self.trades_today = 0
        self.daily_stats = {'wins': 0, 'losses': 0}
    
    def get_momentum_score(self, df: pd.DataFrame) -> float:
        """Calculate momentum score for position sizing"""
        # Recent price action
        returns = df['close'].pct_change()
        
        # Momentum indicators
        rsi = self._calculate_rsi(df['close'], 14)
        momentum = returns.rolling(5).mean().iloc[-1]
        
        # Score from 0 to 1
        score = 0.5
        
        if rsi.iloc[-1] > 50 and rsi.iloc[-1] < 70:
            score += 0.2
        elif rsi.iloc[-1] < 30 or rsi.iloc[-1] > 70:
            score -= 0.2
        
        if momentum > 0:
            score += 0.3 * min(momentum * 100, 1)  # Cap at +0.3
        else:
            score -= 0.3 * min(abs(momentum * 100), 1)  # Cap at -0.3
        
        return max(0.2, min(score, 1.0))
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi