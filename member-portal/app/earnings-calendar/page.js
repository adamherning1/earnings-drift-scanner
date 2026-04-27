'use client';

import { useEffect, useState } from 'react';
import '../globals.css';

export default function EarningsCalendarPage() {
  const [earnings, setEarnings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUpcomingEarnings();
  }, []);

  const fetchUpcomingEarnings = async () => {
    try {
      const res = await fetch('https://post-earnings-scanner-v2.onrender.com/api/upcoming-earnings');
      const data = await res.json();
      setEarnings(data.earnings || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching earnings calendar:', error);
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading earnings calendar...</div>;

  return (
    <div className="calendar-page">
      <nav className="nav">
        <div className="container nav-content">
          <h3>Post-Earnings Scanner</h3>
          <div className="nav-links">
            <a href="/dashboard">Dashboard</a>
            <a href="/earnings-calendar" className="active">Calendar</a>
          </div>
        </div>
      </nav>

      <div className="container">
        <h1>Upcoming Earnings Calendar</h1>
        <p className="subtitle">Real-time earnings announcements for the next 7 days</p>

        {earnings.length === 0 ? (
          <div className="no-earnings">No earnings scheduled for the next 7 days</div>
        ) : (
          <div className="earnings-grid">
            {earnings.map((earning, idx) => (
              <div key={idx} className="earning-card">
                <div className="earning-header">
                  <h3>{earning.symbol}</h3>
                  <span className="earning-date">{new Date(earning.date).toLocaleDateString()}</span>
                </div>
                
                {earning.current_price && (
                  <div className="earning-price">
                    <span className="label">Current Price:</span>
                    <span className="price">${Number(earning.current_price).toFixed(2)}</span>
                  </div>
                )}
                
                <div className="earning-footer">
                  <span className="time">{earning.time}</span>
                  <a href={`/analyze/${earning.symbol}`} className="analyze-btn">
                    Analyze →
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="calendar-footer">
          <p>Data provided by Finnhub • Updates hourly</p>
        </div>
      </div>

      <style jsx>{`
        .loading {
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          font-size: 1.2rem;
          color: #666;
        }

        .calendar-page {
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
          margin: 0;
        }

        .nav-links {
          display: flex;
          gap: 2rem;
        }

        .nav-links a {
          color: #666;
          text-decoration: none;
          font-weight: 500;
        }

        .nav-links a.active,
        .nav-links a:hover {
          color: #1e3c72;
        }

        .container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 3rem 20px;
        }

        h1 {
          color: #1e3c72;
          font-size: 2.5rem;
          margin-bottom: 0.5rem;
        }

        .subtitle {
          color: #666;
          font-size: 1.1rem;
          margin-bottom: 3rem;
        }

        .no-earnings {
          text-align: center;
          padding: 4rem;
          background: white;
          border-radius: 12px;
          color: #666;
          font-size: 1.1rem;
        }

        .earnings-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
          gap: 1.5rem;
          margin-bottom: 3rem;
        }

        .earning-card {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 2px 8px rgba(0,0,0,0.08);
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .earning-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        }

        .earning-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 1rem;
        }

        .earning-header h3 {
          color: #1e3c72;
          font-size: 1.4rem;
          margin: 0;
        }

        .earning-date {
          color: #666;
          font-size: 0.9rem;
          background: #f0f0f0;
          padding: 0.3rem 0.8rem;
          border-radius: 20px;
        }

        .earning-price {
          display: flex;
          justify-content: space-between;
          margin-bottom: 1rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid #eee;
        }

        .earning-price .label {
          color: #666;
          font-size: 0.9rem;
        }

        .earning-price .price {
          font-size: 1.2rem;
          font-weight: 600;
          color: #333;
        }

        .earning-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .time {
          background: #e3f2fd;
          color: #1976d2;
          padding: 0.3rem 0.8rem;
          border-radius: 20px;
          font-size: 0.85rem;
          font-weight: 500;
        }

        .analyze-btn {
          color: #27ae60;
          text-decoration: none;
          font-weight: 600;
          transition: color 0.2s;
        }

        .analyze-btn:hover {
          color: #219a52;
        }

        .calendar-footer {
          text-align: center;
          color: #666;
          font-size: 0.9rem;
        }

        @media (max-width: 768px) {
          .earnings-grid {
            grid-template-columns: 1fr;
          }
          
          h1 {
            font-size: 2rem;
          }
        }
      `}</style>
    </div>
  );
}