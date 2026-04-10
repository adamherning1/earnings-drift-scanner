# 📱 iPhone Setup for FREE Bot Monitoring

## Recommended App: Termius (Free)

### Step 1: Install Termius
1. Open App Store
2. Search "Termius"
3. Install (free version is fine)

### Step 2: Add Your Dell Server
1. Open Termius
2. Tap "+" → "New Host"
3. Enter:
   - Label: "Dell Trading Bot"
   - Hostname: 192.168.0.58
   - Username: adam
   - Password: [save it]
4. Save

### Step 3: Create Quick Commands (Snippets)
1. In Termius, tap "Snippets"
2. Create these snippets:

**"Bot Status"**:
```
cd mgc_trader && python quick_status.py
```

**"Bot Alert"**:
```
cd mgc_trader && python alert_check.py
```

**"Bot Report"**:
```
cd mgc_trader && python monitor_suite.py all
```

**"Bot Position"**:
```
cd mgc_trader && python monitor_suite.py position
```

### Step 4: Create iPhone Shortcuts

1. Open Shortcuts app
2. Create new shortcut
3. Add action: "Text"
4. Enter: `cd mgc_trader && python quick_status.py`
5. Add action: "Run Script over SSH"
6. Configure:
   - Host: 192.168.0.58
   - User: adam
   - Password: [your password]
   - Script: (use the text from step 4)
7. Name it: "Bot Status"
8. Add to Home Screen

Repeat for other commands!

## Even Easier: After Running Setup on Dell

Once you run `create_remote_shortcuts.bat` on Dell, your shortcuts become:

| What You Want | Type This |
|--------------|-----------|
| Quick status | `remote_status` |
| Check alerts | `remote_alert` |
| Full report | `remote_report` |
| Positions | `remote_position` |

## 💰 Daily Savings Example

### Your Old Way (Expensive):
- Morning: "Warren, is bot running?" = $3
- Lunch: "Warren, check positions" = $3  
- Evening: "Warren, daily summary" = $8
- **Daily Cost: $14**

### New Way (FREE):
- Morning: Tap "Bot Status" shortcut = $0
- Lunch: Tap "Bot Position" shortcut = $0
- Evening: Tap "Bot Report" shortcut = $0
- **Daily Cost: $0**

**Monthly Savings: $420+**

## 🚀 Pro Setup: Widget

1. After creating shortcuts
2. Long press home screen
3. Add widget → Shortcuts
4. Select your bot shortcuts
5. Now you have one-tap monitoring!

## Remember:
- WiFi must be ON (same network as Dell)
- Or use VPN if checking remotely
- Each check saves you $2-5!

---

*Only message Warren for complex strategy work. Everything else = FREE via your Dell!*