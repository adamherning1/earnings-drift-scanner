# 📦 Save Before Move Checklist - April 11, 2026

## Critical Files to Backup

### 1. Trading Logs
- [ ] adaptive_bot.log (complete history)
- [ ] mgc_trader.log
- [ ] All .log files in mgc_trader/

### 2. Trading Performance
- [ ] Current account balance
- [ ] Total trades completed (Phase 1: currently 4/50)
- [ ] Win/loss record
- [ ] adaptive_params.json

### 3. Configuration
- [ ] config.py (with all settings)
- [ ] adaptive_trading_bot.py (latest version)
- [ ] All monitoring scripts

### 4. Trade History
- [ ] Screenshot final TWS account statement
- [ ] Export trade history if possible
- [ ] Document any open positions (close before shutdown)

## Shutdown Procedure

1. **Close any open positions**
   - Check bot has no active trades
   - Verify position = 0

2. **Stop the bot gracefully**
   - Ctrl+C in bot window
   - Verify clean shutdown

3. **Save final logs**
   ```bash
   cd mgc_trader
   copy *.log C:\Backup\MGC_Logs_04112026\
   ```

4. **Close TWS/Gateway**
   - File → Exit
   - Don't just close window

## Post-Move Setup Notes

### When Setting Back Up:
1. Use IB Gateway (not TWS)
2. Enable "Save security settings" for auto-login
3. Consider IBC for full automation
4. Update config.py with new IPs if network changed

### Resume Trading:
- Start at Phase 1, trade 5/50
- Daily loss limit back to $500
- Review logs for any patterns
- Implement improvements we discovered

## Important Numbers to Remember
- Account balance: $____________ (fill in tomorrow)
- Total P&L to date: $____________
- Phase 1 trades: ____/50
- Win rate: ____%

---

**Save this file and all mgc_trader contents to external drive or cloud!**