@echo off
REM Setup convenient aliases for Windows
REM Run this once to create easy shortcuts

echo Creating monitoring shortcuts...

REM Create bot-status.bat
echo @echo off > bot-status.bat
echo python "%~dp0monitor_suite.py" status >> bot-status.bat

REM Create bot-check.bat  
echo @echo off > bot-check.bat
echo python "%~dp0quick_status.py" >> bot-check.bat

REM Create bot-alert.bat
echo @echo off > bot-alert.bat
echo python "%~dp0alert_check.py" >> bot-alert.bat

REM Create bot-report.bat
echo @echo off > bot-report.bat
echo python "%~dp0monitor_suite.py" all >> bot-report.bat

REM Create bot-control.bat
echo @echo off > bot-control.bat
echo python "%~dp0bot_control.py" menu >> bot-control.bat

REM Create bot-start.bat
echo @echo off > bot-start.bat
echo python "%~dp0bot_control.py" start >> bot-start.bat

REM Create bot-stop.bat
echo @echo off > bot-stop.bat
echo python "%~dp0bot_control.py" stop >> bot-stop.bat

REM Create bot-monitor.bat
echo @echo off > bot-monitor.bat
echo python "%~dp0continuous_monitor.py" >> bot-monitor.bat

echo.
echo ✅ Shortcuts created! You can now use:
echo.
echo bot-check     - Quick status check
echo bot-status    - Detailed status
echo bot-alert     - Check for alerts
echo bot-report    - Full report
echo bot-control   - Interactive menu
echo bot-start     - Start the bot
echo bot-stop      - Stop the bot
echo bot-monitor   - Continuous monitoring
echo.
echo 💰 All using FREE local AI!
echo.
pause