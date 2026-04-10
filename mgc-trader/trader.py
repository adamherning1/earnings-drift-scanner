"""
MGC Day Trader — Main Trading Loop
Fully synchronous using ib_insync's event-driven model.
"""

import logging
import os
import sys
import json
from datetime import datetime, time as dtime
from pathlib import Path
import pytz

from ib_connection import IBConnection
from strategies import create_strategies, Signal, HigherTimeframeBias
from risk_manager import RiskManager
from data_collector import DataCollector
import config

# Volume Profile filter — assess signal quality based on volume gaps/balance zones
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "volume-profile"))
try:
    from volume_filter import VolumeProfileFilter
    VOLUME_PROFILE_AVAILABLE = True
except ImportError:
    VOLUME_PROFILE_AVAILABLE = False
    logger = logging.getLogger("mgc-trader")
    logger.warning("VolumeProfileFilter not available — running without volume profile filter")

# ── Logging Setup ────────────────────────────────────────────────────────────
os.makedirs(config.LOG_DIR, exist_ok=True)
log_file = os.path.join(config.LOG_DIR, f"trader_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("mgc-trader")

ET = pytz.timezone("US/Eastern")


class MGCTrader:
    """Main trading engine — fully synchronous."""

    def __init__(self):
        self.ib = IBConnection()
        self.risk = RiskManager()
        self.data = DataCollector()
        self.strategies = []
        self.trade_log = []
        self.running = False
        self._context_counter = 0
        self._last_date = None
        self._flattening = False          # prevent re-entry during EOD flatten
        self._cooldown_until_bar = 0      # bar count cooldown after stop-out
        self._bar_count = 0               # total bars processed today
        self._daily_bias = None           # "BUY" or "SELL" — first signal sets it
        self._watchdog_checks = 0         # counter for stop watchdog

        # 4H Breakout Momentum bias filter — only trade in direction of 4H trend
        self._htf_bias = HigherTimeframeBias(lookback=20)
        self._bars_since_bias_refresh = 0  # refresh 4H bias every 48 5-min bars (4 hours)

        # Volume Profile filter — blocks signals heading into HVN walls,
        # flags high-quality signals heading into LVN gaps
        self._volume_filter = None
        if VOLUME_PROFILE_AVAILABLE:
            data_dir = os.path.join(os.path.dirname(__file__), "..", "data-collector", "data")
            self._volume_filter = VolumeProfileFilter(
                symbol="MGC", data_dir=data_dir, lookback_days=20, block_on_hvn=True
            )
        self._bars_since_vp_refresh = 0  # refresh volume profile every 48 bars (~4 hours)

        # Daily max loss circuit breaker ($500)
        self._daily_loss_limit = 500.0     # stop new entries if realized loss exceeds this
        self._daily_realized_pnl = 0.0     # track realized P&L today
        self._loss_breaker_active = False  # True = no new entries allowed

        # Multi-timeframe: aggregate 5-min bars into 15-min bars
        self._5m_buffer = []              # buffer of 5-min bars for 15-min aggregation
        self._15m_bars = []               # completed 15-min bars
        self._pending_mtf_signal = None   # signal from 15-min evaluation, execute on next 5-min bar
        self._mtf_enabled = getattr(config, 'MTF_ENABLED', False)

        # Position tracking for exit detection
        self._last_position_size = 0      # track position changes to detect stop/TP fills
        self._active_trades = []          # list of active trade entry records

    def start(self):
        """Initialize and start the trading loop."""
        logger.info("=" * 60)
        logger.info("MGC Day Trader starting up")
        logger.info(f"Config: max_daily_loss=${config.MAX_DAILY_LOSS}, "
                     f"max_trades={config.MAX_DAILY_TRADES}, "
                     f"max_position={config.MAX_POSITION_SIZE}")
        logger.info("=" * 60)

        # Connect to IB
        connected = self.ib.connect()
        if not connected:
            logger.error("Failed to connect to IB. Exiting.")
            return

        # Account info
        summary = self.ib.get_account_summary()
        logger.info(f"Account: {json.dumps(summary, indent=2)}")

        # Load strategies
        self.strategies = create_strategies()
        logger.info(f"Loaded {len(self.strategies)} strategies")

        # Warm up indicators with historical data
        self._warmup()

        # CRITICAL: Cancel ALL orphaned orders from prior sessions before doing anything
        self._cancel_all_orphaned_orders()

        # Check for orphaned positions (from prior runs) and ensure they have protection
        self._check_orphaned_positions()

        # Start trading loop
        self.running = True
        self._run_loop()

    def _warmup(self):
        """Fetch historical bars to warm up indicators."""
        logger.info("Warming up indicators with historical data...")
        bars = self.ib.get_historical_bars(duration="20 D", bar_size="5 mins")
        if bars:
            for bar in bars:
                for strat in self.strategies:
                    strat.evaluate(
                        bar.date, bar.open, bar.high, bar.low, bar.close,
                        bar.volume if hasattr(bar, "volume") else 0,
                    )
            logger.info(f"Warmed up with {len(bars)} historical bars")

        # Warm up 4H bias filter with separate historical fetch
        try:
            bars_4h = self.ib.get_historical_bars(duration="30 D", bar_size="4 hours")
            if bars_4h:
                for bar in bars_4h:
                    self._htf_bias.update(bar.high, bar.low, bar.close)
                logger.info(f"4H Bias warmed with {len(bars_4h)} bars → "
                            f"direction={self._htf_bias.direction}, "
                            f"level={self._htf_bias.breakout_level}")
            else:
                logger.warning("No 4H bars returned — bias filter will start neutral")
        except Exception as e:
            logger.warning(f"4H bias warmup failed: {e} — bias filter will start neutral")

        if bars:
            # Reset trade counts after warmup — signals during warmup don't count
            for strat in self.strategies:
                if hasattr(strat, 'trades_today'):
                    strat.trades_today = 0
                if hasattr(strat, 'near_vwap_count'):
                    strat.near_vwap_count = 0

        # Load volume profile filter
        if self._volume_filter:
            if self._volume_filter.refresh():
                status = self._volume_filter.get_status()
                logger.info(f"Volume Profile loaded: POC={status['poc']}, "
                           f"VA={status['va_low']}-{status['va_high']}, "
                           f"{status['hvn_zones']} HVN zones, {status['lvn_zones']} LVN zones")
            else:
                logger.warning("Volume Profile filter failed to load — running without it")

    def _cancel_all_orphaned_orders(self):
        """Cancel ALL existing orders on startup to prevent orphans from prior sessions."""
        open_trades = self.ib.ib.openTrades()
        cancelled = 0
        for t in open_trades:
            if t.contract.symbol == config.SYMBOL:
                try:
                    self.ib.ib.cancelOrder(t.order)
                    cancelled += 1
                    logger.info(f"Cancelled orphaned order {t.order.orderId}: "
                                f"{t.order.action} {t.order.totalQuantity} {t.order.orderType}")
                except Exception as e:
                    logger.error(f"Failed to cancel order {t.order.orderId}: {e}")
        if cancelled:
            self.ib.ib.sleep(3)  # wait for cancels to process
            logger.info(f"Cancelled {cancelled} orphaned orders from prior session")
        else:
            logger.info("No orphaned orders found on startup")

    def _check_orphaned_positions(self):
        """On startup, check for existing positions without protective orders."""
        positions = self.ib.get_positions()
        if not positions:
            logger.info("No existing positions on startup")
            return

        # Check if there are open orders protecting these positions
        open_trades = self.ib.ib.openTrades()
        has_stop = False
        has_tp = False
        for t in open_trades:
            if t.contract.symbol == config.SYMBOL:
                if t.order.orderType == "STP":
                    has_stop = True
                elif t.order.orderType == "LMT" and t.order.action in ("BUY", "SELL"):
                    has_tp = True

        for pos in positions:
            size = pos["size"]
            # IB avgCost for futures = price * multiplier (e.g. 52160 = 5216.0 * 10)
            avg_cost_raw = pos.get("avg_cost", 0)
            avg_cost = avg_cost_raw / config.POINT_VALUE if avg_cost_raw > 10000 else avg_cost_raw
            logger.info(f"Existing position: {size} contracts @ avg {avg_cost:.2f}")

            if has_stop and has_tp:
                logger.info("Position has both stop and TP orders — OK")
                continue

            if not has_stop or not has_tp:
                logger.warning(f"Position MISSING protection (stop={has_stop}, tp={has_tp}) — placing emergency orders")
                # Use ATR from the last strategy that has it warmed up
                atr_val = None
                for strat in self.strategies:
                    if hasattr(strat, 'atr') and strat.atr.ready:
                        atr_val = strat.atr.value
                        break

                if atr_val is None:
                    atr_val = 10.0  # fallback ~$100 risk per contract
                    logger.warning(f"No ATR available, using fallback {atr_val}")

                if size > 0:  # Long position
                    stop_price = avg_cost - atr_val * 1.5
                    tp_price = avg_cost + atr_val * 2.0
                    cover_action = "SELL"
                else:  # Short position
                    stop_price = avg_cost + atr_val * 1.5
                    tp_price = avg_cost - atr_val * 2.0
                    cover_action = "BUY"

                qty = abs(size)
                if not has_stop:
                    self.ib.place_stop_order(cover_action, qty, stop_price)
                    logger.info(f"Emergency STOP placed: {cover_action} {qty} @ {stop_price:.2f}")
                if not has_tp:
                    self.ib.place_limit_order(cover_action, qty, tp_price)
                    logger.info(f"Emergency TP placed: {cover_action} {qty} @ {tp_price:.2f}")

    def _run_loop(self):
        """Main trading loop — polls historical bars instead of real-time subscription."""
        logger.info("Entering main trading loop...")

        # Poll historical bars every 30s (real-time bars require L1 market data sub)
        # TODO: switch to self.ib.subscribe_bars() once COMEX real-time is confirmed working
        use_realtime = False
        logger.info("Polling mode: fetching 5-min bars every 30 seconds")

        _last_bar_time = None

        consecutive_errors = 0
        MAX_CONSECUTIVE_ERRORS = 5  # reconnect after this many back-to-back errors

        try:
            while self.running:
                try:
                    now_et = datetime.now(ET)

                    # Reset at new day
                    today = now_et.date()
                    if self._last_date is None or self._last_date != today:
                        self._last_date = today
                        self.risk.reset_daily()
                        self.trade_log.clear()
                        self._flattening = False
                        self._cooldown_until_bar = 0
                        self._bar_count = 0
                        self._daily_bias = None
                        self._5m_buffer = []
                        self._15m_bars = []
                        self._pending_mtf_signal = None
                        self._daily_realized_pnl = 0.0
                        self._loss_breaker_active = False
                        for strat in self.strategies:
                            if hasattr(strat, 'on_new_day'):
                                strat.on_new_day()
                        logger.info(f"New trading day: {today}")

                    # Flatten at COMEX close — daytrading only, no overnight holds
                    flatten_time = dtime.fromisoformat(config.FLATTEN_BY_ET)
                    past_flatten = now_et.time() >= flatten_time

                    # Reset flattening flag at start of next trading day (before COMEX open)
                    trading_start = dtime.fromisoformat(config.TRADING_START_ET)
                    if not past_flatten and self._flattening and now_et.time() < trading_start:
                        self._flattening = False
                        self._daily_bias = None
                        self._cooldown_until_bar = 0
                        self._bar_count = 0
                        self._5m_buffer = []
                        self._15m_bars = []
                        self._pending_mtf_signal = None
                        self.trade_log.clear()
                        for strat in self.strategies:
                            if hasattr(strat, 'on_new_day'):
                                strat.on_new_day()
                        logger.info("Pre-market reset — new trading day")

                    if past_flatten:
                        if not self._flattening:
                            self._flattening = True
                            logger.info("COMEX close — flattening all positions (daytrading only)")
                            self.ib.cancel_all_orders()
                            self.ib.ib.sleep(2)  # wait for cancels to process

                            # Get last price before flatten for P&L calc
                            positions = self.ib.get_positions()

                            self.ib.flatten_position()
                            self.ib.ib.sleep(3)  # wait for flatten fills

                            # Get actual fill price from the flatten order, fallback to bar close
                            flatten_price = None
                            try:
                                open_trades = self.ib.ib.openTrades()
                                # Check recent fills for our flatten order
                                for t in self.ib.ib.fills():
                                    if (t.contract.symbol == config.SYMBOL and
                                        t.execution.time and
                                        (datetime.now(ET) - t.execution.time.astimezone(ET)).total_seconds() < 30):
                                        flatten_price = t.execution.price
                                        logger.info(f"EOD flatten fill price: {flatten_price}")
                                        break
                            except Exception as e:
                                logger.debug(f"Could not get fill price: {e}")

                            if not flatten_price:
                                # Fallback: try historical bars
                                bars = self.ib.get_historical_bars(duration="300 S", bar_size="5 mins")
                                flatten_price = bars[-1].close if bars else None

                            # Record exit events for all open trades in dashboard
                            if flatten_price:
                                self._record_eod_exits(flatten_price)
                            else:
                                logger.warning("Could not determine flatten price — exits not recorded")

                            logger.info("EOD flatten complete — no new entries until next session")

                    # Watchdog: verify stop protection on open positions
                    if not self._flattening:
                        self._verify_stop_protection()

                    # Update position count for risk manager
                    positions = self.ib.get_positions()
                    total_pos = sum(abs(p["size"]) for p in positions)
                    self.risk.update_positions(total_pos)

                    # If polling mode, fetch latest bars and evaluate
                    if not use_realtime:
                        bars = self.ib.get_historical_bars(duration="900 S", bar_size="5 mins")
                        if bars and len(bars) > 0:
                            latest = bars[-1]
                            bar_time = str(latest.date)
                            if bar_time != _last_bar_time:
                                _last_bar_time = bar_time
                                vol = latest.volume if hasattr(latest, "volume") else 0
                                logger.debug(f"Bar: {bar_time} O={latest.open} H={latest.high} L={latest.low} C={latest.close} V={vol}")
                                self._process_bar(now_et, latest.open, latest.high,
                                                  latest.low, latest.close, vol)
                        elif not bars:
                            logger.warning("No bars returned from IB")

                    # Wait before next cycle
                    self.ib.ib.sleep(30 if not use_realtime else 5)
                    consecutive_errors = 0  # reset on success

                except (ConnectionError, OSError, TimeoutError) as e:
                    # Connection lost — attempt reconnect
                    logger.warning(f"Connection error: {e} — attempting reconnect...")
                    self.ib.connected = False
                    if self.ib.reconnect():
                        logger.info("Reconnected — re-checking positions then re-warming")
                        # CRITICAL: check orphaned positions FIRST (re-place protection
                        # before cancelling stale orders) to minimize naked exposure
                        self._check_orphaned_positions()
                        self._warmup()
                        consecutive_errors = 0
                    else:
                        logger.error("Reconnect failed — shutting down")
                        break

                except Exception as e:
                    consecutive_errors += 1
                    logger.warning(f"Loop error ({consecutive_errors}/{MAX_CONSECUTIVE_ERRORS}): {e}")
                    if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                        logger.warning("Too many consecutive errors — forcing reconnect")
                        if self.ib.reconnect():
                            self._check_orphaned_positions()
                            self._warmup()
                            consecutive_errors = 0
                        else:
                            logger.error("Reconnect failed — shutting down")
                            break
                    else:
                        import time
                        time.sleep(10)

        except KeyboardInterrupt:
            logger.info("Shutdown requested")
        finally:
            self._shutdown()

    def _on_realtime_bar(self, bars, hasNewBar):
        """Callback for real-time bars from IB."""
        if not hasNewBar:
            return
        bar = bars[-1]
        now_et = datetime.now(ET)
        vol = bar.volume if hasattr(bar, "volume") else 0
        self._process_bar(now_et, bar.open, bar.high, bar.low, bar.close, vol)

    def _process_bar(self, now_et, open_p, high, low, close, volume):
        """Process a 5-min bar (from real-time or polling).
        
        Multi-TF mode:
        - Every 5-min bar is buffered for 15-min aggregation
        - When 3 bars complete a 15-min bar, strategies evaluate on 15-min data
        - Signals fire on the NEXT 5-min bar for precise entry timing
        """
        self._bar_count += 1

        # Refresh volume profile every 48 bars (~4 hours)
        self._bars_since_vp_refresh += 1
        if self._bars_since_vp_refresh >= 48 and self._volume_filter:
            self._volume_filter.refresh()
            self._bars_since_vp_refresh = 0

        # Refresh 4H bias every 48 bars (~4 hours of 5-min bars)
        self._bars_since_bias_refresh += 1
        if self._bars_since_bias_refresh >= 48:
            try:
                bars_4h = self.ib.get_historical_bars(duration="5 D", bar_size="4 hours")
                if bars_4h:
                    for bar in bars_4h[-3:]:  # just update with recent bars
                        self._htf_bias.update(bar.high, bar.low, bar.close)
                    logger.info(f"4H Bias refreshed → direction={self._htf_bias.direction}, "
                                f"level={self._htf_bias.breakout_level}")
            except Exception as e:
                logger.warning(f"4H bias refresh failed: {e}")
            self._bars_since_bias_refresh = 0

        # ── Detect position changes (stop/TP fills) ────────────────────────
        try:
            current_positions = self.ib.get_positions()
            current_size = sum(p["size"] for p in current_positions) if current_positions else 0
            if self._last_position_size != 0 and current_size == 0 and not self._flattening:
                # Position went from open → flat = stop or TP hit
                logger.info(f"Position closed (stop/TP fill detected): was {self._last_position_size}, now flat")
                # Record exit for all active trades and track realized P&L
                for entry in self._active_trades:
                    entry_price = entry.get('entry_price', 0)
                    contracts = entry.get('contracts', 1)
                    action = entry.get('action', 'BUY')
                    # Estimate P&L from entry vs current close
                    if action == "BUY":
                        trade_pnl = (close - entry_price) * contracts * config.POINT_VALUE
                    else:
                        trade_pnl = (entry_price - close) * contracts * config.POINT_VALUE
                    self._daily_realized_pnl += trade_pnl
                    logger.info(f"Trade P&L: ~${trade_pnl:.2f} | Daily realized: ${self._daily_realized_pnl:.2f}")

                    self.data.record_trade_exit(
                        trade_id=entry.get('trade_id', 'unknown'),
                        strategy=entry.get('strategy', 'Unknown'),
                        action=action,
                        entry_price=entry_price,
                        exit_price=close,  # approximate with current bar close
                        contracts=contracts,
                        exit_reason='stop_or_tp',
                    )
                    logger.info(f"Recorded exit: {entry.get('trade_id')} @ ~{close}")
                self._active_trades.clear()

                # Check daily loss breaker
                if self._daily_realized_pnl <= -self._daily_loss_limit:
                    self._loss_breaker_active = True
                    logger.warning(f"🛑 DAILY LOSS BREAKER: realized P&L ${self._daily_realized_pnl:.2f} "
                                   f"exceeds -${self._daily_loss_limit}. No new entries today.")
                # Activate cooldown after stop-out
                self._cooldown_until_bar = self._bar_count + getattr(config, 'COOLDOWN_BARS', 10)
            elif abs(current_size) < abs(self._last_position_size) and current_size != 0 and not self._flattening:
                # Partial fill (e.g., partial TP at 1R)
                logger.info(f"Partial exit detected: was {self._last_position_size}, now {current_size}")
            self._last_position_size = current_size
        except Exception as e:
            logger.debug(f"Position tracking error: {e}")

        # Record every bar
        self.data.record_bar(now_et.isoformat(), open_p, high, low, close, volume)

        # Write account snapshot every 2 bars (~60s) for dashboard
        self._context_counter += 1
        if self._context_counter % 2 == 0:
            self._write_account_snapshot(close)

        # Periodic context snapshot
        if self._context_counter % 60 == 0:
            self.data.record_context({
                "hour_et": now_et.hour,
                "minute_et": now_et.minute,
                "day_of_week": now_et.strftime("%A"),
                "price": float(close),
                "positions": len(self.ib.get_positions()),
                "daily_pnl": self.risk.daily_pnl,
                "trades_today": len(self.trade_log),
            })

        # Check if we're in trading hours
        # Full day: 18:00 - 13:15 ET (crosses midnight)
        start = dtime.fromisoformat(config.TRADING_START_ET)
        end = dtime.fromisoformat(config.TRADING_END_ET)
        now_time = now_et.time()
        if start > end:  # crosses midnight (e.g. 18:00 - 13:15)
            in_window = now_time >= start or now_time <= end
        else:
            in_window = start <= now_time <= end
        if not in_window:
            return

        # Activate ORB strategy at COMEX open (8:20 ET)
        comex_open = dtime.fromisoformat(config.COMEX_OPEN_ET)
        if now_time >= comex_open:
            for strat in self.strategies:
                if hasattr(strat, 'on_session_open') and hasattr(strat, 'active') and not strat.active:
                    strat.on_session_open(now_et)
                    logger.info(f"Activated {strat.NAME} at COMEX open")

        # No new entries during EOD flatten
        if self._flattening:
            return

        # ── Multi-Timeframe Bar Aggregation ──────────────────────────────
        new_15m_bar = None
        if self._mtf_enabled:
            self._5m_buffer.append({
                "dt": now_et, "open": open_p, "high": high,
                "low": low, "close": close, "volume": volume,
            })
            if len(self._5m_buffer) >= 3:
                buf = self._5m_buffer
                new_15m_bar = {
                    "dt": buf[0]["dt"],
                    "open": buf[0]["open"],
                    "high": max(b["high"] for b in buf),
                    "low": min(b["low"] for b in buf),
                    "close": buf[-1]["close"],
                    "volume": sum(b["volume"] for b in buf),
                }
                self._15m_bars.append(new_15m_bar)
                self._5m_buffer = []
                logger.debug(f"15m bar complete: {new_15m_bar['dt']} "
                             f"O={new_15m_bar['open']} H={new_15m_bar['high']} "
                             f"L={new_15m_bar['low']} C={new_15m_bar['close']}")

        # ── Execute pending MTF signal on this 5-min bar ─────────────────
        if self._mtf_enabled and self._pending_mtf_signal:
            signal = self._pending_mtf_signal
            self._pending_mtf_signal = None
            # Update entry price to current 5-min close for precise timing
            signal.price = close
            if signal.action == "BUY":
                signal.stop = close - signal.risk_points  # preserve risk distance
                signal.target = close + signal.reward_points  # preserve reward distance
            else:
                signal.stop = close + signal.risk_points
                signal.target = close - signal.reward_points
            logger.info(f"📊 Executing MTF signal on 5-min bar: {signal}")
            self._handle_signal(signal)
            return  # don't double-evaluate

        # ── Evaluate Strategies ──────────────────────────────────────────
        for strat in self.strategies:
            try:
                strat_tf = strat.params.get("timeframe", "5m") if hasattr(strat, 'params') else "5m"
                
                if self._mtf_enabled and strat_tf == "mtf":
                    # MTF strategies: only evaluate when a new 15-min bar completes
                    if new_15m_bar is None:
                        continue
                    signal = strat.evaluate(
                        new_15m_bar["dt"], new_15m_bar["open"], new_15m_bar["high"],
                        new_15m_bar["low"], new_15m_bar["close"], new_15m_bar["volume"],
                    )
                    if signal:
                        # Queue signal for execution on next 5-min bar
                        logger.info(f"📊 15-min signal from {strat.NAME}: {signal} — queued for 5-min entry")
                        self._pending_mtf_signal = signal
                else:
                    # Non-MTF strategies: evaluate on every 5-min bar as before
                    signal = strat.evaluate(
                        now_et, open_p, high, low, close, volume,
                    )
                    if signal:
                        logger.info(f"📊 Signal from {strat.NAME}: {signal}")
                        self._handle_signal(signal)
                
                if not signal:
                    # Debug: log why no signal (every 10th bar to reduce noise)
                    if self._context_counter % 10 == 0:
                        trades_today = getattr(strat, 'trades_today', '?')
                        active = getattr(strat, 'active', '?')
                        ready = True
                        if hasattr(strat, 'atr'):
                            ready = strat.atr.ready
                        logger.debug(f"No signal from {strat.NAME}: trades_today={trades_today}, active={active}, atr_ready={ready}")
            except Exception as e:
                logger.error(f"Strategy {strat.NAME} error: {e}", exc_info=True)

    def _write_account_snapshot(self, last_price):
        """Write account summary to JSON for dashboard consumption."""
        try:
            summary = self.ib.get_account_summary()
            positions = self.ib.get_positions()
            open_orders = self.ib.get_open_orders()
            snapshot = {
                "ts": datetime.now().isoformat(),
                "net_liquidation": summary.get("NetLiquidation", 0),
                "total_cash": summary.get("TotalCashValue", 0),
                "unrealized_pnl": summary.get("UnrealizedPnL", 0),
                "realized_pnl": summary.get("RealizedPnL", 0),
                "buying_power": summary.get("BuyingPower", 0),
                "last_price": float(last_price),
                "position_count": sum(abs(p["size"]) for p in positions),
                "open_order_count": len(open_orders),
                "positions": positions,
                "open_orders": open_orders,
            }
            acct_file = Path(__file__).parent / "data" / "account.json"
            acct_file.parent.mkdir(parents=True, exist_ok=True)
            with open(acct_file, "w") as f:
                json.dump(snapshot, f, indent=2, default=str)
        except Exception as e:
            logger.debug(f"Account snapshot write error: {e}")

    def _verify_stop_protection(self):
        """Watchdog: verify stop order is active when we have a position.
        Called every loop cycle (~30s). If no active stop found, emergency flatten."""
        try:
            positions = self.ib.get_positions()
            if not positions:
                return  # no position, nothing to protect

            has_position = any(abs(p["size"]) > 0 for p in positions)
            if not has_position:
                return

            # Check open orders for an active stop
            open_orders = self.ib.get_open_orders()
            has_active_stop = False
            for o in open_orders:
                if o["type"] == "STP" and o["status"] in ("Submitted", "PreSubmitted"):
                    has_active_stop = True
                    break

            if not has_active_stop:
                self._watchdog_checks += 1
                if self._watchdog_checks >= 3:
                    # 3 consecutive checks (~90s) with no stop — flatten
                    logger.error("🚨 WATCHDOG: No active stop order for 3 checks — emergency flatten!")
                    self._flattening = True
                    self.ib.cancel_all_orders()
                    self.ib.ib.sleep(2)

                    # Get price for exit record
                    bars = self.ib.get_historical_bars(duration="300 S", bar_size="5 mins")
                    flatten_price = bars[-1].close if bars else None

                    self.ib.flatten_position()
                    self.ib.ib.sleep(3)
                    if flatten_price:
                        self._record_eod_exits(flatten_price)
                    logger.error("🚨 WATCHDOG: Emergency flatten complete — position was unprotected")
                    self._watchdog_checks = 0
                else:
                    logger.warning(f"⚠️ WATCHDOG: No active stop detected (check {self._watchdog_checks}/3)")
            else:
                self._watchdog_checks = 0  # reset on success
        except Exception as e:
            logger.error(f"Watchdog error: {e}", exc_info=True)

    def _handle_signal(self, signal: Signal):
        """Process a trade signal — check risk, place order."""
        logger.info(f"📊 Signal: {signal}")

        # Block entries during EOD flatten
        if self._flattening:
            logger.info("Signal blocked: EOD flattening in progress")
            return

        # Daily loss breaker — no new entries if daily realized loss exceeded
        if self._loss_breaker_active:
            logger.info(f"Signal blocked: daily loss breaker active "
                        f"(realized P&L: ${self._daily_realized_pnl:.2f})")
            return

        # Cooldown after stop-out (10 bars = ~50 min on 5-min bars)
        if self._bar_count < self._cooldown_until_bar:
            bars_left = self._cooldown_until_bar - self._bar_count
            logger.info(f"Signal blocked: cooldown active ({bars_left} bars remaining)")
            return

        # 4H Breakout Momentum bias filter — only trade in direction of 4H trend
        # BUY only when 4H bias = BUY, SELL (short) only when 4H bias = SELL
        # Proximity override: allows any direction if price >2% from bias level
        if not self._htf_bias.allows(signal.action, current_price=signal.price):
            bias_dir = self._htf_bias.direction or "NEUTRAL"
            logger.info(f"Signal blocked: {signal.action} against 4H bias "
                        f"({bias_dir}, level={self._htf_bias.breakout_level})")
            self.data.record_signal(
                signal.strategy, signal.action, signal.price,
                signal.stop, signal.target, signal.reason,
                taken=False, skip_reason=f"4h_bias_{bias_dir}",
            )
            return

        # Volume Profile filter — block signals heading into HVN walls
        if self._volume_filter and self._volume_filter.ready:
            vp_result = self._volume_filter.assess_signal(signal.action, signal.price)
            vp_quality = vp_result["quality"]
            vp_reason = vp_result["reason"]
            logger.info(f"Volume Profile: quality={vp_quality}, in_gap={vp_result['in_volume_gap']}, "
                       f"va_pos={vp_result['position_vs_va']}, reason={vp_reason}")
            if vp_result.get("nearest_obstacle"):
                obs = vp_result["nearest_obstacle"]
                logger.info(f"  Nearest obstacle: {obs['type']} at {obs['price_low']:.1f}-{obs['price_high']:.1f} "
                           f"({obs['dist']:.1f} pts)")
            if vp_result.get("nearest_runway"):
                run = vp_result["nearest_runway"]
                logger.info(f"  Nearest runway: {run['type']} at {run['price_low']:.1f}-{run['price_high']:.1f} "
                           f"({run['dist']:.1f} pts, {run['width']:.1f} wide)")
            
            if not vp_result["allowed"]:
                logger.info(f"Signal BLOCKED by volume profile: {vp_reason}")
                self.data.record_signal(
                    signal.strategy, signal.action, signal.price,
                    signal.stop, signal.target, signal.reason,
                    taken=False, skip_reason=f"volume_profile_{vp_quality}: {vp_reason}",
                )
                return

        # Risk check
        can_trade, reason = self.risk.can_trade(signal.strategy)
        if not can_trade:
            logger.info(f"Signal blocked: {reason}")
            self.data.record_signal(
                signal.strategy, signal.action, signal.price,
                signal.stop, signal.target, signal.reason,
                taken=False, skip_reason=reason,
            )
            return

        # Position sizing
        contracts = self.risk.calculate_position_size(signal.risk_points)
        if contracts <= 0:
            logger.info("Signal blocked: position size = 0")
            self.data.record_signal(
                signal.strategy, signal.action, signal.price,
                signal.stop, signal.target, signal.reason,
                taken=False, skip_reason="position_size_zero",
            )
            return

        # Record the signal as taken
        self.data.record_signal(
            signal.strategy, signal.action, signal.price,
            signal.stop, signal.target, signal.reason,
            taken=True,
        )

        # Generate trade ID
        trade_id = f"{signal.strategy}_{datetime.now().strftime('%H%M%S')}_{self.data.get_trade_count()}"

        # Record trade entry
        self.data.record_trade_entry(
            trade_id, signal.strategy, signal.action,
            contracts, signal.price, signal.stop, signal.target,
        )

        # Track active trade for exit detection
        self._active_trades.append({
            'trade_id': trade_id,
            'strategy': signal.strategy,
            'action': signal.action,
            'entry_price': signal.price,
            'contracts': contracts,
            'stop': signal.stop,
            'target': signal.target,
        })

        logger.info(f"🚀 Executing: {signal.action} {contracts}x MGC @ {signal.price:.2f} "
                     f"(stop={signal.stop:.2f}, tp={signal.target:.2f})")

        try:
            # Partial profit-taking at 1R: close half at 1R, let rest ride to full TP
            if getattr(signal, 'partial_tp_at_1r', False) and contracts >= 2:
                half = contracts // 2
                remainder = contracts - half
                # 1R target = entry +/- risk
                risk = signal.risk_points
                if signal.action == "BUY":
                    tp_1r = signal.price + risk
                else:
                    tp_1r = signal.price - risk
                logger.info(f"📊 Partial TP: {half} contracts at 1R ({tp_1r:.2f}), "
                            f"{remainder} contracts at full TP ({signal.target:.2f})")
                # First half: TP at 1R, same stop
                self.ib.place_bracket_order(
                    action=signal.action,
                    quantity=half,
                    entry_price=signal.price,
                    stop_price=signal.stop,
                    tp_price=tp_1r,
                )
                # Second half: TP at full target, same stop (trail stop will manage)
                self.ib.place_bracket_order(
                    action=signal.action,
                    quantity=remainder,
                    entry_price=signal.price,
                    stop_price=signal.stop,
                    tp_price=signal.target,
                )
            else:
                self.ib.place_bracket_order(
                    action=signal.action,
                    quantity=contracts,
                    entry_price=signal.price,
                    stop_price=signal.stop,
                    tp_price=signal.target,
                )

            # Set cooldown: no new entries for 10 bars after any entry
            self._cooldown_until_bar = self._bar_count + 10
            logger.info(f"Entry cooldown set: no new trades until bar {self._cooldown_until_bar}")

            # Log the trade
            trade_entry = {
                "timestamp": datetime.now().isoformat(),
                "trade_id": trade_id,
                "strategy": signal.strategy,
                "action": signal.action,
                "contracts": contracts,
                "entry": signal.price,
                "stop": signal.stop,
                "target": signal.target,
                "reason": signal.reason,
                "rr_ratio": signal.rr_ratio,
            }
            self.trade_log.append(trade_entry)

            if config.LOG_TRADES:
                self._save_trade_log(trade_entry)

        except Exception as e:
            logger.error(f"Order placement failed: {e}", exc_info=True)

    def _save_trade_log(self, entry):
        """Append trade to daily log file."""
        log_path = os.path.join(config.LOG_DIR, f"trades_{datetime.now().strftime('%Y%m%d')}.jsonl")
        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def _record_eod_exits(self, flatten_price):
        """Record exit events for all open trades when EOD flatten fires."""
        try:
            # Read today's trade entries from data collector
            from pathlib import Path
            data_dir = Path(__file__).parent / "data"
            ds = datetime.now().strftime('%Y%m%d')
            trades_file = data_dir / f"trades_{ds}.jsonl"
            if not trades_file.exists():
                return

            entries = []
            exited_ids = set()
            with open(trades_file) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    rec = json.loads(line)
                    if rec.get('event') == 'entry':
                        entries.append(rec)
                    elif rec.get('event') == 'exit':
                        exited_ids.add(rec.get('trade_id'))

            # Write exit records for any trade without an exit
            for e in entries:
                if e['trade_id'] in exited_ids:
                    continue
                self.data.record_trade_exit(
                    trade_id=e['trade_id'],
                    strategy=e.get('strategy', 'Unknown'),
                    action=e['action'],
                    entry_price=e['entry_price'],
                    exit_price=flatten_price,
                    contracts=e.get('contracts', 1),
                    exit_reason='eod_flatten',
                )
                logger.info(f"Recorded EOD exit: {e['trade_id']} @ {flatten_price}")
        except Exception as ex:
            logger.error(f"Error recording EOD exits: {ex}", exc_info=True)

    def _shutdown(self):
        """Graceful shutdown — preserve protective orders on existing positions."""
        logger.info("Shutting down...")
        try:
            # DON'T cancel all orders or flatten on shutdown — positions may need
            # their stop/TP orders to stay active while the bot is restarting.
            # Only cancel non-protective orders if needed.
            positions = self.ib.get_positions()
            if not positions:
                # No positions — safe to cancel any stale orders
                self.ib.cancel_all_orders()
                logger.info("No positions — cancelled stale orders")
            else:
                logger.info(f"Positions open ({len(positions)}) — preserving protective orders")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        finally:
            try:
                wins = sum(1 for t in self.trade_log if t.get("pnl", 0) > 0)
                self.data.record_daily_summary(
                    trades_taken=len(self.trade_log),
                    trades_won=wins,
                    total_pnl=self.risk.daily_pnl,
                    max_drawdown=self.risk.max_drawdown,
                )
            except Exception:
                pass
            self.data.close()
            self.ib.disconnect()
            logger.info("MGC Day Trader stopped")

    def get_status(self):
        """Return current trader status."""
        return {
            "running": self.running,
            "risk": self.risk.get_status(),
            "strategies": [s.NAME for s in self.strategies],
            "trades_today": len(self.trade_log),
            "connected": self.ib.connected,
        }


def main():
    trader = MGCTrader()
    trader.start()


if __name__ == "__main__":
    main()
