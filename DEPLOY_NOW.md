# 🚀 Deploy in 5 Minutes

## What We Have Ready

✅ **Hybrid scanner** using Yahoo Finance + manual calendar
✅ **Playbook generator** creating 3 strategies per stock  
✅ **Paper trader** for transparency
✅ **API endpoints** all working
✅ **No API costs** during development

## Quick Deploy Steps

### 1. Update requirements.txt
```bash
fastapi==0.111.0
uvicorn==0.30.1
pydantic==2.7.1
yfinance==0.2.38
pandas==2.2.2
numpy==1.26.4
python-dotenv==1.0.1
```

### 2. Update render.yaml
```yaml
services:
  - type: web
    name: earnings-scanner-v2
    runtime: python
    buildCommand: pip install -r api/requirements.txt
    startCommand: cd api && uvicorn main_v2:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABENTO_API_KEY
        value: db-4pAagaTp8Q3GmwYLxYAny8jvvKPLu
```

### 3. Push to GitHub
```bash
git add .
git commit -m "V2 with Yahoo Finance + Databento ready"
git push
```

### 4. Deploy on Render
- Go to Render dashboard
- Update start command to use main_v2.py
- Add DATABENTO_API_KEY env var
- Deploy!

## API Endpoints Ready

- `/` - Service info
- `/api/opportunities` - Current scanner results
- `/api/upcoming-earnings?days=7` - Next earnings
- `/api/recent-surprises?days=5` - Recent surprises  
- `/api/sue/{symbol}` - Calculate SUE score
- `/api/playbook` - Generate trading playbook
- `/api/paper-trades` - View paper trading

## What's Working Now

1. **Manual earnings calendar** - 20 stocks we track
2. **Yahoo Finance** - Real-time prices, volume, basic data
3. **SUE calculation** - Using Yahoo earnings history
4. **Playbook generation** - 3 strategies per stock

## Production Upgrades (Later)

- Add Databento for options chains
- Expand to 100+ stocks
- Real-time alerts
- Automated paper trading

Ready to deploy? This gets us live TODAY! 🚀