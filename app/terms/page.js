'use client';

import '../globals.css';

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-gradient">
      <nav className="nav">
        <div className="container nav-content">
          <h3>Drift Analytics</h3>
          <div className="nav-links">
            <a href="/">Home</a>
            <a href="/dashboard">Dashboard</a>
            <a href="/membership">Pricing</a>
            <a href="/terms" className="active">Terms</a>
          </div>
        </div>
      </nav>

      <div className="terms-content">
        <div className="container">
          <h1>Terms of Service</h1>
          <p className="last-updated">Last Updated: April 28, 2026</p>
          
          <div className="risk-disclosure-banner">
            <h2>🚨 RISK DISCLOSURE WARNING</h2>
            <p><strong>Trading is risky and you will likely lose money. Past performance does not guarantee future results. This is not investment advice. Only trade with money you can afford to lose.</strong></p>
          </div>

          <div className="terms-section">
            <h2>1. Acceptance of Terms</h2>
            <p>By accessing and using Drift Analytics ("Service"), you accept and agree to be bound by the terms and provision of this agreement.</p>
          </div>

          <div className="terms-section">
            <h2>2. Description of Service</h2>
            <p>Drift Analytics provides post-earnings drift analysis, AI-powered trading recommendations, and market data ("Service"). The Service is provided "as is" and is intended for informational purposes only.</p>
          </div>

          <div className="terms-section">
            <h2>3. Subscription and Billing</h2>
            <h3>3.1 Free Trial</h3>
            <p>New users receive a 7-day free trial. No credit card required to start. You may cancel at any time during the trial period without charge.</p>
            
            <h3>3.2 Subscription Plans</h3>
            <p>After the trial period, continued use requires a paid subscription:</p>
            <ul>
              <li>Starter Plan: $97/month</li>
              <li>Professional Plan: $297/month (includes API access)</li>
              <li>Enterprise Plan: $997/month (includes unlimited API access)</li>
            </ul>
            
            <h3>3.3 Billing</h3>
            <p>Subscriptions are billed monthly in advance. All prices are in USD. Payments are processed securely through Stripe.</p>
          </div>

          <div className="terms-section">
            <h2>4. Cancellation and Refund Policy</h2>
            <h3>4.1 30-Day Money Back Guarantee</h3>
            <p>If you cancel within the first 30 days of your paid subscription, you will receive a full refund. Cancellation is immediate.</p>
            
            <h3>4.2 Cancellation After 30 Days</h3>
            <p>After the initial 30-day period, you may cancel your subscription at any time. Upon cancellation:</p>
            <ul>
              <li>Your subscription will remain active until the end of your current billing period</li>
              <li>You will retain full access to all features until your paid period expires</li>
              <li>No future charges will be made to your payment method</li>
              <li>No partial refunds are provided for unused time in the billing period</li>
            </ul>
            
            <h3>4.3 Reactivation</h3>
            <p>If you cancel your subscription, your account data will be retained for 90 days. You may reactivate your subscription at any time during this period without losing your settings, watchlists, or historical data.</p>
          </div>

          <div className="terms-section">
            <h2>5. User Conduct</h2>
            <p>You agree not to:</p>
            <ul>
              <li>Share your account credentials with others</li>
              <li>Attempt to reverse engineer or scrape the Service</li>
              <li>Use the Service for any illegal or unauthorized purpose</li>
              <li>Violate any laws in your jurisdiction</li>
              <li>Resell or redistribute our data without permission</li>
            </ul>
          </div>

          <div className="terms-section">
            <h2>6. Risk Disclosure & Investment Disclaimer</h2>
            
            <div className="risk-warning">
              <p><strong>⚠️ IMPORTANT RISK DISCLOSURE:</strong></p>
              <p>Trading stocks, options, and other securities involves substantial risk of loss and is not suitable for all investors. The high degree of leverage that is often obtainable in securities trading can work against you as well as for you. The use of leverage can lead to large losses as well as gains.</p>
            </div>
            
            <h3>6.1 No Investment Advice</h3>
            <p>Drift Analytics is NOT a registered investment advisor, broker dealer, or member of any association for investment professionals. All information provided is for educational and informational purposes only and does not constitute investment advice.</p>
            
            <h3>6.2 Trading Risks</h3>
            <p>You acknowledge and agree that:</p>
            <ul>
              <li>All trading decisions are your sole responsibility</li>
              <li>Past performance is NEVER indicative of future results</li>
              <li>You may lose some or all of your invested capital</li>
              <li>Only trade with money you can afford to lose</li>
              <li>Post-earnings drift patterns may not continue to work in the future</li>
              <li>Market conditions can change rapidly and without warning</li>
            </ul>
            
            <h3>6.3 Accuracy Disclaimer</h3>
            <p>While we strive for accuracy, we make NO guarantees regarding:</p>
            <ul>
              <li>The accuracy of earnings data or predictions</li>
              <li>The profitability of any suggested trades</li>
              <li>The continuation of historical patterns</li>
              <li>The timeliness of alerts or notifications</li>
            </ul>
            
            <h3>6.4 No Guarantees</h3>
            <p>We do NOT guarantee that you will make money using our Service. In fact, you should assume you will lose money. Only experienced traders who can afford losses should use this Service.</p>
            
            <h3>6.5 Seek Professional Advice</h3>
            <p>You should consult with a qualified financial advisor before making any investment decisions. Consider your financial situation, investment objectives, and risk tolerance before trading.</p>
            
            <h3>6.6 Paper Trading Disclosure</h3>
            <p>Paper trading results displayed on our platform are simulated and may not reflect actual trading results. Simulated results DO NOT represent actual trading and may over or under-compensate for market factors.</p>
          </div>

          <div className="terms-section">
            <h2>7. Data Accuracy</h2>
            <p>While we strive to provide accurate and timely information, we make no warranties about the accuracy, completeness, or timeliness of any data provided through the Service. Market data may be delayed or incorrect.</p>
          </div>

          <div className="terms-section">
            <h2>8. Limitation of Liability</h2>
            <p>IN NO EVENT SHALL DRIFT ANALYTICS, ITS OFFICERS, DIRECTORS, EMPLOYEES, OR AGENTS, BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES RESULTING FROM YOUR USE OF THE SERVICE.</p>
            <p>Our total liability shall not exceed the amount you paid for the Service in the 12 months prior to the claim.</p>
          </div>

          <div className="terms-section">
            <h2>9. Privacy</h2>
            <p>Your use of the Service is also governed by our Privacy Policy. We take your privacy seriously and do not sell your personal information.</p>
          </div>

          <div className="terms-section">
            <h2>10. Changes to Terms</h2>
            <p>We reserve the right to modify these terms at any time. We will notify you of any material changes via email. Continued use of the Service after changes constitutes acceptance of the new terms.</p>
          </div>

          <div className="terms-section">
            <h2>11. Termination</h2>
            <p>We reserve the right to terminate or suspend your account at any time for violation of these terms. In case of termination for cause, no refunds will be provided.</p>
          </div>

          <div className="terms-section">
            <h2>12. Governing Law</h2>
            <p>These Terms shall be governed by the laws of Delaware, United States, without regard to conflict of law principles.</p>
          </div>

          <div className="terms-section">
            <h2>13. Contact Information</h2>
            <p>For questions about these Terms, please contact us at:</p>
            <p>Email: support@driftanalytics.io<br />
            Website: https://driftanalytics.io</p>
          </div>

          <div className="terms-footer">
            <p>By using Drift Analytics, you acknowledge that you have read, understood, and agree to be bound by these Terms of Service.</p>
            <div className="terms-links">
              <a href="/privacy">Privacy Policy</a>
              <a href="/membership">View Pricing</a>
              <a href="/dashboard">Back to Dashboard</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}