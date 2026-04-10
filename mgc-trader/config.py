"""
MGC Day Trader — Configuration
"""

# ── IB Connection ────────────────────────────────────────────────────────────
IB_HOST = "127.0.0.1"
IB_PORT = 4002          # 7497 = TWS paper, 4002 = IB Gateway paper
IB_CLIENT_ID = 1

# ── Contract ─────────────────────────────────────────────────────────────────
SYMBOL = "MGC"
EXCHANGE = "COMEX"
CURRENCY = "USD"
SEC_TYPE = "FUT"
# Contract month will be auto-resolved to front month

# ── Contract Specs ───────────────────────────────────────────────────────────
TICK_SIZE = 0.10        # Minimum price increment
POINT_VALUE = 10.0      # $10 per 1.0 point move
TICK_VALUE = 1.00       # $1 per tick (0.10 * $10)

# ── Risk Management ─────────────────────────────────────────────────────────
INITIAL_CAPITAL = 100_000   # Paper account size
MAX_POSITION_SIZE = 3       # Max contracts at once
MAX_DAILY_LOSS = 2000       # Stop trading for the day if down $2000
MAX_DAILY_TRADES = 30       # Max trades per day (avoid overtrading)
MAX_LOSS_PER_TRADE = 500    # Max risk per trade in dollars

# ── Trading Hours (all in ET) ────────────────────────────────────────────────
# Gold futures trade nearly 24h: Sun 6PM - Fri 5PM ET
# Best intraday windows:
LONDON_OPEN_ET = "03:00"        # London session start
NY_OPEN_ET = "08:00"            # Pre-market activity
COMEX_OPEN_ET = "08:20"         # COMEX floor open — key time
LONDON_FIX_ET = "10:30"         # London AM fix — can cause moves
NY_CLOSE_ET = "13:30"           # COMEX close
AVOID_AFTER_ET = "14:00"        # Low vol after COMEX close

# Active trading window — Full Day (multi-session) per backtest optimization
# Includes Asian, London, and US/COMEX sessions for maximum edge
TRADING_START_ET = "18:00"      # Asian session open (6 PM ET)
TRADING_END_ET = "13:15"        # Stop new entries 15 min before COMEX close
FLATTEN_BY_ET = "13:30"         # Flatten everything at COMEX close — go home flat

# Multi-timeframe settings
MTF_ENABLED = True              # Use 15-min signals with 5-min execution
MTF_SIGNAL_TF_MINUTES = 15     # Signal timeframe (aggregate from 5-min bars)
MTF_ENTRY_TF_MINUTES = 5       # Entry/exit timeframe (raw bars from IB)

# ── Strategy Parameters (defaults, will be tuned) ────────────────────────────
STRATEGIES = {
    "orb": {
        "enabled": True,
        "timeframe": "mtf",         # Multi-TF: 15-min ORB detection, 5-min entry
        "orb_minutes": 15,          # Opening range = first 15 min after COMEX open
        "orb_start_et": "08:20",    # COMEX open
        "atr_period": 14,
        "atr_stop_mult": 1.5,      # optimized from backtest (Sharpe 5.48)
        "profit_target_mult": 1.5,  # optimized: 1.5:1 R:R
        "max_trades": 2,
    },
    "vwap_bounce": {
        "enabled": False,           # disabled — too noisy on gold 5-min
        "timeframe": "5m",
        "lookback_bars": 3,
        "atr_period": 14,
        "atr_stop_mult": 2.0,
        "profit_target_mult": 1.5,
        "max_distance_ticks": 10,
        "max_trades": 4,
    },
    "ema_momentum": {
        "enabled": True,
        "timeframe": "mtf",         # Multi-TF: 15-min signals, 5-min entry
        "fast_ema": 9,              # optimized (9,21,50) combo
        "slow_ema": 21,
        "trend_ema": 50,
        "atr_period": 14,
        "atr_stop_mult": 3.0,      # optimized from backtest (Sharpe 7.83)
        "profit_target_mult": 3.0,  # optimized: 3:1 R:R
        "max_trades": 3,
    },
    "level_scalp": {
        "enabled": False,           # disabled — 0.75 ATR stop = instant stop-outs
        "timeframe": "1m",
        "use_prior_day_hl": True,
        "use_round_numbers": True,
        "use_overnight_hl": True,
        "atr_period": 14,
        "atr_stop_mult": 2.0,
        "profit_target_mult": 1.5,
        "max_trades": 6,
    },
}

# ── Logging ──────────────────────────────────────────────────────────────────
LOG_DIR = r"C:\Users\adamh\.openclaw\workspace\mgc-trader\logs"
LOG_TRADES = True
LOG_SIGNALS = True
