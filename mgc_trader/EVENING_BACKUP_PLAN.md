# 🌙 Evening Backup Plan - April 10, 2026

## When to Run: Tonight after market close (5:00 PM ET / 2:00 PM PT)

## Step 1: Check Final Status
```bash
cd mgc_trader
python quick_status.py
```

## Step 2: Stop Bot Gracefully
1. Wait for any open positions to close
2. Press Ctrl+C in bot window
3. Verify clean shutdown message

## Step 3: Create Backup Folder
```bash
mkdir C:\MGC_Backup_04102026
cd mgc_trader
```

## Step 4: Copy All Critical Files
```bash
# Copy entire mgc_trader folder
xcopy /E /I . C:\MGC_Backup_04102026\mgc_trader\

# Specifically ensure these are included:
# - adaptive_bot.log (complete trading history)
# - config.py (all settings)
# - adaptive_trading_bot.py (latest bot version)
# - All monitoring scripts (*.py)
# - adaptive_params.json
```

## Step 5: Document Current Status
Create a file: `C:\MGC_Backup_04102026\FINAL_STATUS.txt`
```
MGC Trading Bot Status - April 10, 2026
======================================
Final Account Balance: $________
Total P&L Since Start: $________
Phase 1 Progress: ___/50 trades
Win Rate: ____%
Last Day Results: $________

Notes for Restart:
- Use IB Gateway (not TWS)
- Enable saved login credentials
- Update daily loss limit back to $500
```

## Step 6: Export from TWS/Gateway
1. File → Export → Trade Log
2. Save to backup folder
3. Take screenshot of account

## Step 7: Cloud Backup (Optional but Recommended)
Upload the entire backup folder to:
- Google Drive
- Dropbox
- OneDrive
- Or USB drive

## For Next Week's Restart

When you return, you'll have:
- Complete trade logs
- All bot code and configs
- Performance history
- Ready to resume at Phase 1, trade 5/50

## Reminder: Run This Tonight!
Set a reminder for 5:30 PM ET (2:30 PM PT) to start the backup process.