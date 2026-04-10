"""Refine the grid search winner KC(15,0.75) on MES 4H - fine-tune around best params."""
import asyncio; asyncio.set_event_loop(asyncio.new_event_loop())

import csv, json, os, sys
from pathlib import Path

# Reuse the backtest engine
sys.path.insert(0, str(Path(__file__).parent))
from backtest_mes_4h import (
    load_data, run_backtest, make_keltner_breakout, BACKTEST_DIR
)

def main():
    bars = load_data()
    
    print("Fine-tuning around KC(15, 0.75), Trail 2.0, TP 1.5...")
    print("Testing tighter parameter grid...\n")
    
    results = []
    
    kc_lengths = [12, 13, 14, 15, 16, 17, 18]
    kc_mults = [0.5, 0.6, 0.7, 0.75, 0.8, 0.9, 1.0]
    trail_mults = [1.5, 1.75, 2.0, 2.25, 2.5, 3.0]
    tp_rs = [1.0, 1.25, 1.5, 1.75, 2.0]
    adx_threshs = [0, 5, 10, 15, 20]
    
    total = len(kc_lengths) * len(kc_mults) * len(trail_mults) * len(tp_rs) * len(adx_threshs)
    print(f"Testing {total} combinations...")
    
    tested = 0
    for kl in kc_lengths:
        for km in kc_mults:
            for tm in trail_mults:
                for tpr in tp_rs:
                    for adx_t in adx_threshs:
                        tested += 1
                        if tested % 500 == 0:
                            print(f"  {tested}/{total}...")
                        
                        sig_fn = make_keltner_breakout(kc_len=kl, kc_mult=km, adx_thresh=adx_t, trail_mult=tm, tp_r=tpr)
                        stats = run_backtest(bars, sig_fn, direction_mode="both")
                        
                        if stats["num_trades"] < 30:
                            continue
                        
                        results.append({
                            "kc_len": kl, "kc_mult": km, "adx": adx_t,
                            "trail": tm, "tp_r": tpr,
                            **stats
                        })
    
    # Sort by composite score
    for r in results:
        r["score"] = (r["profit_factor"] * r["win_rate"] / 100 
                      * min(r["num_trades"] / 50, 1.5)
                      * max(0, 1 - r["max_dd_pct"] / 50))
    
    results.sort(key=lambda x: x["score"], reverse=True)
    
    print(f"\nTop 20 parameter sets:")
    print(f"{'KC Len':>6} {'Mult':>5} {'ADX':>4} {'Trail':>5} {'TP':>4} | {'P&L':>10} {'Trades':>6} {'WR%':>6} {'PF':>7} {'DD%':>6} {'Score':>6}")
    print("-" * 80)
    
    for r in results[:20]:
        marker = " ***" if r["win_rate"] >= 65 and r["profit_factor"] >= 1.5 and r["num_trades"] >= 50 and r["max_dd_pct"] < 25 else ""
        print(f"{r['kc_len']:>6} {r['kc_mult']:>5.2f} {r['adx']:>4} {r['trail']:>5.2f} {r['tp_r']:>4.1f} | "
              f"${r['total_pnl']:>9,.2f} {r['num_trades']:>6} {r['win_rate']:>5.1f}% {r['profit_factor']:>6.3f} {r['max_dd_pct']:>5.1f}% {r['score']:>5.2f}{marker}")
    
    # Find strategies meeting full threshold
    winners = [r for r in results if r["win_rate"] >= 65 and r["profit_factor"] >= 1.5 and r["num_trades"] >= 50 and r["max_dd_pct"] < 25]
    
    if winners:
        print(f"\n{'='*60}")
        print(f"WINNERS meeting full threshold ({len(winners)} found):")
        print(f"{'='*60}")
        for r in winners[:10]:
            print(f"  KC({r['kc_len']},{r['kc_mult']}), ADX>{r['adx']}, Trail {r['trail']}x, TP {r['tp_r']}R")
            print(f"    ${r['total_pnl']:.2f} | {r['num_trades']} trades | {r['win_rate']}% WR | PF {r['profit_factor']} | DD {r['max_dd_pct']}%")
        
        # Generate Pine Script for the best winner
        best = winners[0]
        pine = f'''// MES 4H Optimized Keltner Breakout
// KC({best['kc_len']}, {best['kc_mult']}), ADX>{best['adx']}, Trail {best['trail']}x ATR, TP {best['tp_r']}R
// Backtest: ${best['total_pnl']:.2f} | {best['num_trades']} trades | {best['win_rate']}% WR | PF {best['profit_factor']} | DD {best['max_dd_pct']}%
//@version=5
strategy("MES Keltner Breakout Optimized", overlay=true, default_qty_type=strategy.fixed, default_qty_value=1,
         commission_type=strategy.commission.cash_per_contract, commission_value=0.62,
         slippage=1)

// Inputs
kcLen   = input.int({best['kc_len']}, "KC Length", minval=5, maxval=50)
kcMult  = input.float({best['kc_mult']}, "KC Multiplier", minval=0.1, maxval=5.0, step=0.05)
adxThresh = input.float({best['adx']}, "ADX Threshold", minval=0, maxval=50)
trailMult = input.float({best['trail']}, "Trail ATR Multiplier", minval=0.5, maxval=10.0, step=0.25)
tpMult  = input.float({best['tp_r']}, "TP as R multiple", minval=0.1, maxval=5.0, step=0.1)

// Keltner Channel
basis = ta.ema(close, kcLen)
atrVal = ta.atr(kcLen)
upper = basis + kcMult * atrVal
lower = basis - kcMult * atrVal

// ADX
[diPlus, diMinus, adxVal] = ta.dmi(14, 14)

// Entry conditions
longCond  = close[1] > upper[1] and adxVal > adxThresh
shortCond = close[1] < lower[1] and adxVal > adxThresh

// Risk calculation
risk = atrVal * trailMult

// Long entry
if longCond and strategy.position_size == 0
    strategy.entry("Long", strategy.long)
    strategy.exit("Long TP/SL", "Long", stop=close - risk, limit=close + risk * tpMult)

// Short entry  
if shortCond and strategy.position_size == 0
    strategy.entry("Short", strategy.short)
    strategy.exit("Short TP/SL", "Short", stop=close + risk, limit=close - risk * tpMult)

// Plots
p1 = plot(upper, "Upper KC", color=color.green)
p2 = plot(lower, "Lower KC", color=color.red)
plot(basis, "Basis", color=color.blue)
fill(p1, p2, color=color.new(color.blue, 90))
'''
        pine_path = BACKTEST_DIR / "mes_keltner_optimized.pine"
        with open(pine_path, "w") as f:
            f.write(pine)
        print(f"\nPine script saved: {pine_path}")
    else:
        print("\nNo combos met full threshold. Closest:")
        # Show closest to threshold
        close_ones = [r for r in results if r["profit_factor"] >= 1.3 and r["num_trades"] >= 40]
        close_ones.sort(key=lambda x: x["score"], reverse=True)
        for r in close_ones[:5]:
            print(f"  KC({r['kc_len']},{r['kc_mult']}), ADX>{r['adx']}, Trail {r['trail']}x, TP {r['tp_r']}R")
            print(f"    ${r['total_pnl']:.2f} | {r['num_trades']} trades | {r['win_rate']}% WR | PF {r['profit_factor']} | DD {r['max_dd_pct']}%")

    # Save all results
    with open(Path(__file__).parent / "backtest_mes_4h_refine_results.json", "w") as f:
        json.dump(results[:100], f, indent=2)
    print(f"\nRefined results saved.")


if __name__ == "__main__":
    main()
