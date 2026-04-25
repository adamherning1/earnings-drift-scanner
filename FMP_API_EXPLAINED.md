# What is FMP API?

## Financial Modeling Prep (FMP)

**FMP** is a financial data provider that gives us real-time and historical market data. Think of it as our "Bloomberg Terminal" but much cheaper!

### What We Use It For:

1. **Earnings Data**
   - When companies report earnings
   - Actual EPS vs Expected EPS  
   - Revenue numbers
   - Historical earnings (last 12 quarters)

2. **Stock Screening**
   - Find stocks by market cap
   - Filter by volume
   - Check which stocks have options

3. **Real-time Quotes**
   - Current stock prices
   - Market cap
   - Trading volume

### Example API Calls:

```python
# Get Apple's latest earnings
https://financialmodelingprep.com/api/v3/earning_calendar?symbol=AAPL

# Returns:
{
  "symbol": "AAPL",
  "date": "2026-04-30",
  "eps": 1.52,           # Actual earnings per share
  "epsEstimated": 1.43,  # What analysts expected
  "revenue": 94.8B,
  "revenueEstimated": 92.5B
}

# Get all stocks between $500M-$5B market cap
https://financialmodelingprep.com/api/v3/stock-screener?marketCapMoreThan=500000000&marketCapLowerThan=5000000000
```

### Pricing:

- **Starter**: $19/month (limited calls)
- **Standard**: $49/month (250K calls)
- **Professional**: $149/month (unlimited) ← We need this

### Why FMP Over Others:

1. **Polygon**: Great for options but $199/mo just for options
2. **Alpha Vantage**: Free tier too limited, paid is expensive
3. **Yahoo Finance**: Free but unreliable, gets rate limited
4. **IEX Cloud**: Good but missing historical earnings

### How We Use It:

```python
# Our scanner runs every 15 minutes:
1. Check FMP for new earnings → "Who reported today?"
2. Calculate surprise → "Did they beat or miss?"  
3. Get stock details → "What's the market cap?"
4. Generate signals → "Is this tradeable?"
5. Send alerts → "Tell our subscribers!"
```

### Getting Your API Key:

1. Go to https://site.financialmodelingprep.com
2. Sign up (free to start)
3. Get your API key from dashboard
4. We'll upgrade to Professional plan when we launch

### Our Architecture:

```
FMP API (Data Source)
    ↓
Our Scanner (Cloud)
    ↓
Signal Generation
    ↓
Subscriber Alerts
```

**Bottom Line**: FMP gives us institutional-quality data for $149/month instead of $2,000/month for Bloomberg. It's the backbone of our earnings detection system!