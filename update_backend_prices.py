#!/usr/bin/env python3
"""
Update the backend to use real Massive API prices
"""

import os

# Get the Massive API key from environment or prompt
api_key = os.getenv("MASSIVE_API_KEY", "")

if not api_key:
    print("\n=== Massive API Configuration ===")
    print("You need to set your Massive API key for real-time stock prices.")
    print("You can find your API key at: https://polygon.io/dashboard/api-keys")
    print("\nTo set it permanently, add to your environment variables:")
    print('set MASSIVE_API_KEY=your_actual_api_key_here')
    print("\nOr add it to a .env file in the backend directory:")
    print('MASSIVE_API_KEY=your_actual_api_key_here')
    
    api_key = input("\nEnter your Massive API key: ")

# Update instructions
print("\n=== Next Steps ===")
print("1. Update the backend on Render:")
print("   - Go to https://dashboard.render.com")
print("   - Find your 'post-earnings-scanner-v2' service")
print("   - Go to Environment → Add Environment Variable")
print(f"   - Add: MASSIVE_API_KEY = {api_key[:10]}...")
print("\n2. The backend will automatically restart and use real prices")
print("\n3. All pages will show current market prices:")
print("   - Dashboard opportunities")
print("   - Stock analysis pages")
print("   - Paper trading history")

# Create a .env file for local testing
if api_key:
    with open(".env", "w") as f:
        f.write(f"MASSIVE_API_KEY={api_key}\n")
    print("\nCreated .env file for local testing")