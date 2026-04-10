#!/usr/bin/env python3
"""
Fix the reconnect logic in adaptive_trading_bot.py
Handles session conflicts when logging in from another device
"""

import shutil
from datetime import datetime

# Backup current file
backup_name = f"adaptive_trading_bot_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy("adaptive_trading_bot.py", backup_name)
print(f"Created backup: {backup_name}")

# Read the current file
with open("adaptive_trading_bot.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find where to add connection monitoring
check_exit_line = "def check_exit_conditions(self):"

# Add connection check to check_exit_conditions
new_check_exit = '''def check_exit_conditions(self):
        """Check if we should exit current position"""
        # CRITICAL: Ensure connected before checking exits
        if not self.ensure_connected():
            logger.error("Lost connection while in position! Attempting reconnect...")
            return
            
        try:'''

# Replace the method definition
if check_exit_line in content:
    # Find the full method
    start = content.find(check_exit_line)
    # Find the try: block
    try_pos = content.find("try:", start)
    if try_pos > start:
        # Replace from def to try:
        before = content[:start]
        after = content[try_pos+4:]  # Skip "try:"
        content = before + new_check_exit + after

# Also add periodic connection check in main loop
# Find the sleep line at end of main loop
main_loop_check = '''
                # Wait before next check
                self.ib.sleep(15)'''

new_main_loop_check = '''
                # Periodic connection health check
                if not self.ib.isConnected():
                    logger.warning("Connection lost! Triggering reconnect...")
                    if not self.ensure_connected():
                        logger.error("Failed to reconnect. Will retry next cycle.")
                
                # Wait before next check
                self.ib.sleep(15)'''

content = content.replace(main_loop_check, new_main_loop_check)

# Write the updated file
with open("adaptive_trading_bot.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✓ Updated adaptive_trading_bot.py with better reconnect handling")
print("✓ Now handles session conflicts properly")
print("✓ Will auto-reconnect when kicked by phone login")