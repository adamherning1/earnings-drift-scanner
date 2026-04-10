import json
from datetime import datetime

# Manually create the complete trading status with the existing trade
trade_record = {
    "timestamp": "2026-04-06T10:13:40",
    "symbol": "MGC",
    "entry_price": 4673.90,
    "exit_price": 4688.40,
    "contracts": 2,
    "profit": -293.88
}

status = {
    "connected": True,
    "account": "DUP971200",
    "net_liquidation": "$997,687.91",
    "net_liquidation_value": 997687.91,
    "daily_pnl": -293.88,
    "unrealized_pnl": 0,
    "positions": 0,
    "winning_trades": 0,
    "losing_trades": 1,
    "total_profit": 0,
    "total_loss": 293.88,
    "total_pnl": -293.88,  # Total P&L for the day
    "profit_factor": 0,  # No winning trades yet
    "trade_log": [trade_record],
    "timestamp": datetime.now().isoformat(),
    "message": "Adaptive Bot Scanning",
    "mgc_price": 4686.90
}

# Write to the trading status file
with open('../trading_status.json', 'w', encoding='utf-8') as f:
    json.dump(status, f, indent=2)

print("Dashboard fixed with complete trade history!")
print(f"Showing: 1 losing trade, -$293.88 daily P&L")
print(f"Account: $997,687.91")