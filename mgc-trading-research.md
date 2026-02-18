# Micro Gold Futures (MGC) Algorithmic Trading Research Report
*Compiled: February 13, 2026*

---

## 1. Contract Specifications

| Detail | GC (Full) | MGC (Micro) |
|--------|-----------|-------------|
| Exchange | CME COMEX | CME COMEX |
| Contract Size | 100 troy oz | 10 troy oz |
| Tick Size | $0.10/oz ($10/tick) | $0.10/oz ($1/tick) |
| Trading Hours | Sun-Fri 6:00pm-5:00pm ET (23hrs) | Same |
| Settlement | Physical delivery | Physical delivery |
| Margin (approx) | ~$11,000-13,000 | ~$1,100-1,300 |
| Tax Treatment | 60/40 (60% long-term, 40% short-term) | Same |

**Why MGC for algo trading:** 1/10th the capital risk of GC, same price discovery, ideal for scaling in/out and strategy testing with real money.

---

## 2. Historical Price Characteristics of Gold Futures

### 2.1 Volatility Patterns

- **Average daily range:** Gold typically moves 1.0-2.0% per day. In dollar terms (at ~$2,000/oz), that's $20-40/day on average, with spikes to $50-80 during high-vol events.
- **Intraday volatility clustering:** Volatility is NOT uniform through the day. It clusters around:
  - London open (3:00 AM ET)
  - US economic data releases (8:30 AM ET)
  - FOMC announcements (2:00 PM ET)
  - London PM fix (~10:00 AM ET / 3:00 PM London)
- **Historical volatility (HV):** Gold's 30-day HV typically ranges 10-20% annualized in calm markets, spiking to 25-40% during crises (COVID, banking panics, geopolitical events).
- **Volatility smile:** Gold options show a notable put skew, reflecting hedging demand.
- **Seasonal volatility:** January-February and September-October tend to be higher volatility months. Summer (June-August) is often quieter.

### 2.2 Session Behavior

Gold trades nearly 24 hours. Each session has distinct personality:

**Asian Session (6:00 PM - 2:00 AM ET / Sydney + Tokyo)**
- Lowest volume and volatility
- Often range-bound, consolidation phase
- Chinese demand (Shanghai Gold Exchange) can create directional moves
- Good for mean reversion strategies
- Typical range: 30-50% of daily range

**London Session (3:00 AM - 11:30 AM ET)**
- **Most important session for gold** — London is the world's largest physical gold market
- Sharp directional moves at London open (3:00 AM ET)
- London AM fix (~10:30 AM London / 5:30 AM ET) and PM fix (~3:00 PM London / 10:00 AM ET) create volatility
- Often sets the day's high or low within first 2 hours
- 40-60% of daily range established here
- **London open breakout is a well-documented edge**

**New York Session (8:00 AM - 5:00 PM ET)**
- Highest volume when overlapping with London (8:00 AM - 11:30 AM ET)
- US economic data (NFP, CPI, GDP at 8:30 AM ET) creates explosive moves
- COMEX pit open (8:20 AM ET) historically significant
- Afternoon (post-London close) often mean-reverts or drifts
- FOMC days are special — massive vol at 2:00 PM ET

### 2.3 Trending vs Mean-Reverting

Gold exhibits **dual personality**:

- **Macro trending:** On daily/weekly timeframes, gold is strongly trending. It has long, persistent moves driven by monetary policy, inflation expectations, and USD strength. Multi-month trends of 10-30% are common.
- **Intraday mean-reverting:** On 1-5 minute bars during Asian session and NY afternoon, gold tends to mean-revert. Intraday RSI extremes (>75 or <25) frequently revert.
- **Session-to-session:** London session tends to establish a trend; NY session often continues OR reverses it. There's a documented "London reversal" pattern where NY reverses the London move.
- **Key insight:** Trend-following works best on 4H+ timeframes. Mean reversion works best on 1-15 min intraday, especially during low-volatility sessions.

### 2.4 Support/Resistance Formation

Gold respects:
- **Round numbers:** $1,800, $1,900, $2,000, $2,100 — psychological barriers with heavy options positioning
- **Previous day high/low and close** — institutional reference points
- **Weekly/monthly open** — swing traders anchor to these
- **VWAP** — institutional execution benchmark
- **Fibonacci levels** — widely watched by gold traders (38.2%, 50%, 61.8% retracements)
- **200-day moving average** — major trend filter; gold above 200 DMA = bullish regime
- **Options strikes with high open interest** — act as magnets/barriers

---

## 3. Algorithmic Strategies for Gold Futures

### 3.1 Trend Following

**A. Dual Moving Average Crossover**
- **Parameters that work on gold:**
  - Fast: 10-20 EMA, Slow: 50-100 EMA (daily bars)
  - For intraday (15min bars): Fast 20 EMA, Slow 50 EMA
  - Filter: Only take longs above 200 SMA, shorts below
- **Edge:** Gold trends persistently; MA crossovers capture the meat of macro moves
- **Weakness:** Whipsaws in ranging markets (summer, pre-FOMC)
- **Enhancement:** Add ADX filter (only trade when ADX > 20-25)

**B. Donchian Channel Breakout (Turtle-style)**
- **Parameters:**
  - Entry: 20-day high/low breakout (classic Turtle)
  - Exit: 10-day opposite breakout
  - For intraday: 20-bar high/low on 30min or 1H chart
- **Gold-specific:** Works well because gold has fat tails and persistent trends
- **Enhancement:** Volatility-based position sizing using ATR(14)

**C. Bollinger Band Breakout**
- **Parameters:** 20-period, 2.0 standard deviations
- **Entry:** Close above upper band = long, below lower = short
- **Gold-specific twist:** Use 2.5 SD for entry (gold has fat tails, 2.0 gives too many false signals)

### 3.2 Mean Reversion

**A. RSI Mean Reversion (Intraday)**
- **Parameters:**
  - RSI(2) or RSI(3) on 5-minute bars
  - Buy when RSI < 10, sell when RSI > 90
  - Target: VWAP or 20-period EMA
  - Stop: 1.5x ATR(14)
- **Best session:** Asian session and NY afternoon (low vol, mean-reverting regime)
- **Filter:** Only trade when ADX(14) < 20 (non-trending)

**B. Bollinger Band Mean Reversion**
- **Parameters:** 20-period, 2.0 SD on 5-15 min bars
- **Entry:** Price touches lower band = buy, upper band = sell
- **Exit:** Price returns to middle band (20 SMA)
- **Filter:** Avoid London open and US data releases

**C. Opening Range Reversion**
- Define first 30-min range after Asian open
- If price breaks out and fails (returns inside range within 15 min), fade the breakout
- Works because Asian session false breakouts are common

### 3.3 Momentum / RSI-Based

**A. RSI Momentum**
- **Parameters:** RSI(14) on 1H or 4H bars
- **Entry:** RSI crosses above 50 from below = long, below 50 from above = short
- **Exit:** RSI reaches 70 (longs) or 30 (shorts)
- **Filter:** Aligned with daily trend (200 SMA direction)

**B. Rate of Change (ROC) Momentum**
- **Parameters:** 10-period ROC on daily bars
- **Entry:** ROC crosses above 0 = long; below 0 = short
- **Enhancement:** Require ROC > 1.0% for entry (filter noise)

**C. MACD Momentum**
- **Parameters:** MACD(12,26,9) on 4H bars — the classic
- Gold-specific: MACD histogram divergence at major S/R levels is high-probability
- **Entry:** MACD histogram turns positive = long, negative = short
- **Filter:** Only trade in direction of daily MACD

### 3.4 Volume Profile / VWAP Strategies

**A. VWAP Reversion**
- **Concept:** Institutional traders use VWAP as execution benchmark. Price tends to return to VWAP.
- **Entry:** 
  - Long: Price > 2 SD below VWAP + bullish candle pattern
  - Short: Price > 2 SD above VWAP + bearish candle
- **Target:** VWAP
- **Best for:** Intraday only (VWAP resets daily)

**B. Volume Profile / Point of Control (POC)**
- **Concept:** POC is the price with most volume traded. Acts as magnet.
- **Strategy:** 
  - Use previous day's POC as support/resistance
  - Fade moves away from developing POC
  - Trade breakouts when price moves away from multi-day value area
- **Parameters:** Use 30-min bars, TPO-style profiles

**C. Volume Spike Breakout**
- **Entry:** Price breakout + volume > 2x 20-period average volume
- **Confirmation:** Volume confirms genuine breakout vs. false break
- **Gold-specific:** Works well at London open and US data releases

### 3.5 Session-Based Strategies

**A. London Open Breakout (HIGH PROBABILITY)**
- **This is arguably the single best-known gold intraday strategy**
- **Methodology:**
  1. Define the Asian session range (6:00 PM - 2:00 AM ET)
  2. At London open (3:00 AM ET), wait for breakout above/below Asian range
  3. Enter on confirmed breakout (close above/below on 5-min bar)
  4. Stop: Opposite end of Asian range (or midpoint for tighter stops)
  5. Target: 1:1 or 1.5:1 R:R, or trail with 20 EMA on 15-min
- **Win rate:** Historically 50-55%, but R:R of 1.5:1+ makes it profitable
- **Enhancement:** Filter with daily trend direction; don't trade Fridays (lower vol)

**B. NY Session Momentum**
- **Concept:** Trade the continuation or reversal of London's move at NY open
- **Methodology:**
  1. Note London session direction (up or down from London open to 8:00 AM ET)
  2. If US data aligns with London direction → continuation trade
  3. If contradicts → reversal trade after first 15-min bar confirms
- **Parameters:** Enter at 8:30 AM or 9:00 AM ET, stop below NY session low

**C. London Close Fade**
- After London close (11:30 AM ET), gold often fades or consolidates
- Short if extended above daily VWAP at London close; long if below
- Target: Return to VWAP or daily POC
- **Stop:** New session high/low

**D. Kill Zone Strategy**
- Trade only during "kill zones" — periods of highest institutional activity:
  - London Kill Zone: 2:00-5:00 AM ET
  - NY Kill Zone: 7:00-10:00 AM ET
- Look for liquidity sweeps (fakeouts above/below session highs/lows) then trade the reversal
- Based on ICT (Inner Circle Trader) methodology — very popular in gold

### 3.6 Spread / Correlation Strategies

**A. Gold vs US Dollar Index (DXY) — Inverse Correlation**
- Gold and DXY have ~-0.7 to -0.85 correlation over most periods
- **Strategy:** 
  - If DXY drops sharply and gold hasn't moved → buy gold (catch-up trade)
  - If DXY and gold both rise → unsustainable divergence, short gold
- **Parameters:** Monitor 1H correlation; trade when z-score of spread > 2.0
- **Data:** DXY futures (DX) or via USD ETF (UUP)

**B. Gold vs US Treasury Bonds (Inverse Real Yields)**
- Gold moves inversely with real interest rates (TIPS yields)
- When 10Y TIPS yield drops → gold should rise
- **Strategy:** Monitor TLT or /ZN alongside gold
- **Pairs trade:** Long gold / short bonds when spread deviates > 2 SD from 20-day mean

**C. Gold/Silver Ratio**
- Gold/silver ratio (normally 60-80) reverts to mean
- When ratio > 80: Buy silver, sell gold (ratio mean reversion)
- When ratio < 60: Buy gold, sell silver
- **Implementation:** MGC vs SIL or /SI micro contracts

**D. Gold vs Miners (GDX)**
- Miners typically lead gold
- If GDX breaks out and GC hasn't → buy GC
- Divergences signal potential reversals

---

## 4. Data Sources for Historical Gold Futures Data

### 4.1 Free Sources

| Source | Data Type | Coverage | Access |
|--------|-----------|----------|--------|
| **Yahoo Finance** (yfinance) | Daily OHLCV | GC=F continuous | `pip install yfinance` → `yf.download("GC=F")` |
| **FRED (St. Louis Fed)** | Daily gold price | Spot gold, long history | API or CSV download |
| **Quandl/Nasdaq Data Link** | Daily OHLCV | GC continuous, free tier | `pip install nasdaq-data-link` |
| **Investing.com** | Daily/weekly OHLCV | GC, historical | CSV download (manual) |
| **TradingView** (export) | Any timeframe OHLCV | GC1!, MGC1! | Manual CSV export (limited bars) |

### 4.2 Cheap Sources ($10-50/month)

| Source | Data Type | Coverage | Price |
|--------|-----------|----------|-------|
| **Databento** | Tick, 1-sec, 1-min+ | CME full depth | Pay-per-use, very cheap |
| **Polygon.io** | 1-min+ OHLCV | Futures included | $29/mo (Starter) |
| **FirstRate Data** | Tick to daily | GC back to 1975 | One-time $15-40 per symbol |
| **Norgate Data** | Daily, adjusted continuous | All CME metals | $55/mo |
| **Sierra Chart** | Tick data | Real-time + historical | $26/mo (includes data) |

### 4.3 Broker-Provided (Free with Account)

| Broker | Data Type | Notes |
|--------|-----------|-------|
| **Interactive Brokers** | Tick to daily | Free with account; API access via `ib_insync` Python lib |
| **NinjaTrader** | 1-min to daily | Free with Continuum data ($20/mo for CME) |
| **TradeStation** | Tick to daily | Free with funded account |
| **ThinkorSwim (Schwab)** | 1-min to daily | Free, but limited export |

### 4.4 Python Libraries for Data Access

```python
# Yahoo Finance (free, daily only)
import yfinance as yf
gold = yf.download("GC=F", start="2010-01-01")

# Interactive Brokers (need account)
from ib_insync import *
ib = IB()
ib.connect()
contract = Future('MGC', '202403', 'COMEX')
bars = ib.reqHistoricalData(contract, '', '1 Y', '1 hour', 'TRADES', True)

# Databento (pay per use, cheapest tick data)
import databento as db
client = db.Historical("YOUR_KEY")
data = client.timeseries.get_range(
    dataset="GLBX.MDP3",
    symbols=["MGC.FUT"],
    start="2023-01-01",
    end="2024-01-01",
    schema="ohlcv-1m"
)

# Polygon.io
import requests
url = "https://api.polygon.io/v2/aggs/ticker/GC/range/1/minute/2024-01-01/2024-01-31"
```

**Recommendation:** Start with **yfinance** for daily data (free), upgrade to **Databento** or **Interactive Brokers** for intraday/tick data when you need it.

---

## 5. Backtesting Frameworks

### 5.1 Framework Comparison

| Framework | Futures Support | Speed | Ease of Use | Active Dev | Best For |
|-----------|----------------|-------|-------------|------------|----------|
| **Backtrader** | ✅ Excellent | Medium | Medium | Slow | Full futures support, commissions, margin |
| **vectorbt** | ⚠️ Limited | 🚀 Fastest | Medium | Active | Rapid prototyping, portfolio optimization |
| **Zipline (Reloaded)** | ⚠️ Equity-focused | Medium | Hard | Moderate | Equity strategies (not ideal for futures) |
| **QuantConnect (Lean)** | ✅ Excellent | Fast | Medium | Very Active | Cloud, multi-asset, live trading |
| **Nautilus Trader** | ✅ Excellent | 🚀 Very Fast | Hard | Active | Production-grade, event-driven |
| **bt (pmorissette)** | ❌ No | Fast | Easy | Moderate | Simple portfolio backtests |
| **PyAlgoTrade** | ⚠️ Basic | Medium | Easy | Dead | Avoid — unmaintained |

### 5.2 Detailed Recommendations

**For Gold Futures Specifically:**

**1. Backtrader (Best Starting Point)**
```python
import backtrader as bt

class GoldMA(bt.Strategy):
    params = (('fast', 10), ('slow', 50),)
    
    def __init__(self):
        self.fast_ma = bt.indicators.EMA(period=self.p.fast)
        self.slow_ma = bt.indicators.EMA(period=self.p.slow)
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
    
    def next(self):
        if self.crossover > 0:
            self.buy(size=1)
        elif self.crossover < 0:
            self.sell(size=1)

cerebro = bt.Cerebro()
cerebro.adddata(bt.feeds.GenericCSVData(dataname='gold_data.csv'))
cerebro.addstrategy(GoldMA)
cerebro.broker.setcommission(commission=2.50, margin=1300, mult=10)  # MGC specs
cerebro.run()
```
- ✅ Native futures support (commission, margin, multiplier)
- ✅ Excellent for single-strategy development
- ✅ Built-in analyzers (Sharpe, drawdown, trade log)
- ⚠️ Slow for large parameter sweeps
- ⚠️ Development has slowed

**2. vectorbt (Best for Parameter Optimization)**
```python
import vectorbt as vbt
import numpy as np

price = vbt.YFData.download("GC=F").get("Close")

# Test 100 MA combinations instantly
fast_windows = np.arange(5, 50, 5)
slow_windows = np.arange(20, 200, 10)
fast_ma, slow_ma = vbt.MA.run_combs(price, fast_windows, slow_windows)
entries = fast_ma.ma_crossed_above(slow_ma)
exits = fast_ma.ma_crossed_below(slow_ma)

pf = vbt.Portfolio.from_signals(price, entries, exits, fees=0.0001)
pf.total_return().sort_values(ascending=False).head(20)
```
- 🚀 100-1000x faster than backtrader for parameter sweeps
- ✅ Beautiful built-in plotting
- ⚠️ Doesn't natively handle futures margin/multiplier (need workarounds)
- ⚠️ Signal-based (harder for complex order logic)

**3. QuantConnect / Lean (Best for Live Trading Path)**
- Cloud-based, free tier available
- Native futures data included (CME, etc.)
- Supports continuous contracts, rollovers
- Direct path to live trading
- Python and C# support

**4. Nautilus Trader (Best for Production)**
- Rust core, Python API — extremely fast
- Full event-driven architecture
- Built for institutional-grade algo trading
- Steep learning curve but most capable

### 5.3 Recommendation Path

1. **Prototype** strategies with **vectorbt** (fast iteration)
2. **Validate** with **backtrader** (proper futures mechanics)
3. **Go live** with **QuantConnect** or **Nautilus Trader**

---

## 6. Key Performance Metrics

### 6.1 Must-Track Metrics

| Metric | Target (Good) | Target (Excellent) | Description |
|--------|--------------|---------------------|-------------|
| **Sharpe Ratio** | > 1.0 | > 2.0 | Risk-adjusted return (annualized) |
| **Sortino Ratio** | > 1.5 | > 2.5 | Like Sharpe but only penalizes downside vol |
| **Max Drawdown** | < 20% | < 10% | Worst peak-to-trough decline |
| **Profit Factor** | > 1.3 | > 2.0 | Gross profit / gross loss |
| **Win Rate** | > 40% (trend) | > 55% (mean rev) | Wins / total trades |
| **Avg Win / Avg Loss** | > 1.5:1 | > 2.5:1 | Reward-to-risk ratio per trade |
| **Calmar Ratio** | > 1.0 | > 3.0 | Annual return / max drawdown |
| **Recovery Factor** | > 3.0 | > 6.0 | Net profit / max drawdown |
| **Expectancy** | > $0 | — | (Win% × Avg Win) - (Loss% × Avg Loss) |
| **Avg Trades/Month** | > 10 | > 30 | Statistical significance |

### 6.2 Gold-Specific Metrics to Track

- **Performance by session:** Break down P&L by Asian/London/NY session
- **Performance on data days:** NFP, CPI, FOMC days vs. normal days
- **Drawdown duration:** How long are drawdowns? Gold trends can stall for months
- **Slippage analysis:** MGC has good liquidity but wider spreads than GC during Asian session
- **Correlation to gold price:** Is the strategy directional or market-neutral?

### 6.3 Avoiding Overfitting

- **Out-of-sample testing:** Train on 60-70% of data, test on 30-40%
- **Walk-forward optimization:** Rolling train/test windows
- **Parameter sensitivity:** Good strategies work across a RANGE of parameters, not just one magic number
- **Minimum 100 trades** in backtest for statistical significance
- **Monte Carlo simulation:** Randomize trade order to test robustness
- **Cross-market validation:** Does the strategy also work on silver (/SI)? If yes, more robust

---

## 7. Practical Implementation Roadmap

### Phase 1: Data & Infrastructure (Week 1)
- [ ] Open Interactive Brokers account (if not already)
- [ ] Set up Python environment: `pip install backtrader vectorbt yfinance pandas numpy`
- [ ] Download daily GC data via yfinance (2010-present)
- [ ] Download 1-min data via IB or Databento (2 years minimum)

### Phase 2: Strategy Development (Weeks 2-4)
- [ ] Implement London Open Breakout (highest expected edge)
- [ ] Implement dual EMA crossover with 200 SMA filter
- [ ] Implement RSI mean reversion for Asian session
- [ ] Run parameter sweeps with vectorbt

### Phase 3: Validation (Weeks 5-6)
- [ ] Walk-forward optimization on all strategies
- [ ] Out-of-sample testing
- [ ] Monte Carlo simulation
- [ ] Calculate all metrics from Section 6

### Phase 4: Paper Trading (Weeks 7-10)
- [ ] Deploy best 1-2 strategies on paper account
- [ ] Compare live fills vs. backtest assumptions
- [ ] Measure actual slippage on MGC

### Phase 5: Live Trading (Week 11+)
- [ ] Start with 1 MGC contract per signal
- [ ] Scale position size based on account equity and Kelly criterion
- [ ] Monitor daily; review weekly

---

## 8. Key Takeaways

1. **London Open Breakout is your first strategy** — well-documented edge, simple to implement, specific to gold's session dynamics.

2. **Gold trends on daily+ timeframes, mean-reverts intraday** — use this dual personality to run complementary strategies.

3. **Start with backtrader for proper futures backtesting** (margin, commission, contract multiplier), use vectorbt for rapid parameter sweeps.

4. **MGC at $1/tick is perfect for algo development** — real market microstructure at 1/10th the risk of GC.

5. **Data path: yfinance (free daily) → Databento (cheap intraday) → IB (live)**

6. **Target metrics: Sharpe > 1.5, Max DD < 15%, Profit Factor > 1.5, 100+ trades minimum.**

7. **Gold's key drivers are DXY, real yields (TIPS), and FOMC** — incorporate these as regime filters.
