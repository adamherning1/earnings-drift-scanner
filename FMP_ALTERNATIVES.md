# FMP API Issue & Alternatives

## The Problem
FMP has deprecated their v3 API endpoints for new users (as of August 31, 2025). Your new account can't access the endpoints we need for:
- Earnings calendar
- Stock quotes
- Market data
- Company financials

## Quick Alternatives

### 1. **Alpha Vantage** (Immediate Option)
- **Free tier**: 25 requests/day, 500/month
- **Pros**: Has earnings data, free to start
- **Cons**: Very limited for production
- **Get key**: https://www.alphavantage.co/support/#api-key

### 2. **Polygon.io** (Best for Options Data)
- **Free tier**: Very limited
- **Starter**: $29/month - includes options data
- **Pros**: Great options data, reliable
- **Get key**: https://polygon.io/

### 3. **Yahoo Finance** (Free Workaround)
- **Cost**: FREE
- **Method**: Use yfinance Python library
- **Pros**: No API key needed, unlimited calls
- **Cons**: Less reliable, no official support
- **Code**: `pip install yfinance`

### 4. **IEX Cloud** (Good Middle Ground)
- **Free tier**: 50,000 messages/month
- **Launch**: $19/month
- **Pros**: Reliable, has earnings data
- **Get key**: https://iexcloud.io/

## Immediate Solution: Yahoo Finance

Since we need to move fast, let's use Yahoo Finance for now:

```python
import yfinance as yf
from datetime import datetime, timedelta

# Get earnings calendar
earnings = yf.get_earnings_dates('AAPL')
print(earnings.head())

# Get stock data
stock = yf.Ticker('AAPL')
info = stock.info
print(f"Market Cap: ${info['marketCap']:,}")
print(f"Price: ${info['regularMarketPrice']}")

# Get options data
options = stock.option_chain(stock.options[0])
print(f"Calls: {len(options.calls)}")
print(f"Puts: {len(options.puts)}")
```

## What This Means

1. **For Testing**: Use Yahoo Finance (free, no key needed)
2. **For Production**: Get Polygon.io when ready ($29/mo)
3. **Timeline**: Not delayed - we can build with Yahoo today

## Next Steps

1. Install yfinance: `pip install yfinance`
2. Update our scanner to use yfinance
3. When ready to launch, upgrade to Polygon for reliability

This actually might be better - no API limits during development!