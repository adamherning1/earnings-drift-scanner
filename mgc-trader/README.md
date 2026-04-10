# MGC Day Trader

Automated daytrading system for Micro Gold Futures (MGC) via Interactive Brokers.

## Architecture

```
trader.py          — Main loop: connects to IB, runs strategies, manages orders
ib_connection.py   — IB API wrapper (ib_insync): connection, orders, data
strategies.py      — Strategy engine: ORB, VWAP Bounce, EMA Momentum, Level Scalp
indicators.py      — Streaming indicators: EMA, ATR, VWAP, RSI, Opening Range
risk_manager.py    — Risk enforcement: daily loss limits, position sizing, trade caps
config.py          — All configuration in one place
```

## Strategies

| Strategy | Timeframe | Style | Description |
|----------|-----------|-------|-------------|
| ORB | 5m | Breakout | Opening Range Breakout after COMEX open (8:20 ET) |
| VWAP Bounce | 5m | Mean Reversion | Buy/sell bounces off VWAP with trend filter |
| EMA Momentum | 5m | Trend | 9/21 EMA cross with 50 EMA trend filter |
| Level Scalp | 1m | Scalp | Reactions at prior day H/L, round numbers, overnight H/L |

## Risk Management

- Max daily loss: $2,000
- Max trades/day: 30
- Max risk/trade: $500
- Max position: 5 contracts
- Auto-flatten by 3:30 PM ET

## Setup

1. Install: `pip install ib_insync pytz`
2. Start TWS or IB Gateway (paper trading mode)
3. Enable API: TWS → Config → API → Enable ActiveX and Socket
4. Set port: 7497 (TWS paper) or 4002 (Gateway paper)
5. Run: `python trader.py`

## Status: 🏗️ Building

- [x] IB connection manager
- [x] Streaming indicators
- [x] Strategy framework (4 strategies)
- [x] Risk manager
- [x] Main trading loop
- [ ] IB account connected (waiting for Adam)
- [ ] Historical backtest validation
- [ ] Live paper testing
- [ ] Strategy parameter tuning
