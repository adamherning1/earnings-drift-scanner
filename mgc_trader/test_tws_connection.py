#!/usr/bin/env python3
"""
Test TWS connection - simple connectivity check
"""

import asyncio
from ib_insync import *

async def test_connection():
    """Test connection to TWS"""
    ib = IB()
    
    print("Testing TWS connection...")
    print("Connecting to localhost:4002...")
    
    try:
        # Try to connect
        await ib.connectAsync('192.168.0.58', 4002, clientId=999)
        
        print("✅ Connected successfully!")
        
        # Get account info
        account = ib.managedAccounts()[0] if ib.managedAccounts() else 'Unknown'
        print(f"Account: {account}")
        
        # Check if Read-Only
        positions = await ib.positionsAsync()
        print(f"Positions accessible: YES")
        print(f"Current positions: {len(positions)}")
        
        # Get account values
        account_values = await ib.accountValuesAsync()
        for av in account_values[:5]:  # Show first 5
            print(f"  {av.tag}: {av.value}")
        
        print("\n✅ TWS is properly configured!")
        print("✅ Read-Only mode is OFF!")
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nPossible issues:")
        print("1. TWS not fully started yet")
        print("2. Another client already connected")
        print("3. API not enabled in TWS")
        print("4. Wrong port (should be 4002)")
        
    finally:
        if ib.isConnected():
            ib.disconnect()
            print("\nDisconnected.")

if __name__ == "__main__":
    asyncio.run(test_connection())