@echo off
echo Starting MGC Trading Bot System...
echo.

REM Kill any existing Python processes running our bot
taskkill /F /IM python.exe /FI "WINDOWTITLE eq MGC Trading Bot*" 2>nul

REM Wait a moment
timeout /t 5 /nobreak

REM Start the trading bot
echo Starting trading bot...
cd /d C:\Users\adamh\.openclaw\workspace\mgc_trader
start "MGC Trading Bot" /MIN C:\Python314\python.exe adaptive_trading_bot.py

REM Wait for bot to initialize
timeout /t 30 /nobreak

REM Start the connection monitor
echo Starting connection monitor...
start "MGC Connection Monitor" /MIN C:\Python314\python.exe connection_monitor.py

echo.
echo MGC Trading System started successfully!
echo You can close this window.
pause
