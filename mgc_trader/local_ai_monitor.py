#!/usr/bin/env python3
"""
Local AI Trading Monitor - Uses Ollama instead of expensive API calls
Run this on your Dell for FREE daily monitoring
"""

import subprocess
import json
from datetime import datetime

def query_ollama(prompt, model="llama3"):
    """Query local Ollama instance"""
    cmd = ['ollama', 'run', model, prompt]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def check_trading_status():
    """Check bot status using local AI"""
    
    # Read last 50 lines of log
    try:
        with open('adaptive_bot.log', 'r') as f:
            lines = f.readlines()[-50:]
        log_data = ''.join(lines)
    except:
        log_data = "Could not read log file"
    
    prompt = f"""Analyze this trading bot log and provide a brief status:
    
{log_data}

Report:
1. Is the bot running? (Yes/No)
2. Any errors in the last hour?
3. Current position if any
4. Today's P&L if mentioned
5. Any issues that need attention?

Keep it brief."""

    print("🤖 Querying local AI (FREE!)...")
    response = query_ollama(prompt)
    
    return response

def daily_trading_summary():
    """Generate daily summary using local AI"""
    
    prompt = """Based on the trading log analysis, create a brief daily summary including:
    - Number of trades today
    - Win/loss ratio
    - Total P&L
    - Any technical issues
    - Recommendations for tomorrow
    
    Format as a brief report."""
    
    return query_ollama(prompt)

def should_restart_bot():
    """Ask local AI if bot needs restart"""
    
    prompt = """Check if the trading bot needs a restart based on:
    - Connection errors repeating
    - No trades in strong market conditions
    - Gateway timeout issues
    
    Answer: YES (restart needed) or NO (running fine) with brief reason."""
    
    return query_ollama(prompt)

if __name__ == "__main__":
    print("=" * 60)
    print("LOCAL AI TRADING MONITOR (Cost: $0.00)")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Check status
    print("📊 TRADING STATUS:")
    print(check_trading_status())
    
    # Check if restart needed
    print("\n🔄 RESTART CHECK:")
    print(should_restart_bot())
    
    # Daily summary (run at end of day)
    if datetime.now().hour >= 14:  # After market close
        print("\n📈 DAILY SUMMARY:")
        print(daily_trading_summary())
    
    print("\n" + "=" * 60)
    print("💰 API Cost Saved: ~$5-10")
    print("=" * 60)