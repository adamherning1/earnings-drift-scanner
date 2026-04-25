# Databento Integration for Earnings Scanner

## What is Databento?

Databento is a modern market data provider that offers:
- **Historical & real-time data** - Stocks, options, futures
- **Corporate actions** - Including earnings announcements
- **High-quality data** - Direct from exchanges
- **Developer-friendly** - Great Python SDK

## Key Advantages Over FMP/Yahoo

1. **Professional grade** - Exchange-direct data
2. **Options data included** - Critical for our playbooks
3. **Earnings events** - Accurate announcement times
4. **Better pricing** - Pay only for what you use

## What We Need

For our earnings scanner:
- Corporate actions feed (earnings dates)
- Options chains (for playbook generation)
- Historical price data (for backtesting)
- Real-time quotes (for entry signals)

## Databento API Example

```python
import databento as db

client = db.Historical('YOUR_API_KEY')

# Get earnings announcements
earnings = client.timeseries.get_range(
    dataset='XNYS.TRADES',  # NYSE data
    symbols=['AAPL', 'MSFT'],
    schema='events',
    event_type='earnings',
    start='2026-04-01',
    end='2026-04-30'
)

# Get options chain
options = client.timeseries.get_range(
    dataset='OPRA',
    symbols=['AAPL'],
    schema='ohlcv-1d',
    start='2026-04-24'
)
```

## Pricing

- **Pay-as-you-go** - No monthly minimum
- **Free tier** - $25 credit to start
- **Production** - ~$100-200/mo for our needs

## Next Steps

1. Do you already have a Databento API key?
2. If yes, I'll update our scanner to use Databento
3. If no, should we sign up for the free tier?

This is actually MUCH better than FMP - professional data at reasonable cost!