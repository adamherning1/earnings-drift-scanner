# MGC Bot Monitoring Setup Guide 🤖

## Available Monitoring Scripts

### 1. **monitor_suite.py** - Swiss Army Knife
Your main monitoring tool with multiple commands:
```bash
# Quick status check
python monitor_suite.py status

# Check positions
python monitor_suite.py position

# Scan for errors
python monitor_suite.py errors

# Daily performance
python monitor_suite.py performance

# Check if intervention needed
python monitor_suite.py intervene

# Market conditions
python monitor_suite.py market

# FULL REPORT (all checks)
python monitor_suite.py all
```

### 2. **continuous_monitor.py** - Always Watching
Runs continuously, checking every X minutes:
```bash
# Default: check every 5 minutes
python continuous_monitor.py

# Custom interval (e.g., every 2 minutes)
python continuous_monitor.py --interval 120
```

### 3. **scheduled_reports.py** - Automated Reports
Generate reports at specific times:
```bash
# Morning report (run at 5:45 AM)
python scheduled_reports.py morning

# Midday report (run at 12:00 PM)
python scheduled_reports.py midday

# End of day report (run at 5:30 PM)
python scheduled_reports.py eod

# Weekly summary (run Fridays)
python scheduled_reports.py weekly
```

### 4. **alert_check.py** - Quick Emergency Check
One command to check for urgent issues:
```bash
python alert_check.py
```

### 5. **quick_status.py** - Fastest Status Check
Super simple status in seconds:
```bash
python quick_status.py
```

## Setting Up Automated Monitoring

### Windows Task Scheduler Setup
1. Open Task Scheduler
2. Create Basic Task
3. Set schedule and script path

Example for morning report:
```
Program: python
Arguments: C:\path\to\mgc_trader\scheduled_reports.py morning
Start in: C:\path\to\mgc_trader
```

### OR Use Cron (if WSL/Linux):
```bash
# Edit crontab
crontab -e

# Add scheduled tasks
# Morning report at 5:45 AM
45 5 * * * cd /path/to/mgc_trader && python scheduled_reports.py morning

# Midday report at noon
0 12 * * * cd /path/to/mgc_trader && python scheduled_reports.py midday

# EOD report at 5:30 PM
30 17 * * * cd /path/to/mgc_trader && python scheduled_reports.py eod

# Alert check every 30 minutes during trading hours
*/30 6-17 * * 1-5 cd /path/to/mgc_trader && python alert_check.py
```

## Quick Commands for Your Phone

Create these shortcuts for remote checking:

### Check Everything:
```bash
ssh adam@192.168.0.58 "cd mgc_trader && python monitor_suite.py all"
```

### Quick Status:
```bash
ssh adam@192.168.0.58 "cd mgc_trader && python quick_status.py"
```

### Alert Check:
```bash
ssh adam@192.168.0.58 "cd mgc_trader && python alert_check.py"
```

## Cost Savings Breakdown

| Check Type | Claude API | Local AI | Daily Savings |
|------------|-----------|----------|---------------|
| Status checks (10x) | $30 | $0 | $30 |
| Error scans (5x) | $10 | $0 | $10 |
| Reports (3x) | $15 | $0 | $15 |
| **Total Daily** | **$55** | **$0** | **$55** |
| **Monthly** | **$1,650** | **$0** | **$1,650** |

## Ollama Model Recommendations

For trading monitoring, these models work best:
```bash
# Best overall (8B parameters)
ollama pull llama3

# Fastest (3B parameters)
ollama pull phi3

# Good for code analysis
ollama pull codellama
```

## Tips for Best Results

1. **Keep logs clean** - The AI reads your logs, so good logging = better analysis
2. **Use the right tool** - quick_status.py for speed, monitor_suite.py for detail
3. **Set up alerts** - Use continuous_monitor.py during critical trades
4. **Review reports** - Check the trading_reports/ folder for insights
5. **Trust but verify** - Local AI is good but double-check critical decisions

## Testing Your Setup

Run this test sequence:
```bash
# 1. Check Ollama is working
ollama run llama3 "Say hello"

# 2. Test quick status
python quick_status.py

# 3. Test full monitoring
python monitor_suite.py all

# 4. Generate a report
python scheduled_reports.py eod
```

If all work, you're saving $50+/day! 🎉