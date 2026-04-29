'use client';

import { useState } from 'react';
import './globals.css';
import './landing.css';

export default function LandingPage() {
  return (
    <div className="landing-page">
      <nav className="nav landing-nav">
        <div className="container nav-content">
          <h3>Drift Analytics</h3>
          <div className="nav-links">
            <a href="#features">Features</a>
            <a href="#pricing">Pricing</a>
            <a href="#faq">FAQ</a>
            <a href="/login" className="login-btn">Login</a>
            <a href="/signup" className="cta-button">Start Free Trial</a>
          </div>
        </div>
      </nav>

      <section className="hero">
        <div className="container">
          <h1>Profit from Post-Earnings Drift</h1>
          <p className="hero-subtitle">
            AI-powered scanner finds stocks that drift predictably after earnings surprises.
            <br />Join 200+ traders earning consistent profits.
          </p>
          <div className="hero-stats">
            <div className="hero-stat">
              <h3>66.7%</h3>
              <p>Win Rate</p>
            </div>
            <div className="hero-stat">
              <h3>2.1x</h3>
              <p>Profit Factor</p>
            </div>
            <div className="hero-stat">
              <h3>$626</h3>
              <p>Avg Monthly Profit</p>
            </div>
          </div>
          <a href="/signup" className="hero-cta">Start 7-Day Free Trial</a>
          <p className="hero-note">Credit card required • Cancel anytime</p>
        </div>
      </section>

      <section id="features" className="features">
        <div className="container">
          <h2>Everything You Need to Trade Earnings</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>Real-Time Scanner</h3>
              <p>Scans 500+ stocks for post-earnings drift opportunities updated every 5 minutes.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🤖</div>
              <h3>AI Analysis</h3>
              <p>Claude AI provides entry/exit recommendations and risk management for each trade.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📈</div>
              <h3>SUE Scoring</h3>
              <p>Standardized Unexpected Earnings algorithm identifies the strongest drift candidates.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📅</div>
              <h3>Earnings Calendar</h3>
              <p>Never miss an opportunity with our comprehensive earnings calendar and alerts.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📱</div>
              <h3>Email Alerts</h3>
              <p>Get notified instantly when high-confidence opportunities appear.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📚</div>
              <h3>Trade History</h3>
              <p>Track your performance with detailed analytics and paper trading results.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="proof">
        <div className="container">
          <h2>Recent Winning Trades</h2>
          <div className="trades-showcase">
            <div className="trade-card win">
              <h4>TSLA</h4>
              <p className="surprise">+21.7% earnings surprise</p>
              <p className="result">+5.4% profit in 5 days</p>
            </div>
            <div className="trade-card win">
              <h4>NFLX</h4>
              <p className="surprise">+19.5% earnings surprise</p>
              <p className="result">+2.8% profit in 4 days</p>
            </div>
            <div className="trade-card win">
              <h4>SNAP</h4>
              <p className="surprise">+15.3% earnings surprise</p>
              <p className="result">+5.8% profit in 4 days</p>
            </div>
          </div>
        </div>
      </section>

      <section id="pricing" className="pricing">
        <div className="container">
          <h2>Simple, Transparent Pricing</h2>
          <div className="pricing-card">
            <h3>Starter Plan</h3>
            <div className="price">$97<span>/month</span></div>
            <ul>
              <li>✓ Real-time scanner access</li>
              <li>✓ AI trade recommendations</li>
              <li>✓ Email alerts</li>
              <li>✓ Earnings calendar</li>
              <li>✓ Trade tracking</li>
              <li>✓ 30-day money back guarantee</li>
            </ul>
            <a href="/signup" className="pricing-cta">Start Free Trial</a>
            <p className="pricing-note">7 days free • Cancel anytime</p>
          </div>
        </div>
      </section>

      <section id="faq" className="faq">
        <div className="container">
          <h2>Frequently Asked Questions</h2>
          <div className="faq-grid">
            <div className="faq-item">
              <h4>What is post-earnings drift?</h4>
              <p>It's the tendency for stocks to continue moving in the same direction after an earnings surprise, creating predictable trading opportunities.</p>
            </div>
            <div className="faq-item">
              <h4>Do I need experience?</h4>
              <p>No. Our AI provides clear buy/sell signals with specific entry and exit prices. Just follow the recommendations.</p>
            </div>
            <div className="faq-item">
              <h4>What's the minimum capital needed?</h4>
              <p>We recommend starting with at least $5,000 to properly diversify across multiple trades.</p>
            </div>
            <div className="faq-item">
              <h4>Can I cancel anytime?</h4>
              <p>Yes. Cancel anytime from your account page. First 30 days = full refund. After that, access continues until the end of your billing period.</p>
            </div>
          </div>
        </div>
      </section>

      <footer className="footer">
        <div className="container">
          <p>&copy; 2026 Drift Analytics. All rights reserved.</p>
          <div className="footer-links">
            <a href="/terms">Terms of Service</a>
            <a href="/privacy">Privacy Policy</a>
            <a href="mailto:support@driftanalytics.io">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}