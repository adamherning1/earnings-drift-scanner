#!/usr/bin/env python3
"""Learning Dashboard - Shows AI insights and performance evolution"""

import asyncio
from datetime import datetime, timedelta
import os
from trade_database import TradeDatabase
from adaptive_engine import AdaptiveTradingEngine
from ai_analyzer import AIMarketAnalyzer
import pandas as pd

class LearningDashboard:
    """Display learning progress and insights"""
    
    def __init__(self):
        self.db = TradeDatabase()
        self.ai = AIMarketAnalyzer()
        self.adaptive = AdaptiveTradingEngine(self.db, self.ai)
    
    def clear_screen(self):
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_learning_dashboard(self):
        """Display the learning dashboard"""
        self.clear_screen()
        
        print("=" * 80)
        print("         🧠 MGC ADAPTIVE LEARNING DASHBOARD")
        print("=" * 80)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 80)
        
        # Performance Evolution
        print("\n📈 PERFORMANCE EVOLUTION:")
        self._show_performance_trend()
        
        # Current Adaptive Parameters
        print("\n⚙️  ADAPTIVE PARAMETERS:")
        params = self.adaptive.current_params
        print(f"  KC Length: {params['kc_length']} (default: 15)")
        print(f"  KC Multiplier: {params['kc_mult_long']:.2f} (default: 0.75)")
        print(f"  ADX Threshold: {params['adx_threshold']} (default: 20)")
        print(f"  Position Size: {params['position_size']} contracts")
        print(f"  Confidence: {params['confidence_multiplier']:.2f}x")
        
        # Pattern Recognition
        print("\n🔍 DISCOVERED PATTERNS:")
        patterns = self.db.analyze_patterns()
        if 'by_day' in patterns and not patterns['by_day'].empty:
            print("\n  Best Trading Days:")
            day_names = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
            for _, row in patterns['by_day'].iterrows():
                day_idx = int(row['day_of_week'])
                win_rate = row['wins'] / row['total_trades'] * 100 if row['total_trades'] > 0 else 0
                print(f"    {day_names[day_idx]}: {win_rate:.1f}% win rate ({row['total_trades']} trades)")
        
        # Recent Insights
        print("\n💡 RECENT LEARNING INSIGHTS:")
        self._show_recent_insights()
        
        # AI Recommendations
        print("\n🤖 AI RECOMMENDATIONS:")
        self._show_ai_recommendations()
        
        print("\n" + "=" * 80)
        print("The bot is learning and improving with every trade!")
    
    def _show_performance_trend(self):
        """Show performance trend over time"""
        # Get trades by week
        trades_df = self.db.get_recent_performance(days=30)
        
        if trades_df.empty:
            print("  No trades yet - learning will begin with first trades")
            return
        
        # Group by week
        trades_df['week'] = pd.to_datetime(trades_df['timestamp']).dt.to_period('W')
        weekly_stats = trades_df.groupby('week').agg({
            'pnl': ['sum', 'count'],
            'pnl_percent': lambda x: (x > 0).mean()
        }).round(2)
        
        print("\n  Weekly Performance:")
        for week, stats in weekly_stats.iterrows():
            total_pnl = stats[('pnl', 'sum')]
            trade_count = stats[('pnl', 'count')]
            win_rate = stats[('pnl_percent', '<lambda>')] * 100
            
            # Visual indicator
            if total_pnl > 0:
                indicator = "📊⬆️"
            else:
                indicator = "📊⬇️"
                
            print(f"    Week {week}: {indicator} ${total_pnl:,.2f} ({trade_count} trades, {win_rate:.1f}% wins)")
    
    def _show_recent_insights(self):
        """Display recent learning insights"""
        try:
            conn = self.db.db_path
            insights_df = pd.read_sql_query('''
                SELECT timestamp, insight_type, description
                FROM learning_insights
                ORDER BY timestamp DESC
                LIMIT 5
            ''', conn)
            
            if insights_df.empty:
                print("  No insights recorded yet")
            else:
                for _, insight in insights_df.iterrows():
                    time_ago = datetime.now() - pd.to_datetime(insight['timestamp'])
                    hours_ago = time_ago.total_seconds() / 3600
                    
                    if hours_ago < 1:
                        time_str = f"{int(time_ago.total_seconds() / 60)}m ago"
                    elif hours_ago < 24:
                        time_str = f"{int(hours_ago)}h ago"
                    else:
                        time_str = f"{int(hours_ago / 24)}d ago"
                    
                    print(f"  • [{time_str}] {insight['description'][:80]}...")
        except:
            print("  No insights recorded yet")
    
    def _show_ai_recommendations(self):
        """Get current AI recommendations"""
        # Get recent performance for AI analysis
        trades_df = self.db.get_recent_performance(days=7)
        
        if trades_df.empty:
            print("  Start trading to receive AI recommendations")
            return
        
        # Calculate current state
        recent_wins = len(trades_df[trades_df['pnl'] > 0])
        recent_losses = len(trades_df[trades_df['pnl'] < 0])
        avg_pnl = trades_df['pnl'].mean()
        
        if recent_losses > recent_wins * 1.5:
            print("  ⚠️  High loss rate detected - AI recommends:")
            print("     • Reduce position size temporarily")
            print("     • Wait for stronger setups (higher ADX)")
            print("     • Consider skipping choppy market days")
        elif avg_pnl > 100:
            print("  ✅ Strong performance - AI recommends:")
            print("     • Maintain current parameters")
            print("     • Consider slight position size increase")
            print("     • Keep following the current strategy")
        else:
            print("  📊 Neutral performance - AI recommends:")
            print("     • Continue gathering data")
            print("     • Focus on high-probability setups")
            print("     • Review trades for pattern recognition")
    
    async def run(self):
        """Run the dashboard loop"""
        print("Starting Learning Dashboard...")
        
        try:
            while True:
                self.display_learning_dashboard()
                await asyncio.sleep(30)  # Update every 30 seconds
        except KeyboardInterrupt:
            print("\nLearning Dashboard stopped.")

if __name__ == "__main__":
    dashboard = LearningDashboard()
    asyncio.run(dashboard.run())