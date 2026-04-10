"""
MGC Day Trader — Risk Manager
Enforces daily loss limits, position sizing, and trade limits.
"""

import logging
from datetime import datetime, date
import config

logger = logging.getLogger("mgc-trader.risk")


class RiskManager:
    """Enforces all risk rules before allowing trades."""

    def __init__(self):
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.current_date = date.today()
        self.open_positions = 0
        self.halted = False
        self.halt_reason = ""

    def reset_daily(self):
        """Reset daily counters. Call at start of each trading day."""
        today = date.today()
        if today != self.current_date:
            logger.info(f"New trading day: {today}. Resetting daily counters. "
                        f"Yesterday P&L: ${self.daily_pnl:.2f}, Trades: {self.daily_trades}")
            self.daily_pnl = 0.0
            self.daily_trades = 0
            self.current_date = today
            self.halted = False
            self.halt_reason = ""

    def record_trade(self, pnl):
        """Record a completed trade."""
        self.daily_pnl += pnl
        self.daily_trades += 1
        logger.info(f"Trade recorded: PnL ${pnl:.2f} | Daily PnL: ${self.daily_pnl:.2f} | "
                     f"Trades today: {self.daily_trades}")

        # Check daily loss limit
        if self.daily_pnl <= -config.MAX_DAILY_LOSS:
            self.halted = True
            self.halt_reason = f"Daily loss limit hit: ${self.daily_pnl:.2f}"
            logger.warning(f"🛑 TRADING HALTED: {self.halt_reason}")

    def can_trade(self, strategy_name=""):
        """Check if a new trade is allowed."""
        self.reset_daily()

        if self.halted:
            logger.debug(f"Trade blocked ({strategy_name}): {self.halt_reason}")
            return False, self.halt_reason

        if self.daily_trades >= config.MAX_DAILY_TRADES:
            reason = f"Max daily trades reached ({config.MAX_DAILY_TRADES})"
            logger.debug(f"Trade blocked ({strategy_name}): {reason}")
            return False, reason

        if self.open_positions >= config.MAX_POSITION_SIZE:
            reason = f"Max position size reached ({config.MAX_POSITION_SIZE})"
            logger.debug(f"Trade blocked ({strategy_name}): {reason}")
            return False, reason

        return True, "OK"

    def calculate_position_size(self, stop_distance_points):
        """
        Calculate position size based on max risk per trade.
        stop_distance_points: distance from entry to stop in price points
        """
        if stop_distance_points <= 0:
            return 0

        dollar_risk_per_contract = stop_distance_points * config.POINT_VALUE
        max_contracts = int(config.MAX_LOSS_PER_TRADE / dollar_risk_per_contract)

        # Clamp to position limits
        available = config.MAX_POSITION_SIZE - self.open_positions
        contracts = min(max(max_contracts, 1), available)

        logger.debug(f"Position size: stop={stop_distance_points:.2f}pts, "
                     f"risk/ct=${dollar_risk_per_contract:.2f}, size={contracts}")
        return contracts

    def update_positions(self, count):
        """Update current open position count."""
        self.open_positions = count

    def get_status(self):
        """Return current risk status."""
        return {
            "date": str(self.current_date),
            "daily_pnl": self.daily_pnl,
            "daily_trades": self.daily_trades,
            "open_positions": self.open_positions,
            "halted": self.halted,
            "halt_reason": self.halt_reason,
            "remaining_risk": config.MAX_DAILY_LOSS + self.daily_pnl,
            "remaining_trades": config.MAX_DAILY_TRADES - self.daily_trades,
        }
