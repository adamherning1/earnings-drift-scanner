# Deploy Member Portal to Vercel

## Quick Deploy Steps

1. **Go to Vercel**
   - https://vercel.com/new

2. **Import Repository**
   - Select `adamherning1/earnings-drift-scanner`
   - Click Import

3. **Configure Project**
   - **Project Name**: `earnings-scanner-portal`
   - **Framework Preset**: Next.js (should auto-detect)
   - **Root Directory**: `member-portal` ← IMPORTANT!
   - **Build Command**: (leave default)
   - **Output Directory**: (leave default)

4. **Add Environment Variables**
   ```
   NEXT_PUBLIC_API_URL=https://post-earning-scanner.onrender.com
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_your_key
   STRIPE_SECRET_KEY=sk_live_your_key
   ```

5. **Deploy**
   - Click Deploy
   - Takes ~1-2 minutes

## After Deployment

1. **Custom Domain** (optional)
   - Add your domain in Vercel settings
   - Or use the free `.vercel.app` domain

2. **Set up Stripe**
   - Create products in Stripe Dashboard
   - Add webhook endpoint: `https://your-domain.vercel.app/api/webhooks/stripe`

3. **Authentication** (next step)
   - We'll add Supabase for user auth
   - Members get API keys after payment

## What You Get

- **Landing Page**: Beautiful conversion-optimized homepage
- **Member Dashboard**: Real-time trading opportunities
- **Payment Processing**: Stripe integration ready
- **API Integration**: Connected to your scanner API
- **Mobile Responsive**: Works on all devices

## Costs

- **Vercel Pro**: $20/month (needed for commercial use)
- **Includes**: Analytics, faster builds, team features
- **Worth it**: Professional deployment for a business

Your portal is ready to attract founding members! 🚀