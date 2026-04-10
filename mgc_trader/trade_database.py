"""Trade Database for Learning and Analysis"""

import sqlite3
import pandas as pd
from datetime import datetime
import json
from typing import Dict, List, Optional

class TradeDatabase:
    """Persistent storage for all trades and market conditions"""
    
    def __init__(self, db_path: str = "data/trades.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                symbol TEXT,
                direction TEXT,
                entry_price REAL,
                exit_price REAL,
                quantity INTEGER,
                pnl REAL,
                pnl_percent REAL,
                stop_loss REAL,
                take_profit REAL,
                entry_reason TEXT,
                exit_reason TEXT,
                market_conditions TEXT,
                ai_score REAL,
                duration_minutes INTEGER
            )
        ''')
        
        # Market conditions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_conditions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                symbol TEXT,
                timeframe TEXT,
                trend TEXT,
                volatility REAL,
                adx REAL,
                volume_ratio REAL,
                price_position REAL,
                day_of_week INTEGER,
                hour_of_day INTEGER,
                conditions_json TEXT
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                date DATE PRIMARY KEY,
                total_trades INTEGER,
                winning_trades INTEGER,
                losing_trades INTEGER,
                total_pnl REAL,
                win_rate REAL,
                avg_win REAL,
                avg_loss REAL,
                profit_factor REAL,
                max_drawdown REAL,
                sharpe_ratio REAL
            )
        ''')
        
        # Learning insights table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                insight_type TEXT,
                description TEXT,
                confidence REAL,
                action_taken TEXT,
                impact_measured REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_trade_entry(self, trade_data: Dict) -> int:
        """Record a new trade entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (
                timestamp, symbol, direction, entry_price, quantity,
                stop_loss, take_profit, entry_reason, market_conditions, ai_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now(),
            trade_data['symbol'],
            trade_data['direction'],
            trade_data['entry_price'],
            trade_data['quantity'],
            trade_data.get('stop_loss'),
            trade_data.get('take_profit'),
            trade_data.get('entry_reason'),
            json.dumps(trade_data.get('market_conditions', {})),
            trade_data.get('ai_score', 0.5)
        ))
        
        trade_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return trade_id
    
    def update_trade_exit(self, trade_id: int, exit_data: Dict):
        """Update trade with exit information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get entry data
        cursor.execute('SELECT entry_price, quantity, timestamp FROM trades WHERE id = ?', (trade_id,))
        entry_price, quantity, entry_time = cursor.fetchone()
        
        # Calculate P&L
        exit_price = exit_data['exit_price']
        if exit_data['direction'] == 'LONG':
            pnl = (exit_price - entry_price) * quantity
        else:
            pnl = (entry_price - exit_price) * quantity
        
        pnl_percent = (pnl / (entry_price * quantity)) * 100
        
        # Calculate duration
        duration = (datetime.now() - datetime.fromisoformat(entry_time)).seconds // 60
        
        cursor.execute('''
            UPDATE trades SET
                exit_price = ?,
                exit_reason = ?,
                pnl = ?,
                pnl_percent = ?,
                duration_minutes = ?
            WHERE id = ?
        ''', (
            exit_price,
            exit_data.get('exit_reason'),
            pnl,
            pnl_percent,
            duration,
            trade_id
        ))
        
        conn.commit()
        conn.close()
    
    def get_recent_performance(self, days: int = 30) -> pd.DataFrame:
        """Get recent trading performance"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT * FROM trades 
            WHERE timestamp > datetime('now', '-{} days')
            AND exit_price IS NOT NULL
            ORDER BY timestamp DESC
        '''.format(days)
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def analyze_patterns(self) -> Dict:
        """Analyze trading patterns for learning"""
        conn = sqlite3.connect(self.db_path)
        
        # Win rate by day of week
        day_analysis = pd.read_sql_query('''
            SELECT 
                strftime('%w', timestamp) as day_of_week,
                COUNT(*) as total_trades,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                AVG(pnl) as avg_pnl
            FROM trades
            WHERE exit_price IS NOT NULL
            GROUP BY day_of_week
        ''', conn)
        
        # Win rate by hour
        hour_analysis = pd.read_sql_query('''
            SELECT 
                strftime('%H', timestamp) as hour,
                COUNT(*) as total_trades,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                AVG(pnl) as avg_pnl
            FROM trades
            WHERE exit_price IS NOT NULL
            GROUP BY hour
        ''', conn)
        
        # Best/worst market conditions
        condition_analysis = pd.read_sql_query('''
            SELECT 
                market_conditions,
                COUNT(*) as trades,
                AVG(pnl) as avg_pnl,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate
            FROM trades
            WHERE exit_price IS NOT NULL
            GROUP BY market_conditions
            HAVING trades > 5
            ORDER BY avg_pnl DESC
        ''', conn)
        
        conn.close()
        
        return {
            'by_day': day_analysis,
            'by_hour': hour_analysis,
            'by_conditions': condition_analysis
        }
    
    def record_market_snapshot(self, data: Dict):
        """Record current market conditions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO market_conditions (
                timestamp, symbol, timeframe, trend, volatility,
                adx, volume_ratio, price_position, day_of_week, hour_of_day,
                conditions_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now(),
            data['symbol'],
            data['timeframe'],
            data.get('trend'),
            data.get('volatility'),
            data.get('adx'),
            data.get('volume_ratio'),
            data.get('price_position'),
            datetime.now().weekday(),
            datetime.now().hour,
            json.dumps(data)
        ))
        
        conn.commit()
        conn.close()
    
    def record_insight(self, insight_type: str, description: str, confidence: float = 0.5):
        """Record a learning insight"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO learning_insights (
                timestamp, insight_type, description, confidence
            ) VALUES (?, ?, ?, ?)
        ''', (datetime.now(), insight_type, description, confidence))
        
        conn.commit()
        conn.close()