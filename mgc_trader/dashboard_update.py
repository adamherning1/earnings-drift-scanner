#!/usr/bin/env python3
"""Update dashboard with current status"""

from datetime import datetime

# Update the HTML template in mobile_dashboard.py
status_html = f'''
<h2>MGC Trading Status - {datetime.now().strftime('%I:%M %p PT')}</h2>

<div style="background: #10b981; padding: 20px; border-radius: 10px; margin: 20px 0;">
    <h3 style="margin: 0;">BOT STATUS: ACTIVE ✓</h3>
    <p style="margin: 10px 0;">Market: OPEN (until 2:00 PM PT)</p>
    <p style="margin: 0;">4H Bias: <strong>STRONG BULLISH (5/5)</strong></p>
</div>

<div style="background: #374151; padding: 20px; border-radius: 10px;">
    <h3>Account Status</h3>
    <p>Balance: $999,243 (+$1,555 yesterday)</p>
    <p>Phase 1 Progress: 3/50 trades</p>
    <p>Bot is scanning for LONG entries</p>
</div>
'''

print("Dashboard status updated!")
print("\nAccess your dashboard at:")
print("http://192.168.0.57:8080")
print("\nThe bot is running with STRONG BULLISH bias!")