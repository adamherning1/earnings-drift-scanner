# Deploy Backend Update for Real-Time Prices

## Quick Steps to Enable Real Prices

### 1. Get Your Massive (Polygon) API Key
- Log in to: https://polygon.io/dashboard
- Go to API Keys section
- Copy your API key (starts with `pk_` or similar)

### 2. Update Render Environment
1. Go to: https://dashboard.render.com
2. Find your service: **post-earnings-scanner-v2**
3. Click on it → Go to **Environment** tab
4. Click **Add Environment Variable**
5. Add:
   - Key: `MASSIVE_API_KEY`
   - Value: `your_actual_api_key_here`
6. Click **Save Changes**

### 3. Redeploy Backend
Option A - Auto Deploy:
- Push the updated `main_massive_quotes.py` to GitHub
- Render will auto-deploy if connected

Option B - Manual Deploy:
1. In Render dashboard, click **Manual Deploy**
2. Select **Deploy latest commit**

### 4. Verify It's Working
- Visit: https://post-earnings-scanner-v2.onrender.com/health
- Should show:
  ```json
  {
    "massive_api_configured": true,
    "api_working": true,
    "test_price": 182.45  // Real AAPL price
  }
  ```

### 5. All Pages Will Now Show Real Prices
- Dashboard: Live stock prices
- Analysis pages: Current market data
- Paper trades: Realistic entry/exit prices

## Troubleshooting

If prices still show as fallback:
1. Check the API key is correct
2. Ensure you have an active Massive/Polygon subscription
3. Check Render logs for any API errors
4. Verify the environment variable is set correctly

## API Limits
- Free tier: 5 API calls/minute
- Basic ($29/mo): 100,000 calls/month
- Professional ($199/mo): Unlimited calls

Your $199/month subscription should handle all traffic easily!