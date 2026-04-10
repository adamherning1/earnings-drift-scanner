@echo off
echo Creating simple remote shortcuts...

REM Create remote_status.bat in user home
echo @echo off > %USERPROFILE%\remote_status.bat
echo cd mgc_trader >> %USERPROFILE%\remote_status.bat
echo python quick_status.py >> %USERPROFILE%\remote_status.bat

REM Create remote_alert.bat
echo @echo off > %USERPROFILE%\remote_alert.bat
echo cd mgc_trader >> %USERPROFILE%\remote_alert.bat
echo python alert_check.py >> %USERPROFILE%\remote_alert.bat

REM Create remote_report.bat  
echo @echo off > %USERPROFILE%\remote_report.bat
echo cd mgc_trader >> %USERPROFILE%\remote_report.bat
echo python monitor_suite.py all >> %USERPROFILE%\remote_report.bat

REM Create remote_position.bat
echo @echo off > %USERPROFILE%\remote_position.bat
echo cd mgc_trader >> %USERPROFILE%\remote_position.bat
echo python monitor_suite.py position >> %USERPROFILE%\remote_position.bat

REM Create remote_performance.bat
echo @echo off > %USERPROFILE%\remote_performance.bat
echo cd mgc_trader >> %USERPROFILE%\remote_performance.bat
echo python monitor_suite.py performance >> %USERPROFILE%\remote_performance.bat

echo.
echo ✅ Remote shortcuts created in %USERPROFILE%
echo.
echo Now from your phone you can use SHORT commands:
echo   ssh adam@192.168.0.58 "remote_status"
echo   ssh adam@192.168.0.58 "remote_alert"
echo   ssh adam@192.168.0.58 "remote_report"
echo   ssh adam@192.168.0.58 "remote_position"
echo   ssh adam@192.168.0.58 "remote_performance"
echo.
pause