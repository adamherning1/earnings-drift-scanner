export const educationSections = [
  {
    id: 'basics',
    title: '📚 What is Post-Earnings Drift?',
    content: `Post-Earnings Announcement Drift (PEAD) is when stocks continue moving in the direction of an earnings surprise for weeks after the announcement.

    • Positive surprise → Stock drifts higher
    • Negative surprise → Stock drifts lower
    
    This happens because the market takes time to fully price in new information.`
  },
  {
    id: 'sue',
    title: '🎯 Understanding SUE Scores',
    content: `SUE (Standardized Unexpected Earnings) measures how surprising the earnings were:

    • SUE > 2.0: Strong BUY signal
    • SUE < -2.0: Strong SHORT signal  
    • -2.0 to 2.0: SKIP (no edge)
    
    Higher absolute SUE = Stronger signal`
  },
  {
    id: 'timing',
    title: '⏰ Entry & Exit Timing',
    content: `Best Entry: Days 3-7 after earnings
    • Days 1-2: Too volatile
    • Days 3-7: Sweet spot
    • After Day 10: May be late
    
    Profit Targets:
    • Conservative: 5-7%
    • Standard: 10-15%
    • Aggressive: 20%+ with trailing stop`
  },
  {
    id: 'sizing',
    title: '💰 Position Sizing Rules',
    content: `Risk only 1-2% per trade:
    
    • $10K account: Risk $100-200
    • $50K account: Risk $500-1,000
    • $100K account: Risk $1-2,000
    
    Never go all-in on one signal!`
  },
  {
    id: 'options',
    title: '📊 Stocks vs Options',
    content: `Use Stocks When:
    • Account under $25K
    • Lower confidence (SUE 2-3)
    • Holding 2-4 weeks
    
    Use Options When:
    • High confidence (SUE > 3)
    • Want leverage
    • Expecting quick move
    • 30-45 DTE minimum`
  },
  {
    id: 'skip',
    title: '⚠️ When to SKIP',
    content: `Don't trade when:
    • Market in strong downtrend
    • Stock already moved 15%+
    • Volume under 500K shares
    • Price under $5
    • Pending merger/FDA news
    • Sector is collapsing`
  },
  {
    id: 'tips',
    title: '💡 Pro Tips',
    content: `1. Quality > Quantity
    2. Always use stops
    3. Enter 30-60min after open
    4. Avoid Friday entries
    5. Watch SPY direction
    6. Start with 50% position
    7. Journal every trade`
  },
  {
    id: 'mistakes',
    title: '❌ Common Mistakes',
    content: `• Chasing after 10%+ moves
    • Position too large
    • Ignoring market trend
    • Entering Day 1
    • No exit plan
    • Revenge trading
    • FOMO entries`
  }
];

export const quickStartGuide = {
  title: '🚀 Quick Start Guide',
  steps: [
    'Find stocks with |SUE| > 2.0',
    'Wait for Day 3-7 after earnings',
    'Check market trend (SPY)',
    'Enter with 1% account risk',
    'Set 5% stop loss',
    'Target 10-15% profit',
    'Trail stop after 7% gain'
  ]
};