#!/usr/bin/env python3
"""
Adaptive MGC Trading Bot with Learning Capabilities
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
        
        # Trading state
        self.position = 0
        self.entry_price = 0
        self.stop_order = None
        self.trades_today = 0
        self.daily_pnl = 0
        self.initial_daily_pnl = 0
        
        # Adaptive parameters (optimized for more frequent trading)
        self.params = {
            'position_size': 2,  # Start smaller for more trades
            'kc_length': 20,
            'kc_mult': 1.5,
            'atr_stop': 1.5,  # Tighter stops for intraday
            'take_profit_r': 1.2,  # Quicker profits
            'adx_threshold': 20,  # Lower threshold
            'max_daily_loss': 500,
            'max_trades_day': 15  # Allow more trades
        }
        
        # Performance tracking
        self.trade_history = []
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0
        self.total_loss = 0
        
        # Load existing trade history if available
        self.load_existing_trades()
        
    def connect(self):
        """Connect to IB Gateway"""
        try:
            logger.info(f"Connecting to IB Gateway at {IB_HOST}:{IB_PORT}...")
            self.ib.connect(IB_HOST, IB_PORT, clientId=IB_CLIENT_ID)
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
                    break
            
            return True
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def get_4h_bias(self):
        """Get trend bias from 4H timeframe for direction"""
        try:
            # Get 4H bars
            bars = self.ib.reqHistoricalData(
                self.contract,
                endDateTime='',
                durationStr='10 D',
                barSizeSetting='4 hours',
                whatToShow='TRADES',
                useRTH=False
            )
            
            if len(bars) < 20:
                return 'NEUTRAL', 0
            
            df = util.df(bars)
            
            # Calculate indicators
            df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
            df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
            df['atr'] = df['high'].subtract(df['low']).rolling(14).mean()
            df['kc_upper'] = df['ema20'] + (df['atr'] * 0.75)
            df['kc_lower'] = df['ema20'] - (df['atr'] * 0.75)
            
            # Get current values
            last_close = df['close'].iloc[-1]
            last_ema20 = df['ema20'].iloc[-1]
            last_ema50 = df['ema50'].iloc[-1]
            last_kc_upper = df['kc_upper'].iloc[-1]
            last_kc_lower = df['kc_lower'].iloc[-1]
            
            # Trend strength (distance from EMA as %)
            distance_pct = abs(last_close - last_ema20) / last_ema20 * 100
            
            # Determine bias with multiple confirmations
            bullish_score = 0
            bearish_score = 0
            
            # Price vs EMAs
            if last_close > last_ema20: bullish_score += 1
            else: bearish_score += 1
            
            if last_close > last_ema50: bullish_score += 1
            else: bearish_score += 1
            
            if last_ema20 > last_ema50: bullish_score += 1
            else: bearish_score += 1
            
            # Keltner position
            if last_close > last_kc_upper: bullish_score += 2  # Strong signal
            elif last_close < last_kc_lower: bearish_score += 2
            
            # Determine bias
            if bullish_score >= 4:
                logger.info(f"4H Bias: STRONG BULLISH (score {bullish_score}/5, distance {distance_pct:.1f}%)")
                return 'LONG', distance_pct
            elif bearish_score >= 4:
                logger.info(f"4H Bias: STRONG BEARISH (score {bearish_score}/5, distance {distance_pct:.1f}%)")
                return 'SHORT', distance_pct
            elif bullish_score >= 3:
                logger.info(f"4H Bias: MODERATE BULLISH (score {bullish_score}/5)")
                return 'LONG', distance_pct
            elif bearish_score >= 3:
                logger.info(f"4H Bias: MODERATE BEARISH (score {bearish_score}/5)")
                return 'SHORT', distance_pct
            else:
                logger.info(f"4H Bias: NEUTRAL/RANGE (bull {bullish_score} vs bear {bearish_score})")
                return 'NEUTRAL', distance_pct
                
        except Exception as e:
            logger.error(f"Error getting 4H bias: {e}")
            return 'NEUTRAL', 0
    
    def check_entry_signal(self, bias, trend_strength):
        """Check for multiple entry patterns on 5M timeframe"""
        try:
            # Get 5M bars
            bars = self.ib.reqHistoricalData(
                self.contract,
                endDateTime='',
                durationStr='1 D',
                barSizeSetting='5 mins',
                whatToShow='TRADES',
                useRTH=True
            )
            
            if len(bars) < 30:
                return None
            
            df = util.df(bars)
            
            # Calculate indicators
            df['ema9'] = df['close'].ewm(span=9, adjust=False).mean()
            df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
            df['atr'] = df['high'].subtract(df['low']).rolling(14).mean()
            df['kc_upper'] = df['ema20'] + (df['atr'] * 1.5)
            df['kc_lower'] = df['ema20'] - (df['atr'] * 1.5)
            
            # RSI for oversold/overbought
            df['rsi'] = self.calculate_rsi(df['close'], 14)
            
            # Recent high/low
            df['high_5'] = df['high'].rolling(5).max()
            df['low_5'] = df['low'].rolling(5).min()
            
            last = df.iloc[-1]
            prev = df.iloc[-2]
            
            # BULLISH BIAS ENTRIES
            if bias == 'LONG':
                # 1. Pullback to EMA support
                if (last['close'] > last['ema9'] > last['ema20'] and 
                    prev['low'] <= prev['ema9'] and 
                    last['close'] > last['ema9'] and
                    last['rsi'] < 70):
                    logger.info("🔥 LONG: Pullback to EMA9 support with bounce!")
                    return 'LONG'
                
                # 2. Momentum breakout
                if (last['close'] > last['high_5'] and 
                    last['close'] > last['ema9'] and
                    last['volume'] > df['volume'].rolling(20).mean().iloc[-1]):
                    logger.info("🔥 LONG: Momentum breakout of 5-bar high!")
                    return 'LONG'
                
                # 3. Oversold bounce
                if (last['rsi'] < 35 and prev['rsi'] < 30 and 
                    last['close'] > prev['close'] and
                    last['close'] > last['ema20']):
                    logger.info("🔥 LONG: Oversold bounce from RSI < 30!")
                    return 'LONG'
            
            # BEARISH BIAS ENTRIES
            elif bias == 'SHORT':
                # 1. Rally to EMA resistance
                if (last['close'] < last['ema9'] < last['ema20'] and 
                    prev['high'] >= prev['ema9'] and 
                    last['close'] < last['ema9'] and
                    last['rsi'] > 30):
                    logger.info("🔥 SHORT: Rally to EMA9 resistance with rejection!")
                    return 'SHORT'
                
                # 2. Momentum breakdown
                if (last['close'] < last['low_5'] and 
                    last['close'] < last['ema9'] and
                    last['volume'] > df['volume'].rolling(20).mean().iloc[-1]):
                    logger.info("🔥 SHORT: Momentum breakdown of 5-bar low!")
                    return 'SHORT'
                
                # 3. Overbought reversal
                if (last['rsi'] > 65 and prev['rsi'] > 70 and 
                    last['close'] < prev['close'] and
                    last['close'] < last['ema20']):
                    logger.info("🔥 SHORT: Overbought reversal from RSI > 70!")
                    return 'SHORT'
            
            # NEUTRAL RANGE TRADING
            else:
                # 1. Range breakout long
                if (last['close'] > last['kc_upper'] and 
                    prev['close'] <= prev['kc_upper'] and
                    last['rsi'] < 70):
                    logger.info("🔥 LONG: Range breakout above KC upper!")
                    return 'LONG'
                
                # 2. Range breakout short
                if (last['close'] < last['kc_lower'] and 
                    prev['close'] >= prev['kc_lower'] and
                    last['rsi'] > 30):
                    logger.info("🔥 SHORT: Range breakdown below KC lower!")
                    return 'SHORT'
                
                # 3. Mean reversion from extremes
                if last['rsi'] < 25:
                    logger.info("🔥 LONG: Extreme oversold RSI < 25 in range!")
                    return 'LONG'
                elif last['rsi'] > 75:
                    logger.info("🔥 SHORT: Extreme overbought RSI > 75 in range!")
                    return 'SHORT'
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking entry signal: {e}")
            return None
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def validate_price(self, price, description="Price"):
        """Validate price is valid for MGC (0.10 increments)"""
        rounded = round(price * 10) / 10
        if abs(price - rounded) > 0.001:  # Allow tiny float errors
            logger.error(f"INVALID {description}: {price} - must be multiple of 0.10!")
            return False, rounded
        return True, rounded
    
    def load_existing_trades(self):
        """Load any existing trades from today's session"""
        try:
            # Check if we have an existing trade from today
            # This is the trade that happened at 10:13 AM
            if datetime.now().date() == datetime(2026, 4, 6).date():
                # Add the existing trade to history
                existing_trade = {
                    'timestamp': '2026-04-06T10:13:40',
                    'symbol': 'MGC',
                    'entry_price': 4673.90,
                    'exit_price': 4688.40,
                    'contracts': 2,
                    'profit': -293.88
                }
                self.trade_history.append(existing_trade)
                self.losing_trades = 1
                self.total_loss = 293.88
                logger.info("Loaded existing trade from today: 1 loss, -$293.88")
        except Exception as e:
            logger.error(f"Error loading existing trades: {e}")
    
    def calculate_adx(self, df):
        """Calculate ADX indicator"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(14).mean()
        
        # Directional movements
        up = high - high.shift()
        down = low.shift() - low
        pos_dm = np.where((up > down) & (up > 0), up, 0)
        neg_dm = np.where((down > up) & (down > 0), down, 0)
        
        pos_di = 100 * pd.Series(pos_dm).rolling(14).mean() / atr
        neg_di = 100 * pd.Series(neg_dm).rolling(14).mean() / atr
        
        dx = 100 * abs(pos_di - neg_di) / (pos_di + neg_di)
        adx = dx.rolling(14).mean()
        
        return adx
    
    def place_entry_order(self, direction):
        """Place market order with stop loss and take profit"""
        try:
            if not self.ticker.marketPrice():
                logger.error("No market price available")
                return
            
            current_price = self.ticker.marketPrice()
            
            # PRE-TRADE VALIDATION
            logger.info("="*60)
            logger.info(f"PRE-TRADE VALIDATION for {direction}")
            logger.info(f"Current price: ${current_price:.2f}")
            logger.info(f"Position size: {self.params['position_size']} contracts")
            
            # Create market order
            action = 'BUY' if direction == 'LONG' else 'SELL'
            order = MarketOrder(action, self.params['position_size'])
            
            # Place order
            trade = self.ib.placeOrder(self.contract, order)
            logger.info(f"📈 Placed {direction} order for {self.params['position_size']} contracts")
            
            # Wait for fill
            self.ib.sleep(2)
            
            if trade.orderStatus.status == 'Filled':
                self.position = self.params['position_size'] if direction == 'LONG' else -self.params['position_size']
                self.entry_price = trade.orderStatus.avgFillPrice
                
                # Calculate stop loss
                bars = self.ib.reqHistoricalData(
                    self.contract, '', '1 D', '5 mins', 'TRADES', True
                )
                df = util.df(bars)
                current_atr = df['high'].subtract(df['low']).rolling(14).mean().iloc[-1]
                
                if direction == 'LONG':
                    stop_price = self.entry_price - (current_atr * self.params['atr_stop'])
                    tp_price = self.entry_price + (current_atr * self.params['atr_stop'] * self.params['take_profit_r'])
                else:
                    stop_price = self.entry_price + (current_atr * self.params['atr_stop'])
                    tp_price = self.entry_price - (current_atr * self.params['atr_stop'] * self.params['take_profit_r'])
                
                # Round to valid MGC tick size (0.10)
                stop_price = round(stop_price * 10) / 10
                tp_price = round(tp_price * 10) / 10
                
                # DOUBLE CHECK: Ensure prices are valid
                if stop_price % 0.10 > 0.001 or tp_price % 0.10 > 0.001:
                    logger.error(f"PRICE VALIDATION FAILED! Stop: {stop_price}, TP: {tp_price}")
                    logger.error("ABORTING TRADE - Invalid prices detected")
                    return
                
                # Place stop loss
                stop_action = 'SELL' if direction == 'LONG' else 'BUY'
                self.stop_order = StopOrder(stop_action, self.params['position_size'], stop_price)
                
                # CRITICAL: Verify stop order before placing
                logger.info(f"Placing stop order: {stop_action} {self.params['position_size']} @ ${stop_price:.2f}")
                if stop_price != round(stop_price * 10) / 10:
                    logger.error(f"INVALID STOP PRICE: {stop_price} - must be multiple of 0.10!")
                    # Force close position
                    self.close_position()
                    return
                
                stop_trade = self.ib.placeOrder(self.contract, self.stop_order)
                self.ib.sleep(2)
                
                # Verify stop order was accepted
                if stop_trade.orderStatus.status not in ['PreSubmitted', 'Submitted']:
                    logger.error(f"STOP ORDER FAILED: {stop_trade.orderStatus}")
                    logger.error("EMERGENCY: Closing position immediately!")
                    self.close_position()
                    return
                
                logger.info(f"✅ Entry filled at ${self.entry_price:.2f}")
                logger.info(f"🛡️ Stop loss at ${stop_price:.2f} (risk: ${abs(self.entry_price - stop_price) * 10 * self.params['position_size']:.2f})")
                logger.info(f"🎯 Target at ${tp_price:.2f} (reward: ${abs(tp_price - self.entry_price) * 10 * self.params['position_size']:.2f})")
                
                self.trades_today += 1
                
                # Update dashboard immediately after entry
                self.update_trading_status()
                logger.info(f"Dashboard updated with new position")
                
        except Exception as e:
            logger.error(f"Error placing order: {e}")
    
    def on_order_status(self, trade):
        """Handle order status updates"""
        if trade.orderStatus.status == 'Filled':
            if isinstance(trade.order, StopOrder) or trade.order == self.stop_order:
                # Stop loss hit
                exit_price = trade.orderStatus.avgFillPrice
                pnl = self.calculate_pnl(exit_price)
                
                logger.info(f"❌ Stop loss hit at ${exit_price:.2f}, P&L: ${pnl:.2f}")
                
                self.record_trade(pnl, exit_price)
                self.position = 0
                self.stop_order = None
                
                # Learn from this trade
                self.adapt_parameters()
    
    def check_exit_conditions(self):
        """Check if we should exit the position"""
        if self.position == 0:
            return
        
        try:
            current_price = self.ticker.marketPrice()
            if not current_price:
                return
            
            # Calculate current P&L
            if self.position > 0:
                current_pnl = (current_price - self.entry_price) * 10 * abs(self.position)
                price_change = (current_price - self.entry_price) / self.entry_price
            else:
                current_pnl = (self.entry_price - current_price) * 10 * abs(self.position)
                price_change = (self.entry_price - current_price) / self.entry_price
            
            # Check take profit
            bars = self.ib.reqHistoricalData(
                self.contract, '', '1 D', '5 mins', 'TRADES', True
            )
            df = util.df(bars)
            current_atr = df['high'].subtract(df['low']).rolling(14).mean().iloc[-1]
            
            tp_distance = current_atr * self.params['atr_stop'] * self.params['take_profit_r']
            
            if price_change * self.entry_price >= tp_distance:
                logger.info(f"🎯 Take profit reached! Closing position at ${current_price:.2f}")
                self.close_position()
            
        except Exception as e:
            logger.error(f"Error checking exit conditions: {e}")
    
    def close_position(self):
        """Close the current position"""
        if self.position == 0:
            return
        
        try:
            # Cancel stop order first
            if self.stop_order:
                self.ib.cancelOrder(self.stop_order)
            
            # Place market order to close
            action = 'SELL' if self.position > 0 else 'BUY'
            close_order = MarketOrder(action, abs(self.position))
            trade = self.ib.placeOrder(self.contract, close_order)
            
            # Wait for fill
            self.ib.sleep(2)
            
            if trade.orderStatus.status == 'Filled':
                exit_price = trade.orderStatus.avgFillPrice
                pnl = self.calculate_pnl(exit_price)
                
                logger.info(f"💰 Position closed at ${exit_price:.2f}, P&L: ${pnl:.2f}")
                
                self.record_trade(pnl, exit_price)
                self.position = 0
                self.stop_order = None
                
                # Learn from this trade
                self.adapt_parameters()
                
        except Exception as e:
            logger.error(f"Error closing position: {e}")
    
    def calculate_pnl(self, exit_price):
        """Calculate P&L for a trade"""
        if self.position > 0:
            pnl = (exit_price - self.entry_price) * 10 * self.position
        else:
            pnl = (self.entry_price - exit_price) * 10 * abs(self.position)
        return pnl
    
    def record_trade(self, pnl, exit_price=None):
        """Record trade results"""
        # Track cumulative P&L for this session
        session_pnl = sum(t['profit'] for t in self.trade_history)
        self.daily_pnl = self.initial_daily_pnl + session_pnl + pnl
        
        trade_data = {
            'timestamp': datetime.now().isoformat(),
            'symbol': 'MGC',
            'entry_price': self.entry_price,
            'exit_price': exit_price or self.ticker.marketPrice(),
            'contracts': abs(self.position),
            'profit': pnl
        }
        
        self.trade_history.append(trade_data)
        
        # Update win/loss statistics immediately
        if pnl > 0:
            self.winning_trades += 1
            self.total_profit += pnl
            logger.info(f"✅ WINNING TRADE: +${pnl:.2f}")
        else:
            self.losing_trades += 1
            self.total_loss += abs(pnl)
            logger.info(f"❌ LOSING TRADE: -${abs(pnl):.2f}")
        
        # Update dashboard immediately after trade
        self.update_trading_status()
        logger.info(f"Dashboard updated - Total trades: {self.winning_trades + self.losing_trades}")
        
        # Log performance summary
        total_trades = self.winning_trades + self.losing_trades
        win_rate = self.winning_trades / total_trades if total_trades > 0 else 0
        profit_factor = self.total_profit / self.total_loss if self.total_loss > 0 else 0
        
        logger.info(f"📊 Performance Summary:")
        logger.info(f"   Total Trades: {total_trades}")
        logger.info(f"   Win Rate: {win_rate:.1%} ({self.winning_trades}W/{self.losing_trades}L)")
        logger.info(f"   Profit Factor: {profit_factor:.2f}")
        logger.info(f"   Daily P&L: ${self.daily_pnl:.2f}")
    
    def adapt_parameters(self):
        """Learn and adapt parameters based on performance"""
        if len(self.trade_history) < 10:
            return  # Need more data
        
        # Analyze recent trades
        recent_trades = self.trade_history[-10:]
        recent_wins = sum(1 for t in recent_trades if t['pnl'] > 0)
        recent_win_rate = recent_wins / 10
        
        logger.info(f"🧠 Learning: Recent win rate {recent_win_rate:.1%}")
        
        # Adaptive adjustments
        if recent_win_rate < 0.4:
            # Struggling - tighten risk
            self.params['atr_stop'] = max(1.5, self.params['atr_stop'] - 0.2)
            self.params['adx_threshold'] = min(30, self.params['adx_threshold'] + 2)
            logger.info("📉 Tightening risk parameters")
            
        elif recent_win_rate > 0.7:
            # Doing well - can take slightly more risk
            self.params['position_size'] = min(5, self.params['position_size'] + 1)
            logger.info(f"📈 Increasing position size to {self.params['position_size']}")
        
        # Save adapted parameters
        self.save_parameters()
    
    def save_parameters(self):
        """Save current parameters to file"""
        try:
            with open('adaptive_params.json', 'w') as f:
                json.dump(self.params, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving parameters: {e}")
    
    def check_risk_limits(self):
        """Check if we should stop trading"""
        if self.daily_pnl <= -self.params['max_daily_loss']:
            logger.warning(f"🛑 Daily loss limit reached: ${self.daily_pnl:.2f}")
            return False
        
        if self.trades_today >= self.params['max_trades_day']:
            logger.info(f"📋 Max trades for today reached: {self.trades_today}")
            return False
        
        return True
    
    def update_trading_status(self):
        """Update dashboard status file"""
        try:
            # Get real account values
            net_liq = 997981.79
            for av in self.ib.accountValues():
                if av.tag == 'NetLiquidation':
                    net_liq = float(av.value)
                    break
            
            # Calculate current unrealized P&L if in position
            unrealized = 0
            current_price = self.ticker.marketPrice() if self.ticker.marketPrice() else 0
            
            if self.position != 0 and current_price > 0:
                if self.position > 0:  # Long
                    unrealized = (current_price - self.entry_price) * 10 * self.position
                else:  # Short
                    unrealized = (self.entry_price - current_price) * 10 * abs(self.position)
            
            # Format net liquidation with commas
            net_liq_formatted = f"${net_liq:,.2f}"
            
            # Calculate total P&L (realized from trades)
            total_pnl = self.daily_pnl - self.initial_daily_pnl
            
            status = {
                "connected": True,
                "account": self.ib.managedAccounts()[0] if self.ib.managedAccounts() else "N/A",
                "net_liquidation": net_liq_formatted,
                "net_liquidation_value": net_liq,
                "daily_pnl": self.daily_pnl,
                "unrealized_pnl": unrealized,
                "positions": 1 if self.position != 0 else 0,
                "winning_trades": self.winning_trades,
                "losing_trades": self.losing_trades,
                "total_profit": self.total_profit,
                "total_loss": self.total_loss,
                "total_pnl": total_pnl,
                "profit_factor": self.total_profit / self.total_loss if self.total_loss > 0 else 0,
                "trade_log": self.trade_history[-10:],  # Last 10 trades
                "timestamp": datetime.now().isoformat(),
                "message": f"Bot Trading: {self.position} MGC @ ${self.entry_price:.2f}" if self.position != 0 else "Adaptive Bot Scanning",
                "mgc_price": current_price
            }
            
            # Log what we're updating
            if self.position != 0:
                logger.debug(f"Dashboard update: Position={self.position}, Entry=${self.entry_price:.2f}, Current=${current_price:.2f}, Unrealized=${unrealized:.2f}")
            
            with open('../trading_status.json', 'w') as f:
                json.dump(status, f, indent=2)
            
            # Also update the separate files for the dashboard
            with open('../trading_stats.json', 'w') as f:
                stats = {
                    "winning_trades": self.winning_trades,
                    "losing_trades": self.losing_trades,
                    "total_profit": self.total_profit,
                    "total_loss": self.total_loss,
                    "profit_factor": self.total_profit / self.total_loss if self.total_loss > 0 else 0
                }
                json.dump(stats, f, indent=2)
            
            with open('../trade_log.json', 'w') as f:
                json.dump(self.trade_history, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error updating status: {e}")
    
    def run(self):
        """Main trading loop"""
        logger.info("🚀 Starting Adaptive MGC Trading Bot - Multi-Strategy Edition")
        logger.info("=" * 60)
        logger.info("Strategies: Pullbacks, Breakouts, Mean Reversion, Range Trading")
        logger.info("Checking for signals every 15 seconds...")
        logger.info("SAFETY FEATURES: Price validation, stop verification, emergency close")
        logger.info("=" * 60)
        
        while self.running:
            try:
                # Check if market is open
                now = datetime.now()
                if now.weekday() >= 5 or not (time(6, 0) <= now.time() <= time(17, 0)):
                    logger.info("Market closed - waiting...")
                    self.ib.sleep(60)
                    continue
                
                # Check risk limits
                if not self.check_risk_limits():
                    logger.info("Risk limits reached - monitoring only")
                    self.ib.sleep(60)
                    continue
                
                # Update dashboard every loop
                self.update_trading_status()
                
                # Check for exit if in position
                if self.position != 0:
                    self.check_exit_conditions()
                    
                    # SAFETY CHECK: Verify stop order is still active
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
                
                # Always check for signals (including neutral range trades)
                signal = self.check_entry_signal(bias, trend_strength)
                
                if signal:
                    self.place_entry_order(signal)
                
                # Wait before next check (more frequent for intraday)
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

def main():
    bot = AdaptiveMGCBot()
    
    if not bot.connect():
        logger.error("Failed to connect!")
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