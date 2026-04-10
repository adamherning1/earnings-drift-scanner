# MGC Bot Adaptive Learning Implementation Plan

## Overview
Transform the MGC trading bot from rule-based to self-learning in 3 phases over 8-12 weeks.

## Current State (April 7, 2026)
- Bot Version: Adaptive Trading Bot v1 (rules-based)
- Trades Completed: 1 (loss of $293.88)
- Trading Hours: Fixed (was stopping at 1 PM, now runs until 5 PM ET)
- Auto-Reconnect: Implemented
- Learning Status: Framework present but not active

## Phase Timeline

### Phase 1: Baseline Performance (April 7 - April 21, 2026)
**Goal**: Establish baseline with 50-100 trades

**Metrics to Track**:
- Win rate
- Average win size
- Average loss size
- Profit factor
- Best/worst performing strategies
- Time of day performance

**Actions**:
- Monitor daily
- No parameter changes
- Document any issues
- Build trade database

**Exit Criteria**: 
- Minimum 50 trades completed
- 2 weeks of operation
- Stable performance pattern emerges

### Phase 2: Conservative Learning (April 21 - May 12, 2026)
**Goal**: Implement position sizing adaptation

**Features to Add**:
```python
# Position sizing based on recent performance
- Start: 2 contracts
- After 5 consecutive wins: 3 contracts
- After 8 consecutive wins: 4 contracts  
- After ANY loss: Back to 2 contracts
- Daily max: 4 contracts regardless of streak
```

**Safety Rules**:
- Never exceed 4 contracts
- Reset to base size on any loss
- Reduce if daily loss > $300

**Exit Criteria**:
- 100+ total trades
- Position sizing working smoothly
- Clear improvement in profit/drawdown ratio

### Phase 3: Full Adaptive Learning (May 12 - June 2026)
**Goal**: Full parameter optimization

**Features to Add**:
1. **Dynamic Stop Loss**
   - Tighten stops in choppy markets
   - Widen stops in trending markets
   - Based on ATR and recent win rate

2. **Strategy Filtering**
   - Track performance by strategy type
   - Disable strategies with <40% win rate
   - Increase frequency of high-performing setups

3. **Time-Based Adaptation**
   - Learn best trading hours
   - Reduce position size in typically bad hours
   - Skip low-probability times

4. **Market Regime Detection**
   - Trend vs Range identification
   - Adjust strategies based on regime
   - Different parameters for different market types

## Tracking Metrics

### Daily Metrics
- Trades taken
- Win/Loss ratio  
- P&L
- Strategies used
- Market regime

### Weekly Metrics
- Total P&L
- Win rate progression
- Parameter changes made
- Strategy performance breakdown

### Monthly Metrics
- ROI
- Maximum drawdown
- Sharpe ratio
- Best/worst days analysis

## Risk Management

### Phase 2 Limits
- Max position: 4 contracts
- Daily loss limit: $500
- Only adjust position size, nothing else

### Phase 3 Limits
- Parameter changes max once per day
- Backtesting required before any strategy change
- Manual approval for major adjustments

## Success Milestones

### End of Phase 1
- [ ] 50+ trades completed
- [ ] Baseline win rate established
- [ ] All bugs fixed
- [ ] Daily P&L tracking automated

### End of Phase 2  
- [ ] Position sizing algorithm active
- [ ] 100+ total trades
- [ ] Improved profit factor
- [ ] Lower drawdowns

### End of Phase 3
- [ ] 200+ total trades
- [ ] All adaptive features active
- [ ] Consistent profitability
- [ ] Ready for live trading consideration

## Implementation Notes

### Phase 2 Code Location
- `/mgc_trader/adaptive_position_sizing.py`
- Integrates with existing `adaptive_trading_bot.py`
- Activated via config flag

### Phase 3 Code Location
- `/mgc_trader/full_adaptive_learning.py`
- Modular design for easy enable/disable
- Extensive logging for all adaptations

## Reminder Schedule
- April 19: Phase 1 checkpoint (2 days before phase 2)
- April 21: Begin Phase 2 implementation  
- May 10: Phase 2 checkpoint
- May 12: Begin Phase 3 implementation
- June 1: Final review and optimization

## Contact for Each Phase
Warren will proactively notify Adam when:
1. Approaching phase transitions
2. Milestones are reached
3. Issues requiring attention arise
4. Performance significantly deviates from expectations