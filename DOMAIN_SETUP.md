# Setting up driftanalytics.io on Vercel

## Step 1: Add Domain in Vercel

1. Go to https://vercel.com/dashboard
2. Click on your project: "earnings-drift-scanner"
3. Go to "Settings" tab
4. Click on "Domains" in the left sidebar
5. Enter: driftanalytics.io
6. Click "Add"

Vercel will show you DNS records to add.

## Step 2: Configure DNS Records

Where you bought the domain (likely Namecheap, GoDaddy, or similar), add these records:

### For apex domain (driftanalytics.io):
- Type: A
- Name: @ (or leave blank)
- Value: 76.76.21.21

### For www subdomain (www.driftanalytics.io):
- Type: CNAME
- Name: www
- Value: cname.vercel-dns.com

## Step 3: Wait for Propagation

- DNS changes can take 5-48 hours to propagate
- Vercel will automatically provision SSL certificates
- You'll see a green checkmark in Vercel when ready

## Step 4: Update Environment Variables

After domain is connected, update any hardcoded URLs in the code from:
- https://earnings-drift-scanner.vercel.app
to:
- https://driftanalytics.io

## Current Status
- Domain purchased: ✅ (April 27, 2026)
- Vercel deployment: ✅ (earnings-drift-scanner.vercel.app)
- DNS configuration: ⏳ Pending
- SSL certificate: ⏳ Will auto-provision after DNS

## Testing
Once DNS propagates, test:
1. https://driftanalytics.io (should load)
2. https://www.driftanalytics.io (should redirect to apex)
3. https://earnings-drift-scanner.vercel.app (old URL should still work)