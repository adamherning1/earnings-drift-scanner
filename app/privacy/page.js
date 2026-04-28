'use client';

import '../globals.css';

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-gradient">
      <nav className="nav">
        <div className="container nav-content">
          <h3>Drift Analytics</h3>
          <div className="nav-links">
            <a href="/">Home</a>
            <a href="/dashboard">Dashboard</a>
            <a href="/membership">Pricing</a>
            <a href="/privacy" className="active">Privacy</a>
          </div>
        </div>
      </nav>

      <div className="privacy-content">
        <div className="container">
          <h1>Privacy Policy</h1>
          <p className="last-updated">Last Updated: April 28, 2026</p>

          <div className="privacy-section">
            <h2>1. Information We Collect</h2>
            <h3>1.1 Information You Provide</h3>
            <ul>
              <li>Email address (for account creation)</li>
              <li>Payment information (processed securely by Stripe - we never see your card number)</li>
              <li>Watchlist preferences and saved searches</li>
            </ul>
            
            <h3>1.2 Information Collected Automatically</h3>
            <ul>
              <li>Usage data (features used, frequency of access)</li>
              <li>Device information (browser type, IP address)</li>
              <li>Cookies for session management</li>
            </ul>
          </div>

          <div className="privacy-section">
            <h2>2. How We Use Your Information</h2>
            <p>We use collected information to:</p>
            <ul>
              <li>Provide and improve the Service</li>
              <li>Process payments and manage subscriptions</li>
              <li>Send service updates and trading alerts (if enabled)</li>
              <li>Provide customer support</li>
              <li>Detect and prevent fraud</li>
            </ul>
          </div>

          <div className="privacy-section">
            <h2>3. Information Sharing</h2>
            <p><strong>We do NOT sell, trade, or rent your personal information to third parties.</strong></p>
            <p>We may share information only in these cases:</p>
            <ul>
              <li>With Stripe for payment processing</li>
              <li>With service providers who help us operate the Service (e.g., email delivery)</li>
              <li>If required by law or legal process</li>
              <li>To protect our rights or the safety of users</li>
            </ul>
          </div>

          <div className="privacy-section">
            <h2>4. Data Security</h2>
            <p>We implement industry-standard security measures including:</p>
            <ul>
              <li>SSL/TLS encryption for all data transmission</li>
              <li>Encrypted storage of sensitive information</li>
              <li>Regular security audits</li>
              <li>Limited access to personal information (need-to-know basis)</li>
            </ul>
          </div>

          <div className="privacy-section">
            <h2>5. Data Retention</h2>
            <ul>
              <li>Active accounts: Data retained while subscription is active</li>
              <li>Cancelled accounts: Data retained for 90 days for reactivation</li>
              <li>After 90 days: Personal information is deleted, anonymized usage data may be retained</li>
              <li>Legal requirements: Some data may be retained longer if required by law</li>
            </ul>
          </div>

          <div className="privacy-section">
            <h2>6. Your Rights</h2>
            <p>You have the right to:</p>
            <ul>
              <li>Access your personal information</li>
              <li>Correct inaccurate information</li>
              <li>Request deletion of your account and data</li>
              <li>Export your data in a common format</li>
              <li>Opt-out of marketing communications</li>
            </ul>
            <p>To exercise these rights, contact support@driftanalytics.io</p>
          </div>

          <div className="privacy-section">
            <h2>7. Cookies</h2>
            <p>We use cookies for:</p>
            <ul>
              <li>Keeping you logged in</li>
              <li>Remembering your preferences</li>
              <li>Analytics to improve the Service</li>
            </ul>
            <p>You can disable cookies in your browser, but some features may not work properly.</p>
          </div>

          <div className="privacy-section">
            <h2>8. Third-Party Links</h2>
            <p>Our Service may contain links to third-party websites. We are not responsible for their privacy practices. Please review their privacy policies before providing any information.</p>
          </div>

          <div className="privacy-section">
            <h2>9. Children's Privacy</h2>
            <p>Drift Analytics is not intended for anyone under 18. We do not knowingly collect information from children. If you believe we have collected information from a minor, please contact us immediately.</p>
          </div>

          <div className="privacy-section">
            <h2>10. Changes to Privacy Policy</h2>
            <p>We may update this policy from time to time. Material changes will be notified via email. Continued use after changes constitutes acceptance.</p>
          </div>

          <div className="privacy-section">
            <h2>11. International Users</h2>
            <p>If you access the Service from outside the United States, your information may be transferred to and processed in the United States. By using the Service, you consent to this transfer.</p>
          </div>

          <div className="privacy-section">
            <h2>12. Contact Us</h2>
            <p>For privacy-related questions or concerns:</p>
            <p>Email: support@driftanalytics.io<br />
            Website: https://driftanalytics.io</p>
          </div>

          <div className="privacy-footer">
            <p>This Privacy Policy is part of our Terms of Service.</p>
            <div className="privacy-links">
              <a href="/terms">Terms of Service</a>
              <a href="/membership">View Pricing</a>
              <a href="/dashboard">Back to Dashboard</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}