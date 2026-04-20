# 🚀 DigitalOcean App Platform Setup Guide

## Step 1: Create Your First App

After clicking "App Platform", you'll see options to connect your GitHub repo. For now, let's create the app structure first.

## Step 2: Initial App Configuration

When creating the app, use these settings:

### App Name
`earnings-drift-scanner`

### Resources to Add:
1. **Web Service** (FastAPI backend)
   - Name: `api`
   - Run Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
   - HTTP Port: 8000
   - Instance: Basic ($5/mo)

2. **Static Site** (Next.js frontend)
   - Name: `web`
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Instance: Starter ($3/mo)

3. **Database** (PostgreSQL)
   - Name: `db`
   - Engine: PostgreSQL
   - Version: 15
   - Plan: Basic ($15/mo)

4. **Redis** (For caching)
   - Name: `cache`
   - Plan: Basic ($10/mo)

### Total Initial Cost: ~$33/month

## Step 3: Environment Variables

Add these in the App settings:

```
DATABASE_URL=${db.DATABASE_URL}
REDIS_URL=${cache.REDIS_URL}
STRIPE_SECRET_KEY=sk_test_... (we'll add later)
CLAUDE_API_KEY=... (we'll add later)
ENVIRONMENT=production
SECRET_KEY=<generate-a-random-string>
```

## Step 4: Domain Setup

1. Add custom domain: `driftedge.io` (or your choice)
2. DigitalOcean will provide DNS records to add
3. SSL certificate auto-configured

## What Happens Next

Once configured, DigitalOcean will:
- Provision all resources
- Set up networking between components
- Configure SSL certificates
- Create deployment pipeline
- Set up monitoring

You'll get:
- Deployment URL: `earnings-drift-scanner-xxxxx.ondigitalocean.app`
- GitHub integration for auto-deploy
- Built-in logs and monitoring

## GitHub Repository Structure

Create this structure in your repo:

```
earnings-drift-scanner/
├── api/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── routes/
│   │   └── services/
│   ├── requirements.txt
│   └── Dockerfile
├── web/                    # Next.js frontend
│   ├── pages/
│   ├── components/
│   ├── package.json
│   └── Dockerfile
├── .github/
│   └── workflows/
│       └── deploy.yml     # CI/CD pipeline
└── README.md
```

## Quick Start Commands

```bash
# Create GitHub repo first
git init earnings-drift-scanner
cd earnings-drift-scanner

# Create basic structure
mkdir -p api/app web/pages .github/workflows

# Initialize projects
cd api && pip install fastapi uvicorn
cd ../web && npx create-next-app@latest . --typescript --tailwind

# Connect to DigitalOcean
git remote add origin https://github.com/YOUR_USERNAME/earnings-drift-scanner
git add .
git commit -m "Initial commit"
git push -u origin main
```

## Next Steps After Setup

1. ✓ App Platform configured
2. → Create GitHub repository  
3. → Build MVP locally
4. → Connect GitHub to DigitalOcean
5. → Deploy first version
6. → Add payment processing
7. → Launch to beta users

---

The beautiful part: Once this is set up, every `git push` automatically deploys your changes live. No SSH, no server management, just code and ship! 🚀