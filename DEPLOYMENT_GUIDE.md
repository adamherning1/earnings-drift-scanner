# 🚀 Deployment Guide

## Step 1: Push to GitHub ✅

After creating your GitHub repository, run:

```powershell
cd C:\Users\adamh\.openclaw\workspace\earnings_drift_scanner
.\push_to_github.ps1
```

Enter your GitHub username when prompted.

## Step 2: Deploy to DigitalOcean 

1. Go to: https://cloud.digitalocean.com/apps
2. Click "Create App"
3. Choose "GitHub" as source
4. Authorize DigitalOcean to access your GitHub
5. Select repository: `earnings-drift-scanner`
6. Click "Next"
7. DigitalOcean will auto-detect the app structure
8. Click "Next" through the resource configuration
9. Set environment variables:

### Required Environment Variables:

```
SECRET_KEY=generate-a-random-32-character-string-here
STRIPE_SECRET_KEY=sk_test_your_stripe_key_here
CLAUDE_API_KEY=your_anthropic_api_key_here
SENDGRID_API_KEY=your_sendgrid_key_here
```

### To Generate SECRET_KEY:
Run this in PowerShell:
```powershell
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})
```

## Step 3: Domain Setup

1. Register domain (suggestions):
   - driftedge.io
   - earningstrade.io
   - driftscanner.com

2. In DigitalOcean App settings:
   - Add your custom domain
   - Follow DNS instructions
   - SSL certificate auto-configured

## Step 4: Stripe Setup

1. Create Stripe account: https://stripe.com
2. Get API keys from: https://dashboard.stripe.com/test/apikeys
3. Create products:
   - Starter: $29/month
   - Professional: $49/month
   - Institution: $149/month
4. Update environment variables with price IDs

## Step 5: Launch Checklist

- [ ] GitHub repository created and code pushed
- [ ] DigitalOcean app deployed successfully
- [ ] Environment variables configured
- [ ] Custom domain connected
- [ ] Stripe products created
- [ ] Test user registration works
- [ ] Test subscription upgrade works
- [ ] Monitor first 24 hours for errors

## Monitoring URLs

Once deployed, you'll have:
- API: `https://your-app.ondigitalocean.app/docs`
- Frontend: `https://your-app.ondigitalocean.app`
- Logs: DigitalOcean App Platform dashboard

## Common Issues

1. **Database connection fails**: Check DATABASE_URL is properly set
2. **Build fails**: Check Node.js/Python versions in build logs
3. **Domain not working**: Verify DNS propagation (can take 48h)

## Support

- DigitalOcean Support: https://www.digitalocean.com/support
- Community: https://www.digitalocean.com/community

---

Ready to launch! 🚀