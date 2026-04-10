#!/usr/bin/env python3
"""MGC Autonomous Trading Bot"""

import asyncio
import logging
from datetime import datetime, time
from ib_insync import IB, Future, MarketOrder, StopOrder, LimitOrder, util
import pandas as pd
from typing import Optional, Tuple

from config import *
from day_trading_strategy import DayTradingStrategy
from ai_analyzer import AIMarketAnalyzer
from trade_database import TradeDatabase
from adaptive_engine import AdaptiveTradingEngine

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MGCTradingBot:
    """Autonomous MGC Trading Bot with Keltner Trend Rider Strategy"""
    
    def __init__(self):
        self.ib = IB()
        self.strategy = DayTradingStrategy(self)
        self.ai = AIMarketAnalyzer()  # AI on Dell RTX 3090
        self.db = TradeDatabase()  # Learning database
        self.adaptive = AdaptiveTradingEngine(self.db, self.ai)  # Adaptive engine
        self.contract = None
        self.position_size = 0
        self.daily_pnl = 0
        self.trades_today = 0
        self.last_position_direction = None
        self.stopped_out_recently = False
        self.running = False
        self.todays_trades = []  # Track for AI summary
        self.current_trade_id = None  # Track active trade
        self.recent_pnls = []  # Track recent P&Ls for position sizing
        
    def connect(self):
        """Connect to IB Gateway on Dell"""
        try:
            logger.info(f"Connecting to IB Gateway at {IB_HOST}:{IB_PORT}")
            self.ib.connect(IB_HOST, IB_PORT, clientId=IB_CLIENT_ID)
            logger.info("✅ Connected to IB Gateway successfully")
            
            # Create contract
            self.contract = Future(SYMBOL, CONTRACT_MONTH, EXCHANGE)
            self.ib.qualifyContracts(self.contract)
            logger.info(f"Contract qualified: {self.contract.localSymbol}")
            
            # Subscribe to account updates
            self.ib.accountSummaryEvent += self.on_account_update
            self.ib.orderStatusEvent += self.on_order_status
            
            return True
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def on_account_update(self, account_value):
        """Handle account updates"""
        if account_value.tag == 'DailyPnL':
            self.daily_pnl = float(account_value.value)
            
    def on_order_status(self, trade):
        """Handle order status updates"""
        if trade.orderStatus.status == 'Filled':
            logger.info(f"Order filled: {trade.order.action} {trade.orderStatus.filled} @ {trade.orderStatus.avgFillPrice}")
            
            # Check if this is an exit (stop or take profit)
            if isinstance(trade.order, (StopOrder, LimitOrder)) and self.current_trade_id:
                # Record exit
                exit_data = {
                    'exit_price': trade.orderStatus.avgFillPrice,
                    'exit_reason': 'Stop Loss' if isinstance(trade.order, StopOrder) else 'Take Profit',
                    'direction': 'LONG' if trade.order.action == 'SELL' else 'SHORT'
                }
                self.db.update_trade_exit(self.current_trade_id, exit_data)
                
                # Calculate P&L for adaptive sizing
                if exit_data['direction'] == 'LONG':
                    pnl = (exit_data['exit_price'] - self.strategy.entry_price) * trade.orderStatus.filled
                else:
                    pnl = (self.strategy.entry_price - exit_data['exit_price']) * trade.orderStatus.filled
                
                self.recent_pnls.append(pnl)
                if len(self.recent_pnls) > 20:
                    self.recent_pnls.pop(0)
                
                # Trigger post-trade analysis
                asyncio.create_task(self.adaptive.post_trade_analysis(self.current_trade_id))
                
                self.current_trade_id = None
            
            # Check if we were stopped out
            if isinstance(trade.order, StopOrder):
                self.stopped_out_recently = True
                self.last_position_direction = 'LONG' if trade.order.action == 'SELL' else 'SHORT'
    
    async def get_historical_data(self, duration: str = '2 D', bar_size: str = '5 mins') -> pd.DataFrame:
        """Fetch historical data from IB"""
        bars = await self.ib.reqHistoricalDataAsync(
            self.contract,
            endDateTime='',
            durationStr=duration,
            barSizeSetting=bar_size,
            whatToShow='TRADES',
            useRTH=True  # Regular trading hours for day trading
        )
        
        df = util.df(bars)
        df.set_index('date', inplace=True)
        return df
    
    async def get_multi_timeframe_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Get 5M, 15M, and 4H data for analysis"""
        # Get 5-minute data for entries
        df_5m = await self.get_historical_data('1 D', '5 mins')
        
        # Get 15-minute data for momentum
        df_15m = await self.get_historical_data('2 D', '15 mins')
        
        # Get 4-hour data for bias (proven strategy)
        df_4h = await self.get_historical_data('10 D', '4 hours')
        
        return df_5m, df_15m, df_4h
    
    def check_trading_hours(self) -> bool:
        """Check if we're within trading hours"""
        now = datetime.now()
        current_time = now.time()
        
        start = time(*TRADING_START)
        end = time(*TRADING_END)
        
        # Skip weekends
        if now.weekday() >= 5:
            return False
            
        return start <= current_time <= end
    
    def check_risk_limits(self) -> bool:
        """Check daily loss limit"""
        if self.daily_pnl <= -MAX_DAILY_LOSS:
            logger.warning(f"Daily loss limit reached: ${self.daily_pnl}")
            return False
        return True
    
    def get_current_position(self) -> int:
        """Get current position size"""
        positions = self.ib.positions()
        for pos in positions:
            if pos.contract.localSymbol == self.contract.localSymbol:
                return pos.position
        return 0
    
    def update_adaptive_params(self):
        """Update strategy with adaptive parameters"""
        # Update strategy with learned parameters
        for key, value in self.adaptive.current_params.items():
            if hasattr(self.strategy.config, key.upper()):
                setattr(self.strategy.config, key.upper(), value)
    
    async def place_entry_order(self, signal: str, df: pd.DataFrame):
        """Place entry order with stops and targets"""
        # AI validation check
        if not self.ai.validate_trade_setup(signal, df):
            logger.info(f"AI rejected {signal} trade setup")
            return
        
        current_price = self.ib.reqMktData(self.contract).marketPrice()
        
        # Calculate stops and targets
        stop_price, tp_price = self.strategy.calculate_stops_and_targets(
            df, signal, current_price
        )
        
        # Calculate adaptive position size
        adaptive_size = self.adaptive.calculate_position_size(self.recent_pnls)
        
        # Record market conditions
        market_snapshot = {
            'symbol': SYMBOL,
            'timeframe': PRIMARY_TIMEFRAME,
            'adx': df['adx'].iloc[-1] if 'adx' in df.columns else None,
            'volatility': df['atr'].iloc[-1] if 'atr' in df.columns else None,
            'trend': signal
        }
        self.db.record_market_snapshot(market_snapshot)
        
        # Create market order
        action = 'BUY' if signal == 'LONG' else 'SELL'
        entry_order = MarketOrder(action, adaptive_size)
        
        # Place entry order
        logger.info(f"Placing {signal} order for {adaptive_size} contracts")
        entry_trade = self.ib.placeOrder(self.contract, entry_order)
        
        # Wait for fill
        await asyncio.sleep(2)
        
        if entry_trade.orderStatus.status == 'Filled':
            fill_price = entry_trade.orderStatus.avgFillPrice
            
            # Record trade entry
            trade_data = {
                'symbol': SYMBOL,
                'direction': signal,
                'entry_price': fill_price,
                'quantity': adaptive_size,
                'stop_loss': stop_price,
                'take_profit': tp_price,
                'entry_reason': f"{signal} signal with AI approval",
                'market_conditions': market_snapshot,
                'ai_score': 0.8  # High score since AI approved
            }
            self.current_trade_id = self.db.record_trade_entry(trade_data)
            
            # Place stop order
            stop_action = 'SELL' if signal == 'LONG' else 'BUY'
            stop_order = StopOrder(stop_action, adaptive_size, stop_price)
            self.ib.placeOrder(self.contract, stop_order)
            logger.info(f"Stop placed at ${stop_price}")
            
            # Place take profit if applicable (shorts only)
            if tp_price:
                tp_order = LimitOrder(stop_action, adaptive_size, tp_price)
                self.ib.placeOrder(self.contract, tp_order)
                logger.info(f"Take profit placed at ${tp_price}")
            
            self.trades_today += 1
            self.stopped_out_recently = False
            self.entry_time = datetime.now()  # Track for time-based exits
    
    async def daily_learning_routine(self):
        """Run daily analysis and optimization"""
        logger.info("Running daily learning routine...")
        
        # Analyze recent performance
        performance = await self.adaptive.analyze_recent_performance()
        
        if performance['status'] == 'analyzed':
            logger.info(f"Performance metrics: {performance['metrics']}")
            logger.info(f"AI insights: {performance['ai_insights'][:200]}...")
            
            # Run parameter optimization if we have enough data
            if performance['metrics']['total_trades'] > 50:
                optimization = await self.adaptive.optimize_parameters()
                if optimization['status'] == 'optimized':
                    logger.info(f"Parameters optimized for {optimization['improvement']:.1%} improvement")
                    self.update_adaptive_params()
        
        # Check if we should trade today
        should_trade, reason = self.adaptive.should_trade_today()
        if not should_trade:
            logger.warning(f"Skipping trading today: {reason}")
            self.running = False
    
    async def run_strategy_loop(self):
        """Main strategy loop"""
        logger.info("Starting strategy loop...")
        
        # Run daily learning first
        await self.daily_learning_routine()
        
        # Update parameters from adaptive engine
        self.update_adaptive_params()
        
        while self.running:
            try:
                # Check trading conditions
                if not self.check_trading_hours():
                    await asyncio.sleep(60)
                    continue
                
                if not self.check_risk_limits():
                    logger.info("Risk limits exceeded, stopping for the day")
                    self.running = False
                    break
                
                # Get current position
                current_pos = self.get_current_position()
                
                # Get multi-timeframe data
                df_5m, df_15m, df_4h = await self.get_multi_timeframe_data()
                
                # Reset daily stats if new day
                if datetime.now().date() != getattr(self, 'last_trading_date', None):
                    self.strategy.reset_daily_stats()
                    self.last_trading_date = datetime.now().date()
                
                # Check for signals only if flat
                if current_pos == 0:
                    # Check for new signals with 4H bias
                    signal_data = self.strategy.check_entry_signals(df_5m, df_15m, df_4h)
                    if signal_data:
                        logger.info(f"New {signal_data['signal']} signal: {signal_data['reason']} (4H bias aligned)")
                        await self.place_entry_order(signal_data['signal'], df_5m)
                else:
                    # Check for time-based exits (day trading)
                    if hasattr(self, 'entry_time') and self.strategy.should_exit_time_based(self.entry_time):
                        logger.info("Time-based exit triggered")
                        # Place market order to exit
                        action = 'SELL' if current_pos > 0 else 'BUY'
                        exit_order = MarketOrder(action, abs(current_pos))
                        self.ib.placeOrder(self.contract, exit_order)
                
                # Sleep before next check
                await asyncio.sleep(30)  # 30 seconds for day trading
                
            except Exception as e:
                logger.error(f"Strategy loop error: {e}")
                await asyncio.sleep(60)
    
    async def start(self):
        """Start the trading bot"""
        if not self.connect():
            return
        
        self.running = True
        logger.info("MGC Trading Bot started")
        
        # Start strategy loop
        await self.run_strategy_loop()
    
    def stop(self):
        """Stop the trading bot"""
        logger.info("Stopping MGC Trading Bot...")
        self.running = False
        
        # Cancel all orders
        self.ib.reqGlobalCancel()
        
        # Disconnect
        if self.ib.isConnected():
            self.ib.disconnect()
        
        logger.info("MGC Trading Bot stopped")

async def main():
    """Main entry point"""
    bot = MGCTradingBot()
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        bot.stop()

if __name__ == "__main__":
    asyncio.run(main())