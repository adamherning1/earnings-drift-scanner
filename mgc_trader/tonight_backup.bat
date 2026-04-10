@echo off
echo ====================================
echo    MGC BOT BACKUP - APRIL 10, 2026
echo ====================================
echo.
echo This script will help you backup everything before your move!
echo.
echo STEP 1: Checking bot status...
cd /d C:\Users\adamh\.openclaw\workspace\mgc_trader
python quick_status.py
echo.
pause

echo STEP 2: Creating backup folder...
mkdir C:\MGC_Backup_04102026 2>nul
echo.

echo STEP 3: Copying all files...
echo This may take a minute...
xcopy /E /I /Y *.* C:\MGC_Backup_04102026\mgc_trader\
echo.
echo Backup complete!
echo.

echo IMPORTANT REMINDERS:
echo 1. Stop the bot with Ctrl+C
echo 2. Export trade logs from TWS
echo 3. Note final account balance
echo 4. Upload backup to cloud storage
echo.
echo Your backup is saved in: C:\MGC_Backup_04102026
echo.
pause