"""
MGC Day Trader — Data Collection Layer
========================================
Logs everything needed for future optimization and learning:
- Every bar of market data
- Every signal generated (taken or skipped)
- Every trade with full lifecycle (entry, fills, exit, P&L)
- Market context at signal time (indicators, regime, session)
- Daily summaries

Data stored as JSONL files in data/ directory, one file per type per day.
Easy to load into pandas for analysis.
"""

import json
import os
import logging
from datetime import datetime, date
from pathlib import Path

import config

logger = logging.getLogger("mgc-trader.data")

DATA_DIR = Path(config.LOG_DIR).parent / "data"


class DataCollector:
    """Collects and persists all trading data for future analysis."""

    def __init__(self):
        self.data_dir = DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._today = None
        self._files = {}
        self._bar_count = 0
        self._signal_count = 0
        self._trade_count = 0
        self._daily_bars = []  # In-memory buffer for regime calc
        self._rotate_files()
        logger.info(f"Data collector initialized — writing to {self.data_dir}")

    def _rotate_files(self):
        """Open new files for a new day."""
        today = date.today()
        if self._today == today:
            return
        self._today = today
        self._bar_count = 0
        self._signal_count = 0
        self._trade_count = 0
        self._daily_bars = []
        ds = today.strftime("%Y%m%d")

        # Close old file handles
        for f in self._files.values():
            try:
                f.close()
            except Exception:
                pass

        self._files = {
            "bars": open(self.data_dir / f"bars_{ds}.jsonl", "a"),
            "signals": open(self.data_dir / f"signals_{ds}.jsonl", "a"),
            "trades": open(self.data_dir / f"trades_{ds}.jsonl", "a"),
            "context": open(self.data_dir / f"context_{ds}.jsonl", "a"),
            "summary": open(self.data_dir / f"summary_{ds}.jsonl", "a"),
        }

    def _write(self, stream: str, data: dict):
        """Write a JSON line to the specified stream."""
        self._rotate_files()
        try:
            self._files[stream].write(json.dumps(data, default=str) + "\n")
            self._files[stream].flush()
        except Exception as e:
            logger.error(f"Data write error ({stream}): {e}")

    # ── Bar Data ─────────────────────────────────────────────────────────

    def record_bar(self, timestamp, open_p, high, low, close, volume,
                   indicators: dict = None):
        """Record every market data bar with indicator values."""
        self._bar_count += 1
        bar = {
            "ts": timestamp,
            "o": round(float(open_p), 2),
            "h": round(float(high), 2),
            "l": round(float(low), 2),
            "c": round(float(close), 2),
            "v": int(volume) if volume else 0,
            "bar_num": self._bar_count,
        }
        if indicators:
            bar["ind"] = {k: round(float(v), 4) if isinstance(v, (int, float)) else v
                          for k, v in indicators.items() if v is not None}
        self._write("bars", bar)
        self._daily_bars.append(bar)

    # ── Signal Data ──────────────────────────────────────────────────────

    def record_signal(self, strategy: str, action: str, price: float,
                      stop: float, target: float, reason: str,
                      taken: bool, skip_reason: str = None,
                      context: dict = None):
        """Record every signal — whether taken or skipped, and why."""
        self._signal_count += 1
        sig = {
            "ts": datetime.now().isoformat(),
            "strategy": strategy,
            "action": action,
            "price": round(float(price), 2),
            "stop": round(float(stop), 2),
            "target": round(float(target), 2),
            "risk_pts": round(abs(price - stop), 2),
            "reward_pts": round(abs(target - price), 2),
            "rr_ratio": round(abs(target - price) / max(abs(price - stop), 0.01), 2),
            "reason": reason,
            "taken": taken,
            "skip_reason": skip_reason,
            "signal_num": self._signal_count,
        }
        if context:
            sig["ctx"] = context
        self._write("signals", sig)
        return sig

    # ── Trade Lifecycle ──────────────────────────────────────────────────

    def record_trade_entry(self, trade_id: str, strategy: str, action: str,
                           contracts: int, entry_price: float,
                           stop_price: float, tp_price: float,
                           signal_context: dict = None):
        """Record a trade entry."""
        self._trade_count += 1
        entry = {
            "event": "entry",
            "ts": datetime.now().isoformat(),
            "trade_id": trade_id,
            "strategy": strategy,
            "action": action,
            "contracts": contracts,
            "entry_price": round(float(entry_price), 2),
            "stop_price": round(float(stop_price), 2),
            "tp_price": round(float(tp_price), 2),
            "risk_per_contract": round(abs(entry_price - stop_price) * config.POINT_VALUE, 2),
            "total_risk": round(abs(entry_price - stop_price) * config.POINT_VALUE * contracts, 2),
            "trade_num": self._trade_count,
        }
        if signal_context:
            entry["signal_ctx"] = signal_context
        self._write("trades", entry)
        return trade_id

    def record_trade_fill(self, trade_id: str, fill_price: float,
                          fill_qty: int, order_type: str):
        """Record an order fill (entry, stop, or TP)."""
        fill = {
            "event": "fill",
            "ts": datetime.now().isoformat(),
            "trade_id": trade_id,
            "fill_price": round(float(fill_price), 2),
            "fill_qty": fill_qty,
            "order_type": order_type,
        }
        self._write("trades", fill)

    def record_trade_exit(self, trade_id: str, strategy: str, action: str,
                          entry_price: float, exit_price: float,
                          contracts: int, exit_reason: str,
                          duration_seconds: int = None):
        """Record a trade exit with P&L calculation."""
        if action == "BUY":
            pnl_per_contract = (exit_price - entry_price) * config.POINT_VALUE
        else:
            pnl_per_contract = (entry_price - exit_price) * config.POINT_VALUE

        total_pnl = pnl_per_contract * contracts

        exit_rec = {
            "event": "exit",
            "ts": datetime.now().isoformat(),
            "trade_id": trade_id,
            "strategy": strategy,
            "action": action,
            "entry_price": round(float(entry_price), 2),
            "exit_price": round(float(exit_price), 2),
            "contracts": contracts,
            "pnl_per_contract": round(pnl_per_contract, 2),
            "total_pnl": round(total_pnl, 2),
            "exit_reason": exit_reason,  # "stop", "tp", "flatten", "manual"
            "duration_s": duration_seconds,
            "won": total_pnl > 0,
        }
        self._write("trades", exit_rec)
        return total_pnl

    # ── Market Context Snapshots ─────────────────────────────────────────

    def record_context(self, snapshot: dict):
        """
        Record a periodic market context snapshot.
        Call every ~5 min or at signal time.

        snapshot should include things like:
        - atr, atr_percentile
        - ema_fast, ema_slow, ema_trend
        - vwap, vwap_std
        - rsi
        - spread (bid-ask)
        - volume_rate (bars per hour vs average)
        - session (asia/london/ny/comex)
        - regime (trending/ranging/volatile)
        - day_of_week, hour_et
        - prior_day_high, prior_day_low
        """
        snapshot["ts"] = datetime.now().isoformat()
        self._write("context", snapshot)

    # ── Daily Summary ────────────────────────────────────────────────────

    def record_daily_summary(self, trades_taken: int, trades_won: int,
                             total_pnl: float, max_drawdown: float,
                             strategies_breakdown: dict = None,
                             notes: str = None):
        """Record end-of-day summary."""
        summary = {
            "ts": datetime.now().isoformat(),
            "date": date.today().isoformat(),
            "bars_recorded": self._bar_count,
            "signals_generated": self._signal_count,
            "trades_taken": trades_taken,
            "trades_won": trades_won,
            "win_rate": round(trades_won / max(trades_taken, 1) * 100, 1),
            "total_pnl": round(total_pnl, 2),
            "max_drawdown": round(max_drawdown, 2),
        }
        if strategies_breakdown:
            summary["by_strategy"] = strategies_breakdown
        if notes:
            summary["notes"] = notes
        self._write("summary", summary)
        logger.info(f"Daily summary: {trades_taken} trades, {trades_won} wins, "
                     f"PnL=${total_pnl:.2f}, DD=${max_drawdown:.2f}")

    # ── Helpers ──────────────────────────────────────────────────────────

    def get_bar_count(self):
        return self._bar_count

    def get_signal_count(self):
        return self._signal_count

    def get_trade_count(self):
        return self._trade_count

    def close(self):
        """Flush and close all files."""
        for f in self._files.values():
            try:
                f.flush()
                f.close()
            except Exception:
                pass
        logger.info("Data collector closed")
