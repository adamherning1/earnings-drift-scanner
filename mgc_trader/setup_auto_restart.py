#!/usr/bin/env python3
"""
Setup automatic restart for MGC trading bot
Creates scheduled tasks to ensure bot stays running
"""

import os
import sys
import platform

def create_windows_task():
    """Create Windows Task Scheduler tasks for bot monitoring"""
    
    # Bot startup task (runs at system startup and at 6:25 AM ET daily)
    startup_xml = '''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Start MGC Trading Bot at market open</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-04-07T06:25:00-05:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
    <BootTrigger>
      <Enabled>true</Enabled>
      <Delay>PT2M</Delay>
    </BootTrigger>
  </Triggers>
  <Actions Context="Author">
    <Exec>
      <Command>C:\\Python314\\python.exe</Command>
      <Arguments>C:\\Users\\adamh\\.openclaw\\workspace\\mgc_trader\\adaptive_trading_bot.py</Arguments>
      <WorkingDirectory>C:\\Users\\adamh\\.openclaw\\workspace\\mgc_trader</WorkingDirectory>
    </Exec>
  </Actions>
  <Settings>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>false</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
  </Settings>
</Task>'''

    # Monitor task (runs every 15 minutes during market hours)
    monitor_xml = '''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Monitor MGC Trading Bot connection health</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-04-07T06:30:00-05:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
      <Repetition>
        <Interval>PT15M</Interval>
        <Duration>PT11H</Duration>
        <StopAtDurationEnd>true</StopAtDurationEnd>
      </Repetition>
    </CalendarTrigger>
  </Triggers>
  <Actions Context="Author">
    <Exec>
      <Command>C:\\Python314\\python.exe</Command>
      <Arguments>C:\\Users\\adamh\\.openclaw\\workspace\\mgc_trader\\connection_monitor.py</Arguments>
      <WorkingDirectory>C:\\Users\\adamh\\.openclaw\\workspace\\mgc_trader</WorkingDirectory>
    </Exec>
  </Actions>
  <Settings>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
  </Settings>
</Task>'''

    # Save XML files
    with open('mgc_bot_startup.xml', 'w') as f:
        f.write(startup_xml)
    
    with open('mgc_bot_monitor.xml', 'w') as f:
        f.write(monitor_xml)
    
    print("\nWindows Task Scheduler setup:")
    print("=" * 60)
    print("1. Open Task Scheduler (taskschd.msc)")
    print("2. Import the following tasks:")
    print(f"   - {os.path.abspath('mgc_bot_startup.xml')}")
    print(f"   - {os.path.abspath('mgc_bot_monitor.xml')}")
    print("\nOr run these commands as Administrator:")
    print(f'schtasks /create /tn "MGC Bot Startup" /xml "{os.path.abspath("mgc_bot_startup.xml")}"')
    print(f'schtasks /create /tn "MGC Bot Monitor" /xml "{os.path.abspath("mgc_bot_monitor.xml")}"')
    
def create_startup_script():
    """Create a startup script for the bot"""
    
    startup_script = '''@echo off
echo Starting MGC Trading Bot System...
echo.

REM Kill any existing Python processes running our bot
taskkill /F /IM python.exe /FI "WINDOWTITLE eq MGC Trading Bot*" 2>nul

REM Wait a moment
timeout /t 5 /nobreak

REM Start the trading bot
echo Starting trading bot...
cd /d C:\\Users\\adamh\\.openclaw\\workspace\\mgc_trader
start "MGC Trading Bot" /MIN C:\\Python314\\python.exe adaptive_trading_bot.py

REM Wait for bot to initialize
timeout /t 30 /nobreak

REM Start the connection monitor
echo Starting connection monitor...
start "MGC Connection Monitor" /MIN C:\\Python314\\python.exe connection_monitor.py

echo.
echo MGC Trading System started successfully!
echo You can close this window.
pause
'''

    with open('start_mgc_system.bat', 'w') as f:
        f.write(startup_script)
    
    print(f"\nStartup script created: {os.path.abspath('start_mgc_system.bat')}")
    print("You can run this script to start the entire system manually.")

def main():
    print("MGC Trading Bot Auto-Restart Setup")
    print("=" * 60)
    
    if platform.system() != 'Windows':
        print("This setup script is for Windows only.")
        return
    
    # Create scheduled task XML files
    create_windows_task()
    
    # Create startup batch script
    create_startup_script()
    
    print("\n" + "=" * 60)
    print("Setup complete! The bot will now:")
    print("1. Start automatically at system boot")
    print("2. Start daily at 6:25 AM ET (before market open)")
    print("3. Monitor connection health every 15 minutes")
    print("4. Restart automatically if disconnected")
    print("=" * 60)

if __name__ == "__main__":
    main()