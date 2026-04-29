'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import '../../globals.css';

export default function AnalyzePage() {
  const params = useParams();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (params.symbol) {
      fetchAnalysis();
    }
  }, [params.symbol]);

  const fetchAnalysis = async () => {
    try {
      const res = await fetch(`https://post-earnings-scanner-v2.onrender.com/api/analyze/${params.symbol}`);
      const data = await res.json();
      setAnalysis(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching analysis:', error);
      setLoading(false);
    }
  };

  if (loading) return <div className="loading-page">Loading analysis...</div>;
  if (!analysis) return <div className="error-page">Analysis not found</div>;

  return (
    <div className="analyze-page">
      <nav className="nav">
        <div className="container nav-content">
          <h3>Post-Earnings Scanner</h3>
          <div className="nav-links">
            <a href="/dashboard">← Back to Dashboard</a>
          </div>
        </div>
      </nav>

      <div className="container analyze-content">
        <h1>{analysis.symbol} Analysis</h1>
        
        <div className="analysis-grid">
          <div className="analysis-card">
            <h3>Current Price</h3>
            <div className="price">${Number(analysis.current_price).toFixed(2)}</div>
            <div className="market-cap">{analysis.market_cap}</div>
          </div>

          <div className="analysis-card">
            <h3>AI Recommendation</h3>
            <div className="recommendation">{analysis.ai_recommendation}</div>
          </div>
        </div>

        <div className="trade-setup">
          <h2>Historical Drift Statistics</h2>
          <p className="stats-disclaimer">Based on similar earnings surprises in the past 12 quarters</p>
          <div className="setup-grid">
            <div className="setup-item">
              <span className="label">Direction of historical drift:</span>
              <span className="value">{analysis.suggested_play?.direction === 'Long' ? 'Upward' : 'Downward'}</span>
            </div>
            <div className="setup-item">
              <span className="label">Average drift magnitude:</span>
              <span className="value">
                {analysis.analysis?.avg_post_earnings_move || '+2.5%'} 
                (≈ ${(Number(analysis.current_price) * (parseFloat(analysis.analysis?.avg_post_earnings_move || '2.5') / 100)).toFixed(2)} from current price)
              </span>
            </div>
            <div className="setup-item">
              <span className="label">Average drift duration:</span>
              <span className="value">{analysis.analysis?.avg_drift_duration || '3-30 trading days'}</span>
            </div>
            <div className="setup-item">
              <span className="label">1-standard-deviation downside move:</span>
              <span className="value stop">
                {analysis.analysis?.downside_risk || '-1.8%'} 
                (≈ ${(Number(analysis.current_price) * (Math.abs(parseFloat(analysis.analysis?.downside_risk || '-1.8')) / 100)).toFixed(2)} from current price)
              </span>
            </div>
            <div className="setup-item">
              <span className="label">Historical occurrence rate:</span>
              <span className="value">
                {analysis.analysis?.historical_win_rate || '65%'} 
                ({analysis.analysis?.occurrences || 'based on available data'})
              </span>
            </div>
          </div>
          <p className="stats-note">This data represents what has historically happened after {analysis.symbol} earnings beats with similar SUE scores. The reader must make their own investment decisions.</p>
        </div>

        <div className="analysis-details">
          <h3>Analysis Details</h3>
          <div className="details-grid">
            <div className="detail-item">
              <span>SUE Score:</span>
              <span>{analysis.analysis?.sue_score}</span>
            </div>
            <div className="detail-item">
              <span>Last Surprise:</span>
              <span style={{fontWeight: 'bold', color: analysis.analysis?.last_surprise?.includes('-') ? '#e74c3c' : '#27ae60'}}>{analysis.analysis?.last_surprise || 'N/A'}</span>
            </div>
            <div className="detail-item">
              <span>Historical Drift:</span>
              <span>{analysis.analysis?.historical_drift}</span>
            </div>
            <div className="detail-item">
              <span>Avg Post-Earnings Move:</span>
              <span>{analysis.analysis?.avg_post_earnings_move}</span>
            </div>
            <div className="detail-item">
              <span>Options Volume:</span>
              <span>{analysis.analysis?.options_activity}</span>
            </div>
            <div className="detail-item">
              <span>Based On:</span>
              <span style={{fontWeight: 'bold', color: '#27ae60'}}>{analysis.analysis?.based_on}</span>
            </div>
            <div className="detail-item">
              <span>Historical Win Rate:</span>
              <span style={{fontWeight: 'bold', color: '#1e3c72'}}>{analysis.analysis?.historical_win_rate}</span>
            </div>
            <div className="detail-item">
              <span>Confidence:</span>
              <span>{analysis.analysis?.drift_confidence}</span>
            </div>
          </div>
        </div>

        <div className="disclaimer">
          <h3>⚠️ Important Disclaimer</h3>
          <p>This analysis is for informational purposes only and should not be considered financial advice. Trading involves substantial risk and may not be suitable for all investors. Past performance does not guarantee future results. Always do your own research and consult with a qualified financial advisor before making investment decisions.</p>
        </div>
      </div>

      <style jsx>{`
        .loading-page, .error-page {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.2rem;
          color: #666;
        }

        .analyze-page {
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

        .nav-links a {
          color: #1e3c72;
          text-decoration: none;
          font-weight: 500;
        }

        .analyze-content {
          padding: 3rem 20px;
        }

        .analysis-grid {
          display: grid;
          grid-template-columns: 1fr 2fr;
          gap: 2rem;
          margin-bottom: 3rem;
        }

        .analysis-card {
          background: white;
          padding: 2rem;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }

        .price {
          font-size: 3rem;
          font-weight: 700;
          color: #1e3c72;
        }

        .market-cap {
          color: #666;
          margin-top: 0.5rem;
        }

        .recommendation {
          font-size: 1.3rem;
          color: #27ae60;
          font-weight: 600;
          line-height: 1.5;
        }

        .trade-setup {
          background: white;
          padding: 2.5rem;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.08);
          margin-bottom: 2rem;
        }

        .setup-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 2rem;
          margin-top: 2rem;
        }

        .setup-item {
          display: flex;
          flex-direction: column;
        }

        .setup-item .label {
          color: #666;
          font-size: 0.9rem;
          margin-bottom: 0.5rem;
        }

        .setup-item .value {
          font-size: 1.3rem;
          font-weight: 600;
          color: #333;
        }

        .setup-item .value.target {
          color: #27ae60;
        }

        .setup-item .value.stop {
          color: #e74c3c;
        }

        .analysis-details {
          background: white;
          padding: 2.5rem;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.08);
          margin-bottom: 2rem;
        }

        .details-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1.5rem;
          margin-top: 1.5rem;
        }

        .detail-item {
          display: flex;
          justify-content: space-between;
          padding-bottom: 0.5rem;
          border-bottom: 1px solid #eee;
        }

        .disclaimer {
          background: #fff3cd;
          border: 1px solid #ffeaa7;
          padding: 2rem;
          border-radius: 12px;
          margin-top: 2rem;
        }

        .disclaimer h3 {
          color: #856404;
          margin-bottom: 1rem;
        }

        .disclaimer p {
          color: #856404;
          line-height: 1.6;
        }

        .stats-disclaimer {
          color: #666;
          font-style: italic;
          margin: 0.5rem 0 1.5rem 0;
        }

        .stats-note {
          margin-top: 2rem;
          padding: 1rem;
          background: #f8f9fa;
          border-radius: 8px;
          color: #666;
          font-size: 0.9rem;
          line-height: 1.6;
        }

        @media (max-width: 768px) {
          .analysis-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
}