# 🎯 Render.com Quick Start Guide

## 5-Minute Deployment for Your Earnings Scanner

### Step 1: Sign Up
1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with your GitHub account (easiest)

### Step 2: Create New Web Service
1. Dashboard → Click "New +" → "Web Service"
2. Connect your GitHub account if not already
3. Select `adamherning1/earnings-drift-scanner` repository
4. Click "Connect"

### Step 3: Configure Your Service

Fill in these exact settings:

**Name**: `earnings-scanner-api`

**Root Directory**: `api`

**Environment**: `Python 3`

**Build Command**: 
```
pip install -r requirements.txt
```

**Start Command**:
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Instance Type**: Free

### Step 4: Environment Variables

Click "Advanced" and add:

```
PYTHON_VERSION=3.11
DATABASE_URL=sqlite:///./earnings.db
SECRET_KEY=your-secret-key-here
```

### Step 5: Deploy!

Click "Create Web Service"

Render will:
- Pull your code from GitHub
- Install dependencies
- Start your FastAPI app
- Give you a live URL!

### Your API will be live at:
```
https://earnings-scanner-api.onrender.com
```

### Test it:
```
https://earnings-scanner-api.onrender.com/docs
```

## Troubleshooting

If deployment fails:

1. **Check logs** - Render shows detailed build logs
2. **Python version** - Make sure PYTHON_VERSION=3.11 is set
3. **Dependencies** - Scipy is removed, right?
4. **Path issues** - Root directory must be `api`

## After Success

1. **Save your URL** - You'll need it for the frontend
2. **Test endpoints** in /docs
3. **Add custom domain** (optional)
4. **Set up Stripe** environment variables when ready

---

This should work first try! Render handles Python apps much better than DigitalOcean.