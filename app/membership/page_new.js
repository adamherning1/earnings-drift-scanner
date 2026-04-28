'use client';

import { useState } from 'react';
import '../globals.css';

export default function MembershipPage() {
  const [email, setEmail] = useState('');
  const [selectedPlan, setSelectedPlan] = useState('starter');

  const handleCheckout = () => {
    // TODO: Integrate with Stripe
    alert(`Starting checkout for ${selectedPlan} plan with email: ${email}`);
    // window.location.href = `https://buy.stripe.com/test_${selectedPlan}`;
  };

  return (
    <div className="min-h-screen bg-gradient">
      <nav className="nav">
        <div className="container nav-content">
          <h3>Drift Analytics</h3>
          <div className="nav-links">
            <a href="/">Home</a>
            <a href="/dashboard">Dashboard</a>
            <a href="/membership" className="active">Membership</a>
          </div>
        </div>
      </nav>

      <div className="membership-content">
        <div className="container">
          <h1>Choose Your Plan</h1>
          <p className="subheader">Get instant access to AI-powered post-earnings drift analysis</p>

          <div className="pricing-grid">
            <div className={`plan-card ${selectedPlan === 'starter' ? 'selected' : ''}`} 
                 onClick={() => setSelectedPlan('starter')}>
              <div className="plan-header">
                <h3>Starter</h3>
                <div className="price-section">
                  <div className="price">$97</div>
                  <div className="price-period">/month</div>
                </div>
                <p className="regular-price">Perfect for individual traders</p>
              </div>
              <ul className="plan-features">
                <li>✅ Real-time earnings scanner</li>
                <li>✅ AI drift predictions</li>
                <li>✅ Paper trading tracker</li>
                <li>✅ Email alerts</li>
                <li>✅ Basic support</li>
                <li>❌ <span style={{opacity: 0.5}}>API access</span></li>
                <li>❌ <span style={{opacity: 0.5}}>Webhook notifications</span></li>
              </ul>
            </div>

            <div className={`plan-card ${selectedPlan === 'professional' ? 'selected' : ''} popular`} 
                 onClick={() => setSelectedPlan('professional')}>
              <div className="popular-badge">BEST FOR DEVELOPERS</div>
              <div className="plan-header">
                <h3>Professional</h3>
                <div className="price-section">
                  <div className="price">$297</div>
                  <div className="price-period">/month</div>
                </div>
                <p className="regular-price">Includes full API access</p>
              </div>
              <ul className="plan-features">
                <li>✅ Everything in Starter</li>
                <li>✅ <strong>Full API access</strong></li>
                <li>✅ 10,000 API calls/month</li>
                <li>✅ Webhook notifications</li>
                <li>✅ Historical data export</li>
                <li>✅ Priority support</li>
                <li>✅ Custom integrations</li>
              </ul>
            </div>

            <div className={`plan-card ${selectedPlan === 'enterprise' ? 'selected' : ''}`} 
                 onClick={() => setSelectedPlan('enterprise')}>
              <div className="plan-header">
                <h3>Enterprise</h3>
                <div className="price-section">
                  <div className="price">$997</div>
                  <div className="price-period">/month</div>
                </div>
                <p className="regular-price">For funds & trading teams</p>
              </div>
              <ul className="plan-features">
                <li>✅ Everything in Professional</li>
                <li>✅ <strong>Unlimited API calls</strong></li>
                <li>✅ Dedicated infrastructure</li>
                <li>✅ White-glove onboarding</li>
                <li>✅ SLA guarantee</li>
                <li>✅ Custom features</li>
                <li>✅ Phone support</li>
              </ul>
            </div>
          </div>

          <div className="api-highlight">
            <h3>🔌 API Access Details</h3>
            <p>Professional and Enterprise plans include REST API access for:</p>
            <ul>
              <li>• Real-time earnings data and SUE scores</li>
              <li>• AI drift predictions and confidence levels</li>
              <li>• Historical earnings surprise data</li>
              <li>• Webhook notifications for new opportunities</li>
              <li>• Custom watchlist monitoring</li>
            </ul>
            <p className="api-note">Perfect for automated trading systems, custom dashboards, and algorithmic strategies.</p>
          </div>

          <div className="checkout-section">
            <h2>Ready to Start?</h2>
            <p>7-day free trial on all plans. Cancel anytime.</p>
            
            <div className="checkout-form">
              <input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="email-input"
              />
              <button 
                onClick={handleCheckout} 
                className="cta-button"
                disabled={!email}
              >
                Start Free Trial - {selectedPlan === 'starter' ? '$97' : selectedPlan === 'professional' ? '$297' : '$997'}/mo
              </button>
            </div>
          </div>

          <div className="guarantee-section">
            <h3>30-Day Money Back Guarantee</h3>
            <p>Not satisfied? Get a full refund within 30 days. No questions asked.</p>
          </div>

          <div className="faq-section">
            <h2>Frequently Asked Questions</h2>
            <div className="faq-grid">
              <div className="faq-item">
                <h4>Do I need API access?</h4>
                <p>Only if you want to integrate our data into your own trading systems. Most traders use the web dashboard.</p>
              </div>
              <div className="faq-item">
                <h4>Can I upgrade later?</h4>
                <p>Yes! Upgrade anytime and we'll prorate the difference. Downgrade at the end of any billing cycle.</p>
              </div>
              <div className="faq-item">
                <h4>What's included in API calls?</h4>
                <p>Each data request counts as one call. Professional gets 10,000/month, Enterprise is unlimited.</p>
              </div>
              <div className="faq-item">
                <h4>Is there a setup fee?</h4>
                <p>No setup fees. Start with a free trial and cancel anytime if it's not for you.</p>
              </div>
            </div>
          </div>

          <p className="disclaimer">
            Trading involves risk. Past performance doesn't guarantee future results. 
            Drift Analytics provides information only, not financial advice.
          </p>
        </div>
      </div>
    </div>
  );
}