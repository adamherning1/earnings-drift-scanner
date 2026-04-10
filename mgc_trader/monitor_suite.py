#!/usr/bin/env python3
"""
MGC Trading Bot Monitor Suite - Local AI Powered (FREE!)
Runs on Dell server using Ollama - No API costs
"""

import subprocess
import json
import os
from datetime import datetime, timedelta
import time
import sys

class TradingMonitor:
    def __init__(self):
        self.log_file = "adaptive_bot.log"
        self.ollama_model = "llama3"  # Change if using different model
        
    def query_ollama(self, prompt, model=None):
        """Query local Ollama instance"""
        if model is None:
            model = self.ollama_model
            
        try:
            # Use echo to pipe prompt to ollama
            cmd = f'echo "{prompt}" | ollama run {model}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            return f"Ollama Error: {e}"
    
    def get_recent_logs(self, lines=50):
        """Get recent log entries"""
        try:
            cmd = f"tail -{lines} {self.log_file}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout
        except:
            return "Could not read log file"
    
    def quick_status(self):
        """Quick bot status check"""
        logs = self.get_recent_logs(30)
        
        prompt = f"""Analyze this trading bot log. Answer concisely:
1. Is bot running? (YES/NO)
2. Current position? (e.g., "2 LONG" or "None")
3. Last trade time?
4. Any errors in last hour?

LOG: {logs}"""
        
        return self.query_ollama(prompt)
    
    def position_check(self):
        """Detailed position analysis"""
        logs = self.get_recent_logs(100)
        
        prompt = f"""From this trading bot log, extract:
1. Open positions (contracts and direction)
2. Entry price
3. Current P&L
4. Stop loss level if mentioned
5. How long position held

LOG: {logs}

Format: Brief bullet points"""
        
        return self.query_ollama(prompt)
    
    def error_scan(self):
        """Scan for errors and issues"""
        logs = self.get_recent_logs(200)
        
        prompt = f"""Scan this log for problems:
1. Connection errors
2. Failed orders
3. API errors
4. Timeout issues
5. Any WARNING or ERROR messages

LOG: {logs}

List only actual issues found. If none, say "No issues detected"."""
        
        return self.query_ollama(prompt)
    
    def performance_summary(self):
        """Daily performance summary"""
        # Get whole day's logs
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
                # Get today's logs
                today = datetime.now().strftime('%Y-%m-%d')
                today_logs = [l for l in lines if today in l][-500:]  # Last 500 lines from today
                logs = ''.join(today_logs)
        except:
            logs = self.get_recent_logs(200)
        
        prompt = f"""Analyze today's trading performance:
1. Total trades executed
2. Winners vs Losers
3. Total P&L for the day
4. Best and worst trades
5. Market bias (BULLISH/BEARISH/NEUTRAL)

LOG: {logs}

Format as brief summary."""
        
        return self.query_ollama(prompt)
    
    def should_intervene(self):
        """Check if manual intervention needed"""
        logs = self.get_recent_logs(100)
        
        prompt = f"""Check if urgent action needed:
1. Position without stop loss?
2. Connection lost for >10 minutes?
3. Large drawdown (>$1000)?
4. Repeated order failures?
5. Bot stuck or frozen?

LOG: {logs}

Answer: "INTERVENE: [reason]" or "ALL GOOD"."""
        
        return self.query_ollama(prompt)
    
    def market_conditions(self):
        """Analyze current market conditions"""
        logs = self.get_recent_logs(50)
        
        prompt = f"""From the trading bot log, determine:
1. Current market bias (1-5 score)
2. Trend direction
3. Volatility level
4. Good trading conditions? (YES/NO)

LOG: {logs}"""
        
        return self.query_ollama(prompt)

def main():
    monitor = TradingMonitor()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "status":
            print("🔍 Quick Status Check")
            print("=" * 50)
            print(monitor.quick_status())
            
        elif command == "position":
            print("📊 Position Analysis")
            print("=" * 50)
            print(monitor.position_check())
            
        elif command == "errors":
            print("⚠️  Error Scan")
            print("=" * 50)
            print(monitor.error_scan())
            
        elif command == "performance":
            print("📈 Daily Performance")
            print("=" * 50)
            print(monitor.performance_summary())
            
        elif command == "intervene":
            print("🚨 Intervention Check")
            print("=" * 50)
            print(monitor.should_intervene())
            
        elif command == "market":
            print("🌍 Market Conditions")
            print("=" * 50)
            print(monitor.market_conditions())
            
        elif command == "all":
            # Run all checks
            print("\n🤖 COMPLETE MGC BOT MONITORING REPORT")
            print("=" * 60)
            print(f"Time: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
            print("=" * 60)
            
            print("\n🔍 QUICK STATUS")
            print("-" * 30)
            print(monitor.quick_status())
            
            print("\n\n📊 POSITIONS")
            print("-" * 30)
            print(monitor.position_check())
            
            print("\n\n⚠️  ERRORS")
            print("-" * 30)
            print(monitor.error_scan())
            
            print("\n\n🚨 INTERVENTION")
            print("-" * 30)
            print(monitor.should_intervene())
            
            print("\n\n📈 PERFORMANCE")
            print("-" * 30)
            print(monitor.performance_summary())
            
            print("\n" + "=" * 60)
            print("💰 Cost: $0.00 (saved ~$10-20 vs API)")
            
        else:
            print("Usage: python monitor_suite.py [command]")
            print("Commands: status, position, errors, performance, intervene, market, all")
    else:
        # Default to quick status
        print("🔍 Quick Status Check")
        print("=" * 50)
        print(monitor.quick_status())
        print("\nFor full report: python monitor_suite.py all")

if __name__ == "__main__":
    main()