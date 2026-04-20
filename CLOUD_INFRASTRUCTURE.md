# ☁️ Cloud Infrastructure Plan - Earnings Drift Scanner

## Why Cloud is Non-Negotiable

1. **24/7 Availability** - Customers trade globally, need access anytime
2. **Reliability** - 99.9% uptime SLA vs your home internet
3. **Scalability** - Handle 10 or 10,000 users without infrastructure changes
4. **Professional** - Cloud hosting = legitimate business
5. **Data Processing** - Continuous earnings data updates run in background

## Recommended Architecture

### Option 1: DigitalOcean (Recommended for Start)
**Cost: $40-60/month initially**

```
┌─────────────────┐
│   Cloudflare    │ ← DDoS Protection & CDN
│   (Free tier)   │
└────────┬────────┘
         │
┌────────┴────────┐
│  DigitalOcean   │
│   App Platform  │ ← Auto-scaling, managed
├─────────────────┤
│  • FastAPI App  │
│  • Next.js App  │
│  • PostgreSQL   │
│  • Redis Cache  │
└─────────────────┘
         │
┌────────┴────────┐
│  Background     │
│  Workers        │ ← Celery for data updates
└─────────────────┘
```

**Pros:**
- Simple deployment via GitHub
- Automatic SSL certificates
- Built-in monitoring
- One-click scaling
- $200 free credits for new accounts

### Option 2: AWS (For Scale)
**Cost: $50-100/month with proper optimization**

```
┌─────────────────┐
│   CloudFront    │ ← Global CDN
└────────┬────────┘
         │
┌────────┴────────┐
│   Route 53      │ ← DNS Management
└────────┬────────┘
         │
┌────────┴────────┐
│ Elastic Beanstalk│ ← Managed application
├─────────────────┤
│  • EC2 Instance │
│  • RDS PostgreSQL│
│  • ElastiCache  │
│  • S3 Storage   │
└─────────────────┘
```

## Initial Setup Plan (DigitalOcean)

### Step 1: Create Accounts
- [ ] DigitalOcean account (use $200 credit)
- [ ] Cloudflare account (free)
- [ ] Domain registration ($12/year)
- [ ] Stripe account for payments

### Step 2: Set Up Infrastructure
```bash
# 1. Create DigitalOcean App
doctl apps create --spec app.yaml

# 2. Configure environment variables
DATABASE_URL=postgresql://...
STRIPE_SECRET_KEY=sk_live_...
CLAUDE_API_KEY=...

# 3. Deploy from GitHub
git push origin main  # Auto-deploys
```

### Step 3: Database Setup
```yaml
# app.yaml
databases:
  - engine: PG
    name: earnings-db
    num_nodes: 1
    size: basic-xxs  # $15/month
    version: "15"
```

### Step 4: Background Workers
```python
# celery_worker.py
from celery import Celery
app = Celery('tasks', broker='redis://...')

@app.task
def update_earnings_data():
    """Runs every hour in the cloud"""
    fetch_new_earnings()
    calculate_drift_patterns()
    
@app.task
def generate_morning_alerts():
    """Runs at 8:30 AM ET daily"""
    send_drift_alerts()
```

## Data Pipeline Architecture

```
IBKR Gateway (Your PC)        Cloud Infrastructure
     │                              │
     ├─[Secure Tunnel]─────────────→├─ Data Collector Service
     │                              │  (Fetches once/hour)
     │                              ↓
     │                         PostgreSQL
     │                              ↓
     │                         API Service
     │                              ↓
     │                         Web Frontend
     │                              │
     └──────────────────────────────┘
```

### Critical: IBKR Data Access
Since IBKR requires Gateway connection, we have 3 options:

1. **Cloud Gateway** ($50/mo VPS with IB Gateway)
2. **Scheduled Sync** (Your PC pushes data hourly)
3. **Hybrid** (Real-time from your PC, historical from cloud)

## Security Essentials

1. **SSL Everywhere** - Cloudflare provides free SSL
2. **API Rate Limiting** - Prevent abuse
3. **Database Encryption** - At rest and in transit
4. **Secrets Management** - Never commit API keys
5. **Regular Backups** - Daily automated backups

## Monitoring & Alerts

```python
# monitoring.py
def health_check():
    """Endpoint hit by UptimeRobot every 5 min"""
    return {
        "status": "healthy",
        "db_connected": check_db(),
        "redis_connected": check_redis(),
        "last_data_update": get_last_update()
    }
```

## Cost Breakdown

### Month 1-3 (Beta)
- DigitalOcean App Platform: $20/mo
- Database: $15/mo
- Domain: $1/mo
- **Total: $36/month**

### Month 4-12 (Growth)
- Scaled infrastructure: $60/mo
- CDN/Bandwidth: $20/mo
- Monitoring tools: $10/mo
- **Total: $90/month**

## Deployment Checklist

- [ ] Register domain (driftedge.io or similar)
- [ ] Set up DigitalOcean account
- [ ] Configure GitHub → DigitalOcean auto-deploy
- [ ] Set up PostgreSQL database
- [ ] Configure Redis for caching
- [ ] Install SSL certificate via Cloudflare
- [ ] Set up monitoring (UptimeRobot)
- [ ] Configure automated backups
- [ ] Test payment processing (Stripe)
- [ ] Load test with 100 concurrent users

## Launch Commands

```bash
# Local development
python -m uvicorn app.main:app --reload

# Deploy to cloud (from local machine)
git push origin main  # Triggers auto-deploy

# Check deployment status
doctl apps list
doctl apps logs $APP_ID --follow

# Scale up when needed
doctl apps update $APP_ID --spec app-scaled.yaml
```

## Why Start with DigitalOcean?

1. **Simplicity** - Get running in 1 hour vs 1 week with AWS
2. **Cost** - Predictable pricing, no surprises
3. **Support** - Excellent documentation and community
4. **Migration** - Easy to move to AWS later if needed
5. **Free Credits** - $200 covers 3-5 months of hosting

---

**Bottom Line:** Cloud hosting turns this from a "project" into a real business. Customers need reliability, and you need sleep. The $40/month pays for itself with just ONE customer.