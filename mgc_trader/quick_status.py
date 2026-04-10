#!/usr/bin/env python3
"""
Quick Trading Status - Uses Local AI (FREE)
Run on Dell: python quick_status.py
"""

import subprocess
import os
from datetime import datetime

def quick_check():
    """Super simple status check using Ollama"""
    
    # Get last 30 lines of log
    log_cmd = "tail -30 adaptive_bot.log"
    log_output = subprocess.run(log_cmd, shell=True, capture_output=True, text=True).stdout
    
    # Create focused prompt
    prompt = f'''Look at this trading bot log and answer:
1. Bot running? (YES/NO)
2. Any position open? (If yes, how many contracts)
3. Today\'s P&L?
4. Any errors?

LOG:
{log_output}

Give brief answers only.'''
    
    # Query Ollama (assuming llama3 is installed)
    cmd = f'echo "{prompt}" | ollama run llama3'
    
    print("Checking bot status with local AI...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    return result.stdout

if __name__ == "__main__":
    print("\n🤖 MGC BOT STATUS (via Local AI - FREE!)")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%I:%M %p')}")
    print("=" * 50)
    
    status = quick_check()
    print(status)
    
    print("\n💰 Cost: $0.00 (vs ~$2-5 with Claude)")
    print("=" * 50)