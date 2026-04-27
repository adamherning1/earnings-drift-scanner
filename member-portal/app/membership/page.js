'use client';

import { useState } from 'react';
import '../globals.css';

export default function MembershipPage() {
  const [email, setEmail] = useState('');
  const [selectedPlan, setSelectedPlan] = useState('monthly');

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

      <div className="membership-page">
        <div className="container">
          <h1>Choose Your Plan</h1>
          <p className="subtitle">Join as a Founding Member and Save 35%</p>

          <div className="plans-grid">
            <div className={`plan-card ${selectedPlan === 'monthly' ? 'selected' : ''}`} 
                 onClick={() => setSelectedPlan('monthly')}>
              <div className="plan-header">
                <h3>Monthly</h3>
                <div className="price-section">
                  <div className="price">$97</div>
                  <div className="price-period">/month</div>
                </div>
                <p className="regular-price">Regular price: $149/month</p>
              </div>
              <ul className="plan-features">
                <li>✅ Real-time earnings drift scanner</li>
                <li>✅ AI-powered recommendations</li>
                <li>✅ Up to 1,000 API calls/month</li>
                <li>✅ Email & SMS alerts</li>
                <li>✅ Historical drift analysis</li>
                <li>✅ Priority support</li>
                <li>✅ Cancel anytime</li>
              </ul>
            </div>

            <div className={`plan-card ${selectedPlan === 'annual' ? 'selected' : ''} popular`} 
                 onClick={() => setSelectedPlan('annual')}>
              <div className="popular-badge">BEST VALUE</div>
              <div className="plan-header">
                <h3>Annual</h3>
                <div className="price-section">
                  <div className="price">$970</div>
                  <div className="price-period">/year</div>
                </div>
                <p className="regular-price">Save $194 (2 months free!)</p>
              </div>
              <ul className="plan-features">
                <li>✅ Everything in Monthly</li>
                <li>✅ 2 months FREE</li>
                <li>✅ Unlimited API calls</li>
                <li>✅ Advanced analytics</li>
                <li>✅ Custom alerts</li>
                <li>✅ API webhook integration</li>
                <li>✅ White-glove onboarding</li>
              </ul>
            </div>
          </div>

          <div className="checkout-section">
            <h2>Start Your 7-Day Free Trial</h2>
            <p>No credit card required for trial. Cancel anytime.</p>
            
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
                Start Free Trial
              </button>
            </div>
          </div>

          <div className="guarantee-section">
            <h3>30-Day Money Back Guarantee</h3>
            <p>If you're not completely satisfied with the Post-Earnings Scanner, we'll refund your payment. No questions asked.</p>
          </div>

          <div className="faq-section">
            <h2>Frequently Asked Questions</h2>
            <div className="faq-grid">
              <div className="faq-item">
                <h4>What happens after the free trial?</h4>
                <p>After 7 days, you'll be charged for your selected plan. You can cancel anytime before the trial ends.</p>
              </div>
              <div className="faq-item">
                <h4>Can I change plans later?</h4>
                <p>Yes! You can upgrade or downgrade your plan at any time from your account dashboard.</p>
              </div>
              <div className="faq-item">
                <h4>What payment methods do you accept?</h4>
                <p>We accept all major credit cards, debit cards, and ACH bank transfers through Stripe.</p>
              </div>
              <div className="faq-item">
                <h4>Is my data secure?</h4>
                <p>Yes. We use bank-level encryption and never store your payment information directly.</p>
              </div>
            </div>
          </div>

          <p className="disclaimer">
            All trading involves risk. Past performance does not guarantee future results. 
            The Post-Earnings Scanner is for informational purposes only and is not financial advice.
          </p>
        </div>
      </div>
    </div>
  );
}