'use client';

import { useEffect, useState } from 'react';
import '../globals.css';

export default function AutoTraderPage() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [configOpen, setConfigOpen] = useState(false);

  const fetchStatus = async () => {
    try {
      const response = await fetch('https://post-earnings-scanner-v2.onrender.com/api/auto-trader/status');
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
      }
    } catch (error) {
      console.error('Error fetching auto trader status:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const toggleAutoTrading = async () => {
    try {
      const response = await fetch('https://post-earnings-scanner-v2.onrender.com/api/auto-trader/toggle', {
        method: 'POST'
      });
      if (response.ok) {
        fetchStatus();
      }
    } catch (error) {
      console.error('Error toggling auto trader:', error);
    }
  };

  const runManualScan = async () => {
    try {
      const response = await fetch('https://post-earnings-scanner-v2.onrender.com/api/auto-trader/scan', {
        method: 'POST'
      });
      if (response.ok) {
        alert('Manual scan initiated! Check back in a minute for results.');
        setTimeout(fetchStatus, 5000);
      }
    } catch (error) {
      console.error('Error running manual scan:', error);
    }
  };

  const updateConfig = async (key, value) => {
    try {
      const newConfig = { [key]: value };
      const response = await fetch('https://post-earnings-scanner-v2.onrender.com/api/auto-trader/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newConfig)
      });
      if (response.ok) {
        fetchStatus();
      }
    } catch (error) {
      console.error('Error updating config:', error);
    }
  };

  if (loading) {
    return (
      <div className="dashboard">
        <nav className="nav">
          <div className="container nav-content">
            <h3>Drift Analytics</h3>
            <div className="nav-links">
              <a href="/dashboard">Dashboard</a>
              <a href="/auto-trader" className="active">Auto Trader</a>
              <a href="/trades">Trade History</a>
              <a href="/account">Account</a>
            </div>
          </div>
        </nav>
        <div className="dashboard-content">
          <div className="container">
            <h1>Loading Automated Trader...</h1>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <nav className="nav">
        <div className="container nav-content">
          <h3>Drift Analytics</h3>
          <div className="nav-links">
            <a href="/dashboard">Dashboard</a>
            <a href="/auto-trader" className="active">Auto Trader</a>
            <a href="/trades">Trade History</a>
            <a href="/account">Account</a>
            <a href="/logout">Logout</a>
          </div>
        </div>
      </nav>

      <div className="dashboard-content">
        <div className="container">
          <h1>🤖 Automated Paper Trading System</h1>
          <p style={{fontSize: '1.1em', marginBottom: '2rem'}}>
            Set it and forget it! Our AI monitors earnings releases 24/7 and automatically enters high-confidence trades.
          </p>

          <div className="stats-grid">
            <div className="stat-card">
              <h3>Status</h3>
              <p style={{fontSize: '1.8em', color: status?.config?.enabled ? '#4caf50' : '#f44336'}}>
                {status?.config?.enabled ? '🟢 ACTIVE' : '🔴 INACTIVE'}
              </p>
              <button 
                onClick={toggleAutoTrading}
                style={{
                  marginTop: '10px',
                  padding: '10px 20px',
                  background: status?.config?.enabled ? '#f44336' : '#4caf50',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer'
                }}
              >
                {status?.config?.enabled ? 'Stop Auto Trading' : 'Start Auto Trading'}
              </button>
            </div>
            
            <div className="stat-card">
              <h3>Open Positions</h3>
              <p className="value-neutral" style={{fontSize: '2em'}}>
                {status?.open_positions || 0} / {status?.config?.max_positions || 5}
              </p>
              <small>Max positions allowed</small>
            </div>
            
            <div className="stat-card">
              <h3>Total P&L</h3>
              <p className={status?.total_pl >= 0 ? 'value-positive' : 'value-negative'} style={{fontSize: '1.8em'}}>
                ${status?.total_pl?.toFixed(2) || '0.00'}
              </p>
              <small>From {status?.total_trades || 0} trades</small>
            </div>
            
            <div className="stat-card">
              <h3>Win Rate</h3>
              <p className="value-neutral" style={{fontSize: '2em'}}>
                {status?.win_rate || 0}%
              </p>
              <small>Success rate</small>
            </div>
          </div>

          <div style={{marginTop: '2rem', display: 'flex', gap: '1rem'}}>
            <button 
              onClick={runManualScan}
              className="button primary"
              style={{
                padding: '12px 24px',
                background: '#1976d2',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '1.1em'
              }}
            >
              🔍 Run Manual Scan Now
            </button>
            
            <button 
              onClick={() => setConfigOpen(!configOpen)}
              className="button secondary"
              style={{
                padding: '12px 24px',
                background: '#f0f0f0',
                color: '#333',
                border: '1px solid #ddd',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '1.1em'
              }}
            >
              ⚙️ {configOpen ? 'Hide' : 'Show'} Settings
            </button>
          </div>

          {configOpen && (
            <div style={{
              marginTop: '2rem',
              padding: '25px',
              background: '#f8f9fa',
              borderRadius: '12px'
            }}>
              <h2>Trading Configuration</h2>
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '20px'}}>
                <div>
                  <label>Position Size ($)</label>
                  <input
                    type="number"
                    value={status?.config?.position_size_dollars || 10000}
                    onChange={(e) => updateConfig('position_size_dollars', parseFloat(e.target.value))}
                    style={{
                      width: '100%',
                      padding: '8px',
                      marginTop: '5px',
                      border: '1px solid #ddd',
                      borderRadius: '4px'
                    }}
                  />
                </div>
                
                <div>
                  <label>Max Positions</label>
                  <input
                    type="number"
                    value={status?.config?.max_positions || 5}
                    onChange={(e) => updateConfig('max_positions', parseInt(e.target.value))}
                    min="1"
                    max="10"
                    style={{
                      width: '100%',
                      padding: '8px',
                      marginTop: '5px',
                      border: '1px solid #ddd',
                      borderRadius: '4px'
                    }}
                  />
                </div>
                
                <div>
                  <label>Min SUE Score</label>
                  <input
                    type="number"
                    value={status?.config?.min_sue_score || 2.0}
                    onChange={(e) => updateConfig('min_sue_score', parseFloat(e.target.value))}
                    step="0.1"
                    min="1.0"
                    max="5.0"
                    style={{
                      width: '100%',
                      padding: '8px',
                      marginTop: '5px',
                      border: '1px solid #ddd',
                      borderRadius: '4px'
                    }}
                  />
                </div>
                
                <div>
                  <label>Min Surprise %</label>
                  <input
                    type="number"
                    value={status?.config?.min_surprise_percent || 10}
                    onChange={(e) => updateConfig('min_surprise_percent', parseFloat(e.target.value))}
                    step="1"
                    min="5"
                    max="25"
                    style={{
                      width: '100%',
                      padding: '8px',
                      marginTop: '5px',
                      border: '1px solid #ddd',
                      borderRadius: '4px'
                    }}
                  />
                </div>
                
                <div>
                  <label>Stop Loss %</label>
                  <input
                    type="number"
                    value={status?.config?.stop_loss_percent || 5}
                    onChange={(e) => updateConfig('stop_loss_percent', parseFloat(e.target.value))}
                    step="0.5"
                    min="1"
                    max="10"
                    style={{
                      width: '100%',
                      padding: '8px',
                      marginTop: '5px',
                      border: '1px solid #ddd',
                      borderRadius: '4px'
                    }}
                  />
                </div>
                
                <div>
                  <label>Take Profit %</label>
                  <input
                    type="number"
                    value={status?.config?.take_profit_percent || 3}
                    onChange={(e) => updateConfig('take_profit_percent', parseFloat(e.target.value))}
                    step="0.5"
                    min="1"
                    max="10"
                    style={{
                      width: '100%',
                      padding: '8px',
                      marginTop: '5px',
                      border: '1px solid #ddd',
                      borderRadius: '4px'
                    }}
                  />
                </div>
              </div>
            </div>
          )}

          {status?.recent_trades && status.recent_trades.length > 0 && (
            <div style={{marginTop: '2rem'}}>
              <h2>Recent Activity</h2>
              <div style={{
                background: '#fff',
                border: '1px solid #e0e0e0',
                borderRadius: '8px',
                overflow: 'hidden'
              }}>
                {status.recent_trades.slice(-10).reverse().map((trade, idx) => (
                  <div key={idx} style={{
                    padding: '15px 20px',
                    borderBottom: idx < status.recent_trades.length - 1 ? '1px solid #f0f0f0' : 'none',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}>
                    <div>
                      <strong>{trade.action === 'enter' ? '🟢' : '🔴'} {trade.action.toUpperCase()} {trade.symbol}</strong>
                      <div style={{fontSize: '0.9em', color: '#666', marginTop: '5px'}}>
                        {new Date(trade.timestamp).toLocaleString()} - {trade.reason}
                      </div>
                    </div>
                    {trade.pl !== undefined && (
                      <div style={{
                        fontSize: '1.1em',
                        fontWeight: 'bold',
                        color: trade.pl >= 0 ? '#4caf50' : '#f44336'
                      }}>
                        ${trade.pl.toFixed(2)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          <div style={{
            marginTop: '3rem',
            padding: '30px',
            background: '#e3f2fd',
            borderRadius: '12px',
            textAlign: 'center'
          }}>
            <h3>🎯 How It Works</h3>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(4, 1fr)',
              gap: '20px',
              marginTop: '20px',
              textAlign: 'left'
            }}>
              <div>
                <h4>1. Monitor</h4>
                <p>Scans for earnings releases every 30 minutes</p>
              </div>
              <div>
                <h4>2. Analyze</h4>
                <p>Calculates SUE scores and surprise metrics</p>
              </div>
              <div>
                <h4>3. Enter</h4>
                <p>Automatically enters high-confidence trades</p>
              </div>
              <div>
                <h4>4. Manage</h4>
                <p>Exits with stops, targets, or time limits</p>
              </div>
            </div>
            <p style={{marginTop: '20px', fontSize: '0.9em', color: '#666'}}>
              All trades use real-time market prices. 100% transparent paper trading.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}