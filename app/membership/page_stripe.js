'use client';

import { useState } from 'react';
import '../globals.css';
import StripeCheckout from '../components/StripeCheckout';

export default function MembershipPage() {
  const [showCheckout, setShowCheckout] = useState(false);
  const [signupComplete, setSignupComplete] = useState(false);

  const handleSignupSuccess = (data) => {
    setSignupComplete(true);
    setShowCheckout(false);
    // Could redirect to dashboard or show success message
    window.location.href = '/dashboard';
  };

  const handleStartTrial = () => {
    setShowCheckout(true);
  };

  if (signupComplete) {
    return (
      <div className="min-h-screen bg-gradient flex items-center justify-center">
        <div className="success-message">
          <h2>Welcome to Drift Analytics!</h2>
          <p>Your 7-day trial has started. Redirecting to dashboard...</p>
        </div>
      </div>
    );
  }

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
          {!showCheckout ? (
            <>
              <h1>Start Your 7-Day Free Trial</h1>
              <p className="subheader">Get instant access to AI-powered post-earnings drift analysis</p>

              <div className="pricing-highlight">
                <div className="price-box">
                  <h2>Simple Pricing</h2>
                  <div className="price">$97<span>/month</span></div>
                  <p>after 7-day free trial</p>
                </div>
              </div>

              <div className="features-grid">
                <div className="feature">
                  <h3>✅ What's Included</h3>
                  <ul>
                    <li>Real-time earnings scanner</li>
                    <li>AI-powered drift predictions</li>
                    <li>Historical win rate analysis</li>
                    <li>Paper trading tracker</li>
                    <li>Email alerts for high-confidence plays</li>
                    <li>Earnings calendar</li>
                    <li>Full customer support</li>
                  </ul>
                </div>
                
                <div className="feature">
                  <h3>💳 Trial Details</h3>
                  <ul>
                    <li>7 days free - no charge today</li>
                    <li>Credit card required (secure)</li>
                    <li>Auto-bills $97 after trial</li>
                    <li>Cancel anytime, even during trial</li>
                    <li>30-day money back guarantee</li>
                  </ul>
                </div>
              </div>

              <div className="cta-section">
                <button onClick={handleStartTrial} className="cta-button">
                  Start Your Free Trial →
                </button>
                <p className="security-note">
                  🔒 Secured by Stripe • Your card info never touches our servers
                </p>
              </div>

              <div className="testimonial-section">
                <h3>Why Traders Choose Drift Analytics</h3>
                <div className="testimonials">
                  <div className="testimonial">
                    <p>"The post-earnings scanner paid for itself in the first week. Found TSLA before the 8% move."</p>
                    <cite>- Day Trader, California</cite>
                  </div>
                  <div className="testimonial">
                    <p>"Finally, a tool that actually explains WHY stocks move after earnings. The AI insights are gold."</p>
                    <cite>- Options Trader, New York</cite>
                  </div>
                  <div className="testimonial">
                    <p>"66% win rate on paper trades convinced me. Now using it live with great results."</p>
                    <cite>- Swing Trader, Texas</cite>
                  </div>
                </div>
              </div>

              <div className="faq-section">
                <h2>Frequently Asked Questions</h2>
                <div className="faq-grid">
                  <div className="faq-item">
                    <h4>Why do you need my credit card?</h4>
                    <p>To prevent abuse and ensure serious traders. You won't be charged for 7 days, and you can cancel anytime.</p>
                  </div>
                  <div className="faq-item">
                    <h4>How do I cancel?</h4>
                    <p>One click in your account settings. No phone calls, no hassle. Cancel even during the trial.</p>
                  </div>
                  <div className="faq-item">
                    <h4>What happens after 7 days?</h4>
                    <p>You'll be charged $97 for your first month. Then monthly after that until you cancel.</p>
                  </div>
                  <div className="faq-item">
                    <h4>Is my payment info secure?</h4>
                    <p>Yes! We use Stripe (same as Amazon, Google). Your card details never touch our servers.</p>
                  </div>
                </div>
              </div>

              <p className="disclaimer">
                Trading involves risk. Past performance doesn't guarantee future results. 
                Drift Analytics provides information only, not financial advice.
              </p>
            </>
          ) : (
            <div className="checkout-container">
              <h2>Complete Your Signup</h2>
              <p>Enter your payment details to start your 7-day free trial</p>
              <StripeCheckout onSuccess={handleSignupSuccess} />
              <button 
                onClick={() => setShowCheckout(false)} 
                className="back-button"
              >
                ← Back
              </button>
            </div>
          )}
        </div>
      </div>

      <footer className="legal-footer">
        <div className="footer-content">
          <p>&copy; 2026 Drift Analytics. All rights reserved.</p>
          <div className="footer-links">
            <a href="/terms">Terms of Service</a>
            <span className="separator">|</span>
            <a href="/privacy">Privacy Policy</a>
          </div>
        </div>
      </footer>
    </div>
  );
}