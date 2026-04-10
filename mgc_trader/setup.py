#!/usr/bin/env python3
"""Setup script for MGC Trading Bot"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    packages = [
        'ib_insync',
        'pandas',
        'numpy',
        'python-dotenv',
        'colorama',  # For colored console output
        'pyautogui',  # For Gateway auto-login
        'psutil',  # For process management
        'pywin32',  # For Windows automation
        'flask'  # For web dashboard
    ]
    
    print("Installing required packages...")
    for package in packages:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
    
    print("\nAll packages installed successfully!")

def create_directories():
    """Create necessary directories"""
    dirs = ['logs', 'data', 'backups']
    
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
        print(f"Created directory: {dir_name}/")

def test_ib_connection():
    """Test IB Gateway connection"""
    print("\nTesting IB Gateway connection...")
    
    try:
        from ib_insync import IB
        from config import IB_HOST, IB_PORT
        
        ib = IB()
        ib.connect(IB_HOST, IB_PORT, clientId=99)
        print("✅ Successfully connected to IB Gateway!")
        
        # Get account info
        account = ib.accountSummary()[0]
        print(f"Account: {account.account}")
        
        ib.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 50)
    print("    MGC TRADING BOT SETUP")
    print("=" * 50)
    
    # Install packages
    install_requirements()
    
    # Create directories
    create_directories()
    
    # Test connection
    print("\nSetup complete!")
    
    if test_ib_connection():
        print("\n✅ Ready to start trading!")
        print("\nTo run the bot: python trading_bot.py")
        print("To view dashboard: python dashboard.py")
    else:
        print("\n⚠️  Please ensure IB Gateway is running on the Dell")
        print("and API connections are enabled.")

if __name__ == "__main__":
    main()