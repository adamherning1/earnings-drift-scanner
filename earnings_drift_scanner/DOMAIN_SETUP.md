# Drift Analytics Domain Setup

## Domain Information
- **Domain**: driftanalytics.io
- **Registrar**: Namecheap
- **Purchased**: April 27, 2026
- **Cost**: $34.98/year
- **Privacy**: Free WHOIS privacy included

## Next Steps

### 1. Point Domain to Vercel
1. Log into Namecheap
2. Go to Domain List → Manage → Advanced DNS
3. Delete any existing records
4. Add these DNS records:
   - Type: A, Host: @, Value: 76.76.21.21
   - Type: CNAME, Host: www, Value: cname.vercel-dns.com

### 2. Add Domain to Vercel
1. Go to your Vercel dashboard
2. Select the earnings-drift-scanner project
3. Go to Settings → Domains
4. Add domain: driftanalytics.io
5. Add domain: www.driftanalytics.io

### 3. Update All Branding
Files to update with "Drift Analytics":
- member-portal/app/page.js (homepage)
- member-portal/app/dashboard/page.js
- member-portal/app/layout.js (site title)
- All navigation headers
- Footer copyright

### 4. Business Info for Stripe
- Business Name: Drift Analytics
- Website: https://driftanalytics.io
- Support Email: support@driftanalytics.io
- Business Category: Software/Financial Services

### 5. Email Setup (Later)
- Google Workspace: $6/month
- Or Namecheap email: $11.88/year
- Forward to personal email initially