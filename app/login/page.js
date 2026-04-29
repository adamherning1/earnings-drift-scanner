'use client';

import { useState } from 'react';
import '../globals.css';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Admin login check
    if (email === 'admin@driftanalytics.io' && password === 'DriftAdmin2026!') {
      // Admin login successful
      setTimeout(() => {
        localStorage.setItem('isLoggedIn', 'true');
        localStorage.setItem('userRole', 'admin');
        localStorage.setItem('userName', 'Adam');
        window.location.href = '/dashboard';
      }, 1000);
    } else if (email && password) {
      // Regular user login would go here in production
      setError('Invalid email or password');
      setLoading(false);
    } else {
      setError('Please enter your email and password');
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <nav className="nav">
        <div className="container nav-content">
          <h3><a href="/" style={{color: 'white', textDecoration: 'none'}}>Drift Analytics</a></h3>
          <div className="nav-links">
            <a href="/">Home</a>
            <a href="/signup" className="cta-button">Sign Up</a>
          </div>
        </div>
      </nav>

      <div className="auth-container">
        <div className="auth-card">
          <h2>Welcome Back</h2>
          <p className="auth-subtitle">Log in to access your earnings scanner</p>

          <form onSubmit={handleSubmit} className="auth-form">
            {error && <div className="error-message">{error}</div>}
            
            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>

            <div className="form-options">
              <label className="checkbox-label">
                <input type="checkbox" />
                Remember me
              </label>
              <a href="/forgot-password" className="forgot-link">Forgot password?</a>
            </div>

            <button type="submit" className="auth-submit" disabled={loading}>
              {loading ? 'Logging in...' : 'Log In'}
            </button>
          </form>

          <div className="auth-footer">
            <p>Don't have an account? <a href="/signup">Start free trial</a></p>
          </div>
        </div>

        <div className="auth-features">
          <h3>Your Trading Edge Awaits</h3>
          <ul>
            <li>📊 Real-time earnings scanner</li>
            <li>🤖 AI-powered recommendations</li>
            <li>📈 66.7% historical win rate</li>
            <li>📱 Instant email alerts</li>
          </ul>
        </div>
      </div>
    </div>
  );
}