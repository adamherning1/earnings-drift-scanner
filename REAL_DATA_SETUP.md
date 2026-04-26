# Get REAL Stock Prices - Free Setup

## Problem
- Yahoo Finance is unreliable
- Mock prices destroy credibility
- Need real data for paying customers

## Solution: Alpha Vantage (FREE)

### 1. Get Free API Key (2 minutes)
1. Go to: https://www.alphavantage.co/support/#api-key
2. Enter your email
3. Get instant API key
4. Free tier: 25 requests/day (plenty with caching!)

### 2. Add to Render Environment
1. Go to Render Dashboard
2. Environment → Add Environment Variable
3. Key: `ALPHA_VANTAGE_KEY`
4. Value: `your-api-key-here`

### 3. Update Start Command
```
uvicorn main_alphaadvantage:app --host 0.0.0.0 --port $PORT
```

### 4. Deploy
- Render will auto-deploy
- Real prices in 2 minutes!

## What You Get
- REAL stock prices
- Updates every 5 minutes
- Professional credibility
- Happy paying customers
- $0/month cost

## Backup Options (if needed)
1. **Finnhub.io** - 60 calls/minute free
2. **Twelve Data** - 800 calls/day free
3. **IEX Cloud** - 50k calls/month free

## The Double Dollar Sign Fix
The frontend is adding $ and the API is also adding $. 
Quick fix in member-portal:
- Remove $ from API responses
- OR remove $ from frontend display

This gives you REAL data that updates every 5 minutes!