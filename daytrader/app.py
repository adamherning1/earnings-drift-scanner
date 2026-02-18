"""Day Trading Futures Dashboard — Flask app."""
from flask import Flask, render_template, request, jsonify
import numpy as np, pandas as pd, json, traceback
from datetime import datetime
from pathlib import Path

try:
    import yfinance as yf
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance", "-q"])
    import yfinance as yf

app = Flask(__name__)

# ── Config ────────────────────────────────────────────────────────────
CONTRACTS = {
    "ES=F":  {"name": "E-mini S&P 500",    "micro": "MES", "pt_val": 5.0,  "comm": 1.24, "tick": 0.25},
    "NQ=F":  {"name": "E-mini Nasdaq 100",  "micro": "MNQ", "pt_val": 2.0,  "comm": 1.24, "tick": 0.25},
    "YM=F":  {"name": "E-mini Dow",         "micro": "MYM", "pt_val": 0.50, "comm": 1.24, "tick": 1.0},
    "RTY=F": {"name": "E-mini Russell 2000","micro": "M2K", "pt_val": 5.0,  "comm": 1.24, "tick": 0.10},
}
DEFAULT_CAPITAL = 5000.0

# ── Data Cache ────────────────────────────────────────────────────────
_data_cache = {}

def fetch_data(symbol="ES=F", period="730d", interval="1h"):
    key = f"{symbol}_{period}_{interval}"
    if key not in _data_cache:
        df = yf.download(symbol, period=period, interval=interval, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.dropna(subset=["Close","Volume"], inplace=True)
        _data_cache[key] = df
    return _data_cache[key].copy()


# ── Strategy Implementations ──────────────────────────────────────────
def strat_orb(df, orb_bars=1, target_mult=1.0, min_range=2.0):
    """Opening Range Breakout."""
    trades = []
    df["date"] = df.index.date
    for date, group in df.groupby("date"):
        if len(group) < orb_bars + 2: continue
        orb_high = group.iloc[:orb_bars]["High"].max()
        orb_low = group.iloc[:orb_bars]["Low"].min()
        orb_range = orb_high - orb_low
        if orb_range < min_range: continue
        for i in range(orb_bars, min(orb_bars + 3, len(group))):
            bar = group.iloc[i]
            if bar["High"] > orb_high:
                entry = orb_high + 0.25; stop = orb_low; target = entry + orb_range * target_mult
                exit_p, pnl_dir = _sim_long(group, i, entry, stop, target)
                trades.append(_trade(date, "long", entry, exit_p, (exit_p-entry)*5.0, group.iloc[i].name, group.iloc[min(i+6,len(group)-1)].name))
                break
            elif bar["Low"] < orb_low:
                entry = orb_low - 0.25; stop = orb_high; target = entry - orb_range * target_mult
                exit_p, _ = _sim_short(group, i, entry, stop, target)
                trades.append(_trade(date, "short", entry, exit_p, (entry-exit_p)*5.0, group.iloc[i].name, group.iloc[min(i+6,len(group)-1)].name))
                break
    return trades

def strat_vwap(df, entry_std=1.5, stop_std=2.0):
    """VWAP Mean Reversion."""
    trades = []
    df["date"] = df.index.date
    df["typical"] = (df["High"] + df["Low"] + df["Close"]) / 3
    for date, group in df.groupby("date"):
        if len(group) < 4: continue
        g = group.copy()
        g["cum_vol"] = g["Volume"].cumsum()
        g["cum_tp_vol"] = (g["typical"] * g["Volume"]).cumsum()
        g["vwap"] = g["cum_tp_vol"] / g["cum_vol"]
        g["vwap_dev"] = ((g["typical"] - g["vwap"])**2 * g["Volume"]).cumsum() / g["cum_vol"]
        g["vwap_std"] = np.sqrt(g["vwap_dev"].clip(lower=0))
        traded = False
        for i in range(2, len(g)):
            if traded: break
            row = g.iloc[i]; vwap = row["vwap"]; std = row["vwap_std"]
            if std < 1: continue
            if row["Close"] > vwap + entry_std * std:
                entry = row["Close"]; stop = vwap + stop_std * std
                for j in range(i+1, len(g)):
                    b = g.iloc[j]
                    if b["High"] >= stop:
                        trades.append(_trade(date,"short",entry,stop,(entry-stop)*5.0,row.name,b.name)); traded=True; break
                    if b["Low"] <= b["vwap"]:
                        trades.append(_trade(date,"short",entry,b["vwap"],(entry-b["vwap"])*5.0,row.name,b.name)); traded=True; break
                else:
                    ep = g.iloc[-1]["Close"]
                    trades.append(_trade(date,"short",entry,ep,(entry-ep)*5.0,row.name,g.iloc[-1].name)); traded=True
            elif row["Close"] < vwap - entry_std * std:
                entry = row["Close"]; stop = vwap - stop_std * std
                for j in range(i+1, len(g)):
                    b = g.iloc[j]
                    if b["Low"] <= stop:
                        trades.append(_trade(date,"long",entry,stop,(stop-entry)*5.0,row.name,b.name)); traded=True; break
                    if b["High"] >= b["vwap"]:
                        trades.append(_trade(date,"long",entry,b["vwap"],(b["vwap"]-entry)*5.0,row.name,b.name)); traded=True; break
                else:
                    ep = g.iloc[-1]["Close"]
                    trades.append(_trade(date,"long",entry,ep,(ep-entry)*5.0,row.name,g.iloc[-1].name)); traded=True
    return trades

def strat_ema_cross(df, fast=8, slow=21, stop_pts=10, target_pts=20):
    """EMA Momentum Crossover."""
    trades = []
    df["ema_f"] = df["Close"].ewm(span=fast, adjust=False).mean()
    df["ema_s"] = df["Close"].ewm(span=slow, adjust=False).mean()
    df["date"] = df.index.date
    for i in range(1, len(df)):
        prev, curr = df.iloc[i-1], df.iloc[i]
        if prev["ema_f"] <= prev["ema_s"] and curr["ema_f"] > curr["ema_s"]:
            entry = curr["Close"]; stop = entry - stop_pts; target = entry + target_pts
            exit_p, _ = _sim_long(df, i, entry, stop, target, max_bars=8)
            trades.append(_trade(curr.name.date() if hasattr(curr.name,'date') else None, "long", entry, exit_p, (exit_p-entry)*5.0, curr.name, df.iloc[min(i+8,len(df)-1)].name))
        elif prev["ema_f"] >= prev["ema_s"] and curr["ema_f"] < curr["ema_s"]:
            entry = curr["Close"]; stop = entry + stop_pts; target = entry - target_pts
            exit_p, _ = _sim_short(df, i, entry, stop, target, max_bars=8)
            trades.append(_trade(curr.name.date() if hasattr(curr.name,'date') else None, "short", entry, exit_p, (entry-exit_p)*5.0, curr.name, df.iloc[min(i+8,len(df)-1)].name))
    return trades

def strat_prev_day_levels(df, atr_stop_mult=1.5, tp_mult=2.0):
    """Previous Day High/Low Breakout."""
    trades = []
    df["date"] = df.index.date
    dates = sorted(df["date"].unique())
    for d_idx in range(1, len(dates)):
        prev_day = df[df["date"] == dates[d_idx-1]]
        today = df[df["date"] == dates[d_idx]]
        if len(prev_day) < 2 or len(today) < 3: continue
        pdh = prev_day["High"].max(); pdl = prev_day["Low"].min()
        atr = prev_day["High"].values - prev_day["Low"].values
        avg_atr = np.mean(atr) if len(atr) > 0 else 5.0
        for i in range(1, min(5, len(today))):
            bar = today.iloc[i]
            if bar["High"] > pdh and today.iloc[i-1]["High"] <= pdh:
                entry = pdh + 0.25; stop = entry - avg_atr * atr_stop_mult; target = entry + avg_atr * tp_mult
                exit_p, _ = _sim_long(today, i, entry, stop, target)
                trades.append(_trade(dates[d_idx], "long", entry, exit_p, (exit_p-entry)*5.0, bar.name, today.iloc[min(i+6,len(today)-1)].name))
                break
            elif bar["Low"] < pdl and today.iloc[i-1]["Low"] >= pdl:
                entry = pdl - 0.25; stop = entry + avg_atr * atr_stop_mult; target = entry - avg_atr * tp_mult
                exit_p, _ = _sim_short(today, i, entry, stop, target)
                trades.append(_trade(dates[d_idx], "short", entry, exit_p, (entry-exit_p)*5.0, bar.name, today.iloc[min(i+6,len(today)-1)].name))
                break
    return trades

# ── Sim helpers ───────────────────────────────────────────────────────
def _sim_long(df_or_group, start_i, entry, stop, target, max_bars=20):
    for j in range(start_i+1, min(start_i+max_bars, len(df_or_group))):
        b = df_or_group.iloc[j]
        if b["Low"] <= stop: return stop, -1
        if b["High"] >= target: return target, 1
    return df_or_group.iloc[min(start_i+max_bars-1, len(df_or_group)-1)]["Close"], 0

def _sim_short(df_or_group, start_i, entry, stop, target, max_bars=20):
    for j in range(start_i+1, min(start_i+max_bars, len(df_or_group))):
        b = df_or_group.iloc[j]
        if b["High"] >= stop: return stop, -1
        if b["Low"] <= target: return target, 1
    return df_or_group.iloc[min(start_i+max_bars-1, len(df_or_group)-1)]["Close"], 0

def _trade(date, side, entry, exit_p, pnl, entry_time, exit_time):
    return {
        "date": str(date), "side": side,
        "entry_price": round(float(entry), 2), "exit_price": round(float(exit_p), 2),
        "pnl": round(float(pnl), 2),
        "entry_time": str(entry_time), "exit_time": str(exit_time),
    }

# ── Compute metrics ──────────────────────────────────────────────────
def compute_metrics(trades, capital, commission):
    if not trades: return _empty_metrics(capital)
    pnls = [t["pnl"] for t in trades]
    gross = sum(pnls); total_comm = len(trades) * commission; net = gross - total_comm
    wins = [p for p in pnls if p > 0]; losses = [p for p in pnls if p <= 0]
    gw = sum(wins) if wins else 0; gl = abs(sum(losses)) if losses else 0.001
    
    # Equity curve
    eq = [capital]
    for p in pnls: eq.append(eq[-1] + p - commission)
    eq_arr = np.array(eq)
    rm = np.maximum.accumulate(eq_arr)
    dd = eq_arr - rm
    max_dd = float(abs(dd.min()))
    max_dd_pct = float(abs((dd / np.where(rm > 0, rm, 1)).min()) * 100)
    
    # By hour analysis
    hour_pnl = {}
    for t in trades:
        try:
            h = pd.Timestamp(t["entry_time"]).hour
            hour_pnl.setdefault(h, []).append(t["pnl"] - commission)
        except: pass
    hour_stats = {str(h): {"trades": len(ps), "net": round(sum(ps),2), "avg": round(np.mean(ps),2), "wr": round(len([p for p in ps if p > 0])/len(ps)*100,1)} for h, ps in sorted(hour_pnl.items())}
    
    # By day of week
    dow_pnl = {}
    for t in trades:
        try:
            d = pd.Timestamp(t["entry_time"]).day_name()
            dow_pnl.setdefault(d, []).append(t["pnl"] - commission)
        except: pass
    dow_stats = {d: {"trades": len(ps), "net": round(sum(ps),2), "avg": round(np.mean(ps),2), "wr": round(len([p for p in ps if p > 0])/len(ps)*100,1)} for d, ps in dow_pnl.items()}
    
    # Streak analysis
    streak = 0; max_win_streak = 0; max_loss_streak = 0; curr_streak = 0
    for p in pnls:
        if p > 0:
            curr_streak = curr_streak + 1 if curr_streak > 0 else 1
            max_win_streak = max(max_win_streak, curr_streak)
        else:
            curr_streak = curr_streak - 1 if curr_streak < 0 else -1
            max_loss_streak = max(max_loss_streak, abs(curr_streak))
    
    return {
        "net_profit": round(net, 2),
        "gross_profit": round(gross, 2),
        "total_trades": len(trades),
        "winners": len(wins),
        "losers": len(losses),
        "win_rate": round(len(wins)/len(trades)*100, 1),
        "profit_factor": round(gw/gl, 2),
        "avg_win": round(np.mean(wins), 2) if wins else 0,
        "avg_loss": round(np.mean(losses), 2) if losses else 0,
        "avg_pnl": round(net/len(trades), 2),
        "max_win": round(max(pnls), 2),
        "max_loss": round(min(pnls), 2),
        "max_drawdown": round(max_dd, 2),
        "max_drawdown_pct": round(max_dd_pct, 2),
        "return_pct": round(net/capital*100, 2),
        "total_commissions": round(total_comm, 2),
        "max_win_streak": max_win_streak,
        "max_loss_streak": max_loss_streak,
        "expectancy": round(net/len(trades), 2),
        "hour_stats": hour_stats,
        "dow_stats": dow_stats,
    }

def _empty_metrics(capital):
    return {"net_profit":0,"gross_profit":0,"total_trades":0,"winners":0,"losers":0,"win_rate":0,
            "profit_factor":0,"avg_win":0,"avg_loss":0,"avg_pnl":0,"max_win":0,"max_loss":0,
            "max_drawdown":0,"max_drawdown_pct":0,"return_pct":0,"total_commissions":0,
            "max_win_streak":0,"max_loss_streak":0,"expectancy":0,"hour_stats":{},"dow_stats":{}}

# ── Strategy registry ────────────────────────────────────────────────
STRATEGIES = {
    "orb": {"name": "Opening Range Breakout", "func": strat_orb, "desc": "First bar breakout with range target"},
    "vwap": {"name": "VWAP Mean Reversion", "func": strat_vwap, "desc": "Fade moves away from daily VWAP"},
    "ema_cross": {"name": "EMA Momentum Crossover", "func": strat_ema_cross, "desc": "8/21 EMA cross, fixed R:R"},
    "prev_day": {"name": "Prev Day Level Breakout", "func": strat_prev_day_levels, "desc": "Break above/below PDH/PDL"},
}

# ── Routes ────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/strategies")
def list_strategies():
    return jsonify([{"key":k,"name":v["name"],"desc":v["desc"]} for k,v in STRATEGIES.items()])

@app.route("/api/contracts")
def list_contracts():
    return jsonify([{"symbol":k,**v} for k,v in CONTRACTS.items()])

@app.route("/api/backtest", methods=["POST"])
def run_backtest():
    try:
        body = request.json or {}
        symbol = body.get("symbol", "ES=F")
        strat_key = body.get("strategy", "vwap")
        capital = float(body.get("capital", DEFAULT_CAPITAL))
        
        contract = CONTRACTS.get(symbol, CONTRACTS["ES=F"])
        df = fetch_data(symbol)
        
        if strat_key not in STRATEGIES:
            return jsonify({"error": f"Unknown strategy: {strat_key}"}), 400
        
        trades = STRATEGIES[strat_key]["func"](df)
        metrics = compute_metrics(trades, capital, contract["comm"])
        
        # Equity curve
        eq_vals = [capital]
        for t in trades: eq_vals.append(eq_vals[-1] + t["pnl"] - contract["comm"])
        eq_dates = ["start"] + [t.get("exit_time", t["date"]) for t in trades]
        
        # Drawdown
        eq_arr = np.array(eq_vals)
        rm = np.maximum.accumulate(eq_arr)
        dd_vals = ((eq_arr - rm) / np.where(rm > 0, rm, 1) * 100).tolist()
        
        # Price data
        price = {
            "dates": [str(d) for d in df.index],
            "open": df["Open"].round(2).tolist(),
            "high": df["High"].round(2).tolist(),
            "low": df["Low"].round(2).tolist(),
            "close": df["Close"].round(2).tolist(),
        }
        
        return jsonify({
            "metrics": metrics,
            "trades": trades,
            "equity": {"dates": eq_dates, "values": eq_vals},
            "drawdown": {"dates": eq_dates, "values": dd_vals},
            "price": price,
            "strategy_name": STRATEGIES[strat_key]["name"],
            "symbol": symbol,
            "contract": contract,
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/compare", methods=["POST"])
def run_compare():
    try:
        body = request.json or {}
        symbol = body.get("symbol", "ES=F")
        capital = float(body.get("capital", DEFAULT_CAPITAL))
        contract = CONTRACTS.get(symbol, CONTRACTS["ES=F"])
        df = fetch_data(symbol)
        
        results = {}
        for key, strat in STRATEGIES.items():
            trades = strat["func"](df)
            metrics = compute_metrics(trades, capital, contract["comm"])
            results[key] = {"name": strat["name"], "metrics": metrics, "trade_count": len(trades)}
        
        return jsonify({"results": results, "symbol": symbol})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("\n📈 Day Trading Dashboard running at http://localhost:5001\n")
    app.run(debug=True, port=5001)
