# 📊 Earnings Drift Scanner

AI-powered tool for analyzing pre-earnings drift patterns in stocks.

## 🚀 Quick Start

### Backend (FastAPI)
```bash
cd api
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API will be available at: http://localhost:8000
API docs: http://localhost:8000/docs

### Frontend (Next.js)
```bash
cd web
npm install
npm run dev
```

Frontend will be available at: http://localhost:3000

## 📁 Project Structure

```
earnings_drift_scanner/
├── api/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py        # Application entry
│   │   ├── models/        # SQLAlchemy models
│   │   ├── routes/        # API endpoints
│   │   ├── services/      # Business logic
│   │   └── schemas/       # Pydantic models
│   ├── requirements.txt
│   └── Dockerfile
├── web/                    # Next.js frontend
│   ├── pages/             # Next.js pages
│   ├── components/        # React components
│   └── package.json
└── .github/workflows/     # CI/CD pipelines
```

## 🌟 Features

- **Historical Analysis**: View 12 quarters of earnings drift patterns
- **AI Playbooks**: Claude-generated trading strategies
- **Real-time Alerts**: Get notified of drift opportunities
- **Statistical Insights**: Advanced pattern recognition

## 🔐 Environment Variables

Create `.env` file in the `api` directory:

```env
DATABASE_URL=postgresql://user:pass@localhost/earnings_db
REDIS_URL=redis://localhost:6379
STRIPE_SECRET_KEY=sk_test_...
CLAUDE_API_KEY=...
SECRET_KEY=your-secret-key-here
```

## 📦 Deployment

This project is configured for DigitalOcean App Platform:

1. Push to GitHub
2. Connect repo to DigitalOcean
3. Deploy automatically

## 🛠️ Tech Stack

- **Backend**: FastAPI, PostgreSQL, Redis, Celery
- **Frontend**: Next.js, React, Tailwind CSS
- **AI**: Claude API for playbook generation
- **Data**: Yahoo Finance, yfinance
- **Payments**: Stripe

## 📄 License

Copyright 2026 - All rights reserved