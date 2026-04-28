'use client';

import { useEffect, useState } from 'react';
import '../globals.css';

export default function TradesPage() {
  const [trades, setTrades] = useState([
    {
      id: 1,
      symbol: 'SNAP',
      entryDate: '2026-04-20',
      entryPrice: 15.42,
      exitDate: '2026-04-22',
      exitPrice: 16.01,
      shares: 100,
      pl: 59.00,
      plPercent: 3.83,
      status: 'closed',
      sue: 2.3,
      recommendation: 'Short bias - negative earnings surprise'
    },
    {
      id: 2,
      symbol: 'AAPL',
      entryDate: '2026-04-19',
      entryPrice: 172.45,
      exitDate: '2026-04-24',
      exitPrice: 178.23,
      shares: 50,
      pl: 289.00,
      plPercent: 3.35,
      status: 'closed',
      sue: -1.8,
      recommendation: 'Short bias - missed estimates'
    },
    {
      id: 3,
      symbol: 'MSFT',
      entryDate: '2026-04-21',
      entryPrice: 425.67,
      exitDate: '2026-04-23',
      exitPrice: 418.92,
      shares: 25,
      pl: -168.75,
      plPercent: -1.59,
      status: 'closed',
      sue: 1.5,
      recommendation: 'Short bias - below consensus'
    },
    {
      id: 4,
      symbol: 'PINS',
      entryDate: '2026-04-25',
      entryPrice: 28.76,
      exitDate: null,
      exitPrice: null,
      currentPrice: 29.14,
      shares: 150,
      pl: 57.00,
      plPercent: 1.32,
      status: 'open',
      sue: 2.1,
      recommendation: 'Short bias - negative surprise expected'
    },
    {
      id: 5,
      symbol: 'DKNG',
      entryDate: '2026-04-24',
      entryPrice: 38.93,
      exitDate: '2026-04-26',
      exitPrice: 40.15,
      shares: 100,
      pl: 122.00,
      plPercent: 3.13,
      status: 'closed',
      sue: -2.2,
      recommendation: 'Short bias - earnings miss'
    },
    {
      id: 6,
      symbol: 'ROKU',
      entryDate: '2026-04-26',
      entryPrice: 63.45,
      exitDate: null,
      exitPrice: null,
      currentPrice: 62.89,
      shares: 75,
      pl: -42.00,
      plPercent: -0.88,
      status: 'open',
      sue: 1.9,
      recommendation: 'Short bias - weak guidance'
    }
  ]);

  const [stats, setStats] = useState({
    totalTrades: 6,
    winRate: 66.7,
    totalPL: 316.25,
    avgWin: 141.75,
    avgLoss: -168.75,
    profitFactor: 2.52,
    sharpeRatio: 1.8
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
            <a href="/api-docs">API Docs</a>
            <a href="/account">Account</a>
            <a href="/logout">Logout</a>
          </div>
        </div>
      </nav>

      <div className="dashboard-content">
        <div className="container">
          <h1>Paper Trading History</h1>
          <p className="disclaimer">All trades shown are paper trades for demonstration purposes only.</p>

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
                  <th>SUE Score</th>
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