# Setting up Finnhub for Accurate Earnings Data

## 1. Get your FREE API Key

1. Go to https://finnhub.io
2. Click "Get free API key"
3. Sign up with your email
4. Copy your API key

## 2. Add to Render Environment

1. Go to your Render dashboard
2. Select your service
3. Go to Environment
4. Add new variable:
   - Key: `FINNHUB_API_KEY`
   - Value: `your_api_key_here`
5. Save changes

## 3. What you get:

- ✅ **60 API calls per minute** (no monthly limit!)
- ✅ **Real earnings data** - actual EPS, estimates, surprises
- ✅ **Earnings calendar** - upcoming earnings dates
- ✅ **Company fundamentals** - additional financial data
- ✅ **100% FREE** - no credit card required

## 4. Features:

- Historical earnings for any ticker
- Earnings surprises calculated automatically
- Before/during/after market indicators
- Revenue data (if available)
- Reliable data used by production apps

## 5. Example Response:

```json
{
  "symbol": "AAPL",
  "actual": 1.53,
  "estimate": 1.51,
  "period": "2024-03-31",
  "surprise": 0.02,
  "surprisePercent": 1.32
}
```

## Alternative: API Ninjas

If you prefer API Ninjas instead:

1. Go to https://api-ninjas.com
2. Sign up for free
3. Get your API key
4. Add to Render: `API_NINJAS_KEY = your_key`
5. 10,000 calls/month free

Both are excellent choices for accurate earnings data!