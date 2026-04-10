"""AI Market Analysis using Ollama on Dell RTX 3090"""

import requests
import json
import logging
from typing import Dict, Optional
import pandas as pd

logger = logging.getLogger(__name__)

class AIMarketAnalyzer:
    """Local AI analysis using Ollama on Dell"""
    
    def __init__(self, ollama_host: str = "192.168.0.58", ollama_port: int = 11434):
        self.base_url = f"http://{ollama_host}:{ollama_port}/api"
        self.model = "llama3:8b"  # Fast model for real-time analysis
        
    def test_connection(self) -> bool:
        """Test connection to Ollama"""
        try:
            response = requests.get(f"{self.base_url}/tags")
            return response.status_code == 200
        except:
            return False
    
    def analyze_market_conditions(self, df: pd.DataFrame) -> Dict:
        """AI analysis of current market conditions"""
        # Prepare market data summary
        latest = df.tail(10)
        
        prompt = f"""Analyze the following MGC gold futures 5-minute data for day trading:

Recent 10 bars:
{latest[['open', 'high', 'low', 'close', 'volume']].to_string()}

Current price: ${df['close'].iloc[-1]:.2f}
Session high: ${df['high'].max():.2f}
Session low: ${df['low'].min():.2f}
VWAP: ${df['close'].mean():.2f}
Current volume vs avg: {df['volume'].iloc[-1] / df['volume'].mean():.1f}x

Questions for day trading:
1. Is momentum accelerating or slowing?
2. Any volume divergence signals?
3. Key intraday support/resistance levels?
4. Best direction for next 5-30 minutes?

Provide brief, direct answers focused on short-term day trades."""

        try:
            response = requests.post(
                f"{self.base_url}/generate",
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.3,  # Lower temp for consistency
                        'top_p': 0.9
                    }
                }
            )
            
            if response.status_code == 200:
                analysis = response.json()['response']
                logger.info(f"AI Analysis: {analysis[:200]}...")
                
                # Parse AI response for trading signals
                analysis_lower = analysis.lower()
                
                return {
                    'bullish': 'bullish' in analysis_lower or 'uptrend' in analysis_lower,
                    'bearish': 'bearish' in analysis_lower or 'downtrend' in analysis_lower,
                    'warning': 'warning' in analysis_lower or 'avoid' in analysis_lower or 'caution' in analysis_lower,
                    'full_analysis': analysis
                }
            else:
                logger.error(f"AI request failed: {response.status_code}")
                return {'bullish': False, 'bearish': False, 'warning': False, 'full_analysis': 'AI unavailable'}
                
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return {'bullish': False, 'bearish': False, 'warning': False, 'full_analysis': 'AI error'}
    
    def validate_trade_setup(self, signal: str, df: pd.DataFrame) -> bool:
        """Use AI to validate a trade setup before entry"""
        
        prompt = f"""You are a risk management AI. Evaluate this MGC gold futures trade setup:

Signal: {signal}
Current price: ${df['close'].iloc[-1]:.2f}
ATR(14): ${df['close'].diff().abs().rolling(14).mean().iloc[-1]:.2f}
Volume trend: {'Increasing' if df['volume'].iloc[-1] > df['volume'].rolling(20).mean().iloc[-1] else 'Decreasing'}

Should we take this {signal} trade? Consider:
1. Market conditions
2. Risk/reward potential  
3. Any red flags

Reply with either:
- "APPROVED: [brief reason]" 
- "REJECTED: [brief reason]"
"""

        try:
            response = requests.post(
                f"{self.base_url}/generate",
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.2,  # Very low for consistency
                        'max_tokens': 100
                    }
                }
            )
            
            if response.status_code == 200:
                decision = response.json()['response']
                logger.info(f"AI Trade Validation: {decision}")
                
                return 'APPROVED' in decision.upper()
            else:
                logger.warning("AI validation unavailable, proceeding without AI check")
                return True  # Default to allowing trade if AI is down
                
        except Exception as e:
            logger.error(f"AI validation error: {e}")
            return True  # Default to allowing trade if AI fails
    
    def generate_daily_summary(self, trades: list, pnl: float) -> str:
        """Generate end-of-day summary using AI"""
        
        prompt = f"""Generate a brief trading summary for today's MGC gold futures trading:

Trades: {len(trades)}
Total P&L: ${pnl:,.2f}
Win rate: {sum(1 for t in trades if t['pnl'] > 0) / len(trades) * 100:.1f}% if trades else 0%

Key insights and recommendations for tomorrow in 2-3 sentences."""

        try:
            response = requests.post(
                f"{self.base_url}/generate",
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False
                }
            )
            
            if response.status_code == 200:
                return response.json()['response']
            else:
                return "Unable to generate AI summary"
                
        except:
            return "AI summary unavailable"