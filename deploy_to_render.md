# Deploy to Render - Quick Steps

## 1. Push to GitHub
```bash
cd earnings_drift_scanner
git add .
git commit -m "Post-earnings drift scanner MVP"
git push origin main
```

## 2. Create render.yaml
Already exists in the repo!

## 3. Deploy on Render
1. Go to https://render.com
2. New > Blueprint
3. Connect GitHub repo
4. Add environment variable: FMP_API_KEY
5. Deploy!

## 4. API Endpoints

Once deployed, your API will be at:
`https://your-app.onrender.com`

Test with:
- `/api/opportunities` - Get current signals
- `/api/paper-performance` - See paper trading results
- `/api/analysis/AAPL` - Analyze specific stock

## 5. Start Scanner

POST to `/api/start-scanner` to begin continuous scanning.

That's it! The API will be live in ~5 minutes.