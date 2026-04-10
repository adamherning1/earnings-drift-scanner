#!/usr/bin/env python3
"""
Quick fix to update the daily loss limit in adaptive_params.json
"""
import json

# Update the parameters
params = {
    'position_size': 2,
    'kc_length': 20,
    'kc_mult': 1.5,
    'atr_stop': 1.5,
    'take_profit_r': 1.2,
    'adx_threshold': 20,
    'max_daily_loss': 1200,  # Increased to allow trading today
    'max_trades_day': 15
}

# Save to file
with open('adaptive_params.json', 'w') as f:
    json.dump(params, f, indent=2)

print("✅ Updated max_daily_loss to $1200")
print("Bot will reload parameters on next check")