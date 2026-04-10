"""
MES 4H Strategy Search v2 - Alternatives to Keltner Channel
Optimized for speed with numpy-based backtesting
"""
import pandas as pd
import numpy as np
import json, time

DATA = "data/history/mes_continuous_4h.csv"
PV = 5.0  # point value
COMM = 1.24  # round trip commission
SLIP = 0.25  # slippage points
CAP = 50000

def load():
    df = pd.read_csv(DATA)
    df['datetime'] = pd.to_datetime(df['datetime'], utc=True)
    df = df.sort_values('datetime').reset_index(drop=True)
    return df

def atr(h, l, c, n=14):
    tr = np.maximum(h-l, np.maximum(np.abs(h-np.roll(c,1)), np.abs(l-np.roll(c,1))))
    tr[:1] = h[:1]-l[:1]
    return pd.Series(tr).rolling(n).mean().values

def ema(s, n):
    return pd.Series(s).ewm(span=n, adjust=False).mean().values

def rsi(c, n=2):
    d = np.diff(c, prepend=c[0])
    up = np.where(d>0, d, 0)
    dn = np.where(d<0, -d, 0)
    up_avg = pd.Series(up).rolling(n).mean().values
    dn_avg = pd.Series(dn).rolling(n).mean().values
    with np.errstate(divide='ignore', invalid='ignore'):
        rs = up_avg / np.where(dn_avg==0, np.nan, dn_avg)
    return 100 - 100/(1+rs)

def backtest_signals(o, h, l, c, signals, atr_vals=None, atr_stop_m=None, atr_tgt_m=None):
    """Fast backtest. signals: 1=go long, -1=go short, 0=no action, nan=ignore.
    Signal means: enter this direction (or reverse). Flat when signal goes to 0."""
    n = len(c)
    trades = []
    pos = 0
    ep = 0.0  # entry price
    sp = 0.0  # stop price
    tp = 0.0  # target price

    for i in range(n):
        sig = signals[i]
        if np.isnan(sig): sig = 0
        sig = int(sig)

        # Check stops/targets
        if pos != 0 and atr_stop_m is not None:
            if pos == 1:
                if l[i] <= sp:
                    pnl = (sp - ep - SLIP) * PV - COMM
                    trades.append(pnl)
                    pos = 0
                    continue
                if atr_tgt_m and h[i] >= tp:
                    pnl = (tp - ep - SLIP) * PV - COMM
                    trades.append(pnl)
                    pos = 0
                    continue
            else:
                if h[i] >= sp:
                    pnl = (ep - sp - SLIP) * PV - COMM
                    trades.append(pnl)
                    pos = 0
                    continue
                if atr_tgt_m and l[i] <= tp:
                    pnl = (ep - tp - SLIP) * PV - COMM
                    trades.append(pnl)
                    pos = 0
                    continue

        if sig != 0 and sig != pos:
            # Close existing
            if pos != 0:
                pnl = (c[i] - ep) * pos
                pnl_d = (pnl - SLIP) * PV - COMM
                trades.append(pnl_d)
            # Open new
            pos = sig
            ep = c[i]
            if atr_stop_m and atr_vals is not None and not np.isnan(atr_vals[i]):
                av = atr_vals[i]
                sp = ep - sig * atr_stop_m * av
                if atr_tgt_m:
                    tp = ep + sig * atr_tgt_m * av
        elif sig == 0 and pos != 0:
            # Only close if signal explicitly goes to 0 (for MR strategies)
            pass  # We don't use 0 signals to close in this version - reversal-based

    # Close open
    if pos != 0:
        pnl = (c[-1] - ep) * pos
        trades.append((pnl - SLIP) * PV - COMM)

    return calc_stats(trades)

def calc_stats(trades):
    if len(trades) < 5:
        return None
    t = np.array(trades)
    total = t.sum()
    w = t[t>0]
    lo = t[t<=0]
    gw = w.sum() if len(w) else 0
    gl = abs(lo.sum()) if len(lo) else 0.01
    pf = gw/gl if gl>0 else 999
    wr = len(w)/len(t)*100
    aw = w.mean() if len(w) else 0
    al = abs(lo.mean()) if len(lo) else 0.01
    wl = aw/al if al>0 else 999
    eq = CAP + np.cumsum(t)
    pk = np.maximum.accumulate(eq)
    dd = pk - eq
    mdd = dd.max()
    mdd_pct = mdd/pk.max()*100 if pk.max()>0 else 0
    return {
        'trades': len(t), 'total_pnl': round(float(total),2), 'pf': round(float(pf),2),
        'win_rate': round(float(wr),1), 'avg_win': round(float(aw),2),
        'avg_loss': round(float(al),2), 'wl_ratio': round(float(wl),2),
        'max_dd': round(float(mdd),2), 'max_dd_pct': round(float(mdd_pct),1)
    }

# ── Strategies ──────────────────────────────────────────────────────────

def gen_rsi2_mr(c, rsi_p=2, os_lv=10, ob_lv=90, ex_lv=50):
    r = rsi(c, rsi_p)
    n = len(c)
    sig = np.zeros(n)
    pos = 0
    for i in range(1, n):
        rv = r[i-1]
        if np.isnan(rv): continue
        if pos == 0:
            if rv < os_lv: sig[i] = 1; pos = 1
            elif rv > ob_lv: sig[i] = -1; pos = -1
        elif pos == 1:
            if rv > ob_lv: sig[i] = -1; pos = -1
            elif rv > ex_lv: sig[i] = -99; pos = 0  # flat marker
        elif pos == -1:
            if rv < os_lv: sig[i] = 1; pos = 1
            elif rv < ex_lv: sig[i] = -99; pos = 0
    return sig

def gen_bb_mr(c, h_arr, l_arr, period=20, mult=2.0):
    mid = pd.Series(c).rolling(period).mean().values
    std = pd.Series(c).rolling(period).std().values
    upper = mid + mult*std
    lower = mid - mult*std
    n = len(c)
    sig = np.zeros(n)
    pos = 0
    for i in range(1, n):
        if np.isnan(upper[i]): continue
        ci = c[i]
        if pos == 0:
            if ci <= lower[i]: sig[i] = 1; pos = 1
            elif ci >= upper[i]: sig[i] = -1; pos = -1
        elif pos == 1:
            if ci >= upper[i]: sig[i] = -1; pos = -1
            elif ci >= mid[i]: sig[i] = -99; pos = 0
        elif pos == -1:
            if ci <= lower[i]: sig[i] = 1; pos = 1
            elif ci <= mid[i]: sig[i] = -99; pos = 0
    return sig

def gen_zscore_mr(c, lookback=20, entry_z=2.0, exit_z=0.0):
    ma = pd.Series(c).rolling(lookback).mean().values
    std = pd.Series(c).rolling(lookback).std().values
    with np.errstate(divide='ignore', invalid='ignore'):
        z = (c - ma) / np.where(std==0, np.nan, std)
    n = len(c)
    sig = np.zeros(n)
    pos = 0
    for i in range(1, n):
        if np.isnan(z[i]): continue
        if pos == 0:
            if z[i] < -entry_z: sig[i] = 1; pos = 1
            elif z[i] > entry_z: sig[i] = -1; pos = -1
        elif pos == 1:
            if z[i] > entry_z: sig[i] = -1; pos = -1
            elif z[i] >= exit_z: sig[i] = -99; pos = 0
        elif pos == -1:
            if z[i] < -entry_z: sig[i] = 1; pos = 1
            elif z[i] <= -exit_z: sig[i] = -99; pos = 0
    return sig

def gen_donchian(h_arr, l_arr, c, entry_p=20, exit_p=10):
    dh = pd.Series(h_arr).rolling(entry_p).max().values
    dl = pd.Series(l_arr).rolling(entry_p).min().values
    exh = pd.Series(h_arr).rolling(exit_p).max().values
    exl = pd.Series(l_arr).rolling(exit_p).min().values
    n = len(c)
    sig = np.zeros(n)
    pos = 0
    for i in range(1, n):
        if np.isnan(dh[i-1]): continue
        ci = c[i]
        if pos == 0:
            if ci > dh[i-1]: sig[i] = 1; pos = 1
            elif ci < dl[i-1]: sig[i] = -1; pos = -1
        elif pos == 1:
            if ci < dl[i-1]: sig[i] = -1; pos = -1
            elif ci < exl[i-1]: sig[i] = -99; pos = 0
        elif pos == -1:
            if ci > dh[i-1]: sig[i] = 1; pos = 1
            elif ci > exh[i-1]: sig[i] = -99; pos = 0
    return sig

def gen_bb_squeeze(c, h_arr, l_arr, bb_p=20, bb_m=2.0, kc_p=20, kc_m=1.5):
    mid_bb = pd.Series(c).rolling(bb_p).mean().values
    std_bb = pd.Series(c).rolling(bb_p).std().values
    upper_bb = mid_bb + bb_m*std_bb
    lower_bb = mid_bb - bb_m*std_bb
    kc_mid = ema(c, kc_p)
    a = atr(h_arr, l_arr, c, kc_p)
    kc_upper = kc_mid + kc_m*a
    kc_lower = kc_mid - kc_m*a
    squeeze = (lower_bb > kc_lower) & (upper_bb < kc_upper)
    mom = c - mid_bb
    n = len(c)
    sig = np.zeros(n)
    pos = 0
    was_sq = False
    for i in range(1, n):
        if np.isnan(upper_bb[i]): continue
        if squeeze[i]:
            was_sq = True
        if pos == 0 and was_sq and not squeeze[i]:
            was_sq = False
            if mom[i] > 0: sig[i] = 1; pos = 1
            else: sig[i] = -1; pos = -1
        elif pos != 0:
            if (pos==1 and mom[i]<0) or (pos==-1 and mom[i]>0):
                sig[i] = -99; pos = 0; was_sq = False
    return sig

def gen_3bar_rev(c):
    n = len(c)
    sig = np.zeros(n)
    pos = 0
    for i in range(3, n):
        if c[i-2]<c[i-3] and c[i-1]<c[i-2] and c[i]>c[i-1]:
            if pos != 1: sig[i] = 1; pos = 1
        elif c[i-2]>c[i-3] and c[i-1]>c[i-2] and c[i]<c[i-1]:
            if pos != -1: sig[i] = -1; pos = -1
    return sig

def gen_consec_mr(c, nb=3):
    n = len(c)
    sig = np.zeros(n)
    pos = 0
    for i in range(nb, n):
        all_down = all(c[i-nb+j+1] < c[i-nb+j] for j in range(nb))
        all_up = all(c[i-nb+j+1] > c[i-nb+j] for j in range(nb))
        if pos == 0:
            if all_down: sig[i] = 1; pos = 1
            elif all_up: sig[i] = -1; pos = -1
        elif pos == 1 and all_up: sig[i] = -1; pos = -1
        elif pos == -1 and all_down: sig[i] = 1; pos = 1
    return sig

def gen_ema_cross(c, fast=9, slow=21):
    ef = ema(c, fast)
    es = ema(c, slow)
    n = len(c)
    sig = np.zeros(n)
    pos = 0
    for i in range(1, n):
        if np.isnan(es[i]): continue
        if ef[i]>es[i] and ef[i-1]<=es[i-1]:
            if pos!=1: sig[i]=1; pos=1
        elif ef[i]<es[i] and ef[i-1]>=es[i-1]:
            if pos!=-1: sig[i]=-1; pos=-1
    return sig

def gen_inside_bar(h_arr, l_arr, c):
    n = len(c)
    sig = np.zeros(n)
    pos = 0
    for i in range(2, n):
        if h_arr[i-1]<=h_arr[i-2] and l_arr[i-1]>=l_arr[i-2]:
            if c[i]>h_arr[i-1] and pos!=1: sig[i]=1; pos=1
            elif c[i]<l_arr[i-1] and pos!=-1: sig[i]=-1; pos=-1
    return sig

def backtest2(o, h, l, c, raw_sig, atr_v=None, sm=None, tm=None):
    """Backtest with reversal signals. -99 = go flat."""
    n = len(c)
    trades = []
    pos = 0
    ep = 0.0
    stop = 0.0
    tgt = 0.0

    for i in range(n):
        s = raw_sig[i]

        # Check ATR stops/targets first
        if pos != 0 and sm is not None and atr_v is not None:
            if pos == 1:
                if l[i] <= stop:
                    trades.append((stop - ep - SLIP)*PV - COMM)
                    pos = 0; continue
                if tm and h[i] >= tgt:
                    trades.append((tgt - ep - SLIP)*PV - COMM)
                    pos = 0; continue
            else:
                if h[i] >= stop:
                    trades.append((ep - stop - SLIP)*PV - COMM)
                    pos = 0; continue
                if tm and l[i] <= tgt:
                    trades.append((ep - tgt - SLIP)*PV - COMM)
                    pos = 0; continue

        if s == -99:  # go flat
            if pos != 0:
                pnl = (c[i]-ep)*pos
                trades.append((pnl-SLIP)*PV - COMM)
                pos = 0
        elif s == 1 and pos != 1:
            if pos != 0:
                trades.append(((c[i]-ep)*pos - SLIP)*PV - COMM)
            pos = 1; ep = c[i]
            if sm and atr_v is not None and not np.isnan(atr_v[i]):
                stop = ep - sm*atr_v[i]
                if tm: tgt = ep + tm*atr_v[i]
        elif s == -1 and pos != -1:
            if pos != 0:
                trades.append(((c[i]-ep)*pos - SLIP)*PV - COMM)
            pos = -1; ep = c[i]
            if sm and atr_v is not None and not np.isnan(atr_v[i]):
                stop = ep + sm*atr_v[i]
                if tm: tgt = ep - tm*atr_v[i]

    if pos != 0:
        trades.append(((c[-1]-ep)*pos - SLIP)*PV - COMM)
    return calc_stats(trades)

def main():
    t0 = time.time()
    df = load()
    o = df['open'].values.astype(float)
    h = df['high'].values.astype(float)
    l = df['low'].values.astype(float)
    c = df['close'].values.astype(float)
    atr14 = atr(h, l, c, 14)

    results = []
    def rec(name, params, stats):
        if stats and stats['trades'] >= 10:
            stats['strategy'] = name
            stats['params'] = str(params)
            results.append(stats)

    # 1. RSI(2) MR - reduced grid
    print("Testing RSI(2) MR...")
    for rp, os_lv, ob_lv, ex_lv in [(2,5,95,50),(2,10,90,50),(2,10,90,60),(2,15,85,50),
                                      (2,20,80,50),(3,10,90,50),(3,15,85,50),(4,15,85,50),
                                      (2,5,95,40),(2,10,90,40),(3,10,90,40),(3,20,80,50)]:
        sig = gen_rsi2_mr(c, rp, os_lv, ob_lv, ex_lv)
        s = backtest2(o,h,l,c,sig)
        rec("RSI2_MR",{'rsi':rp,'os':os_lv,'ob':ob_lv,'ex':ex_lv},s)
        for sm,tm in [(2,3),(2,4),(3,5),(1.5,3)]:
            s = backtest2(o,h,l,c,sig,atr14,sm,tm)
            rec("RSI2_MR_ATR",{'rsi':rp,'os':os_lv,'ob':ob_lv,'ex':ex_lv,'sm':sm,'tm':tm},s)

    # 2. BB MR
    print("Testing BB MR...")
    for bp, bm in [(15,1.5),(15,2.0),(20,1.5),(20,2.0),(20,2.5),(20,3.0),(25,2.0),(25,2.5),(30,2.0),(30,2.5)]:
        sig = gen_bb_mr(c, h, l, bp, bm)
        s = backtest2(o,h,l,c,sig)
        rec("BB_MR",{'p':bp,'m':bm},s)
        for sm,tm in [(2,3),(2,4),(3,5)]:
            s = backtest2(o,h,l,c,sig,atr14,sm,tm)
            rec("BB_MR_ATR",{'p':bp,'m':bm,'sm':sm,'tm':tm},s)

    # 3. Z-Score MR
    print("Testing Z-Score MR...")
    for lb, ez, xz in [(10,1.5,0),(10,2.0,0),(15,1.5,0),(15,2.0,0),(20,1.5,0),(20,2.0,0),
                         (20,2.5,0),(30,2.0,0),(10,1.5,0.5),(15,2.0,0.5),(20,2.0,0.5)]:
        sig = gen_zscore_mr(c, lb, ez, xz)
        s = backtest2(o,h,l,c,sig)
        rec("ZScore_MR",{'lb':lb,'ez':ez,'xz':xz},s)
        for sm,tm in [(2,3),(2,4),(3,5)]:
            s = backtest2(o,h,l,c,sig,atr14,sm,tm)
            rec("ZScore_MR_ATR",{'lb':lb,'ez':ez,'xz':xz,'sm':sm,'tm':tm},s)

    # 4. Donchian
    print("Testing Donchian...")
    for ep, xp in [(10,5),(15,5),(15,7),(20,5),(20,7),(20,10),(30,10),(30,15),(40,15),(40,20)]:
        sig = gen_donchian(h, l, c, ep, xp)
        s = backtest2(o,h,l,c,sig)
        rec("Donchian",{'e':ep,'x':xp},s)
        for sm,tm in [(2,4),(3,5),(3,6)]:
            s = backtest2(o,h,l,c,sig,atr14,sm,tm)
            rec("Donchian_ATR",{'e':ep,'x':xp,'sm':sm,'tm':tm},s)

    # 5. BB Squeeze
    print("Testing BB Squeeze...")
    for kc_m in [1.0, 1.5, 2.0]:
        sig = gen_bb_squeeze(c, h, l, 20, 2.0, 20, kc_m)
        s = backtest2(o,h,l,c,sig)
        rec("BB_Squeeze",{'kc_m':kc_m},s)
        for sm,tm in [(2,3),(2,4),(3,5)]:
            s = backtest2(o,h,l,c,sig,atr14,sm,tm)
            rec("BB_Squeeze_ATR",{'kc_m':kc_m,'sm':sm,'tm':tm},s)

    # 6. 3-Bar Reversal
    print("Testing 3-Bar Reversal...")
    sig = gen_3bar_rev(c)
    s = backtest2(o,h,l,c,sig)
    rec("3BarRev",{},s)
    for sm,tm in [(1.5,2.5),(2,3),(2,4),(3,5),(3,6)]:
        s = backtest2(o,h,l,c,sig,atr14,sm,tm)
        rec("3BarRev_ATR",{'sm':sm,'tm':tm},s)

    # 7. Consecutive MR
    print("Testing Consecutive MR...")
    for nb in [2,3,4,5]:
        sig = gen_consec_mr(c, nb)
        s = backtest2(o,h,l,c,sig)
        rec("ConsecMR",{'n':nb},s)
        for sm,tm in [(1.5,2.5),(2,3),(2,4),(3,5)]:
            s = backtest2(o,h,l,c,sig,atr14,sm,tm)
            rec("ConsecMR_ATR",{'n':nb,'sm':sm,'tm':tm},s)

    # 8. EMA Cross
    print("Testing EMA Cross...")
    for f, sl in [(5,15),(5,20),(8,20),(8,21),(9,21),(9,30),(12,30),(12,50),(5,50)]:
        sig = gen_ema_cross(c, f, sl)
        s = backtest2(o,h,l,c,sig)
        rec("EMA_Cross",{'f':f,'s':sl},s)
        for sm,tm in [(2,3),(2,4),(3,5)]:
            s = backtest2(o,h,l,c,sig,atr14,sm,tm)
            rec("EMA_Cross_ATR",{'f':f,'s':sl,'sm':sm,'tm':tm},s)

    # 9. Inside Bar
    print("Testing Inside Bar...")
    sig = gen_inside_bar(h, l, c)
    s = backtest2(o,h,l,c,sig)
    rec("InsideBar",{},s)
    for sm,tm in [(1.5,2.5),(2,3),(2,4),(3,5),(3,6),(2,5)]:
        s = backtest2(o,h,l,c,sig,atr14,sm,tm)
        rec("InsideBar_ATR",{'sm':sm,'tm':tm},s)

    # Sort by PnL
    results.sort(key=lambda x: x['total_pnl'], reverse=True)

    print(f"\n{'='*130}")
    print(f"{'#':<4} {'Strategy':<20} {'Params':<50} {'Trd':>5} {'PnL($)':>10} {'PF':>6} {'WR%':>6} {'W/L':>5} {'DD%':>6}")
    print(f"{'='*130}")
    for i, r in enumerate(results[:80]):
        print(f"{i+1:<4} {r['strategy']:<20} {r['params'][:49]:<50} {r['trades']:>5} {r['total_pnl']:>10,.0f} {r['pf']:>6.2f} {r['win_rate']:>6.1f} {r['wl_ratio']:>5.1f} {r['max_dd_pct']:>6.1f}")

    winners = [r for r in results if r['pf']>=1.5 and r['trades']>=40 and r['max_dd_pct']<25]
    winners.sort(key=lambda x: x['total_pnl'], reverse=True)

    print(f"\n{'='*80}")
    print(f"WINNERS (PF>=1.5, 40+ trades, DD<25%): {len(winners)}")
    print(f"{'='*80}")
    for i, r in enumerate(winners[:20]):
        print(f"{i+1}. {r['strategy']} {r['params']}")
        print(f"   ${r['total_pnl']:,.0f} | PF {r['pf']} | {r['trades']}t | WR {r['win_rate']}% | W/L {r['wl_ratio']} | DD {r['max_dd_pct']}%")

    # Relax criteria if no winners
    if not winners:
        relaxed = [r for r in results if r['pf']>=1.3 and r['trades']>=20]
        relaxed.sort(key=lambda x: x['total_pnl'], reverse=True)
        print(f"\nRelaxed winners (PF>=1.3, 20+ trades): {len(relaxed)}")
        for i, r in enumerate(relaxed[:20]):
            print(f"{i+1}. {r['strategy']} {r['params']}")
            print(f"   ${r['total_pnl']:,.0f} | PF {r['pf']} | {r['trades']}t | WR {r['win_rate']}% | W/L {r['wl_ratio']} | DD {r['max_dd_pct']}%")

    with open("backtest_mes_4h_v2_results.json","w") as f:
        json.dump(results, f, indent=2)
    with open("backtest_mes_4h_v2_summary.txt","w") as f:
        f.write(f"MES 4H Strategy Search v2\nTotal tested: {len(results)}\nWinners: {len(winners)}\n\n")
        for i, r in enumerate((winners or results)[:20]):
            f.write(f"{i+1}. {r['strategy']} {r['params']}\n")
            f.write(f"   ${r['total_pnl']:,.0f} | PF {r['pf']} | {r['trades']}t | WR {r['win_rate']}% | W/L {r['wl_ratio']} | DD {r['max_dd_pct']}%\n\n")

    print(f"\nDone in {time.time()-t0:.1f}s. {len(results)} configs tested.")
    return results, winners

if __name__ == "__main__":
    main()
