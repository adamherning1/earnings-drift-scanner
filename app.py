"""
Simple standalone FastAPI app for Render
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(
    title="Earnings Scanner API",
    description="Post-earnings drift scanner - simplified version",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "service": "Earnings Scanner API",
        "status": "operational",
        "version": "1.1.0",
        "deployed": datetime.now().isoformat(),
        "endpoints": [
            "/api/health",
            "/api/upcoming", 
            "/api/test"
        ]
    }

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/test")
async def test():
    return {
        "message": "API is working!",
        "data_source": "Yahoo Finance (coming soon)",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/upcoming")
async def upcoming():
    """Manually tracked earnings for now"""
    return {
        "earnings": [
            {"symbol": "SNAP", "date": "2026-04-28", "time": "AMC", "company": "Snap Inc"},
            {"symbol": "PINS", "date": "2026-04-29", "time": "AMC", "company": "Pinterest"},
            {"symbol": "DKNG", "date": "2026-04-30", "time": "BMO", "company": "DraftKings"},
            {"symbol": "ROKU", "date": "2026-04-30", "time": "AMC", "company": "Roku"},
            {"symbol": "ETSY", "date": "2026-05-01", "time": "AMC", "company": "Etsy"}
        ],
        "total": 5,
        "source": "manual_calendar"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)