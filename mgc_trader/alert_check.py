#!/usr/bin/env python3
"""
Quick Alert Check - Run this anytime to check for issues
One-line command: python alert_check.py
"""

import subprocess
from datetime import datetime

def quick_alert_check():
    """Super fast check for issues needing attention"""
    
    # Get last 50 lines
    logs = subprocess.run("tail -50 adaptive_bot.log", shell=True, capture_output=True, text=True).stdout
    
    prompt = f"""URGENT issues only (answer YES or NO for each):
1. Bot disconnected? 
2. Position without stop?
3. Large loss >$500?
4. Errors repeating?

LOG: {logs}

Format: YES/NO for each, then action needed"""
    
    # Query Ollama
    cmd = f'echo "{prompt}" | ollama run llama3'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    return result.stdout.strip()

def main():
    print(f"\n🚨 ALERT CHECK - {datetime.now().strftime('%I:%M %p')}")
    print("=" * 40)
    
    result = quick_alert_check()
    print(result)
    
    if "YES" in result:
        print("\n⚠️  ACTION REQUIRED!")
    else:
        print("\n✅ All systems normal")
    
    print("=" * 40)
    print("Cost: $0 (vs ~$2 API call)")

if __name__ == "__main__":
    main()