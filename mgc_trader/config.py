"""MGC Trading Bot Configuration"""

# IB Gateway Connection (Dell Trading Server)
IB_HOST = '192.168.0.58'  # TWS on Dell server
IB_PORT = 4002
IB_CLIENT_ID = 101  # Unique ID to avoid conflicts

# Trading Parameters
SYMBOL = 'MGC'
EXCHANGE = 'COMEX'  # MGC trades on COMEX, not NYMEX
CONTRACT_MONTH = '20260626'  # June 2026 contract (MGCM6)
POSITION_SIZE = 3  # Start with 3 contracts
MAX_DAILY_LOSS = 1200  # Temporarily increased to account for yesterday's loss
MAX_POSITIONS = 1  # Only 1 position at a time for day trading
MAX_TRADES_PER_DAY = 10  # Limit churning

# Day Trading Strategy Parameters (5M/15M)
KC_LENGTH = 20  # Smoother for day trading
KC_MULT_LONG = 1.5  # Wider bands for 5M
KC_LENGTH_SHORT = 20
KC_MULT_SHORT = 1.5
ADX_PERIOD = 14
ADX_THRESHOLD = 25  # Higher threshold for day trading
ATR_PERIOD = 14

# Risk Management (tighter for day trading)
LONG_STOP_ATR = 2.0  # Tighter stops for day trading
SHORT_STOP_ATR = 2.0  # Same for shorts
LONG_TP_R = 1.5  # Take profits on longs too
SHORT_TP_R = 1.5  # Symmetric targets
MAX_TRADES_PER_DAY = 10  # Limit churning

# Timeframes
PRIMARY_TIMEFRAME = '5M'  # Day trading entries
BIAS_TIMEFRAME = '4H'  # Your PROVEN strategy for direction
CONFIRMATION_TIMEFRAME = '15M'  # Medium-term momentum

# Trading Hours (ET) - Day trading hours
TRADING_START = 9, 30  # 9:30 AM ET (avoid open volatility)
TRADING_END = 15, 45  # 3:45 PM ET (exit before close)

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'mgc_trader.log'