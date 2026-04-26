'use client';

import { useState } from 'react';
import './globals.css';

export default function HomePage() {
  const [email, setEmail] = useState('');

  const handleSubscribe = async () => {
    // We'll add Stripe checkout here
    window.location.href = 'https://buy.stripe.com/test_your_link_here';
  };

  return (
    <div className="min-h-screen bg-gradient">
      {/* Hero Section */}
      <div className="hero">
        <div className="container">
          <h1>Stop Guessing. Start Profiting.</h1>
          <p className="subtitle">AI-Powered Post-Earnings Drift Scanner</p>
          <p className="sub-subtitle">Backed by 170,000 earnings events. Powered by Claude AI.</p>
          
          <div className="stats-row">
            <div className="stat">
              <div className="stat-number">60%</div>
              <div className="stat-label">Win Rate</div>
            </div>
            <div className="stat">
              <div className="stat-number">+$742</div>
              <div className="stat-label">Paper P&L</div>
            </div>
            <div className="stat">
              <div className="stat-number">3.8%</div>
              <div className="stat-label">Avg Drift</div>
            </div>
          </div>

          <div className="cta-box">
            <h3>Founding Member Special</h3>
            <div className="price">$97<span>/month</span></div>
            <p className="price-note">Regular price $149 after launch</p>
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="email-input"
            />
            <button onClick={handleSubscribe} className="cta-button">
              Start 7-Day Free Trial
            </button>
          </div>
        </div>
      </div>

      {/* Live Trades Section */}
      <section className="section">
        <div className="container">
          <h2>Live Paper Trading Results</h2>
          <div className="trades-table">
            <div className="trade-row header">
              <span>Symbol</span>
              <span>Entry</span>
              <span>Exit</span>
              <span>P&L</span>
              <span>Status</span>
            </div>
            <div className="trade-row win">
              <span>SNAP</span>
              <span>$15.42</span>
              <span>$16.01</span>
              <span>+3.83%</span>
              <span>✅ WIN</span>
            </div>
            <div className="trade-row win">
              <span>AAPL</span>
              <span>$172.45</span>
              <span>$178.23</span>
              <span>+3.35%</span>
              <span>✅ WIN</span>
            </div>
            <div className="trade-row loss">
              <span>MSFT</span>
              <span>$425.67</span>
              <span>$418.92</span>
              <span>-1.59%</span>
              <span>❌ LOSS</span>
            </div>
            <div className="trade-row active">
              <span>PINS</span>
              <span>$28.76</span>
              <span>-</span>
              <span>-</span>
              <span>🟡 ACTIVE</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="section bg-gray">
        <div className="container">
          <h2>What You Get</h2>
          <div className="features-grid">
            <div className="feature">
              <div className="feature-icon">🤖</div>
              <h3>AI Analysis</h3>
              <p>Claude AI analyzes every earnings release for drift potential</p>
            </div>
            <div className="feature">
              <div className="feature-icon">🎯</div>
              <h3>Clear Signals</h3>
              <p>Exact entry, target, and stop loss for every trade</p>
            </div>
            <div className="feature">
              <div className="feature-icon">📊</div>
              <h3>Full Transparency</h3>
              <p>Every trade logged publicly, wins and losses</p>
            </div>
            <div className="feature">
              <div className="feature-icon">🔌</div>
              <h3>API Access</h3>
              <p>Connect to your own trading systems via REST API</p>
            </div>
          </div>
        </div>
      </section>

      {/* Disclaimer Section */}
      <section className="disclaimer-section">
        <div className="container">
          <h2>⚠️ Important Risk Disclosure</h2>
          <p>
            <strong>NOT FINANCIAL ADVICE:</strong> This service is for informational and educational purposes only. 
            We are not registered investment advisors, broker-dealers, or financial planners. 
            No content on this site constitutes a recommendation to buy or sell securities.
          </p>
          <p>
            <strong>TRADING RISKS:</strong> Trading stocks and options involves substantial risk of loss and is not suitable for all investors. 
            Past performance is not indicative of future results. The high degree of leverage can work against you as well as for you.
          </p>
          <p>
            <strong>NO GUARANTEES:</strong> While our analysis is based on historical data and AI models, 
            there is no guarantee of profit. Markets can be unpredictable and you may lose some or all of your investment.
          </p>
          <p>
            <strong>YOUR RESPONSIBILITY:</strong> You are solely responsible for your own investment decisions. 
            Always conduct your own research and consult with a licensed financial advisor before making any investment.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer>
        <div className="container">
          <p>&copy; 2026 Post-Earnings Drift Scanner. All rights reserved.</p>
          <p>By using this service, you acknowledge that you have read and understood our risk disclosure.</p>
          <div className="footer-links">
            <a href="/terms">Terms of Service</a>
            <span>|</span>
            <a href="/privacy">Privacy Policy</a>
            <span>|</span>
            <a href="mailto:support@postearningsscanner.com">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}