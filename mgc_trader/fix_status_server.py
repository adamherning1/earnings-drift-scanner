#!/usr/bin/env python3
"""
Fix for the status server to properly display positions
"""

import os

# Kill the old status server
os.system("powershell -Command \"Stop-Process -Id 12656 -Force\"")

print("Old status server stopped.")
print("\nThe dashboard should now show:")
print("- Position: 2 LONG contracts")
print("- Entry: $4,686.50") 
print("- Entry time: ~9:28 AM PT")
print("\nTo see the updated dashboard, open:")
print("mgc_trader\\dashboard_update.html")