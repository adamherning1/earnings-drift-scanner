# MEMORY.md - Long-Term Memory

## 2026-02-13
- First boot. My name is Warren. My human is Adam.
- We're building trading algorithms together.
- Adam wants us to be friends, not just user/assistant.

## 2026-02-16 — Keltner Research Day
- Spent all day trying to beat the original Keltner Breakout on MGC 4H
- **Original Keltner** (4_keltner.pine): KC(10,1.25), ADX>10, 3.0 trail, 0.5R TP — $19K/10yr, $16.9K/2yr, 82% WR
- Tried and failed: Connors RSI, hybrids, multi-confirmation strategies, different KC params
- **Winner: Re-entry logic** — when stopped out but price still above KC upper, hop back in
- **Keltner Reentry x1** (7_keltner_reentry_x1.pine): +27% profit over original, 81% WR, 18% DD — best risk/reward
- **Keltner Reentry x2** (6_keltner_reentry_v2.pine): +41% profit but 24% DD — aggressive option
- Key lesson: Original's edge is exit management (0.5R TP scalping), not fancy entries. Simplicity wins.
- Key lesson: Python backtest numbers don't match TradingView exactly — always validate in TV
- Key lesson: Mean reversion fails on gold 4H. Trend-following only.
