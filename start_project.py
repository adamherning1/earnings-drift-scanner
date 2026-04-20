#!/usr/bin/env python3
"""
Earnings Drift Scanner - Project Setup Script
Run this to create the initial project structure
"""

import os
import json

def create_project_structure():
    """Create all necessary directories and files"""
    
    # Directory structure
    dirs = [
        "backend",
        "backend/api",
        "backend/core",
        "backend/models",
        "backend/services",
        "frontend",
        "frontend/components",
        "frontend/pages",
        "frontend/styles",
        "database",
        "docs",
        "tests"
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✓ Created {dir_path}/")
    
    # Create initial files
    files = {
        "backend/requirements.txt": """fastapi==0.104.1
uvicorn==0.24.0
ib_insync==0.9.86
pandas==2.1.3
numpy==1.25.2
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
celery==5.3.4
stripe==7.8.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
anthropic==0.8.1
yfinance==0.2.33
scipy==1.11.4
python-dotenv==1.0.0
""",
        
        "backend/.env.example": """# Database
DATABASE_URL=postgresql://user:password@localhost/drift_scanner

# IBKR
IB_HOST=127.0.0.1
IB_PORT=7497
IB_CLIENT_ID=1

# Claude AI
ANTHROPIC_API_KEY=your_api_key_here

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# JWT
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Redis
REDIS_URL=redis://localhost:6379
""",
        
        "backend/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Earnings Drift Scanner API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Earnings Drift Scanner API v1.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
""",
        
        "backend/core/config.py": """from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str
    
    # IBKR
    ib_host: str = "127.0.0.1"
    ib_port: int = 7497
    ib_client_id: int = 1
    
    # Claude AI
    anthropic_api_key: str
    
    # Stripe
    stripe_secret_key: str
    stripe_webhook_secret: str
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 43200  # 30 days
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"

settings = Settings()
""",
        
        "frontend/package.json": """{
  "name": "earnings-drift-scanner",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.0.4",
    "react": "^18",
    "react-dom": "^18",
    "@tanstack/react-query": "^5.17.0",
    "axios": "^1.6.5",
    "chart.js": "^4.4.1",
    "react-chartjs-2": "^5.2.0",
    "@stripe/stripe-js": "^2.3.0",
    "@headlessui/react": "^1.7.17",
    "@heroicons/react": "^2.1.1",
    "date-fns": "^3.2.0"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "autoprefixer": "^10.0.1",
    "postcss": "^8",
    "tailwindcss": "^3.3.0",
    "typescript": "^5"
  }
}
""",
        
        "README.md": """# Earnings Drift Scanner

AI-powered tool that analyzes historical earnings drift patterns for options traders.

## Quick Start

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Database Setup
```bash
cd database
psql -U postgres -c "CREATE DATABASE drift_scanner;"
psql -U postgres -d drift_scanner -f schema.sql
```

## Architecture

- **Backend**: FastAPI + PostgreSQL
- **Frontend**: Next.js + Tailwind CSS
- **AI**: Claude Opus for playbook generation
- **Data**: IBKR for historical prices
- **Payments**: Stripe subscriptions

## Development Timeline

See `WEEK_1_BUILD_PLAN.md` for detailed daily tasks.

## Business Plan

See `BUSINESS_PLAN.md` for revenue projections and go-to-market strategy.
"""
    }
    
    for filepath, content in files.items():
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✓ Created {filepath}")
    
    print("\n✅ Project structure created successfully!")
    print("\nNext steps:")
    print("1. cd earnings_drift_scanner")
    print("2. cd backend && pip install -r requirements.txt")
    print("3. Edit backend/.env with your credentials")
    print("4. python main.py")

if __name__ == "__main__":
    create_project_structure()