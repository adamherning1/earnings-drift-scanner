@echo off
echo ========================================
echo    IB GATEWAY MANAGER - 24/7 OPERATION
echo ========================================
echo.
echo This will keep IB Gateway running automatically:
echo - Auto-login on startup
echo - Restart if it crashes  
echo - Handle daily restart at 11:45 PM ET
echo - Monitor connection health
echo.

cd mgc_trader
python gateway_manager.py

pause