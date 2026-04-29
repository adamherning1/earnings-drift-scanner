'use client';

import Link from 'next/link';
import '../globals.css';

export default function EducationPage() {
  return (
    <div className="container">
      <nav>
        <div className="nav-content">
          <div className="logo">
            <Link href="/">Drift Analytics</Link>
          </div>
          <div className="nav-links">
            <Link href="/">Scanner</Link>
            <Link href="/trades">Trades</Link>
            <Link href="/education" className="active">Education</Link>
            <Link href="/account">Account</Link>
            <Link href="/membership">Membership</Link>
          </div>
        </div>
      </nav>

      <main className="education-content">
        <h1>Trading Education Center</h1>
        
        <div className="education-section">
          <h2>📚 What is Post-Earnings Drift?</h2>
          <p>
            Post-Earnings Announcement Drift (PEAD) is one of the most studied and persistent market anomalies. 
            When companies report earnings that surprise the market, their stock prices tend to continue drifting 
            in the direction of the surprise for weeks or even months after the announcement.
          </p>
          <ul>
            <li><strong>Positive surprise →</strong> Stock drifts higher over following weeks</li>
            <li><strong>Negative surprise →</strong> Stock drifts lower over following weeks</li>
          </ul>
          <p>
            This happens because the market takes time to fully digest and price in the new information. 
            Institutional investors often can't trade immediately due to size constraints, creating a gradual drift.
          </p>
        </div>

        <div className="education-section">
          <h2>🎯 Understanding SUE (Standardized Unexpected Earnings)</h2>
          <p>
            SUE is the gold standard for measuring earnings surprises. It's calculated as:
          </p>
          <div className="formula">
            SUE = (Actual EPS - Expected EPS) / Standard Deviation of Past Surprises
          </div>
          <p>Why SUE matters:</p>
          <ul>
            <li><strong>SUE &gt; 2.0:</strong> Strong positive surprise → BUY signal</li>
            <li><strong>SUE &lt; -2.0:</strong> Strong negative surprise → SHORT signal</li>
            <li><strong>-2.0 to 2.0:</strong> Neutral zone → SKIP (no edge)</li>
          </ul>
          <p>
            SUE standardizes surprises across different companies, making a 5% surprise in a stable utility 
            comparable to a 5% surprise in a volatile tech stock.
          </p>
        </div>

        <div className="education-section">
          <h2>📈 How to Trade the Signals</h2>
          
          <h3>Entry Timing</h3>
          <ul>
            <li><strong>Day 1-2:</strong> Initial reaction period - often too volatile</li>
            <li><strong>Day 3-7:</strong> Sweet spot for entry - initial volatility settled</li>
            <li><strong>After Day 10:</strong> Drift may be largely captured</li>
          </ul>

          <h3>Position Sizing</h3>
          <p>Never risk more than 1-2% of your account on any single trade:</p>
          <ul>
            <li><strong>$10,000 account:</strong> Risk $100-200 per trade</li>
            <li><strong>$50,000 account:</strong> Risk $500-1,000 per trade</li>
            <li><strong>$100,000 account:</strong> Risk $1,000-2,000 per trade</li>
          </ul>
          
          <h3>Stop Loss Placement</h3>
          <ul>
            <li><strong>Stocks:</strong> 3-5% stop loss from entry</li>
            <li><strong>Options:</strong> 30-50% stop on premium paid</li>
            <li><strong>Trail stops</strong> after 5-10% profit to protect gains</li>
          </ul>

          <h3>Profit Targets</h3>
          <ul>
            <li><strong>Conservative:</strong> Exit at 5-7% profit</li>
            <li><strong>Standard:</strong> Exit at 10-15% profit</li>
            <li><strong>Aggressive:</strong> Trail stop, aim for 20%+</li>
          </ul>
        </div>

        <div className="education-section">
          <h2>🎯 Options vs Stock Expression</h2>
          
          <h3>When to Use Stock</h3>
          <ul>
            <li>Account under $25,000 (avoid PDT rules)</li>
            <li>Lower confidence signals (SUE between 2.0-3.0)</li>
            <li>Volatile market conditions</li>
            <li>Planning to hold 2-4 weeks</li>
          </ul>

          <h3>When to Use Options</h3>
          <ul>
            <li>High confidence signals (SUE &gt; 3.0)</li>
            <li>Want leverage with defined risk</li>
            <li>Expecting quick move (1-2 weeks)</li>
            <li>Account over $25,000</li>
          </ul>

          <h3>Options Strategy</h3>
          <ul>
            <li><strong>Timeframe:</strong> 30-45 DTE minimum</li>
            <li><strong>Strike:</strong> ATM or slightly OTM (1-2 strikes)</li>
            <li><strong>Greeks:</strong> Delta 0.40-0.60 preferred</li>
            <li><strong>Avoid:</strong> Weekly options (too much decay)</li>
          </ul>
        </div>

        <div className="education-section">
          <h2>⚠️ When to SKIP Signals</h2>
          <p>Not every signal should be traded. Skip when:</p>
          <ul>
            <li><strong>Market conditions:</strong> SPY in strong downtrend</li>
            <li><strong>Sector weakness:</strong> Stock's sector is collapsing</li>
            <li><strong>Low volume:</strong> Average volume under 500K shares</li>
            <li><strong>Penny stocks:</strong> Price under $5 (too manipulated)</li>
            <li><strong>Binary events:</strong> FDA approval, merger pending</li>
            <li><strong>Already moved:</strong> Stock already up/down 15%+ since earnings</li>
          </ul>
        </div>

        <div className="education-section">
          <h2>💡 Pro Tips from Successful Traders</h2>
          <ol>
            <li><strong>Quality over quantity:</strong> Better to take 2-3 high-confidence trades than 10 mediocre ones</li>
            <li><strong>Journal everything:</strong> Track your trades, what worked, what didn't</li>
            <li><strong>Respect stops:</strong> Never average down on a losing drift trade</li>
            <li><strong>Scale in:</strong> Start with 50% position, add on confirmation</li>
            <li><strong>Morning entries:</strong> Best liquidity 30-60 min after open</li>
            <li><strong>Avoid Fridays:</strong> Weekend risk can disrupt drift patterns</li>
            <li><strong>Watch the SPY:</strong> When market tanks, even good drifts fail</li>
          </ol>
        </div>

        <div className="education-section">
          <h2>📊 Real Example</h2>
          <div className="example-box">
            <h3>Netflix (NFLX) - Q4 2025 Earnings</h3>
            <ul>
              <li><strong>EPS Expected:</strong> $4.52</li>
              <li><strong>EPS Actual:</strong> $5.40</li>
              <li><strong>Surprise:</strong> +19.5%</li>
              <li><strong>SUE Score:</strong> 3.8 (Strong Buy)</li>
              <li><strong>Entry Day 3:</strong> $492</li>
              <li><strong>Exit Day 18:</strong> $531</li>
              <li><strong>Profit:</strong> +7.9%</li>
            </ul>
            <p>
              <strong>Why it worked:</strong> High SUE + tech sector strength + beat on subscribers = perfect drift setup
            </p>
          </div>
        </div>

        <div className="education-section">
          <h2>❓ Common Mistakes to Avoid</h2>
          <ul>
            <li><strong>Chasing:</strong> Don't enter after stock already moved 10%+</li>
            <li><strong>Oversizing:</strong> One bad trade shouldn't damage your account</li>
            <li><strong>Ignoring market:</strong> Best drifts fail in bear markets</li>
            <li><strong>Too early:</strong> Day 1 is often a fake-out</li>
            <li><strong>No plan:</strong> Know your entry, stop, and target BEFORE trading</li>
            <li><strong>FOMO:</strong> Missing a signal is better than forcing a bad trade</li>
          </ul>
        </div>

        <div className="education-section">
          <h2>🎓 Recommended Learning Path</h2>
          <ol>
            <li><strong>Week 1:</strong> Paper trade every signal to learn the patterns</li>
            <li><strong>Week 2-3:</strong> Start with 25% normal position size</li>
            <li><strong>Month 2:</strong> Scale to 50% size once profitable</li>
            <li><strong>Month 3+:</strong> Full size only after 20+ successful trades</li>
          </ol>
          <p>
            <strong>Remember:</strong> Post-earnings drift is a statistical edge that plays out over many trades. 
            No single trade matters - focus on executing the system consistently.
          </p>
        </div>

        <div className="cta-section">
          <h2>Ready to Start Trading?</h2>
          <p>Join Drift Analytics to get real-time signals, AI analysis, and trade tracking.</p>
          <Link href="/membership" className="cta-button">Start Your 7-Day Trial</Link>
        </div>
      </main>

      <footer>
        <p>&copy; 2026 Drift Analytics. Educational content for informational purposes only. Not financial advice.</p>
      </footer>

      <style jsx>{`
        .education-content {
          max-width: 900px;
          margin: 0 auto;
          padding: 2rem;
        }

        .education-content h1 {
          font-size: 2.5rem;
          margin-bottom: 2rem;
          text-align: center;
        }

        .education-section {
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 12px;
          padding: 2rem;
          margin-bottom: 2rem;
        }

        .education-section h2 {
          color: #00ff88;
          margin-bottom: 1rem;
        }

        .education-section h3 {
          color: #00cc66;
          margin-top: 1.5rem;
          margin-bottom: 0.75rem;
        }

        .education-section p {
          line-height: 1.8;
          margin-bottom: 1rem;
        }

        .education-section ul {
          list-style: none;
          padding: 0;
        }

        .education-section ul li {
          padding: 0.5rem 0;
          padding-left: 1.5rem;
          position: relative;
        }

        .education-section ul li:before {
          content: "→";
          position: absolute;
          left: 0;
          color: #00ff88;
        }

        .education-section ol {
          padding-left: 1.5rem;
        }

        .education-section ol li {
          margin-bottom: 0.75rem;
        }

        .formula {
          background: rgba(0, 255, 136, 0.1);
          border: 1px solid #00ff88;
          padding: 1rem;
          margin: 1rem 0;
          text-align: center;
          font-family: 'Courier New', monospace;
          border-radius: 8px;
        }

        .example-box {
          background: rgba(0, 136, 255, 0.1);
          border: 1px solid #0088ff;
          padding: 1.5rem;
          border-radius: 8px;
          margin-top: 1rem;
        }

        .example-box h3 {
          margin-top: 0;
          color: #0088ff;
        }

        .cta-section {
          text-align: center;
          margin-top: 3rem;
          padding: 2rem;
          background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 136, 255, 0.1));
          border-radius: 12px;
        }

        .cta-button {
          display: inline-block;
          background: linear-gradient(135deg, #00ff88, #0088ff);
          color: #000;
          padding: 1rem 2rem;
          border-radius: 8px;
          text-decoration: none;
          font-weight: bold;
          margin-top: 1rem;
          transition: transform 0.2s;
        }

        .cta-button:hover {
          transform: scale(1.05);
        }

        .active {
          color: #00ff88 !important;
        }
      `}</style>
    </div>
  );
}