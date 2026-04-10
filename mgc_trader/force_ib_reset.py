#!/usr/bin/env python3
"""
Force IB Gateway to reset by using a different client ID temporarily
"""

from ib_insync import IB
import time
from config import IB_HOST, IB_PORT

print("Forcing IB Gateway session reset...")

# Try to connect with a different client ID to force reset
for client_id in [999, 998, 997]:
    try:
        print(f"Attempting connection with clientId {client_id}...")
        ib = IB()
        ib.connect(IB_HOST, IB_PORT, clientId=client_id, timeout=5)
        print(f"Connected with clientId {client_id}")
        
        # Wait a moment
        time.sleep(2)
        
        # Disconnect cleanly
        ib.disconnect()
        print(f"Disconnected clientId {client_id}")
        
        # Small delay between attempts
        time.sleep(1)
        
    except Exception as e:
        print(f"Client {client_id} failed: {e}")
        continue

print("\nWaiting 5 seconds before restarting bot...")
time.sleep(5)

# Now try the main bot
print("\nRestarting trading bot...")
import subprocess
subprocess.Popen(['python', 'adaptive_trading_bot.py'])

print("Bot restart initiated!")