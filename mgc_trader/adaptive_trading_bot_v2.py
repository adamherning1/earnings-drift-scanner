#!/usr/bin/env python3
"""
Adaptive MGC Trading Bot v2 - With Auto-Reconnect
Combines proven 4H Keltner bias with 5M day trading entries
"""

from ib_insync import *
import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta
import logging
import json
import sys
import io
from config import *

# Fix encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('adaptive_bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class AdaptiveMGCBot:
    def __init__(self):
        self.ib = IB()
        self.contract = None
        self.running = True
        self.connection_retries = 0
        self.max_retries = 5
        
        # Trading state
        self.position = 0
        self.entry_price = 0
        self.stop_order = None
        self.trades_today = 0
        self.daily_pnl = 0
        self.initial_daily_pnl = 0
        
        # Adaptive parameters (optimized for more frequent trading)
        self.params = {
            'position_size': 2,
            'kc_length': 20,
            'kc_mult': 1.5,
            'atr_stop': 1.5,
            'take_profit_r': 1.2,
            'adx_threshold': 20,
            'max_daily_loss': 500,
            'max_trades_day': 15
        }
        
        # Performance tracking
        self.trade_history = []
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0
        self.total_loss = 0
        
        # Load existing trade history if available
        self.load_existing_trades()
        
    def ensure_connected(self):
        """Ensure we have a valid connection, reconnect if needed"""
        if not self.ib.isConnected():
            logger.warning("Connection lost! Attempting to reconnect...")
            return self.reconnect()
        return True
    
    def reconnect(self):
        """Attempt to reconnect to IB Gateway"""
        self.connection_retries = 0
        
        while self.connection_retries < self.max_retries:
            try:
                self.connection_retries += 1
                logger.info(f"Reconnection attempt {self.connection_retries}/{self.max_retries}")
                
                # Disconnect if still partially connected
                try:
                    self.ib.disconnect()
                except:
                    pass
                
                # Wait a bit before reconnecting
                self.ib.sleep(5)
                
                # Try to connect
                if self.connect():
                    logger.info("✅ Reconnected successfully!")
                    self.connection_retries = 0
                    return True
                    
            except Exception as e:
                logger.error(f"Reconnection failed: {e}")
                self.ib.sleep(10)
        
        logger.error(f"Failed to reconnect after {self.max_retries} attempts!")
        return False
        
    def connect(self):
        """Connect to IB Gateway"""
        try:
            logger.info(f"Connecting to IB Gateway at {IB_HOST}:{IB_PORT}...")
            self.ib.connect(IB_HOST, IB_PORT, clientId=IB_CLIENT_ID)
            
            if not self.ib.isConnected():
                return False
                
            logger.info("✅ Connected successfully!")
            
            # Setup contract
            self.contract = Future(SYMBOL, CONTRACT_MONTH, EXCHANGE)
            self.ib.qualifyContracts(self.contract)
            logger.info(f"Contract qualified: {self.contract.localSymbol}")
            
            # Request market data
            self.ib.reqMarketDataType(3)  # Delayed data
            self.ticker = self.ib.reqMktData(self.contract)
            
            # Cancel any orphaned orders
            open_orders = self.ib.orders()
            if open_orders:
                logger.warning(f"Found {len(open_orders)} orphaned orders, cancelling...")
                for order in open_orders:
                    self.ib.cancelOrder(order)
                self.ib.sleep(1)
            
            # Subscribe to order updates
            self.ib.orderStatusEvent += self.on_order_status
            
            # Get initial daily P&L
            for av in self.ib.accountValues():
                if av.tag == 'RealizedPnL':
                    self.initial_daily_pnl = float(av.value)
                    self.daily_pnl = self.initial_daily_pnl
                    if self.initial_daily_pnl != 0:
                        logger.info(f"Starting with daily P&L: ${self.initial_daily_pnl:.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def get_current_price(self):
        """Get current market price with safety checks"""
        if not self.ensure_connected():
            return None
            
        if self.ticker.marketPrice() > 0:
            return self.ticker.marketPrice()
        elif self.ticker.last > 0:
            return self.ticker.last
        elif self.ticker.bid > 0 and self.ticker.ask > 0:
            return (self.ticker.bid + self.ticker.ask) / 2
        return None
    
    def get_4h_bias(self):
        """Determine market bias from 4H timeframe"""
        if not self.ensure_connected():
            return 'NEUTRAL', 0
            
        try:
            # Get 4H bars
            end = datetime.now()
            bars = self.ib.reqHistoricalData(
                self.contract, end, '5 D', '4 hours',
                'TRADES', False, 1, False, []
            )
            
            if not bars or len(bars) < 30:
                return 'NEUTRAL', 0
            
            # Convert to DataFrame
            df = util.df(bars)
            
            # Calculate indicators
            df['KC_mid'] = df['close'].rolling(self.params['kc_length']).mean()
            df['ATR'] = self.calculate_atr(df, 14)
            df['KC_upper'] = df['KC_mid'] + (self.params['kc_mult'] * df['ATR'])
            df['KC_lower'] = df['KC_mid'] - (self.params['kc_mult'] * df['ATR'])
            
            # ADX for trend strength
            df['ADX'] = self.calculate_adx(df, 14)
            
            # Get latest values
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Trend strength scoring (0-5)
            trend_strength = 0
            
            # Price vs Keltner Channels
            if latest['close'] > latest['KC_upper']:
                trend_strength += 2
            elif latest['close'] < latest['KC_lower']:
                trend_strength -= 2
                
            # Previous candle confirmation
            if prev['close'] > prev['KC_upper']:
                trend_strength += 1
            elif prev['close'] < prev['KC_lower']:
                trend_strength -= 1
            
            # ADX strength
            if latest['ADX'] > self.params['adx_threshold']:
                trend_strength += 1 if trend_strength > 0 else -1
            
            # Determine bias
            if trend_strength >= 2:
                bias = 'BULLISH'
            elif trend_strength <= -2:
                bias = 'BEARISH'
            else:
                bias = 'NEUTRAL'
            
            logger.info(f"4H Bias: {bias} (strength: {trend_strength})")
            return bias, abs(trend_strength)
            
        except Exception as e:
            logger.error(f"Error getting 4H bias: {e}")
            return 'NEUTRAL', 0
    
    def check_entry_signal(self, bias, trend_strength):
        """Check for entry signals based on current bias"""
        if not self.ensure_connected():
            return None
            
        try:
            # Get 5-minute bars for entry timing
            end = datetime.now()
            bars = self.ib.reqHistoricalData(
                self.contract, end, '1 D', '5 mins',
                'TRADES', False, 1, False, []
            )
            
            if not bars or len(bars) < 50:
                return None
            
            df = util.df(bars)
            
            # Calculate indicators
            df['EMA20'] = df['close'].ewm(span=20).mean()
            df['EMA50'] = df['close'].ewm(span=50).mean()
            df['RSI'] = self.calculate_rsi(df['close'], 14)
            df['ATR'] = self.calculate_atr(df, 14)
            
            # Keltner for intraday
            df['KC_mid'] = df['close'].rolling(20).mean()
            df['KC_upper'] = df['KC_mid'] + (1.5 * df['ATR'])
            df['KC_lower'] = df['KC_mid'] - (1.5 * df['ATR'])
            
            # Volume analysis
            df['volume_ma'] = df['volume'].rolling(20).mean()
            df['high_volume'] = df['volume'] > df['volume_ma'] * 1.5
            
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            signal = None
            
            # BULLISH STRATEGIES
            if bias == 'BULLISH' or (bias == 'NEUTRAL' and trend_strength < 2):
                # 1. Pullback to EMA support
                if (latest['close'] > latest['EMA20'] and 
                    prev['low'] <= prev['EMA20'] and
                    latest['close'] > prev['high'] and
                    latest['RSI'] < 70):
                    signal = {'direction': 'BUY', 'strategy': 'EMA Pullback', 'confidence': 0.8}
                    
                # 2. Momentum breakout
                elif (latest['close'] > latest['KC_upper'] and
                      prev['close'] < prev['KC_upper'] and
                      latest['high_volume']):
                    signal = {'direction': 'BUY', 'strategy': 'KC Breakout', 'confidence': 0.7}
                    
                # 3. Oversold bounce (works in neutral too)
                elif latest['RSI'] < 30 and latest['close'] > prev['close']:
                    signal = {'direction': 'BUY', 'strategy': 'RSI Oversold', 'confidence': 0.6}
            
            # BEARISH STRATEGIES
            elif bias == 'BEARISH' or (bias == 'NEUTRAL' and trend_strength < 2):
                # 1. Rally to EMA resistance
                if (latest['close'] < latest['EMA20'] and
                    prev['high'] >= prev['EMA20'] and
                    latest['close'] < prev['low'] and
                    latest['RSI'] > 30):
                    signal = {'direction': 'SELL', 'strategy': 'EMA Rejection', 'confidence': 0.8}
                    
                # 2. Momentum breakdown
                elif (latest['close'] < latest['KC_lower'] and
                      prev['close'] > prev['KC_lower'] and
                      latest['high_volume']):
                    signal = {'direction': 'SELL', 'strategy': 'KC Breakdown', 'confidence': 0.7}
                    
                # 3. Overbought reversal
                elif latest['RSI'] > 70 and latest['close'] < prev['close']:
                    signal = {'direction': 'SELL', 'strategy': 'RSI Overbought', 'confidence': 0.6}
            
            # NEUTRAL/RANGE STRATEGIES (work in any bias)
            if bias == 'NEUTRAL':
                # Range breakouts
                recent_high = df['high'].rolling(20).max()
                recent_low = df['low'].rolling(20).min()
                range_size = recent_high - recent_low
                
                if latest['close'] > recent_high.iloc[-2] and latest['high_volume']:
                    signal = {'direction': 'BUY', 'strategy': 'Range Breakout Up', 'confidence': 0.7}
                elif latest['close'] < recent_low.iloc[-2] and latest['high_volume']:
                    signal = {'direction': 'SELL', 'strategy': 'Range Breakout Down', 'confidence': 0.7}
                    
                # Mean reversion from extremes
                elif latest['close'] > df['KC_upper'].iloc[-1] and latest['RSI'] > 65:
                    signal = {'direction': 'SELL', 'strategy': 'Mean Reversion Short', 'confidence': 0.6}
                elif latest['close'] < df['KC_lower'].iloc[-1] and latest['RSI'] < 35:
                    signal = {'direction': 'BUY', 'strategy': 'Mean Reversion Long', 'confidence': 0.6}
            
            if signal:
                logger.info(f"📊 Signal detected: {signal['strategy']} - {signal['direction']} (confidence: {signal['confidence']})")
            
            return signal
            
        except Exception as e:
            logger.error(f"Error checking entry signal: {e}")
            return None
    
    def run(self):
        """Main trading loop with connection monitoring"""
        logger.info("🚀 Starting Adaptive MGC Trading Bot v2 - With Auto-Reconnect")
        logger.info("=" * 60)
        logger.info("Features: Auto-reconnect, connection health checks, safer operation")
        logger.info("Strategies: Pullbacks, Breakouts, Mean Reversion, Range Trading")
        logger.info("=" * 60)
        
        while self.running:
            try:
                # Ensure we're connected before doing anything
                if not self.ensure_connected():
                    logger.error("Cannot establish connection. Waiting 30 seconds...")
                    self.ib.sleep(30)
                    continue
                
                # Check if market is open
                now = datetime.now()
                if now.weekday() >= 5 or not (time(6, 30) <= now.time() <= time(13, 0)):
                    logger.info("Market closed - waiting...")
                    self.ib.sleep(60)
                    continue
                
                # Check risk limits
                if not self.check_risk_limits():
                    logger.info("Risk limits reached - monitoring only")
                    self.ib.sleep(60)
                    continue
                
                # Update dashboard
                self.update_trading_status()
                
                # Check for exit if in position
                if self.position != 0:
                    self.check_exit_conditions()
                    
                    # SAFETY CHECK: Verify stop order
                    if self.stop_order:
                        open_orders = self.ib.orders()
                        stop_found = any(o.orderId == self.stop_order.orderId for o in open_orders)
                        if not stop_found:
                            logger.error("⚠️ STOP ORDER MISSING! Emergency close!")
                            self.close_position()
                    
                    self.ib.sleep(10)
                    continue
                
                # Get 4H bias and strength
                bias, trend_strength = self.get_4h_bias()
                
                # Check for signals
                signal = self.check_entry_signal(bias, trend_strength)
                
                if signal:
                    self.place_entry_order(signal)
                
                # Wait before next check
                self.ib.sleep(15)
                
            except KeyboardInterrupt:
                logger.info("Shutdown signal received")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                self.ib.sleep(10)
        
        # Clean shutdown
        if self.position != 0:
            logger.info("Closing position before shutdown...")
            self.close_position()
        
        logger.info(f"Final daily P&L: ${self.daily_pnl:.2f}")
        self.ib.disconnect()
    
    # Copy all the other methods from the original bot
    def check_risk_limits(self):
        """Check if we're within risk limits"""
        if self.trades_today >= self.params['max_trades_day']:
            return False
        if self.daily_pnl <= -self.params['max_daily_loss']:
            return False
        return True
    
    def place_entry_order(self, signal):
        """Place entry order with proper risk management"""
        # Implementation from original bot
        pass
    
    def check_exit_conditions(self):
        """Check if we should exit current position"""
        # Implementation from original bot
        pass
    
    def close_position(self):
        """Close current position"""
        # Implementation from original bot
        pass
    
    def on_order_status(self, trade):
        """Handle order status updates"""
        # Implementation from original bot
        pass
    
    def calculate_atr(self, df, period):
        """Calculate ATR"""
        # Implementation from original bot
        pass
    
    def calculate_rsi(self, series, period):
        """Calculate RSI"""
        # Implementation from original bot
        pass
    
    def calculate_adx(self, df, period):
        """Calculate ADX"""
        # Implementation from original bot
        pass
    
    def update_trading_status(self):
        """Update trading dashboard status"""
        # Implementation from original bot
        pass
    
    def load_existing_trades(self):
        """Load existing trade history"""
        # Implementation from original bot
        pass

def main():
    bot = AdaptiveMGCBot()
    
    if not bot.connect():
        logger.error("Failed initial connection!")
        return
    
    try:
        bot.run()
    except Exception as e:
        logger.error(f"Bot crashed: {e}", exc_info=True)
    finally:
        if bot.ib.isConnected():
            bot.ib.disconnect()
        logger.info("Bot stopped")

if __name__ == "__main__":
    main()