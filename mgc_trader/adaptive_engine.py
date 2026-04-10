"""Adaptive Learning Engine for Self-Improving Trading"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, List
import json
from datetime import datetime, timedelta
import asyncio
from trade_database import TradeDatabase
from ai_analyzer import AIMarketAnalyzer
import logging

logger = logging.getLogger(__name__)

class AdaptiveTradingEngine:
    """Self-learning and parameter optimization engine"""
    
    def __init__(self, db: TradeDatabase, ai: AIMarketAnalyzer):
        self.db = db
        self.ai = ai
        self.current_params = self._load_current_params()
        self.performance_window = 100  # trades to analyze (more for day trading)
        self.confidence_threshold = 0.7
        
    def _load_current_params(self) -> Dict:
        """Load current trading parameters"""
        # Default parameters (can be overridden from file)
        params = {
            'kc_length': 15,
            'kc_mult_long': 0.75,
            'kc_length_short': 20,
            'kc_mult_short': 1.75,
            'adx_threshold': 20,
            'long_stop_atr': 5.0,
            'short_stop_atr': 2.0,
            'short_tp_r': 0.25,
            'position_size': 3,
            'max_daily_loss': 500,
            'confidence_multiplier': 1.0
        }
        
        try:
            with open('data/adaptive_params.json', 'r') as f:
                saved_params = json.load(f)
                params.update(saved_params)
        except:
            pass
        
        return params
    
    def save_params(self):
        """Save current parameters"""
        with open('data/adaptive_params.json', 'w') as f:
            json.dump(self.current_params, f, indent=2)
    
    async def analyze_recent_performance(self) -> Dict:
        """Analyze recent trades and identify patterns"""
        # Get recent trades
        trades_df = self.db.get_recent_performance(days=30)
        
        if len(trades_df) < 10:
            return {'status': 'insufficient_data'}
        
        # Calculate key metrics
        win_rate = (trades_df['pnl'] > 0).mean()
        avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if any(trades_df['pnl'] > 0) else 0
        avg_loss = abs(trades_df[trades_df['pnl'] < 0]['pnl'].mean()) if any(trades_df['pnl'] < 0) else 0
        profit_factor = avg_win / avg_loss if avg_loss > 0 else 0
        
        # Analyze patterns
        patterns = self.db.analyze_patterns()
        
        # Ask AI for insights
        ai_prompt = f"""Analyze this trading performance:
        - Win rate: {win_rate:.1%}
        - Average win: ${avg_win:.2f}
        - Average loss: ${avg_loss:.2f}
        - Profit factor: {profit_factor:.2f}
        
        Best performing days: {patterns['by_day'].to_string() if 'by_day' in patterns else 'N/A'}
        
        What adjustments would improve performance? Be specific about parameter changes."""
        
        ai_response = await self._get_ai_insight(ai_prompt)
        
        return {
            'status': 'analyzed',
            'metrics': {
                'win_rate': win_rate,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor,
                'total_trades': len(trades_df)
            },
            'patterns': patterns,
            'ai_insights': ai_response
        }
    
    async def _get_ai_insight(self, prompt: str) -> str:
        """Get AI analysis of performance"""
        try:
            import requests
            response = requests.post(
                f"http://192.168.0.58:11434/api/generate",
                json={
                    'model': 'llama3:8b',
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.3
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()['response']
        except:
            pass
        
        return "AI analysis unavailable"
    
    def calculate_position_size(self, recent_performance: List[float]) -> int:
        """Dynamically adjust position size based on performance"""
        if len(recent_performance) < 5:
            return self.current_params['position_size']
        
        # Kelly Criterion simplified
        recent = recent_performance[-10:]  # Last 10 trades
        wins = [p for p in recent if p > 0]
        losses = [abs(p) for p in recent if p < 0]
        
        if not wins or not losses:
            return self.current_params['position_size']
        
        win_rate = len(wins) / len(recent)
        avg_win = np.mean(wins)
        avg_loss = np.mean(losses)
        
        # Kelly percentage
        kelly = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
        kelly = max(0.1, min(kelly, 0.25))  # Cap between 10% and 25%
        
        # Adjust position size
        base_size = self.current_params['position_size']
        adjusted_size = int(base_size * (1 + kelly))
        
        # Never exceed max position
        return min(adjusted_size, base_size * 2)
    
    async def optimize_parameters(self) -> Dict:
        """Run parameter optimization using historical data"""
        logger.info("Starting parameter optimization...")
        
        # Get recent market data
        trades_df = self.db.get_recent_performance(days=60)
        
        if len(trades_df) < 20:
            return {'status': 'insufficient_data'}
        
        # Parameters to optimize
        param_ranges = {
            'kc_length': range(10, 21, 2),
            'kc_mult_long': np.arange(0.5, 1.5, 0.25),
            'adx_threshold': range(15, 31, 5),
            'long_stop_atr': np.arange(3.0, 7.0, 0.5)
        }
        
        best_score = -float('inf')
        best_params = self.current_params.copy()
        
        # Grid search (simplified - in practice use better optimization)
        for kc_len in param_ranges['kc_length']:
            for kc_mult in param_ranges['kc_mult_long']:
                for adx in param_ranges['adx_threshold']:
                    # Simulate performance with these parameters
                    score = self._backtest_params({
                        'kc_length': kc_len,
                        'kc_mult_long': kc_mult,
                        'adx_threshold': adx
                    }, trades_df)
                    
                    if score > best_score:
                        best_score = score
                        best_params.update({
                            'kc_length': kc_len,
                            'kc_mult_long': kc_mult,
                            'adx_threshold': adx
                        })
        
        # Only update if significantly better
        improvement = (best_score - self._current_score()) / abs(self._current_score())
        
        if improvement > 0.1:  # 10% improvement threshold
            self.current_params.update(best_params)
            self.save_params()
            
            self.db.record_insight(
                'parameter_optimization',
                f'Updated parameters for {improvement:.1%} improvement',
                confidence=0.8
            )
            
            return {
                'status': 'optimized',
                'improvement': improvement,
                'new_params': best_params
            }
        
        return {'status': 'no_improvement'}
    
    def _backtest_params(self, params: Dict, trades_df: pd.DataFrame) -> float:
        """Simple scoring function for parameters"""
        # This is simplified - in practice, run actual backtest
        # Score based on win rate and profit factor
        base_score = len(trades_df[trades_df['pnl'] > 0]) / len(trades_df)
        
        # Adjust based on parameter reasonableness
        if params['kc_length'] < 10 or params['kc_length'] > 20:
            base_score *= 0.9
        if params['adx_threshold'] < 15 or params['adx_threshold'] > 30:
            base_score *= 0.9
        
        return base_score
    
    def _current_score(self) -> float:
        """Calculate score for current parameters"""
        trades_df = self.db.get_recent_performance(days=30)
        if len(trades_df) == 0:
            return 0.5
        
        win_rate = (trades_df['pnl'] > 0).mean()
        return win_rate
    
    def should_trade_today(self) -> Tuple[bool, str]:
        """Decide if we should trade today based on patterns"""
        patterns = self.db.analyze_patterns()
        
        # Check day of week performance
        today_dow = str(datetime.now().weekday())
        
        if 'by_day' in patterns and not patterns['by_day'].empty:
            day_data = patterns['by_day']
            today_perf = day_data[day_data['day_of_week'] == today_dow]
            
            if not today_perf.empty:
                win_rate = today_perf.iloc[0]['wins'] / today_perf.iloc[0]['total_trades']
                
                if win_rate < 0.4 and today_perf.iloc[0]['total_trades'] > 10:
                    return False, f"Poor historical performance on {datetime.now().strftime('%A')}s"
        
        # Check recent performance
        recent = self.db.get_recent_performance(days=5)
        if len(recent) > 5:
            recent_losses = (recent['pnl'] < 0).sum()
            if recent_losses >= 4:
                return False, "Too many recent losses - taking a break"
        
        return True, "Good to trade"
    
    async def post_trade_analysis(self, trade_id: int):
        """Analyze a completed trade for learning"""
        conn = self.db.db_path
        trades_df = pd.read_sql_query(
            f'SELECT * FROM trades WHERE id = {trade_id}',
            conn
        )
        
        if trades_df.empty:
            return
        
        trade = trades_df.iloc[0]
        
        # Ask AI why the trade won/lost
        prompt = f"""Analyze this completed trade:
        Direction: {trade['direction']}
        Entry: ${trade['entry_price']}
        Exit: ${trade['exit_price']}
        P&L: ${trade['pnl']}
        Market conditions: {trade['market_conditions']}
        
        Why did this trade {('win' if trade['pnl'] > 0 else 'lose')}? 
        What can we learn for next time?"""
        
        ai_insight = await self._get_ai_insight(prompt)
        
        # Record the learning
        self.db.record_insight(
            'trade_analysis',
            f"Trade {trade_id}: {ai_insight[:200]}",
            confidence=0.6
        )
        
        # Update confidence in similar setups
        if trade['pnl'] > 0:
            self.current_params['confidence_multiplier'] = min(1.2, 
                self.current_params['confidence_multiplier'] * 1.02)
        else:
            self.current_params['confidence_multiplier'] = max(0.8,
                self.current_params['confidence_multiplier'] * 0.98)