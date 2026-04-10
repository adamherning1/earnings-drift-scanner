#!/usr/bin/env python3
"""
Connection monitor to ensure trading bot stays connected
Checks connection status and restarts bot if needed
"""

import subprocess
import psutil
import time
from datetime import datetime
from ib_insync import IB
from config import IB_HOST, IB_PORT

def is_bot_running():
    """Check if the trading bot process is running"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe' and proc.info['cmdline']:
                cmdline = ' '.join(proc.info['cmdline'])
                if 'adaptive_trading_bot.py' in cmdline:
                    return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return None

def test_ib_connection():
    """Test if IB Gateway is accessible and responsive"""
    try:
        ib = IB()
        ib.connect(IB_HOST, IB_PORT, clientId=999, timeout=10)
        connected = ib.isConnected()
        ib.disconnect()
        return connected
    except:
        return False

def restart_bot():
    """Kill existing bot and start a new instance"""
    print(f"\n[{datetime.now()}] Restarting trading bot...")
    
    # Kill existing bot
    bot_pid = is_bot_running()
    if bot_pid:
        print(f"Killing existing bot (PID {bot_pid})...")
        try:
            proc = psutil.Process(bot_pid)
            proc.terminate()
            time.sleep(3)
        except:
            pass
    
    # Start new bot
    print("Starting new bot instance...")
    subprocess.Popen(
        ['python', 'adaptive_trading_bot.py'],
        cwd='C:\\Users\\adamh\\.openclaw\\workspace\\mgc_trader'
    )
    print("Bot restarted successfully!")

def main():
    print("=" * 60)
    print("MGC TRADING BOT CONNECTION MONITOR")
    print("=" * 60)
    print("Monitoring connection health every 2 minutes...")
    print("Will restart bot if connection issues detected\n")
    
    last_restart = None
    
    while True:
        try:
            # Check every 2 minutes
            time.sleep(120)
            
            # Check if market is open (skip weekends)
            now = datetime.now()
            if now.weekday() >= 5:
                continue
            
            # Check if bot is running
            bot_pid = is_bot_running()
            if not bot_pid:
                print(f"[{now}] Bot not running! Restarting...")
                restart_bot()
                last_restart = now
                continue
            
            # Check IB connection
            if not test_ib_connection():
                print(f"[{now}] IB Gateway not responding!")
                # Only restart bot if we haven't done so recently
                if not last_restart or (now - last_restart).seconds > 300:
                    print("Bot may be disconnected, restarting...")
                    restart_bot()
                    last_restart = now
            else:
                # Check bot log for connection errors
                try:
                    with open('adaptive_bot.log', 'r', encoding='utf-8') as f:
                        # Read last 50 lines
                        lines = f.readlines()[-50:]
                        recent_errors = sum(1 for line in lines if 'Not connected' in line)
                        
                        if recent_errors > 10:
                            print(f"[{now}] Bot reporting connection errors! Restarting...")
                            restart_bot()
                            last_restart = now
                except:
                    pass
                    
        except KeyboardInterrupt:
            print("\nMonitor stopped by user")
            break
        except Exception as e:
            print(f"Monitor error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()