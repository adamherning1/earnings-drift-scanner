# Day Trading Stock Index Futures: A Comprehensive Guide

*Last updated: February 2026*

---

## Table of Contents
1. [Market Basics](#market-basics)
2. [Day Trading Fundamentals](#day-trading-fundamentals)
3. [Key Concepts](#key-concepts)
4. [Top Day Trading Strategies](#top-day-trading-strategies)

---

## Market Basics

### The Four Major US Stock Index Futures

| Contract | Index | Tick Size | Tick Value | Point Value | Micro Contract | Micro Point Value |
|----------|-------|-----------|------------|-------------|----------------|-------------------|
| **ES** | S&P 500 | 0.25 | $12.50 | $50.00 | MES | $5.00 |
| **NQ** | Nasdaq 100 | 0.25 | $5.00 | $20.00 | MNQ | $2.00 |
| **YM** | Dow Jones | 1.00 | $5.00 | $5.00 | MYM | $0.50 |
| **RTY** | Russell 2000 | 0.10 | $5.00 | $50.00 | M2K | $5.00 |

### Margin Requirements (Approximate, varies by broker)

| Contract | Intraday Margin (Day Trade) | Overnight (Initial) | Micro Intraday |
|----------|----------------------------|----------------------|----------------|
| ES | $500–$1,000 | ~$13,200 | $50–$100 |
| NQ | $1,000–$2,000 | ~$17,600 | $100–$200 |
| YM | $500–$800 | ~$9,900 | $50–$100 |
| RTY | $500–$800 | ~$7,150 | $50–$100 |

Day trade margins are dramatically lower than overnight margins — this is what makes futures so capital-efficient. A $5,000 account can trade multiple MES contracts intraday. **Note:** Brokers like NinjaTrader, AMP, and Tradovate offer the most competitive intraday margins.

### Trading Hours

Futures trade nearly 24 hours a day, Sunday evening through Friday afternoon:

- **Globex / Electronic Trading Hours (ETH):** Sunday 6:00 PM ET – Friday 5:00 PM ET (with a daily halt 5:00–6:00 PM ET)
- **Regular Trading Hours (RTH):** 9:30 AM – 4:15 PM ET (the "day session")
- **CME Settlement:** 4:00 PM ET for cash-settled index futures

### Key Trading Sessions (all times ET)

| Session | Time (ET) | Characteristics |
|---------|-----------|-----------------|
| **Asia/Tokyo** | 7:00 PM – 2:00 AM | Low volume, tight ranges, mean-reverting |
| **London Open** | 3:00 AM – 4:00 AM | First real liquidity injection, breakouts from Asia range |
| **European Session** | 3:00 AM – 9:30 AM | Establishes the "overnight range" US traders watch |
| **US Pre-Market** | 8:00 AM – 9:30 AM | Economic data releases (8:30 AM), increasing volatility |
| **NYSE Open** | 9:30 AM – 10:00 AM | Highest volume, widest spreads, most volatile |
| **Morning Session** | 10:00 AM – 11:30 AM | Trends often establish or continue |
| **Lunch Chop** | 11:30 AM – 1:30 PM | Low volume, choppy, mean-reverting — many traders sit out |
| **Afternoon Session** | 1:30 PM – 3:00 PM | "2 PM reversal" zone, FOMC announcements (2:00 PM) |
| **Power Hour** | 3:00 PM – 4:00 PM | MOC (Market-On-Close) orders, institutional rebalancing, strong trends |

### Best Times to Day Trade

The highest-probability setups occur during:
1. **9:30–10:30 AM ET** — Opening drive, highest volume (35-40% of daily volume occurs in first and last hours)
2. **2:00–2:30 PM ET** — Afternoon reversal zone
3. **3:00–4:00 PM ET** — Power hour momentum

**Worst time:** 11:30 AM – 1:30 PM ET (lunch). Spreads widen, volume drops 50-60%, and choppy price action grinds accounts.

---

## Day Trading Fundamentals

### Why Futures Over Stocks for Day Trading?

1. **No Pattern Day Trader (PDT) rule** — Stocks require $25,000 minimum for unlimited day trades. Futures have no such rule; you can day trade with $1,000.
2. **No overnight risk** — You close all positions by end of session. No gap risk.
3. **Superior leverage** — Control $250,000+ of S&P exposure with $500 margin on ES.
4. **Tax advantages** — Futures are taxed 60/40 (60% long-term, 40% short-term capital gains) under Section 1256, regardless of holding period.
5. **Nearly 24-hour market** — Trade around economic events, not just during stock market hours.
6. **No short-sale restrictions** — Go short as easily as long. No uptick rule, no borrowing shares.
7. **Centralized exchange** — All orders go through CME. No dark pools, no payment for order flow concerns.

### Day Trading Styles

#### Scalping (1–5 minute charts)
- **Hold time:** 30 seconds to 5 minutes
- **Target:** 2–8 ticks (ES: $25–$100 per contract)
- **Trades per day:** 10–30
- **Win rate needed:** 55–65% (due to tight R:R)
- **Skills needed:** Fast execution, tape reading, order flow analysis
- **Best for:** Experienced traders with low commissions and fast platforms

#### Momentum / Intraday Swing (5–15 minute charts)
- **Hold time:** 15 minutes to 2 hours
- **Target:** 4–20 points on ES ($200–$1,000 per contract)
- **Trades per day:** 2–6
- **Win rate needed:** 40–50% (wider R:R compensates)
- **Skills needed:** Trend identification, patience, level-to-level trading
- **Best for:** Most day traders — balances frequency with quality

#### Intraday Position Trading (15–60 minute charts)
- **Hold time:** 1–6 hours
- **Target:** 10–40+ points on ES
- **Trades per day:** 1–3
- **Win rate needed:** 35–45% (large R:R of 2:1 to 4:1)
- **Skills needed:** Macro awareness, patience, strong conviction
- **Best for:** Part-time traders or those with a strong daily bias

### Risk Management: The Non-Negotiables

Risk management is what separates profitable traders from blown accounts. These rules are not suggestions — they are survival requirements.

#### 1. Maximum Daily Loss
Set a hard daily loss limit before you trade. Common frameworks:
- **Aggressive:** 2% of account per day (e.g., $100 on a $5,000 account)
- **Conservative:** 1% of account per day ($50 on $5,000)
- **Professional:** Fixed dollar amount based on strategy expectancy

When you hit your daily max loss, **you stop trading. Period.** No revenge trading, no "one more trade to get it back."

#### 2. Position Sizing
Never risk more than 1-2% of your account on a single trade.

**Formula:** Position Size = (Account Risk $) / (Stop Distance in Points × Point Value)

Example: $5,000 account, 1% risk = $50 risk per trade. If your stop is 5 points on MES ($5/point), risk = $25 per contract → you can trade 2 MES contracts.

#### 3. Maximum Trades Per Day
Set a maximum number of trades (e.g., 5–8 for momentum trading). This prevents overtrading, which is the #1 account killer.

#### 4. Time-Based Rules
- Don't trade the first 2 minutes after open (chaos, wide spreads)
- Don't trade 11:30 AM–1:00 PM unless you have a specific edge in chop
- Don't trade within 5 minutes of major economic releases unless you have an event-trading strategy
- Stop trading 30 minutes before your scheduled end time

### Time-of-Day Effects

Understanding intraday patterns gives you a structural edge:

#### The First 30 Minutes (9:30–10:00 AM ET)
The opening 30 minutes sets the tone. Studies show:
- ~65% of the day's range is established in the first hour (source: CME Group research)
- Opening range breakouts (first 15 or 30 min) trend ~55-60% of the time
- The first move is often a "fake" — the real trend emerges after 9:45–10:00 AM

#### Lunch Chop (11:30 AM–1:30 PM ET)
- Volume drops 40-60% vs. morning session
- Price oscillates in narrow range
- Mean reversion strategies work; trend strategies fail
- Many professional day traders take a break during this window

#### The 2:00 PM Reversal
- FOMC announcements occur at 2:00 PM (8 times per year)
- Even on non-FOMC days, the 1:30–2:30 PM window often sees a reversal or trend acceleration
- Bond market closes at 3:00 PM, which can shift equity flows
- Historical tendency: if the market trended down in the morning, it's more likely to bounce after 2:00 PM (and vice versa)

#### 3:30 PM MOC (Market-On-Close) Flow
- Mutual funds, ETFs, and institutional rebalancing submit MOC orders around 3:30–3:50 PM
- These create strong directional moves in the last 30 minutes
- MOC imbalances are published by NYSE at 3:50 PM
- Power hour (3:00–4:00 PM) accounts for ~15-20% of daily volume

---

## Key Concepts

### Market Profile / Value Area / POC

Market Profile, developed by J. Peter Steidlmayer at the CBOT, organizes price data by time spent at each level.

- **Value Area (VA):** The price range where 70% of trading activity occurred. Defined by the Value Area High (VAH) and Value Area Low (VAL).
- **Point of Control (POC):** The single price level with the most trading volume/time — the "fairest price."
- **Initial Balance (IB):** The range of the first hour of RTH trading (9:30–10:30 AM ET).

**How to use it:**
- If price opens inside the previous day's value area → expect rotation/range day
- If price opens outside the previous day's value area → expect trend day
- POC acts as a magnet — price tends to revisit it
- VAH and VAL are key support/resistance levels

### VWAP and Standard Deviation Bands

**VWAP (Volume-Weighted Average Price)** is the benchmark institutional traders use. It represents the average price weighted by volume.

- **VWAP** = Σ(Price × Volume) / Σ(Volume), calculated cumulatively from the session open
- **+1σ / -1σ bands** contain ~68% of price action
- **+2σ / -2σ bands** contain ~95% of price action

**Trading rules:**
- Price above VWAP = bullish bias; below = bearish bias
- Institutions are buyers below VWAP and sellers above VWAP
- First touch of VWAP after a move away → high-probability mean reversion
- VWAP acts as strong support/resistance during trending days
- On range days, price oscillates around VWAP — trade the bands

### Order Flow Basics

Order flow analysis looks at actual buy/sell transactions rather than just price movement.

- **Delta:** The difference between aggressive buyers (market orders hitting the ask) and aggressive sellers (market orders hitting the bid) at each price level.
- **Cumulative Delta:** Running sum of delta throughout the session. Rising = buyers in control; falling = sellers in control.
- **Footprint Charts:** Show volume at each price level split by bid/ask, revealing absorption, imbalances, and exhaustion.
- **Key signals:** Divergence between price (making new highs) and cumulative delta (failing to make new highs) suggests weakening momentum and potential reversal.

### Opening Range Breakout (ORB) Theory

The ORB is one of the oldest and most researched intraday strategies, popularized by Toby Crabel in *Day Trading with Short-Term Price Patterns and Opening Range Breakout* (1990).

**Core theory:** The opening range (first 5, 15, or 30 minutes) establishes key levels. A breakout from this range, confirmed by volume, tends to continue in the breakout direction.

**Statistics (approximate, from various backtests):**
- 15-minute ORB on ES: ~55-58% win rate with 1.5:1 R:R
- 30-minute ORB on ES: ~52-55% win rate with 2:1 R:R
- ORB works better in trending markets (VIX 15-25) than extremely low-vol environments

### Gap Fill Statistics

A "gap" occurs when the current session opens above or below the previous session's close.

**Key statistics for ES/SPX (sources: various quant studies, Quantifiable Edges):**
- Gaps of 0.0–0.25% fill same day: ~75-80% of the time
- Gaps of 0.25–0.50% fill same day: ~65-70%
- Gaps of 0.50–1.0% fill same day: ~50-55%
- Gaps > 1.0% fill same day: ~30-35%
- **Gap and go** (gap doesn't fill, trends in gap direction): More likely when gap > 0.75% and aligns with multi-day trend

**Key insight:** Small gaps are high-probability fades; large gaps are often trend continuations ("gap and go").

### Key Levels for Day Trading

Every day trader should have these levels marked before the open:

1. **Overnight High / Low (ONH / ONL)** — The range from 6:00 PM to 9:30 AM ET
2. **Previous Day High / Low / Close (PDH / PDL / PDC)** — Key support/resistance
3. **VWAP** — Calculated from session open
4. **Value Area High / Low / POC** — From previous session's market profile
5. **Weekly / Monthly Pivot Points** — Calculated from prior week/month OHLC
6. **Round numbers** — ES: every 25-point level (5800, 5825, 5850...); NQ: every 100-point level
7. **Initial Balance High / Low** — First hour's range (9:30–10:30 AM)

---

## Top Day Trading Strategies

### Strategy 1: Opening Range Breakout (ORB)

**Concept:** Trade the breakout of the first 15 or 30 minutes of RTH trading.

**Entry Rules:**
- Mark the high and low of the 9:30–9:45 AM (15-min ORB) or 9:30–10:00 AM (30-min ORB) candle
- **Long:** Buy when price breaks above the ORB high by 1-2 ticks, with volume confirmation
- **Short:** Sell when price breaks below the ORB low by 1-2 ticks, with volume confirmation
- **Filter:** Confirm with VWAP direction (long only if VWAP is rising; short only if VWAP is falling)
- **Filter:** Avoid if the ORB range is > 1.5x the 20-day average ORB range (overextended)

**Exit Rules:**
- **Target 1:** 1x the ORB range height from the breakout level (e.g., if ORB range = 10 pts, target = breakout + 10 pts)
- **Target 2:** Previous day high/low or next major level
- **Stop:** Midpoint of the ORB range (or the opposite side of the ORB if conservative)
- **Time stop:** If trade hasn't hit target by 12:00 PM, close at VWAP or breakeven

**Best Timeframe:** 5-minute chart for entries, 15-minute for ORB range definition

**Best Market Conditions:** Moderate volatility (VIX 15-25), trending days, after a catalyst (earnings, economic data)

**Win Rate:** ~55-60% | **R:R:** 1.5:1 to 2:1 | **Expectancy:** Positive with disciplined execution

**Pros:**
- Clear, mechanical rules — reduces emotional decision-making
- Captures the strongest moves of the day
- Well-researched with decades of data

**Cons:**
- Susceptible to false breakouts, especially on range-bound days
- Requires fast execution — late entries get poor fills
- Doesn't work well on low-volatility, no-catalyst days

---

### Strategy 2: VWAP Mean Reversion

**Concept:** Fade extended moves away from VWAP, expecting price to revert to the mean.

**Entry Rules:**
- Wait for price to reach +1.5σ to +2σ VWAP band (for shorts) or -1.5σ to -2σ band (for longs)
- **Confirmation:** Look for a rejection candle (doji, hammer, shooting star) at the band
- **Confirmation:** Cumulative delta divergence (price making new high but delta not confirming)
- **Long:** Enter on the first bullish candle close after touching the -1.5σ to -2σ band
- **Short:** Enter on the first bearish candle close after touching the +1.5σ to +2σ band

**Exit Rules:**
- **Target 1:** VWAP (take 50-75% off)
- **Target 2:** Opposite VWAP band (runner)
- **Stop:** Beyond the 2σ band + 2 points buffer
- **Trail:** Once at VWAP, trail stop to breakeven

**Best Timeframe:** 5-minute chart

**Best Market Conditions:** Range-bound days, inside days, low-catalyst environments. **Do not** use on strong trend days (price can ride the 2σ band all day).

**Win Rate:** ~60-65% | **R:R:** 1:1 to 1.5:1 | **Expectancy:** Positive in range environments

**Pros:**
- High win rate builds confidence
- Well-defined entries with VWAP bands
- Institutional logic (big players use VWAP as benchmark)

**Cons:**
- Gets destroyed on trend days — need to recognize and avoid
- Small R:R means commissions matter more
- Requires patience waiting for extended moves

---

### Strategy 3: Gap Fill Strategy

**Concept:** Fade the opening gap, expecting it to fill (price returns to previous day's close).

**Entry Rules:**
- Calculate the gap: Current open vs. previous close
- **Tradeable gaps:** 0.15% to 0.75% of index value (ES: ~8 to 40 points)
- **Gap up (short):** If gap is 0.15–0.75%, wait for the first 5-minute candle to close, then short if price is below the open
- **Gap down (long):** If gap is 0.15–0.75%, wait for the first 5-minute candle to close, then long if price is above the open
- **Filter:** Don't fade gaps that align with the prevailing trend on the daily chart
- **Filter:** Avoid fading gaps on FOMC/CPI/NFP days

**Exit Rules:**
- **Target:** Previous day's close (the "fill")
- **Stop:** Beyond the session open + 50% of the gap size
- **Time stop:** If gap hasn't filled by 11:00 AM, exit at current price

**Best Timeframe:** 5-minute chart

**Best Market Conditions:** Normal volatility, no major catalyst, gap is counter-trend

**Win Rate:** ~65-70% for small gaps (<0.3%), ~50% for medium gaps | **R:R:** ~1:1 to 1.5:1

**Pros:**
- High probability for small gaps — statistically backed
- Clear target (previous close)
- Works almost every day since gaps occur frequently

**Cons:**
- Large gaps (>0.75%) often don't fill and turn into gap-and-go — must filter
- Can get caught in a trend if you fade a gap in a strong trend
- Risk of early stop-out before the gap fills

---

### Strategy 4: London/Euro Session Breakout

**Concept:** Trade the breakout of the European session range as US liquidity enters the market.

**Entry Rules:**
- Mark the high and low of the 3:00 AM – 9:25 AM ET range (the "Euro range" or overnight range)
- **Long:** Buy when price breaks above the Euro high after 9:30 AM
- **Short:** Sell when price breaks below the Euro low after 9:30 AM
- **Confirmation:** Volume spike on the breakout (>1.5x average bar volume)
- **Filter:** Ignore if the Euro range is abnormally wide (>2x 20-day average overnight range)

**Exit Rules:**
- **Target 1:** 1x the Euro range height
- **Target 2:** Key daily level (PDH/PDL, round number)
- **Stop:** Midpoint of the Euro range
- **Time stop:** Close by 12:00 PM if target not reached

**Best Timeframe:** 5-minute to 15-minute chart

**Best Market Conditions:** Days where the Euro session was quiet (small range = coiled spring), followed by a US catalyst

**Win Rate:** ~50-55% | **R:R:** 2:1 to 3:1 | **Expectancy:** Positive due to large R:R

**Pros:**
- Captures the largest move of the day when it works
- Clear levels defined before you sit down
- Works across all four index futures

**Cons:**
- False breakouts are common — many days, the overnight range holds
- Requires pre-market preparation
- May need to be at screen by 9:25 AM

---

### Strategy 5: First Pullback After Trend Move

**Concept:** After a strong opening drive, buy the first pullback to VWAP or the 9 EMA on the 5-minute chart.

**Entry Rules:**
- Wait for a strong opening move: price moves 8+ points on ES in the first 15-30 minutes, with strong cumulative delta
- Wait for the first pullback (typically 38-50% retracement of the opening move)
- **Long:** Enter when price touches VWAP or 9 EMA on the 5-minute chart and shows a bullish reversal candle
- **Short:** Enter when price touches VWAP or 9 EMA after a strong down-opening and shows a bearish candle
- **Confirmation:** Cumulative delta should still favor the trend direction (buyers dip-buying, not aggressive selling)

**Exit Rules:**
- **Target 1:** Retest of the opening move extreme (the high of the first push)
- **Target 2:** Extension to 1.618x the opening move
- **Stop:** Below the pullback low (longs) or above pullback high (shorts) — typically 4-8 points on ES
- **Trail:** After Target 1, trail with a 3-bar low (5-min chart)

**Best Timeframe:** 5-minute chart

**Best Market Conditions:** Trending days, gap days, post-catalyst mornings

**Win Rate:** ~55-60% | **R:R:** 2:1 to 3:1 | **Expectancy:** One of the highest-expectancy setups

**Pros:**
- Aligns with the trend — "the trend is your friend"
- Clear entry (VWAP/EMA touch) with tight stop
- Large reward potential on trending days

**Cons:**
- The "first pullback" might not come — market trends without you
- On range days, the "pullback" becomes a reversal
- Requires real-time trend assessment

---

### Strategy 6: Midday Reversal

**Concept:** After the lunch chop subsides (11:30 AM–1:30 PM), look for a reversal that sets up the afternoon trend.

**Entry Rules:**
- Identify the lunch range: mark the high/low from 11:30 AM to 1:30 PM
- Wait for a breakout of the lunch range after 1:30 PM
- **Reversal long:** If morning trend was down and price breaks above the lunch high → long
- **Reversal short:** If morning trend was up and price breaks below the lunch low → short
- **Confirmation:** Volume increase on the breakout (>1.5x lunch-period average volume)
- **Filter:** Check if price is approaching a major daily level (PDH/PDL) which would support the reversal thesis

**Exit Rules:**
- **Target 1:** VWAP (if reversing toward it)
- **Target 2:** Morning session extreme (if reversing strongly)
- **Stop:** Inside the lunch range (middle of the chop)
- **Time stop:** If no follow-through by 2:30 PM, scratch the trade

**Best Timeframe:** 15-minute chart for structure, 5-minute for entries

**Best Market Conditions:** Range days that have been trending one direction all morning but are overextended

**Win Rate:** ~45-50% | **R:R:** 2:1 to 3:1 | **Expectancy:** Moderate — works best when combined with level confluence

**Pros:**
- Catches the afternoon trend which can be sustained
- Lower volume period means less noise/whipsaws than the open
- Contrarian edge — fading the morning move

**Cons:**
- Trend days will run you over — if morning trend continues, you're counter-trend
- Lunch chop can extend beyond 1:30 PM
- Fewer occurrences than opening strategies

---

### Strategy 7: Power Hour Momentum

**Concept:** Trade the strong directional move during 3:00–4:00 PM ET driven by MOC orders and institutional rebalancing.

**Entry Rules:**
- At 3:00 PM, assess the day's trend using VWAP slope and cumulative delta
- **Long:** If price is above VWAP and making afternoon highs, buy a pullback to the 9 EMA on the 5-minute chart after 3:00 PM
- **Short:** If price is below VWAP and making afternoon lows, sell a pullback to the 9 EMA
- **Confirmation:** NYSE MOC imbalance data (published ~3:50 PM) can confirm direction
- **Breakout entry:** If price breaks the day's high or low after 3:00 PM, enter with the break

**Exit Rules:**
- **Target:** Hold until 3:55–4:00 PM (ride the MOC flow)
- **Stop:** 4-6 points on ES (tight, since the move should be fast)
- **Trail:** Use a 2-bar trailing stop on the 5-minute chart after the first 10 minutes

**Best Timeframe:** 5-minute chart, 1-minute for scalp entries

**Best Market Conditions:** Triple/quad witching days, month-end/quarter-end rebalancing, strong trend days

**Win Rate:** ~55-60% | **R:R:** 1.5:1 to 2:1

**Pros:**
- Structural edge from MOC order flow
- Moves can be explosive and sustained
- Limited time exposure (1 hour max)

**Cons:**
- Moves can reverse sharply at 3:50 PM when MOC imbalances are published
- End-of-day volatility can cause slippage
- Only one opportunity per day

---

### Strategy 8: Previous Day Level Bounce/Break

**Concept:** Use the previous day's high (PDH) and low (PDL) as key support/resistance for trade entries.

**Entry Rules:**
- Mark PDH, PDL, and PDC (previous day close) before the open
- **Bounce long:** If price approaches PDL and shows a bullish rejection (long wick, volume spike on bid), go long
- **Bounce short:** If price approaches PDH and shows a bearish rejection, go short
- **Break long:** If price breaks above PDH with strong volume and closes above, go long on the retest of PDH as support
- **Break short:** If price breaks below PDL with strong volume and closes below, go short on the retest of PDL as resistance
- **Filter:** Align with the daily trend (prefer bouncing off PDL in uptrends, PDH in downtrends)

**Exit Rules:**
- **Bounce target:** VWAP or POC (center of value)
- **Break target:** Next major level (e.g., 2-day high/low, weekly pivot)
- **Stop:** 2-4 points beyond the level (e.g., long at PDL with stop 3 points below PDL)
- **Trail:** After 1:1 R:R achieved, move stop to breakeven

**Best Timeframe:** 5-minute to 15-minute chart

**Best Market Conditions:** All market conditions — PDH/PDL are universally respected levels

**Win Rate:** ~55-60% | **R:R:** 1.5:1 to 2:1

**Pros:**
- Universally applicable — works every day since PDH/PDL always exist
- Clear, objective levels — no subjectivity
- High confluence when combined with VWAP or value area levels

**Cons:**
- Some days, PDH/PDL are far from current price and never tested
- Breakout trades at PDH/PDL can be false breakouts
- Requires patience waiting for price to reach these levels

---

## Risk Management Framework for Day Trading Futures

### The 6 Rules

1. **Risk no more than 1-2% of account per trade** — On a $5,000 account with MES, that's $50-$100 max loss per trade
2. **Set a daily loss limit of 2-4%** — Stop trading after 2-3 losing trades or $100-$200 loss on a $5,000 account
3. **Use a maximum of 3-5 trades per day** — Quality over quantity
4. **Always use a stop-loss** — Hard stop in the platform, not mental stops
5. **Scale position size with account growth** — Increase MES contracts as account grows, not before
6. **No trading during major news unless you have a news strategy** — FOMC, CPI, NFP can move ES 30+ points in seconds

### Recommended Starting Setup

For a beginner with $5,000 trading MES:
- **Contracts:** 1-2 MES ($5/point each)
- **Max risk per trade:** $50 (10 points on 1 MES)
- **Daily max loss:** $100 (2% of account)
- **Max trades per day:** 4
- **Strategies:** Start with ORB and VWAP Mean Reversion — clear rules, well-studied

### Commission Impact

At $0.62 per side per contract ($1.24 round-trip), commissions significantly impact MES scalping:
- 10 round-trips/day × $1.24 = $12.40/day in commissions
- That's $62/week, $248/month — 5% of a $5,000 account per month
- **Lesson:** Fewer, higher-quality trades beat over-trading every time

---

## Putting It All Together: A Day Trader's Daily Routine

### Pre-Market (8:00–9:25 AM ET)
1. Check overnight news, economic calendar, and any pre-market movers
2. Mark key levels: ONH, ONL, PDH, PDL, PDC, VWAP, weekly pivots
3. Identify the gap: size and direction vs. PDC
4. Form a daily bias (trend up, trend down, or range)
5. Set alerts at key levels in your platform

### Trading Session (9:30 AM–12:00 PM ET)
1. Watch the first 2-3 minutes for the opening drive direction
2. If ORB setup: mark the 15-min range at 9:45 and wait for breakout
3. If gap fill setup: assess gap size and enter if criteria met
4. If first pullback: wait for the initial trend move, then buy/sell the pullback to VWAP/EMA
5. Take profits at targets, move stops to breakeven, manage runners

### Midday (12:00–2:00 PM ET)
- Review morning trades in a journal
- Reduce position size or stop trading during lunch chop
- Watch for midday reversal setup after 1:30 PM

### Afternoon (2:00–4:00 PM ET)
- Watch for the 2:00 PM reversal zone
- Power hour setup after 3:00 PM
- Close all positions by 3:55 PM (unless holding for settlement)

### Post-Market
- Journal every trade: entry, exit, P&L, what you did right/wrong
- Review daily stats: win rate, average R, total P&L, number of trades
- Update your trading plan for tomorrow

---

## Recommended Tools and Platforms

- **Charting:** TradingView (free), Sierra Chart (professional), NinjaTrader
- **Order Flow:** Bookmap, Sierra Chart, Jigsaw
- **Execution:** NinjaTrader, Tradovate, AMP Futures
- **Data:** CME DataMine (official), Kinetick, dxFeed
- **Backtesting:** Python (pandas, backtrader), Sierra Chart replay, NinjaTrader Market Replay
- **Journaling:** Tradervue, Edgewonk, simple spreadsheet

---

## Suggested Reading & Sources

- *Day Trading with Short-Term Price Patterns and Opening Range Breakout* — Toby Crabel (1990)
- *Mind Over Markets* — James Dalton (Market Profile)
- *Order Flow Trading for Fun and Profit* — Daemon Goldsmith
- *Trading in the Zone* — Mark Douglas (psychology)
- CME Group Education Center: [cmegroup.com/education](https://www.cmegroup.com/education.html)
- Quantifiable Edges blog (gap fill statistics)
- Futures Truth Magazine (strategy performance rankings)

---

*Disclaimer: This guide is for educational purposes only. Futures trading involves substantial risk of loss and is not suitable for all investors. Past performance is not indicative of future results. Always paper trade strategies before risking real capital.*
