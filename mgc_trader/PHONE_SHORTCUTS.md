# 📱 Phone Shortcuts for FREE Bot Monitoring

## SSH Commands for Your Phone

### 1. Quick Status (5 seconds)
```bash
ssh adam@192.168.0.58 "cd mgc_trader && python quick_status.py"
```

### 2. Alert Check
```bash
ssh adam@192.168.0.58 "cd mgc_trader && python alert_check.py"
```

### 3. Full Report
```bash
ssh adam@192.168.0.58 "cd mgc_trader && python monitor_suite.py all"
```

### 4. Position Check
```bash
ssh adam@192.168.0.58 "cd mgc_trader && python monitor_suite.py position"
```

### 5. Today's Performance
```bash
ssh adam@192.168.0.58 "cd mgc_trader && python monitor_suite.py performance"
```

### 6. Bot Control Menu
```bash
ssh adam@192.168.0.58 "cd mgc_trader && python bot_control.py menu"
```

## Setting Up on iPhone/Android

### iPhone (Using Shortcuts app):
1. Open Shortcuts app
2. Tap + to create new shortcut
3. Add action → "Run Script over SSH"
4. Enter:
   - Host: 192.168.0.58
   - User: adam
   - Password: [your password]
   - Script: `cd mgc_trader && python quick_status.py`
5. Name it "Bot Status"
6. Add to Home Screen

### Android (Using Termux or JuiceSSH):
1. Install JuiceSSH from Play Store
2. Add connection:
   - Host: 192.168.0.58
   - Username: adam
3. Create snippets for each command
4. Add widget to home screen

## Even Simpler: One-Tap Commands

### Create these batch files on your Dell:

**remote_status.bat**:
```batch
@echo off
python mgc_trader\quick_status.py
pause
```

**remote_alert.bat**:
```batch
@echo off
python mgc_trader\alert_check.py
pause
```

**remote_report.bat**:
```batch
@echo off
python mgc_trader\monitor_suite.py all
pause
```

Then SSH commands become super simple:
```bash
ssh adam@192.168.0.58 "remote_status"
ssh adam@192.168.0.58 "remote_alert"
ssh adam@192.168.0.58 "remote_report"
```

## 💰 Cost Comparison

| Action | Via Warren (This Chat) | Via SSH to Dell | Savings |
|--------|------------------------|-----------------|---------|
| "Is bot running?" | $2-3 | $0 | $2-3 |
| "Check for errors" | $3-5 | $0 | $3-5 |
| "Show positions" | $2-3 | $0 | $2-3 |
| "Daily summary" | $5-10 | $0 | $5-10 |

## 🚀 Pro Tips

1. **Save SSH key** on your phone to avoid typing password
2. **Create widgets** for one-tap access
3. **Use throughout the day** - it's FREE!
4. **Only message Warren** for complex stuff

## Example Daily Routine

**Morning (from bed)**:
```bash
ssh adam@192.168.0.58 "cd mgc_trader && bot-report"
```

**Lunch break**:
```bash
ssh adam@192.168.0.58 "cd mgc_trader && bot-check"
```

**Before bed**:
```bash
ssh adam@192.168.0.58 "cd mgc_trader && python scheduled_reports.py eod"
```

Total daily cost: $0 (vs $30-50 asking Warren)