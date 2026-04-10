@echo off
echo ========================================
echo 🤖 STARTING MGC BOT MONITORING SUITE
echo ========================================
echo.

REM First run setup if needed
if not exist bot-check.bat (
    echo Setting up shortcuts first...
    call setup_aliases.bat
    echo.
)

echo Starting automated monitoring services...
echo.

REM Start continuous monitor in new window (checks every 5 minutes)
echo [1/3] Starting continuous monitor...
start "Continuous Monitor" cmd /k python continuous_monitor.py --interval 300

REM Wait a moment
timeout /t 2 /nobreak > nul

REM Run initial full report
echo [2/3] Generating initial status report...
python monitor_suite.py all

echo.
echo [3/3] Setting up scheduled tasks...
echo.

REM Create scheduled task for EOD report (Windows Task Scheduler)
schtasks /create /tn "MGC_EOD_Report" /tr "python %cd%\scheduled_reports.py eod" /sc daily /st 17:30 /f >nul 2>&1
echo ✅ EOD Report scheduled for 5:30 PM daily

REM Create scheduled task for morning report
schtasks /create /tn "MGC_Morning_Report" /tr "python %cd%\scheduled_reports.py morning" /sc daily /st 05:45 /f >nul 2>&1
echo ✅ Morning Report scheduled for 5:45 AM daily

echo.
echo ========================================
echo ✅ MONITORING SUITE ACTIVE!
echo ========================================
echo.
echo 📊 Continuous Monitor: Running (every 5 min)
echo 📅 Morning Report: 5:45 AM daily
echo 📅 EOD Report: 5:30 PM daily
echo.
echo 💰 Cost: $0/day (using local Ollama AI)
echo.
echo QUICK COMMANDS YOU CAN USE:
echo   bot-check     - Quick status
echo   bot-alert     - Check for issues  
echo   bot-report    - Full report
echo   bot-control   - Interactive menu
echo.
echo Press any key to open the control panel...
pause > nul

REM Open interactive control panel
python bot_control.py menu