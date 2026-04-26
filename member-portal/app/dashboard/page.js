'use client';

import { useEffect, useState } from 'react';
import '../globals.css';

export default function Dashboard() {
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOpportunities();
    const interval = setInterval(fetchOpportunities, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const fetchOpportunities = async () => {
    try {
      const res = await fetch('https://post-earning-scanner.onrender.com/api/opportunities');
      const data = await res.json();
      setOpportunities(data.opportunities || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching opportunities:', error);
      setLoading(false);
    }
  };

  return (
    <div className="dashboard">
      <nav className="nav">
        <div className="container nav-content">
          <h3>Post-Earnings Scanner</h3>
          <div className="nav-links">
            <a href="/dashboard" className="active">Dashboard</a>
            <a href="/trades">Trade History</a>
            <a href="/api-docs">API Docs</a>
            <a href="/account">Account</a>
            <a href="/logout">Logout</a>
          </div>
        </div>
      </nav>

      <div className="dashboard-content">
        <div className="container">
          <h1>Trading Opportunities</h1>
          <p className="last-update">Last updated: {new Date().toLocaleTimeString()}</p>

          {loading ? (
            <div className="loading">Loading opportunities...</div>
          ) : (
            <div className="opportunities-grid">
              {opportunities.map((opp, index) => (
                <div key={index} className={`opportunity-card ${opp.signal}`}>
                  <div className="opp-header">
                    <h3>{opp.symbol}</h3>
                    <span className={`confidence ${opp.confidence}`}>{opp.confidence}</span>
                  </div>
                  <div className="opp-price">${opp.price}</div>
                  <div className="opp-market-cap">{opp.market_cap}</div>
                  <div className="opp-signal">{opp.signal.replace('_', ' ')}</div>
                  <p className="opp-insight">{opp.ai_insight}</p>
                  <button className="analyze-btn" onClick={() => window.location.href = `/analyze/${opp.symbol}`}>
                    View Analysis →
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className="info-section">
            <h2>How to Use This Scanner</h2>
            <div className="info-grid">
              <div className="info-card">
                <h3>1. Monitor Opportunities</h3>
                <p>Check this dashboard for new post-earnings drift setups. We scan every earnings release.</p>
              </div>
              <div className="info-card">
                <h3>2. Review Analysis</h3>
                <p>Click any stock to see detailed AI analysis including entry, target, and stop levels.</p>
              </div>
              <div className="info-card">
                <h3>3. Execute Trades</h3>
                <p>Place trades in your own brokerage account. We provide the signals, you control execution.</p>
              </div>
              <div className="info-card">
                <h3>4. Track Performance</h3>
                <p>Monitor our paper trading results for transparency. All trades are logged publicly.</p>
              </div>
            </div>
          </div>

          <div className="disclaimer-section">
            <h3>⚠️ Risk Disclosure & Disclaimer</h3>
            <p>
              This service provides information and analysis for educational purposes only. It is not personalized investment advice or a recommendation to buy or sell securities.
              Trading involves substantial risk of loss and is not suitable for all investors. Past performance is not indicative of future results.
              Always conduct your own research and consult with a licensed financial advisor before making investment decisions.
              We are not registered investment advisors and do not provide personalized investment advice.
            </p>
          </div>
        </div>
      </div>

      <style jsx>{`
        .dashboard {
          min-height: 100vh;
          background: #f8f9fa;
        }

        .nav {
          background: white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          position: sticky;
          top: 0;
          z-index: 100;
        }

        .nav-content {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem 0;
        }

        .nav h3 {
          color: #1e3c72;
          font-size: 1.5rem;
        }

        .nav-links {
          display: flex;
          gap: 2rem;
        }

        .nav-links a {
          color: #666;
          text-decoration: none;
          font-weight: 500;
          transition: color 0.2s;
        }

        .nav-links a:hover,
        .nav-links a.active {
          color: #1e3c72;
        }

        .dashboard-content {
          padding: 3rem 20px;
        }

        .last-update {
          color: #666;
          margin-bottom: 2rem;
        }

        .loading {
          text-align: center;
          padding: 4rem;
          color: #666;
        }

        .opportunities-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 2rem;
          margin-bottom: 4rem;
        }

        .opportunity-card {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 2px 8px rgba(0,0,0,0.08);
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .opportunity-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        }

        .opportunity-card.POST_EARNINGS {
          border-top: 4px solid #27ae60;
        }

        .opportunity-card.UPCOMING {
          border-top: 4px solid #f39c12;
        }

        .opp-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .opp-header h3 {
          font-size: 1.5rem;
          color: #1e3c72;
        }

        .confidence {
          padding: 0.25rem 0.75rem;
          border-radius: 20px;
          font-size: 0.85rem;
          font-weight: 600;
        }

        .confidence.HIGH {
          background: #d4edda;
          color: #155724;
        }

        .confidence.MEDIUM {
          background: #fff3cd;
          color: #856404;
        }

        .opp-price {
          font-size: 2rem;
          font-weight: 700;
          color: #333;
          margin-bottom: 0.5rem;
        }

        .opp-market-cap {
          color: #666;
          margin-bottom: 0.5rem;
        }

        .opp-signal {
          color: #666;
          font-size: 0.9rem;
          margin-bottom: 1rem;
        }

        .opp-insight {
          color: #666;
          line-height: 1.5;
          margin-bottom: 1rem;
        }

        .analyze-btn {
          width: 100%;
          padding: 0.75rem;
          background: #1e3c72;
          color: white;
          border: none;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.2s;
        }

        .analyze-btn:hover {
          background: #2a5298;
        }

        .info-section {
          margin-top: 4rem;
        }

        .info-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 2rem;
        }

        .info-card {
          background: white;
          padding: 2rem;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }

        .info-card h3 {
          color: #1e3c72;
          margin-bottom: 1rem;
        }

        .info-card p {
          color: #666;
          line-height: 1.6;
        }

        .disclaimer-section {
          background: #fff3cd;
          border: 1px solid #ffeaa7;
          padding: 2rem;
          border-radius: 12px;
          margin-top: 3rem;
        }

        .disclaimer-section h3 {
          color: #856404;
          margin-bottom: 1rem;
        }

        .disclaimer-section p {
          color: #856404;
          line-height: 1.6;
          margin: 0;
        }
      `}</style>
    </div>
  );
}