'use client';

import { useState, useEffect } from 'react';
import '../globals.css';

export default function SecurityPage() {
  const [is2FAEnabled, setIs2FAEnabled] = useState(false);
  const [showSetup, setShowSetup] = useState(false);
  const [qrCode, setQrCode] = useState('');
  const [secret, setSecret] = useState('');
  const [backupCodes, setBackupCodes] = useState([]);
  const [verificationCode, setVerificationCode] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    // Check if 2FA is already enabled for this user
    const enabled = localStorage.getItem('2fa_enabled') === 'true';
    setIs2FAEnabled(enabled);
  }, []);

  const handleEnable2FA = async () => {
    try {
      const userEmail = localStorage.getItem('userEmail') || 'admin@driftanalytics.io';
      
      const response = await fetch('/api/auth/2fa-setup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: userEmail })
      });

      const data = await response.json();
      setQrCode(data.qrCode);
      setSecret(data.secret);
      setBackupCodes(data.backupCodes);
      setShowSetup(true);
    } catch (error) {
      setError('Failed to setup 2FA. Please try again.');
    }
  };

  const handleVerifyAndEnable = async () => {
    try {
      const userEmail = localStorage.getItem('userEmail') || 'admin@driftanalytics.io';
      
      const response = await fetch('/api/auth/2fa-verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          email: userEmail,
          token: verificationCode,
          secret: secret
        })
      });

      const data = await response.json();
      
      if (data.success) {
        // Save 2FA status and secret
        localStorage.setItem('2fa_enabled', 'true');
        localStorage.setItem('2fa_secret', secret);
        localStorage.setItem('2fa_backup_codes', JSON.stringify(backupCodes));
        
        setIs2FAEnabled(true);
        setShowSetup(false);
        setSuccess('Two-factor authentication has been enabled successfully!');
        setVerificationCode('');
      } else {
        setError('Invalid verification code. Please try again.');
      }
    } catch (error) {
      setError('Verification failed. Please try again.');
    }
  };

  const handleDisable2FA = () => {
    localStorage.removeItem('2fa_enabled');
    localStorage.removeItem('2fa_secret');
    localStorage.removeItem('2fa_backup_codes');
    setIs2FAEnabled(false);
    setSuccess('Two-factor authentication has been disabled.');
  };

  return (
    <div className="dashboard">
      <nav className="nav">
        <div className="container nav-content">
          <h3>Drift Analytics</h3>
          <div className="nav-links">
            <a href="/dashboard">Dashboard</a>
            <a href="/account">Account</a>
            <a href="/security" className="active">Security</a>
            <a href="/logout">Logout</a>
          </div>
        </div>
      </nav>

      <div className="dashboard-content">
        <div className="container">
          <h1>Security Settings</h1>

          {error && <div className="alert error">{error}</div>}
          {success && <div className="alert success">{success}</div>}

          <div className="security-card">
            <h2>Two-Factor Authentication (2FA)</h2>
            
            {!is2FAEnabled && !showSetup && (
              <>
                <p>Add an extra layer of security to your account by enabling two-factor authentication.</p>
                <button onClick={handleEnable2FA} className="btn-primary">
                  Enable Two-Factor Authentication
                </button>
              </>
            )}

            {is2FAEnabled && !showSetup && (
              <>
                <p className="status-enabled">✓ Two-factor authentication is enabled</p>
                <button onClick={handleDisable2FA} className="btn-danger">
                  Disable 2FA
                </button>
              </>
            )}

            {showSetup && (
              <div className="setup-2fa">
                <h3>Setup Two-Factor Authentication</h3>
                
                <div className="setup-steps">
                  <div className="step">
                    <h4>Step 1: Scan QR Code</h4>
                    <p>Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.)</p>
                    {qrCode && <img src={qrCode} alt="2FA QR Code" className="qr-code" />}
                    
                    <details>
                      <summary>Can't scan? Enter manually</summary>
                      <p className="manual-key">Secret key: {secret}</p>
                    </details>
                  </div>

                  <div className="step">
                    <h4>Step 2: Save Backup Codes</h4>
                    <p>Save these backup codes in a safe place. You can use them to access your account if you lose your authenticator device.</p>
                    <div className="backup-codes">
                      {backupCodes.map((code, index) => (
                        <div key={index} className="backup-code">{code}</div>
                      ))}
                    </div>
                  </div>

                  <div className="step">
                    <h4>Step 3: Verify</h4>
                    <p>Enter the 6-digit code from your authenticator app:</p>
                    <input
                      type="text"
                      value={verificationCode}
                      onChange={(e) => setVerificationCode(e.target.value)}
                      placeholder="000000"
                      maxLength="6"
                      className="verification-input"
                    />
                    <button 
                      onClick={handleVerifyAndEnable} 
                      disabled={verificationCode.length !== 6}
                      className="btn-primary"
                    >
                      Verify & Enable 2FA
                    </button>
                    <button onClick={() => setShowSetup(false)} className="btn-secondary">
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="security-card">
            <h2>Login History</h2>
            <p>Recent login activity for your account:</p>
            <table className="login-history">
              <thead>
                <tr>
                  <th>Date & Time</th>
                  <th>Location</th>
                  <th>IP Address</th>
                  <th>Device</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>{new Date().toLocaleString()}</td>
                  <td>Denver, CO, USA</td>
                  <td>192.168.1.1</td>
                  <td>Chrome on Windows</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="security-card">
            <h2>Security Recommendations</h2>
            <ul className="security-tips">
              <li>✓ Use a strong, unique password</li>
              <li>{is2FAEnabled ? '✓' : '○'} Enable two-factor authentication</li>
              <li>✓ Review login history regularly</li>
              <li>✓ Keep your browser up to date</li>
              <li>○ Use a password manager</li>
            </ul>
          </div>
        </div>
      </div>

      <style jsx>{`
        .security-card {
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 12px;
          padding: 2rem;
          margin-bottom: 2rem;
        }

        .alert {
          padding: 1rem;
          border-radius: 8px;
          margin-bottom: 2rem;
        }

        .alert.error {
          background: rgba(255, 0, 0, 0.1);
          border: 1px solid rgba(255, 0, 0, 0.3);
          color: #ff6666;
        }

        .alert.success {
          background: rgba(0, 255, 0, 0.1);
          border: 1px solid rgba(0, 255, 0, 0.3);
          color: #66ff66;
        }

        .btn-primary, .btn-danger, .btn-secondary {
          padding: 0.75rem 1.5rem;
          border-radius: 8px;
          border: none;
          font-weight: bold;
          cursor: pointer;
          margin-right: 1rem;
          margin-top: 1rem;
        }

        .btn-primary {
          background: linear-gradient(135deg, #667eea, #764ba2);
          color: white;
        }

        .btn-danger {
          background: #dc3545;
          color: white;
        }

        .btn-secondary {
          background: rgba(255, 255, 255, 0.1);
          color: white;
          border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .status-enabled {
          color: #66ff66;
          font-weight: bold;
          margin-bottom: 1rem;
        }

        .setup-2fa {
          margin-top: 2rem;
        }

        .setup-steps {
          margin-top: 1.5rem;
        }

        .step {
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 8px;
          padding: 1.5rem;
          margin-bottom: 1.5rem;
        }

        .step h4 {
          color: #667eea;
          margin-bottom: 1rem;
        }

        .qr-code {
          display: block;
          margin: 1rem 0;
          border: 4px solid white;
          border-radius: 8px;
        }

        .manual-key {
          font-family: monospace;
          background: rgba(0, 0, 0, 0.3);
          padding: 0.5rem;
          border-radius: 4px;
          word-break: break-all;
        }

        .backup-codes {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 0.5rem;
          margin: 1rem 0;
        }

        .backup-code {
          font-family: monospace;
          background: rgba(0, 0, 0, 0.3);
          padding: 0.5rem;
          border-radius: 4px;
          text-align: center;
        }

        .verification-input {
          display: block;
          width: 200px;
          padding: 0.75rem;
          font-size: 1.5rem;
          text-align: center;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: 8px;
          color: white;
          margin: 1rem 0;
          letter-spacing: 0.3em;
        }

        .login-history {
          width: 100%;
          margin-top: 1rem;
          border-collapse: collapse;
        }

        .login-history th {
          background: rgba(102, 126, 234, 0.1);
          padding: 0.75rem;
          text-align: left;
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .login-history td {
          padding: 0.75rem;
          border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        .security-tips {
          list-style: none;
          padding: 0;
        }

        .security-tips li {
          padding: 0.5rem 0;
          font-size: 1.1rem;
        }

        details {
          margin-top: 1rem;
          cursor: pointer;
        }

        summary {
          color: #667eea;
          text-decoration: underline;
        }
      `}</style>
    </div>
  );
}