#!/usr/bin/env python3
"""
Fix incorrect trading hours in the MGC bot
The bot thinks market closes at 1:00 PM ET, but MGC trades until 5:00 PM ET
"""

import shutil
from datetime import datetime

# Read the current bot file
with open("adaptive_trading_bot.py", "r", encoding="utf-8") as f:
    content = f.read()

# The incorrect line
old_line = "if now.weekday() >= 5 or not (time(6, 30) <= now.time() <= time(13, 0)):"

# The correct line (trades from 6 PM previous day to 5 PM current day)
# For simplicity, we'll just check if it's during RTH (Regular Trading Hours)
# MGC actually trades almost 24 hours, but we'll focus on main session
new_line = "if now.weekday() >= 5 or not (time(6, 0) <= now.time() <= time(17, 0)):"

if old_line in content:
    # Backup current file
    backup_name = f"adaptive_trading_bot_backup_hours_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    shutil.copy("adaptive_trading_bot.py", backup_name)
    print(f"Created backup: {backup_name}")
    
    # Replace the line
    content = content.replace(old_line, new_line)
    
    # Write the fixed file
    with open("adaptive_trading_bot.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ Fixed trading hours in adaptive_trading_bot.py")
    print("Old hours: 6:30 AM - 1:00 PM ET")
    print("New hours: 6:00 AM - 5:00 PM ET")
    print("\nThe bot will now trade until 5:00 PM ET!")
else:
    print("Could not find the incorrect trading hours line.")
    print("Manual fix needed.")

print("\nTo apply the fix:")
print("1. Restart the bot")
print("2. It will now trade until 5:00 PM ET instead of stopping at 1:00 PM")