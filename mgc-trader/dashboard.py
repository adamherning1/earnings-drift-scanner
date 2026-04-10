"""
MGC Day Trader — Live Dashboard
Run: python dashboard.py
Open: http://localhost:5050
"""

import json
import os
import glob
from datetime import date, datetime
from pathlib import Path
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__)
DATA_DIR = Path(__file__).parent / "data"
LOG_DIR = Path(__file__).parent / "logs"


def read_jsonl(filepath):
    """Read a JSONL file and return list of dicts."""
    rows = []
    if not os.path.exists(filepath):
        return rows
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return rows


def available_dates():
    """Get all dates that have data files."""
    dates = set()
    for f in glob.glob(str(DATA_DIR / "bars_*.jsonl")):
        name = os.path.basename(f)
        ds = name.replace("bars_", "").replace(".jsonl", "")
        dates.add(ds)
    return sorted(dates, reverse=True)


@app.route("/")
def index():
    return DASHBOARD_HTML


@app.route("/api/dates")
def api_dates():
    return jsonify(available_dates())


@app.route("/api/data/<ds>")
def api_data(ds):
    """Return all data for a given date (YYYYMMDD)."""
    bars = read_jsonl(DATA_DIR / f"bars_{ds}.jsonl")
    signals = read_jsonl(DATA_DIR / f"signals_{ds}.jsonl")
    trades = read_jsonl(DATA_DIR / f"trades_{ds}.jsonl")
    context = read_jsonl(DATA_DIR / f"context_{ds}.jsonl")
    summary = read_jsonl(DATA_DIR / f"summary_{ds}.jsonl")
    return jsonify({
        "date": ds,
        "bars": bars,
        "signals": signals,
        "trades": trades,
        "context": context,
        "summary": summary,
    })


@app.route("/api/strategy_summary/<ds>")
def api_strategy_summary(ds):
    """Return per-strategy performance summary for a given date."""
    trades = read_jsonl(DATA_DIR / f"trades_{ds}.jsonl")
    signals = read_jsonl(DATA_DIR / f"signals_{ds}.jsonl")

    # Build strategy stats from trades (entries + exits)
    entries_by_strat = {}
    exits_by_strat = {}
    for t in trades:
        strat = t.get("strategy", "Unknown")
        if t.get("event") == "entry":
            entries_by_strat.setdefault(strat, []).append(t)
        elif t.get("event") == "exit":
            exits_by_strat.setdefault(strat, []).append(t)

    # Also count signals (taken vs skipped) per strategy
    signals_by_strat = {}
    for s in signals:
        strat = s.get("strategy", "Unknown")
        signals_by_strat.setdefault(strat, {"taken": 0, "skipped": 0, "total": 0})
        signals_by_strat[strat]["total"] += 1
        if s.get("taken"):
            signals_by_strat[strat]["taken"] += 1
        else:
            signals_by_strat[strat]["skipped"] += 1

    # Build summary per strategy
    all_strats = set(list(entries_by_strat.keys()) + list(signals_by_strat.keys()))
    result = []
    for strat in sorted(all_strats):
        entries = entries_by_strat.get(strat, [])
        exits = exits_by_strat.get(strat, [])
        sig = signals_by_strat.get(strat, {"taken": 0, "skipped": 0, "total": 0})

        wins = [e for e in exits if e.get("total_pnl", 0) > 0]
        losses = [e for e in exits if e.get("total_pnl", 0) <= 0]
        total_pnl = sum(e.get("total_pnl", 0) for e in exits)
        gross_wins = sum(e.get("total_pnl", 0) for e in wins)
        gross_losses = sum(e.get("total_pnl", 0) for e in losses)
        total_contracts = sum(e.get("contracts", 0) for e in entries)
        total_risk = sum(e.get("total_risk", 0) for e in entries)
        open_trades = len(entries) - len(exits)

        result.append({
            "strategy": strat,
            "signals_total": sig["total"],
            "signals_taken": sig["taken"],
            "signals_skipped": sig["skipped"],
            "entries": len(entries),
            "exits": len(exits),
            "open": open_trades,
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(len(wins) / len(exits) * 100, 1) if exits else 0,
            "total_pnl": round(total_pnl, 2),
            "gross_wins": round(gross_wins, 2),
            "gross_losses": round(gross_losses, 2),
            "avg_win": round(gross_wins / len(wins), 2) if wins else 0,
            "avg_loss": round(gross_losses / len(losses), 2) if losses else 0,
            "total_contracts": total_contracts,
            "total_risk": round(total_risk, 2),
        })

    return jsonify(result)


@app.route("/api/open_positions/<ds>")
def api_open_positions(ds):
    """Return open trades with unrealized P&L based on last bar price."""
    bars = read_jsonl(DATA_DIR / f"bars_{ds}.jsonl")
    trades = read_jsonl(DATA_DIR / f"trades_{ds}.jsonl")

    last_price = bars[-1]["c"] if bars else None

    entries = {t["trade_id"]: t for t in trades if t.get("event") == "entry"}
    exited = {t["trade_id"] for t in trades if t.get("event") == "exit"}

    open_trades = []
    total_unrealized = 0.0
    for tid, entry in entries.items():
        if tid in exited:
            continue
        if last_price is None:
            continue
        ep = entry["entry_price"]
        contracts = entry.get("contracts", 1)
        point_value = 10.0  # MGC
        if entry["action"] == "BUY":
            pnl = (last_price - ep) * point_value * contracts
        else:
            pnl = (ep - last_price) * point_value * contracts
        total_unrealized += pnl
        open_trades.append({
            "trade_id": tid,
            "strategy": entry.get("strategy", ""),
            "action": entry["action"],
            "contracts": contracts,
            "entry_price": ep,
            "stop_price": entry.get("stop_price"),
            "tp_price": entry.get("tp_price"),
            "current_price": last_price,
            "unrealized_pnl": round(pnl, 2),
            "entry_time": entry.get("ts", ""),
        })

    return jsonify({
        "last_price": last_price,
        "open_trades": open_trades,
        "total_unrealized": round(total_unrealized, 2),
    })


@app.route("/api/account")
def api_account():
    """Return live account snapshot written by the bot."""
    acct_file = DATA_DIR / "account.json"
    if not acct_file.exists():
        return jsonify({"error": "No account data available"})
    try:
        with open(acct_file) as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/api/logs/<ds>")
def api_logs(ds):
    """Return recent log lines for a given date."""
    log_file = LOG_DIR / f"trader_{ds}.log"
    if not log_file.exists():
        return jsonify({"lines": []})
    lines = log_file.read_text(errors="replace").splitlines()
    # Last 200 lines
    return jsonify({"lines": lines[-200:]})


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MGC Day Trader Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3"></script>
<style>
  :root {
    --bg: #0d1117; --surface: #161b22; --border: #30363d;
    --text: #e6edf3; --text2: #8b949e; --green: #3fb950;
    --red: #f85149; --blue: #58a6ff; --yellow: #d29922;
    --orange: #db6d28;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
  .header { background: var(--surface); border-bottom: 1px solid var(--border); padding: 16px 24px; display: flex; align-items: center; justify-content: space-between; }
  .header h1 { font-size: 20px; font-weight: 600; }
  .header h1 span { color: var(--yellow); }
  .controls { display: flex; gap: 12px; align-items: center; }
  select, button { background: var(--bg); color: var(--text); border: 1px solid var(--border); padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 13px; }
  button:hover { border-color: var(--blue); }
  .auto-label { font-size: 12px; color: var(--text2); }

  .grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 16px; padding: 20px 24px; }
  .card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 16px; }
  .card h3 { font-size: 12px; color: var(--text2); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
  .card .value { font-size: 28px; font-weight: 700; }
  .card .sub { font-size: 12px; color: var(--text2); margin-top: 4px; }
  .positive { color: var(--green); }
  .negative { color: var(--red); }
  .neutral { color: var(--text2); }

  .main { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; padding: 0 24px 20px; }
  .full-width { grid-column: 1 / -1; }
  .chart-card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 16px; }
  .chart-card h3 { font-size: 14px; margin-bottom: 12px; color: var(--text2); }
  .chart-wrap { position: relative; height: 300px; }

  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th { text-align: left; padding: 8px 12px; color: var(--text2); font-weight: 500; border-bottom: 1px solid var(--border); font-size: 11px; text-transform: uppercase; }
  td { padding: 8px 12px; border-bottom: 1px solid var(--border); }
  tr:hover td { background: rgba(88,166,255,0.05); }
  .badge { padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }
  .badge-buy { background: rgba(63,185,80,0.15); color: var(--green); }
  .badge-sell { background: rgba(248,81,73,0.15); color: var(--red); }
  .badge-taken { background: rgba(63,185,80,0.15); color: var(--green); }
  .badge-skipped { background: rgba(139,148,158,0.15); color: var(--text2); }

  .log-box { background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 12px; max-height: 300px; overflow-y: auto; font-family: 'Cascadia Code', 'Fira Code', monospace; font-size: 12px; line-height: 1.6; color: var(--text2); }
  .log-box .log-warn { color: var(--yellow); }
  .log-box .log-error { color: var(--red); }
  .log-box .log-signal { color: var(--blue); }
  .log-box .log-trade { color: var(--green); }

  .no-data { text-align: center; padding: 40px; color: var(--text2); }
  .status-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 6px; }
  .dot-live { background: var(--green); animation: pulse 2s infinite; }
  .dot-off { background: var(--red); }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
</style>
</head>
<body>
<div class="header">
  <h1>📈 <span>MGC</span> Day Trader</h1>
  <div class="controls">
    <span class="status-dot dot-off" id="statusDot"></span>
    <select id="dateSelect"></select>
    <button onclick="refresh()">↻ Refresh</button>
    <label class="auto-label"><input type="checkbox" id="autoRefresh" checked> Auto 30s</label>
  </div>
</div>

<div id="accountBanner" style="padding: 16px 24px 0; display:none;">
  <div style="background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px 24px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
    <div>
      <div style="font-size: 12px; color: var(--text2); text-transform: uppercase; letter-spacing: 0.5px;">Account Value</div>
      <div id="acctNetLiq" style="font-size: 36px; font-weight: 700;">—</div>
      <div id="acctUpdated" style="font-size: 11px; color: var(--text2); margin-top: 2px;"></div>
    </div>
    <div style="display: flex; gap: 32px; flex-wrap: wrap;">
      <div>
        <div style="font-size: 11px; color: var(--text2); text-transform: uppercase;">Cash</div>
        <div id="acctCash" style="font-size: 18px; font-weight: 600;">—</div>
      </div>
      <div>
        <div style="font-size: 11px; color: var(--text2); text-transform: uppercase;">Unrealized P&L</div>
        <div id="acctUnreal" style="font-size: 18px; font-weight: 600;">—</div>
      </div>
      <div>
        <div style="font-size: 11px; color: var(--text2); text-transform: uppercase;">Realized P&L</div>
        <div id="acctReal" style="font-size: 18px; font-weight: 600;">—</div>
      </div>
      <div>
        <div style="font-size: 11px; color: var(--text2); text-transform: uppercase;">Buying Power</div>
        <div id="acctBP" style="font-size: 18px; font-weight: 600;">—</div>
      </div>
      <div>
        <div style="font-size: 11px; color: var(--text2); text-transform: uppercase;">Positions</div>
        <div id="acctPos" style="font-size: 18px; font-weight: 600;">—</div>
      </div>
    </div>
  </div>
</div>

<div class="grid" id="statsGrid">
  <div class="card"><h3>Price</h3><div class="value" id="statPrice">—</div><div class="sub" id="statPriceSub"></div></div>
  <div class="card"><h3>Bars Today</h3><div class="value" id="statBars">—</div><div class="sub" id="statBarsSub"></div></div>
  <div class="card"><h3>Signals</h3><div class="value" id="statSignals">—</div><div class="sub" id="statSignalsSub"></div></div>
  <div class="card"><h3>Trades</h3><div class="value" id="statTrades">—</div><div class="sub" id="statTradesSub"></div></div>
  <div class="card"><h3>Open P&L</h3><div class="value" id="statOpenPnl">—</div><div class="sub" id="statOpenPnlSub"></div></div>
  <div class="card"><h3>Closed P&L</h3><div class="value" id="statClosedPnl">—</div><div class="sub" id="statClosedPnlSub"></div></div>
  <div class="card"><h3>Total P&L</h3><div class="value" id="statTotalPnl">—</div><div class="sub" id="statTotalPnlSub"></div></div>
</div>

<div style="padding: 0 24px 16px;">
  <div class="chart-card" id="openPositionsCard" style="display:none;">
    <h3>🔴 Open Positions (Live)</h3>
    <div id="openPositionsTable"></div>
  </div>
</div>

<div style="padding: 0 24px 16px;">
  <div class="chart-card">
    <h3>Strategy Performance</h3>
    <div id="strategyTable"></div>
  </div>
</div>

<div class="main">
  <div class="chart-card full-width">
    <h3>Price Chart (5-min bars)</h3>
    <div class="chart-wrap"><canvas id="priceChart"></canvas></div>
  </div>

  <div class="chart-card">
    <h3>Signals</h3>
    <div id="signalsTable"></div>
  </div>

  <div class="chart-card">
    <h3>Trades</h3>
    <div id="tradesTable"></div>
  </div>

  <div class="chart-card full-width">
    <h3>Recent Logs</h3>
    <div class="log-box" id="logBox"></div>
  </div>
</div>

<script>
let priceChart = null;
let autoTimer = null;

async function loadDates() {
  const res = await fetch('/api/dates');
  const dates = await res.json();
  const sel = document.getElementById('dateSelect');
  sel.innerHTML = '';
  dates.forEach(d => {
    const opt = document.createElement('option');
    opt.value = d;
    opt.textContent = d.slice(0,4)+'-'+d.slice(4,6)+'-'+d.slice(6,8);
    sel.appendChild(opt);
  });
  sel.addEventListener('change', refresh);
  if (dates.length) refresh();
}

async function refresh() {
  const ds = document.getElementById('dateSelect').value;
  if (!ds) return;
  const [dataRes, logRes, stratRes, openRes, acctRes] = await Promise.all([
    fetch('/api/data/' + ds),
    fetch('/api/logs/' + ds),
    fetch('/api/strategy_summary/' + ds),
    fetch('/api/open_positions/' + ds),
    fetch('/api/account'),
  ]);
  const data = await dataRes.json();
  const logs = await logRes.json();
  const stratData = await stratRes.json();
  const openData = await openRes.json();
  const acctData = await acctRes.json();
  render(data, logs.lines, openData);
  renderStrategyTable(stratData);
  renderAccount(acctData);
}

function renderAccount(acct) {
  const banner = document.getElementById('accountBanner');
  if (!acct || acct.error) {
    banner.style.display = 'none';
    return;
  }
  banner.style.display = 'block';

  const fmt = (v) => v ? '$' + Number(v).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}) : '—';
  const pnlClass = (v) => v > 0 ? 'positive' : v < 0 ? 'negative' : '';

  document.getElementById('acctNetLiq').textContent = fmt(acct.net_liquidation);
  document.getElementById('acctNetLiq').className = '';

  const cashEl = document.getElementById('acctCash');
  cashEl.textContent = fmt(acct.total_cash);

  const unrealEl = document.getElementById('acctUnreal');
  unrealEl.textContent = fmt(acct.unrealized_pnl);
  unrealEl.className = pnlClass(acct.unrealized_pnl);

  const realEl = document.getElementById('acctReal');
  realEl.textContent = fmt(acct.realized_pnl);
  realEl.className = pnlClass(acct.realized_pnl);

  document.getElementById('acctBP').textContent = fmt(acct.buying_power);
  document.getElementById('acctPos').textContent = acct.position_count || '0';

  if (acct.ts) {
    const age = Math.floor((Date.now() - new Date(acct.ts).getTime()) / 1000);
    const ageStr = age < 60 ? age + 's ago' : Math.floor(age/60) + 'm ago';
    document.getElementById('acctUpdated').textContent = 'Updated ' + ageStr + ' • Last price: $' + (acct.last_price || '—');
  }

}

function render(data, logLines, openData) {
  const { bars, signals, trades, summary } = data;

  // Stats
  const lastBar = bars.length ? bars[bars.length-1] : null;
  const firstBar = bars.length ? bars[0] : null;
  document.getElementById('statPrice').textContent = lastBar ? '$' + lastBar.c.toFixed(1) : '—';
  if (lastBar && firstBar) {
    const chg = lastBar.c - firstBar.o;
    const pct = (chg / firstBar.o * 100).toFixed(2);
    const el = document.getElementById('statPriceSub');
    el.textContent = (chg >= 0 ? '+' : '') + chg.toFixed(1) + ' (' + pct + '%)';
    el.className = 'sub ' + (chg >= 0 ? 'positive' : 'negative');
  }
  document.getElementById('statBars').textContent = bars.length;
  document.getElementById('statBarsSub').textContent = lastBar ? 'Last: ' + lastBar.ts.split('T')[1].slice(0,8) : '';

  const takenSignals = signals.filter(s => s.taken);
  const skippedSignals = signals.filter(s => !s.taken);
  document.getElementById('statSignals').textContent = signals.length;
  document.getElementById('statSignalsSub').textContent = takenSignals.length + ' taken, ' + skippedSignals.length + ' skipped';

  const tradeEntries = trades.filter(t => t.event === 'entry');
  const tradeExits = trades.filter(t => t.event === 'exit');
  const openCount = openData.open_trades ? openData.open_trades.length : 0;
  document.getElementById('statTrades').textContent = tradeEntries.length;
  document.getElementById('statTradesSub').textContent = tradeExits.length + ' closed, ' + openCount + ' open';

  // Open P&L
  const unrealized = openData.total_unrealized || 0;
  const openPnlEl = document.getElementById('statOpenPnl');
  openPnlEl.textContent = openCount > 0 ? '$' + unrealized.toFixed(2) : '—';
  openPnlEl.className = 'value ' + (unrealized > 0 ? 'positive' : unrealized < 0 ? 'negative' : '');
  document.getElementById('statOpenPnlSub').textContent = openCount > 0 ? openCount + ' position' + (openCount > 1 ? 's' : '') : 'No open trades';

  // Closed P&L — use IB account realized P&L as source of truth (includes commissions)
  // Fall back to trade log P&L if account data not available
  const tradePnl = tradeExits.reduce((s, t) => s + (t.total_pnl || 0), 0);
  const closedPnlEl = document.getElementById('statClosedPnl');
  // We'll update this from account data in renderAccount if available
  closedPnlEl.textContent = tradeExits.length > 0 ? '$' + tradePnl.toFixed(2) : '—';
  closedPnlEl.className = 'value ' + (tradePnl > 0 ? 'positive' : tradePnl < 0 ? 'negative' : '');
  document.getElementById('statClosedPnlSub').textContent = tradeExits.length + ' trades';

  // Total P&L (realized + unrealized)
  const totalPnl = tradePnl + unrealized;
  const totalPnlEl = document.getElementById('statTotalPnl');
  const hasTrades = tradeExits.length > 0 || openCount > 0;
  totalPnlEl.textContent = hasTrades ? '$' + totalPnl.toFixed(2) : '—';
  totalPnlEl.className = 'value ' + (totalPnl > 0 ? 'positive' : totalPnl < 0 ? 'negative' : '');
  document.getElementById('statTotalPnlSub').textContent = hasTrades ? 'realized + unrealized' : 'No activity';

  // Cache for trades table to use
  window._lastOpenData = openData;

  // Open Positions panel
  renderOpenPositions(openData);

  // Status dot
  const dot = document.getElementById('statusDot');
  if (lastBar) {
    const barTime = new Date(lastBar.ts);
    const age = (Date.now() - barTime.getTime()) / 1000;
    dot.className = age < 120 ? 'status-dot dot-live' : 'status-dot dot-off';
  }

  // Price chart
  renderPriceChart(bars, signals.filter(s => s.taken), tradeEntries);

  // Signals table
  renderSignalsTable(signals);

  // Trades table
  renderTradesTable(trades);

  // Logs
  renderLogs(logLines);
}

function renderOpenPositions(openData) {
  const card = document.getElementById('openPositionsCard');
  const el = document.getElementById('openPositionsTable');
  if (!openData.open_trades || !openData.open_trades.length) {
    card.style.display = 'none';
    return;
  }
  card.style.display = 'block';
  let html = `<table>
    <tr><th>Trade ID</th><th>Strategy</th><th>Side</th><th>Contracts</th><th>Entry</th><th>Current</th><th>Stop</th><th>Target</th><th>Unrealized P&L</th></tr>`;
  openData.open_trades.forEach(t => {
    const actionClass = t.action === 'BUY' ? 'badge-buy' : 'badge-sell';
    const pnlClass = t.unrealized_pnl >= 0 ? 'positive' : 'negative';
    const pctToStop = t.stop_price ? ((t.current_price - t.stop_price) / t.current_price * 100).toFixed(1) : '—';
    const pctToTP = t.tp_price ? ((t.tp_price - t.current_price) / t.current_price * 100).toFixed(1) : '—';
    html += `<tr>
      <td style="font-family:monospace;font-size:11px">${t.trade_id}</td>
      <td>${t.strategy}</td>
      <td><span class="badge ${actionClass}">${t.action}</span></td>
      <td>${t.contracts}</td>
      <td>$${t.entry_price.toFixed(1)}</td>
      <td><strong>$${t.current_price.toFixed(1)}</strong></td>
      <td>$${t.stop_price ? t.stop_price.toFixed(1) : '—'}</td>
      <td>$${t.tp_price ? t.tp_price.toFixed(1) : '—'}</td>
      <td class="${pnlClass}" style="font-weight:700;font-size:15px">$${t.unrealized_pnl.toFixed(2)}</td>
    </tr>`;
  });
  html += `<tr style="border-top:2px solid var(--border)">
    <td colspan="8" style="text-align:right"><strong>Total Unrealized</strong></td>
    <td class="${openData.total_unrealized >= 0 ? 'positive' : 'negative'}" style="font-weight:700;font-size:15px">$${openData.total_unrealized.toFixed(2)}</td>
  </tr></table>`;
  el.innerHTML = html;
}

function renderPriceChart(bars, signals, tradeEntries) {
  const ctx = document.getElementById('priceChart').getContext('2d');
  if (priceChart) priceChart.destroy();

  const labels = bars.map(b => b.ts);
  const prices = bars.map(b => b.c);

  // Signal annotations
  const signalPoints = signals.map(s => ({
    x: s.ts,
    y: s.price,
    action: s.action,
    strategy: s.strategy,
  }));

  const buySignals = signalPoints.filter(s => s.action === 'BUY');
  const sellSignals = signalPoints.filter(s => s.action === 'SELL');

  priceChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'MGC Price',
          data: prices,
          borderColor: '#58a6ff',
          backgroundColor: 'rgba(88,166,255,0.05)',
          borderWidth: 1.5,
          pointRadius: 0,
          fill: true,
          tension: 0.1,
        },
        {
          label: 'Buy Signals',
          data: buySignals.map(s => ({ x: s.x, y: s.y })),
          type: 'scatter',
          pointStyle: 'triangle',
          pointRadius: 10,
          backgroundColor: '#3fb950',
          borderColor: '#3fb950',
        },
        {
          label: 'Sell Signals',
          data: sellSignals.map(s => ({ x: s.x, y: s.y })),
          type: 'scatter',
          pointStyle: 'triangle',
          rotation: 180,
          pointRadius: 10,
          backgroundColor: '#f85149',
          borderColor: '#f85149',
        },
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect: false, mode: 'index' },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#161b22',
          borderColor: '#30363d',
          borderWidth: 1,
          titleColor: '#e6edf3',
          bodyColor: '#8b949e',
        },
      },
      scales: {
        x: {
          display: true,
          ticks: { color: '#8b949e', maxTicksLimit: 12, callback: function(val) {
            const lbl = this.getLabelForValue(val);
            if (!lbl) return '';
            const t = lbl.split('T')[1];
            return t ? t.slice(0,5) : lbl;
          }},
          grid: { color: 'rgba(48,54,61,0.5)' },
        },
        y: {
          ticks: { color: '#8b949e' },
          grid: { color: 'rgba(48,54,61,0.5)' },
        },
      },
    },
  });
}

function renderSignalsTable(signals) {
  const el = document.getElementById('signalsTable');
  if (!signals.length) {
    el.innerHTML = '<div class="no-data">No signals generated today</div>';
    return;
  }
  const recent = signals.slice(-20).reverse();
  let html = '<table><tr><th>Time</th><th>Strategy</th><th>Action</th><th>Price</th><th>R:R</th><th>Status</th></tr>';
  recent.forEach(s => {
    const time = s.ts.split('T')[1].slice(0,8);
    const actionClass = s.action === 'BUY' ? 'badge-buy' : 'badge-sell';
    const statusClass = s.taken ? 'badge-taken' : 'badge-skipped';
    html += `<tr>
      <td>${time}</td>
      <td>${s.strategy}</td>
      <td><span class="badge ${actionClass}">${s.action}</span></td>
      <td>$${s.price.toFixed(1)}</td>
      <td>${s.rr_ratio}:1</td>
      <td><span class="badge ${statusClass}">${s.taken ? 'TAKEN' : 'SKIP'}</span></td>
    </tr>`;
  });
  html += '</table>';
  el.innerHTML = html;
}

function renderTradesTable(trades) {
  const el = document.getElementById('tradesTable');
  const entries = trades.filter(t => t.event === 'entry');
  if (!entries.length) {
    el.innerHTML = '<div class="no-data">No trades executed today</div>';
    return;
  }
  const exits = trades.filter(t => t.event === 'exit');
  const exitMap = {};
  exits.forEach(e => exitMap[e.trade_id] = e);

  let html = '<table><tr><th>Time</th><th>Strategy</th><th>Side</th><th>Entry</th><th>Exit</th><th>P&L</th><th>Status</th></tr>';
  entries.reverse().forEach(t => {
    const time = t.ts.split('T')[1].slice(0,8);
    const actionClass = t.action === 'BUY' ? 'badge-buy' : 'badge-sell';
    const exit = exitMap[t.trade_id];
    let exitPrice, pnlStr, pnlClass, statusBadge;
    if (exit) {
      exitPrice = '$' + exit.exit_price.toFixed(1);
      pnlStr = '$' + exit.total_pnl.toFixed(2);
      pnlClass = exit.total_pnl >= 0 ? 'positive' : 'negative';
      statusBadge = exit.total_pnl >= 0
        ? '<span class="badge badge-taken">WIN</span>'
        : '<span class="badge badge-skipped">LOSS</span>';
    } else {
      // Open trade — find unrealized from cached openData
      const openTrade = window._lastOpenData && window._lastOpenData.open_trades
        ? window._lastOpenData.open_trades.find(o => o.trade_id === t.trade_id) : null;
      if (openTrade) {
        exitPrice = '<span style="color:var(--blue)">$' + openTrade.current_price.toFixed(1) + '</span>';
        pnlStr = '$' + openTrade.unrealized_pnl.toFixed(2);
        pnlClass = openTrade.unrealized_pnl >= 0 ? 'positive' : 'negative';
      } else {
        exitPrice = '—';
        pnlStr = '—';
        pnlClass = '';
      }
      statusBadge = '<span class="badge badge-buy" style="animation:pulse 2s infinite">OPEN</span>';
    }
    html += `<tr>
      <td>${time}</td>
      <td>${t.strategy}</td>
      <td><span class="badge ${actionClass}">${t.action}</span></td>
      <td>$${t.entry_price.toFixed(1)}</td>
      <td>${exitPrice}</td>
      <td class="${pnlClass}" style="font-weight:600">${pnlStr}</td>
      <td>${statusBadge}</td>
    </tr>`;
  });
  html += '</table>';
  el.innerHTML = html;
}

function renderLogs(lines) {
  const el = document.getElementById('logBox');
  const last = lines.slice(-100);
  el.innerHTML = last.map(l => {
    let cls = '';
    if (l.includes('WARNING')) cls = 'log-warn';
    else if (l.includes('ERROR')) cls = 'log-error';
    else if (l.includes('Signal') || l.includes('📊')) cls = 'log-signal';
    else if (l.includes('Executing') || l.includes('🚀')) cls = 'log-trade';
    return `<div class="${cls}">${escapeHtml(l)}</div>`;
  }).join('');
  el.scrollTop = el.scrollHeight;
}

function escapeHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function renderStrategyTable(strategies) {
  const el = document.getElementById('strategyTable');
  if (!strategies.length) {
    el.innerHTML = '<div class="no-data">No strategy data available</div>';
    return;
  }
  let html = `<table>
    <tr>
      <th>Strategy</th>
      <th>Signals</th>
      <th>Trades</th>
      <th>Open</th>
      <th>Wins</th>
      <th>Losses</th>
      <th>Win Rate</th>
      <th>Gross Wins</th>
      <th>Gross Losses</th>
      <th>Net P&L</th>
      <th>Contracts</th>
      <th>Risk</th>
    </tr>`;

  let totalSignals = 0, totalEntries = 0, totalOpen = 0, totalWins = 0;
  let totalLosses = 0, totalPnl = 0, totalGW = 0, totalGL = 0, totalContracts = 0, totalRisk = 0;

  strategies.forEach(s => {
    const pnlClass = s.total_pnl > 0 ? 'positive' : s.total_pnl < 0 ? 'negative' : '';
    const wrClass = s.win_rate >= 60 ? 'positive' : s.win_rate > 0 && s.win_rate < 40 ? 'negative' : '';
    const gwClass = s.gross_wins > 0 ? 'positive' : '';
    const glClass = s.gross_losses < 0 ? 'negative' : '';

    html += `<tr>
      <td><strong>${s.strategy}</strong></td>
      <td>${s.signals_taken}/${s.signals_total} <span style="color:var(--text2);font-size:11px">(${s.signals_skipped} skip)</span></td>
      <td>${s.entries}</td>
      <td>${s.open > 0 ? '<span class="badge badge-buy">' + s.open + ' open</span>' : '0'}</td>
      <td class="positive">${s.wins}</td>
      <td class="negative">${s.losses}</td>
      <td class="${wrClass}">${s.exits > 0 ? s.win_rate + '%' : '—'}</td>
      <td class="${gwClass}">${s.gross_wins ? '$' + s.gross_wins.toFixed(0) : '—'}</td>
      <td class="${glClass}">${s.gross_losses ? '$' + s.gross_losses.toFixed(0) : '—'}</td>
      <td class="${pnlClass}" style="font-weight:700">${s.exits > 0 ? '$' + s.total_pnl.toFixed(2) : '—'}</td>
      <td>${s.total_contracts}</td>
      <td>$${s.total_risk.toFixed(0)}</td>
    </tr>`;

    totalSignals += s.signals_total;
    totalEntries += s.entries;
    totalOpen += s.open;
    totalWins += s.wins;
    totalLosses += s.losses;
    totalPnl += s.total_pnl;
    totalGW += s.gross_wins;
    totalGL += s.gross_losses;
    totalContracts += s.total_contracts;
    totalRisk += s.total_risk;
  });

  const totalExits = totalWins + totalLosses;
  const totalWR = totalExits > 0 ? (totalWins / totalExits * 100).toFixed(1) : '—';
  const totalPnlClass = totalPnl > 0 ? 'positive' : totalPnl < 0 ? 'negative' : '';

  html += `<tr style="border-top:2px solid var(--border)">
    <td><strong>TOTAL</strong></td>
    <td>${totalSignals}</td>
    <td>${totalEntries}</td>
    <td>${totalOpen}</td>
    <td class="positive">${totalWins}</td>
    <td class="negative">${totalLosses}</td>
    <td>${totalExits > 0 ? totalWR + '%' : '—'}</td>
    <td class="positive">${totalGW ? '$' + totalGW.toFixed(0) : '—'}</td>
    <td class="negative">${totalGL ? '$' + totalGL.toFixed(0) : '—'}</td>
    <td class="${totalPnlClass}" style="font-weight:700">${totalExits > 0 ? '$' + totalPnl.toFixed(2) : '—'}</td>
    <td>${totalContracts}</td>
    <td>$${totalRisk.toFixed(0)}</td>
  </tr>`;

  html += '</table>';
  el.innerHTML = html;
}

// Auto-refresh
function startAutoRefresh() {
  if (autoTimer) clearInterval(autoTimer);
  autoTimer = setInterval(() => {
    if (document.getElementById('autoRefresh').checked) refresh();
  }, 30000);
}

loadDates();
startAutoRefresh();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    print("=" * 50)
    print("  MGC Day Trader Dashboard")
    print("  Open: http://localhost:5050")
    print("=" * 50)
    app.run(host="127.0.0.1", port=5050, debug=False)
