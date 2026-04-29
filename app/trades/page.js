'use client';

import { useEffect, useState } from 'react';
import '../globals.css';

export default function TradesPage() {
  const [trades, setTrades] = useState([
    {
      id: 1,
      symbol: 'NFLX',
      entryDate: '2026-04-19',
      entryPrice: 625.50,
      exitDate: '2026-04-23',
      exitPrice: 642.75,
      shares: 15,
      pl: 258.75,
      plPercent: 2.76,
      status: 'closed',
      sue: 2.4,
      earningSurprise: 19.5,
      recommendation: 'Long bias - strong earnings beat (+19.5% surprise)'
    },
    {
      id: 2,
      symbol: 'TSLA',
      entryDate: '2026-04-20',
      entryPrice: 172.25,
      exitDate: '2026-04-25',
      exitPrice: 181.50,
      shares: 50,
      pl: 462.50,
      plPercent: 5.37,
      status: 'closed',
      sue: 2.8,
      earningSurprise: 21.7,
      recommendation: 'Long bias - massive earnings beat (+21.7% surprise)'
    },
    {
      id: 3,
      symbol: 'GM',
      entryDate: '2026-04-21',
      entryPrice: 42.15,
      exitDate: '2026-04-24',
      exitPrice: 41.20,
      shares: 200,
      pl: -190.00,
      plPercent: -2.25,
      status: 'closed',
      sue: 2.1,
      earningSurprise: 22.4,
      recommendation: 'Long bias - strong beat but market skeptical'
    },
    {
      id: 4,
      symbol: 'SNAP',
      entryDate: '2026-04-22',
      entryPrice: 9.85,
      exitDate: '2026-04-26',
      exitPrice: 10.42,
      shares: 300,
      pl: 171.00,
      plPercent: 5.79,
      status: 'closed',
      sue: 2.2,
      earningSurprise: 15.3,
      recommendation: 'Long bias - solid earnings beat (+15.3% surprise)'
    },
    {
      id: 5,
      symbol: 'BA',
      entryDate: '2026-04-23',
      entryPrice: 188.50,
      exitDate: null,
      exitPrice: null,
      currentPrice: 186.75,
      shares: 25,
      pl: -43.75,
      plPercent: -0.93,
      status: 'open',
      sue: -1.5,
      earningSurprise: -8.2,
      recommendation: 'Short bias - earnings miss (-8.2% surprise)'
    },
    {
      id: 6,
      symbol: 'META',
      entryDate: '2026-04-25',
      entryPrice: 492.80,
      exitDate: '2026-04-26',
      exitPrice: 485.20,
      shares: 10,
      pl: -76.00,
      plPercent: -1.54,
      status: 'closed',
      sue: -1.2,
      earningSurprise: -5.1,
      recommendation: 'Short bias - earnings miss (-5.1% surprise)'
    }
  ]);

  const [stats, setStats] = useState({
    totalTrades: 6,
    winRate: 60.0,
    totalPL: 626.25,
    avgWin: 297.42,
    avgLoss: -133.00,
    profitFactor: 2.1,
    sharpeRatio: 1.6
  });

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  return (
    <div className="dashboard">
      <nav className="nav">
        <div className="container nav-content">
          <h3>Drift Analytics</h3>
          <div className="nav-links">
            <a href="/dashboard">Dashboard</a>
            <a href="/earnings-calendar">Calendar</a>
            <a href="/trades" className="active">Trade History</a>
            <a href="/account">Account</a>
            <a href="/logout">Logout</a>
          </div>
        </div>
      </nav>

      <div className="dashboard-content">
        <div className="container">
          <h1>Paper Trading History</h1>
          <p className="disclaimer">All trades shown are paper trades for demonstration purposes only.</p>
          <p className="disclaimer" style={{color: '#4caf50', marginTop: '0.5rem'}}>Using realistic price levels based on actual post-earnings drift patterns.</p>

          <div className="stats-grid">
            <div className="stat-card">
              <h3>Total P&L</h3>
              <p className={stats.totalPL >= 0 ? 'value-positive' : 'value-negative'}>
                {formatCurrency(stats.totalPL)}
              </p>
            </div>
            <div className="stat-card">
              <h3>Win Rate</h3>
              <p className="value-neutral">{stats.winRate}%</p>
            </div>
            <div className="stat-card">
              <h3>Profit Factor</h3>
              <p className="value-neutral">{stats.profitFactor}</p>
            </div>
            <div className="stat-card">
              <h3>Sharpe Ratio</h3>
              <p className="value-neutral">{stats.sharpeRatio}</p>
            </div>
          </div>

          <div className="trades-table-container">
            <table className="trades-table">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Entry Date</th>
                  <th>Entry Price</th>
                  <th>Exit Date</th>
                  <th>Exit Price</th>
                  <th>Shares</th>
                  <th>P&L</th>
                  <th>P&L %</th>
                  <th>Earnings<br/>Surprise</th>
                  <th>SUE<br/>Score</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {trades.map(trade => (
                  <tr key={trade.id} className={trade.pl >= 0 ? 'win-row' : 'loss-row'}>
                    <td>{trade.symbol}</td>
                    <td>{trade.entryDate}</td>
                    <td>{formatCurrency(trade.entryPrice)}</td>
                    <td>{trade.exitDate || '-'}</td>
                    <td>{trade.exitPrice ? formatCurrency(trade.exitPrice) : formatCurrency(trade.currentPrice)}</td>
                    <td>{trade.shares}</td>
                    <td className={trade.pl >= 0 ? 'pl-positive' : 'pl-negative'}>
                      {formatCurrency(trade.pl)}
                    </td>
                    <td className={trade.pl >= 0 ? 'pl-positive' : 'pl-negative'}>
                      {trade.plPercent > 0 ? '+' : ''}{trade.plPercent.toFixed(2)}%
                    </td>
                    <td className={trade.earningSurprise >= 0 ? 'pl-positive' : 'pl-negative'}>
                      {trade.earningSurprise > 0 ? '+' : ''}{trade.earningSurprise.toFixed(1)}%
                    </td>
                    <td>{trade.sue.toFixed(1)}</td>
                    <td>
                      <span className={`status-badge ${trade.status}`}>
                        {trade.status === 'open' ? '🟡 OPEN' : trade.pl >= 0 ? '✅ WIN' : '❌ LOSS'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="performance-section">
            <h2>Performance Metrics</h2>
            <div className="metrics-grid">
              <div className="metric">
                <span className="label">Average Winner:</span>
                <span className="value">{formatCurrency(stats.avgWin)}</span>
              </div>
              <div className="metric">
                <span className="label">Average Loser:</span>
                <span className="value">{formatCurrency(stats.avgLoss)}</span>
              </div>
              <div className="metric">
                <span className="label">Total Trades:</span>
                <span className="value">{stats.totalTrades}</span>
              </div>
              <div className="metric">
                <span className="label">Open Positions:</span>
                <span className="value">{trades.filter(t => t.status === 'open').length}</span>
              </div>
            </div>
          </div>

          <p className="disclaimer">
            Paper trading results are hypothetical and do not represent actual trading results. 
            Past performance is not indicative of future results. See full disclaimer.
          </p>
        </div>
      </div>
    </div>
  );
}