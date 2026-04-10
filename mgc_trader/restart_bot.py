#!/usr/bin/env python3
"""
Restart the MGC trading bot
"""
import subprocess
import psutil
import time
import sys

print("MGC Trading Bot Restart Script")
print("=" * 50)

# Kill any existing Python processes running the bot
print("\n1. Checking for existing bot processes...")
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        if proc.info['name'] == 'python.exe' and proc.info['cmdline']:
            cmdline = ' '.join(proc.info['cmdline'])
            if 'adaptive_trading_bot.py' in cmdline or 'trading_bot.py' in cmdline:
                print(f"   Found bot process PID {proc.info['pid']}, terminating...")
                proc.terminate()
                time.sleep(2)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

# Start the adaptive trading bot
print("\n2. Starting MGC Adaptive Trading Bot...")
bot_path = "C:\\Users\\adamh\\.openclaw\\workspace\\mgc_trader\\adaptive_trading_bot.py"

try:
    # Use subprocess to start the bot in a new process
    process = subprocess.Popen(
        [sys.executable, bot_path],
        cwd="C:\\Users\\adamh\\.openclaw\\workspace\\mgc_trader",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1  # Line buffered
    )
    
    print(f"   Bot started with PID {process.pid}")
    print("\n3. Monitoring startup (30 seconds)...\n")
    
    # Monitor output for 30 seconds
    start_time = time.time()
    connected = False
    
    while time.time() - start_time < 30:
        line = process.stdout.readline()
        if line:
            print(f"   BOT: {line.strip()}")
            if "Connected to IB Gateway" in line:
                connected = True
            elif "Error connecting" in line or "Not connected" in line:
                print("\n   ERROR: Bot failed to connect to IB Gateway!")
        
        if process.poll() is not None:
            print(f"\n   ERROR: Bot process exited with code {process.returncode}")
            break
    
    if process.poll() is None:
        print(f"\n✓ Bot is running (PID {process.pid})")
        if connected:
            print("✓ Connected to IB Gateway successfully")
        else:
            print("⚠ Bot is running but connection status unclear - check logs")
        print("\nTo monitor the bot, check: mgc_trader\\adaptive_bot.log")
    else:
        print("\n✗ Bot failed to start properly")
        
except Exception as e:
    print(f"\n✗ Error starting bot: {e}")