'use client';

import { useEffect, useState } from 'react';
import '../globals.css';
import SymbolSearch from '../components/SymbolSearch';

export default function Dashboard() {
  const [opportunities, setOpportunities] = useState([]);
  const [upcomingEarnings, setUpcomingEarnings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOpportunities();
    fetchUpcomingEarnings();
    const interval = setInterval(() => {
      fetchOpportunities();
      fetchUpcomingEarnings();
    }, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const fetchOpportunities = async () => {
    try {
      const res = await fetch('https://post-earnings-scanner-v2.onrender.com/api/opportunities');
      const data = await res.json();
      setOpportunities(data.opportunities || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching opportunities:', error);
      setLoading(false);
    }
  };

  const fetchUpcomingEarnings = async () => {
    try {
      const res = await fetch('https://post-earnings-scanner-v2.onrender.com/api/upcoming-earnings');
      const data = await res.json();
      setUpcomingEarnings(data.earnings || []);
    } catch (error) {
      console.error('Error fetching earnings calendar:', error);
    }
  };

  return (
    <div className="dashboard">
      <nav className="nav">
        <div className="container nav-content">
          <h3>Drift Analytics</h3>
          <div className="nav-links">
            <a href="/dashboard" className="active">Dashboard</a>
            <a href="/earnings-calendar">Calendar</a>
            <a href="/trades">Trade History</a>
            <a href="/account">Account</a>
            <a href="/membership" className="cta-nav">Upgrade</a>
            <a href="/logout">Logout</a>
          </div>
        </div>
      </nav>

      <div className="dashboard-content">
        <div className="container">
          <h1>Trading Opportunities</h1>
          <p className="last-update">Last updated: {new Date().toLocaleTimeString()}</p>

          <div className="search-section">
            <h3>Analyze Any Stock</h3>
            <p>Enter a ticker symbol to get AI-powered post-earnings drift analysis:</p>
            <SymbolSearch />
            <div className="popular-stocks">
              <p>Popular searches: 
                <a href="/analyze/AAPL">AAPL</a> • 
                <a href="/analyze/MSFT">MSFT</a> • 
                <a href="/analyze/GOOGL">GOOGL</a> • 
                <a href="/analyze/TSLA">TSLA</a> • 
                <a href="/analyze/NVDA">NVDA</a> • 
                <a href="/analyze/META">META</a> • 
                <a href="/analyze/AMZN">AMZN</a>
              </p>
            </div>
          </div>

          <div className="earnings-section">
            <h2>📅 Upcoming Earnings (Next 7 Days)</h2>
            {upcomingEarnings.length === 0 ? (
              <p className="no-earnings">No earnings scheduled for the next 7 days</p>
            ) : (
              <div className="earnings-grid">
                {upcomingEarnings.slice(0, 12).map((earning, idx) => (
                  <div key={idx} className="earning-card">
                    <div className="earning-symbol">{earning.symbol}</div>
                    <div className="earning-date">{new Date(earning.date).toLocaleDateString()}</div>
                    <div className="earning-price">${earning.current_price ? Number(earning.current_price).toFixed(2) : 'N/A'}</div>
                    <a href={`/analyze/${earning.symbol}`} className="earning-analyze">Analyze →</a>
                  </div>
                ))}
              </div>
            )}
            <a href="/earnings-calendar" className="view-all-earnings">View Full Calendar →</a>
          </div>

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
                  <div className="opp-price">{typeof opp.price === 'string' && opp.price.includes('$') ? opp.price : `$${Number(opp.price).toFixed(2)}`}</div>
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

        .search-section {
          background: white;
          padding: 2rem;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.08);
          margin-bottom: 3rem;
          text-align: center;
        }

        .search-section h3 {
          color: #1e3c72;
          margin-bottom: 0.5rem;
        }

        .search-section p {
          color: #666;
          margin-bottom: 1.5rem;
        }

        .popular-stocks {
          margin-top: 1rem;
          font-size: 0.9rem;
        }

        .popular-stocks a {
          color: #1e3c72;
          text-decoration: none;
        }

        .earnings-section {
          background: white;
          padding: 2rem;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.08);
          margin-bottom: 3rem;
        }

        .earnings-section h2 {
          color: #1e3c72;
          margin-bottom: 1.5rem;
        }

        .no-earnings {
          text-align: center;
          color: #666;
          padding: 2rem;
          background: #f8f9fa;
          border-radius: 8px;
        }

        .earnings-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 1rem;
          margin-bottom: 1.5rem;
        }

        .earning-card {
          border: 1px solid #e0e0e0;
          border-radius: 8px;
          padding: 1rem;
          text-align: center;
          transition: all 0.2s;
          background: #fff;
        }

        .earning-card:hover {
          box-shadow: 0 4px 12px rgba(0,0,0,0.1);
          transform: translateY(-2px);
        }

        .earning-symbol {
          font-size: 1.2rem;
          font-weight: 600;
          color: #1e3c72;
          margin-bottom: 0.5rem;
        }

        .earning-date {
          font-size: 0.9rem;
          color: #666;
          margin-bottom: 0.5rem;
        }

        .earning-price {
          font-size: 1.1rem;
          font-weight: 500;
          color: #333;
          margin-bottom: 0.5rem;
        }

        .earning-analyze {
          color: #27ae60;
          text-decoration: none;
          font-weight: 500;
          font-size: 0.9rem;
        }

        .earning-analyze:hover {
          color: #219a52;
        }

        .view-all-earnings {
          display: inline-block;
          color: #1e3c72;
          text-decoration: none;
          font-weight: 500;
          margin-top: 1rem;
        }

        .view-all-earnings:hover {
          text-decoration: underline;
          padding: 0 0.25rem;
          transition: color 0.2s;
        }

        .popular-stocks a:hover {
          color: #2a5298;
          text-decoration: underline;
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