'use client';

import { useEffect, useState } from 'react';
import '../globals.css';

export default function AccountPage() {
  const [user, setUser] = useState({
    email: 'demo@example.com',
    plan: 'Founding Member',
    status: 'Active',
    joinDate: 'April 15, 2026',
    nextBilling: 'May 15, 2026',
    apiCalls: 156,
    apiLimit: 1000
  });

  // Check if user plan includes API access
  const hasApiAccess = user.plan === 'Professional' || user.plan === 'Enterprise';

  return (
    <div className="dashboard">
      <nav className="nav">
        <div className="container nav-content">
          <h3>Drift Analytics</h3>
          <div className="nav-links">
            <a href="/dashboard">Dashboard</a>
            <a href="/earnings-calendar">Calendar</a>
            <a href="/trades">Trade History</a>
            <a href="/account" className="active">Account</a>
            <a href="/logout">Logout</a>
          </div>
        </div>
      </nav>

      <div className="dashboard-content">
        <div className="container">
          <h1>Account Settings</h1>
          
          <div className="account-card">
            <h2>Subscription Details</h2>
            <div className="account-info">
              <div className="info-row">
                <span className="label">Email:</span>
                <span className="value">{user.email}</span>
              </div>
              <div className="info-row">
                <span className="label">Plan:</span>
                <span className="value">{user.plan} - $97/month</span>
              </div>
              <div className="info-row">
                <span className="label">Status:</span>
                <span className="value status-active">{user.status}</span>
              </div>
              <div className="info-row">
                <span className="label">Member Since:</span>
                <span className="value">{user.joinDate}</span>
              </div>
              <div className="info-row">
                <span className="label">Next Billing Date:</span>
                <span className="value">{user.nextBilling}</span>
              </div>
            </div>
            <div className="button-group">
              <button className="btn-secondary">Update Payment Method</button>
              <button className="btn-danger">Cancel Subscription</button>
            </div>
          </div>

          {hasApiAccess && (
            <div className="account-card">
              <h2>API Usage</h2>
              <div className="account-info">
                <div className="info-row">
                  <span className="label">API Calls This Month:</span>
                  <span className="value">{user.apiCalls} / {user.apiLimit}</span>
                </div>
                <div className="usage-bar">
                  <div className="usage-fill" style={{width: `${(user.apiCalls / user.apiLimit) * 100}%`}}></div>
                </div>
                <p className="usage-note">Resets on {user.nextBilling}</p>
              </div>
            </div>
          )}

          {hasApiAccess && (
            <div className="account-card">
              <h2>API Key</h2>
              <div className="api-key-section">
                <code className="api-key">sk_live_51N..............................</code>
                <button className="btn-primary">Regenerate Key</button>
              </div>
              <p className="disclaimer">Keep your API key secure. Do not share it publicly.</p>
            </div>
          )}

          {!hasApiAccess && (
            <div className="account-card upgrade-prompt">
              <h2>🚀 Upgrade to Professional</h2>
              <p>Unlock API access and integrate Drift Analytics into your trading systems.</p>
              <ul className="upgrade-benefits">
                <li>• 10,000 API calls per month</li>
                <li>• Real-time webhook notifications</li>
                <li>• Historical data export</li>
                <li>• Priority support</li>
              </ul>
              <a href="/membership" className="btn-primary">View Upgrade Options</a>
            </div>
          )}

          <div className="account-card">
            <h2>Notification Preferences</h2>
            <div className="preferences">
              <label className="checkbox-label">
                <input type="checkbox" defaultChecked />
                <span>Email alerts for high-confidence opportunities (SUE &gt; 2.0)</span>
              </label>
              <label className="checkbox-label">
                <input type="checkbox" defaultChecked />
                <span>Weekly performance summary</span>
              </label>
              <label className="checkbox-label">
                <input type="checkbox" />
                <span>Real-time SMS alerts (requires phone verification)</span>
              </label>
            </div>
            <button className="btn-primary">Save Preferences</button>
          </div>

          <footer className="legal-footer">
            <div className="footer-content">
              <p>&copy; 2026 Drift Analytics. All rights reserved.</p>
              <div className="footer-links">
                <a href="/terms">Terms of Service</a>
                <span className="separator">|</span>
                <a href="/privacy">Privacy Policy</a>
                <span className="separator">|</span>
                <a href="/membership">Pricing</a>
              </div>
            </div>
          </footer>
        </div>
      </div>
    </div>
  );
}