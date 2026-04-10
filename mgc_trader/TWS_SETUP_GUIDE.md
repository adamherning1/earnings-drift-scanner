# TWS Setup Guide for Auto-Trading

## When to Do This
Best time: After market close today or before market open tomorrow

## Step 1: Install TWS on Dell Server (192.168.0.58)
1. Remote Desktop to 192.168.0.58
2. Copy `mgc_trader\tws-installer.exe` to the Dell
3. Run the installer
4. Install to default location

## Step 2: First Login & Configuration
1. Launch TWS
2. Log in with your IB credentials
3. **IMPORTANT**: Check "Save username and password"

## Step 3: Enable Auto-Restart
1. Go to: File → Global Configuration
2. Navigate to: Configuration → Lock and Exit
3. Settings to configure:
   - ✓ Auto restart
   - ✓ Daily
   - Time: 05:45 (5:45 AM)
   - ✓ Auto logoff
   - Time: 17:15 (5:15 PM after market)

## Step 4: Configure API Settings
1. In Configuration, go to: API → Settings
2. Enable:
   - ✓ Enable ActiveX and Socket Clients
   - ✓ Socket port: 4002 (same as Gateway)
   - ✓ Allow connections from localhost only
3. Add Trusted IPs: 127.0.0.1

## Step 5: Configure Auto-Login
1. Still in Lock and Exit section:
   - ✓ Store settings on server
   - ✓ Minimize on close
   - ✓ Close positions on exit: UNCHECKED!

## Step 6: Disable Unnecessary Features
1. Configuration → Display
   - Uncheck "Show animated tickers"
   - Uncheck "Show news panel"
2. This reduces memory usage

## Step 7: Test Setup
1. Close TWS completely
2. Wait 1 minute
3. Launch TWS again
4. It should auto-login without prompting

## Step 8: Stop IB Gateway & Switch Bot
1. Close IB Gateway (system tray)
2. Make sure it's not set to auto-start
3. Bot will now connect to TWS on port 4002

## Daily Operation
- TWS auto-restarts at 5:45 AM
- Auto-logs in
- Bot connects at 6:00 AM
- Trades until 5:00 PM
- TWS auto-closes at 5:15 PM

## Advantages Over Gateway
- Survives phone logins better
- Auto-reconnects after issues
- Daily fresh start prevents stuck states
- Visual interface for monitoring

## Emergency Backup
If TWS fails to auto-login:
- Create Windows Scheduled Task
- Run AutoHotkey script
- Or use remote desktop to manually start