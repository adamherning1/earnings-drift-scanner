@echo off
REM TWS Daily Restart Script
REM Schedule this with Windows Task Scheduler if TWS auto-restart fails

echo Stopping any running TWS instances...
taskkill /F /IM tws.exe 2>nul
taskkill /F /IM javaw.exe 2>nul

echo Waiting 30 seconds...
timeout /t 30

echo Starting TWS...
cd "C:\Jts"
start tws.exe -J-DjtsConfigDir=C:\Jts

echo TWS restart complete!
echo Bot should auto-connect in 2 minutes.