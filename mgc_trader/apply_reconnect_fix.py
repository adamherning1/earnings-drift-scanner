#!/usr/bin/env python3
"""
Apply reconnection fix to adaptive_trading_bot.py
Adds auto-reconnect capabilities without rewriting the entire file
"""

import shutil
from datetime import datetime

# Backup the original file
backup_name = f"adaptive_trading_bot_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy("adaptive_trading_bot.py", backup_name)
print(f"Created backup: {backup_name}")

# Read the current file
with open("adaptive_trading_bot.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find where to insert the new methods
class_start = None
connect_start = None
run_start = None

for i, line in enumerate(lines):
    if "class AdaptiveMGCBot:" in line:
        class_start = i
    elif "def connect(self):" in line:
        connect_start = i
    elif "def run(self):" in line:
        run_start = i

# Insert connection monitoring attributes after __init__
init_line = None
for i in range(class_start, len(lines)):
    if "self.running = True" in lines[i]:
        init_line = i
        break

if init_line:
    lines.insert(init_line + 1, "        self.connection_retries = 0\n")
    lines.insert(init_line + 2, "        self.max_retries = 5\n")

# Add ensure_connected method before connect method
reconnect_methods = '''
    def ensure_connected(self):
        """Ensure we have a valid connection, reconnect if needed"""
        if not self.ib.isConnected():
            logger.warning("Connection lost! Attempting to reconnect...")
            return self.reconnect()
        return True
    
    def reconnect(self):
        """Attempt to reconnect to IB Gateway"""
        self.connection_retries = 0
        
        while self.connection_retries < self.max_retries:
            try:
                self.connection_retries += 1
                logger.info(f"Reconnection attempt {self.connection_retries}/{self.max_retries}")
                
                # Disconnect if still partially connected
                try:
                    self.ib.disconnect()
                except:
                    pass
                
                # Wait a bit before reconnecting
                time.sleep(5)
                
                # Try to connect
                if self.connect():
                    logger.info("✅ Reconnected successfully!")
                    self.connection_retries = 0
                    return True
                    
            except Exception as e:
                logger.error(f"Reconnection failed: {e}")
                time.sleep(10)
        
        logger.error(f"Failed to reconnect after {self.max_retries} attempts!")
        return False
'''

# Insert before connect method
lines.insert(connect_start, reconnect_methods)

# Update connect method to check connection status
# Find the return True line in connect method
for i in range(connect_start + 30, connect_start + 100):
    if i < len(lines) and "return True" in lines[i] and "def" not in lines[i]:
        # Add connection check before return
        lines.insert(i, "            \n")
        lines.insert(i, "            if not self.ib.isConnected():\n")
        lines.insert(i + 1, "                return False\n")
        lines.insert(i + 2, "                \n")
        break

# Update get_current_price to use ensure_connected
for i in range(connect_start, len(lines)):
    if "def get_current_price(self):" in lines[i]:
        # Replace the method
        j = i + 1
        while j < len(lines) and not lines[j].strip().startswith("def "):
            j += 1
        
        new_method = '''    def get_current_price(self):
        """Get current market price with safety checks"""
        if not self.ensure_connected():
            return None
            
        if self.ticker.marketPrice() > 0:
            return self.ticker.marketPrice()
        elif self.ticker.last > 0:
            return self.ticker.last
        elif self.ticker.bid > 0 and self.ticker.ask > 0:
            return (self.ticker.bid + self.ticker.ask) / 2
        return None
    
'''
        lines[i:j] = [new_method]
        break

# Update methods that need connection to use ensure_connected
methods_to_update = ["get_4h_bias", "check_entry_signal", "place_entry_order"]
for method in methods_to_update:
    for i in range(len(lines)):
        if f"def {method}(" in lines[i]:
            # Find the try: line
            for j in range(i, min(i + 20, len(lines))):
                if "try:" in lines[j]:
                    # Insert connection check before try
                    indent = len(lines[j]) - len(lines[j].lstrip())
                    lines.insert(j, " " * indent + "if not self.ensure_connected():\n")
                    if method == "get_4h_bias":
                        lines.insert(j + 1, " " * indent + "    return 'NEUTRAL', 0\n")
                    else:
                        lines.insert(j + 1, " " * indent + "    return None\n")
                    lines.insert(j + 2, " " * indent + "    \n")
                    break
            break

# Update main run loop to check connection
for i in range(run_start, len(lines)):
    if "while self.running:" in lines[i]:
        # Find the try: line
        for j in range(i, min(i + 10, len(lines))):
            if "try:" in lines[j]:
                # Insert connection check as first thing in loop
                indent = len(lines[j]) - len(lines[j].lstrip()) + 4
                lines.insert(j + 1, " " * indent + "# Ensure we're connected before doing anything\n")
                lines.insert(j + 2, " " * indent + "if not self.ensure_connected():\n")
                lines.insert(j + 3, " " * indent + "    logger.error('Cannot establish connection. Waiting 30 seconds...')\n")
                lines.insert(j + 4, " " * indent + "    self.ib.sleep(30)\n")
                lines.insert(j + 5, " " * indent + "    continue\n")
                lines.insert(j + 6, " " * indent + "    \n")
                break
        break

# Add time import if not present
has_time_import = any("import time" in line for line in lines[:20])
if not has_time_import:
    for i, line in enumerate(lines):
        if "from datetime import" in line:
            lines.insert(i + 1, "import time\n")
            break

# Write the updated file
with open("adaptive_trading_bot_reconnect.py", "w", encoding="utf-8") as f:
    f.writelines(lines)

print("Created adaptive_trading_bot_reconnect.py with auto-reconnect capabilities")
print("\nTo apply the fix:")
print("1. Stop the current bot")
print("2. Copy adaptive_trading_bot_reconnect.py to adaptive_trading_bot.py")
print("3. Restart the bot")
print("\nOr run: copy adaptive_trading_bot_reconnect.py adaptive_trading_bot.py")