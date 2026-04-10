#!/usr/bin/env python3
"""
Continuous Trading Monitor - Runs every X minutes
Uses local AI to detect issues and alert
"""

import subprocess
import time
from datetime import datetime
import os

class ContinuousMonitor:
    def __init__(self, check_interval=300):  # 5 minutes default
        self.check_interval = check_interval
        self.ollama_model = "llama3"
        self.alert_file = "monitor_alerts.log"
        
    def query_ollama(self, prompt):
        """Query local Ollama"""
        try:
            cmd = f'echo "{prompt}" | ollama run {self.ollama_model}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "Ollama query failed"
    
    def get_recent_logs(self, minutes=10):
        """Get logs from last X minutes"""
        try:
            # Simple tail approach
            lines = 100  # Approximate lines per 10 minutes
            cmd = f"tail -{lines} adaptive_bot.log"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout
        except:
            return ""
    
    def check_critical_issues(self):
        """Check for critical issues that need alerts"""
        logs = self.get_recent_logs()
        
        prompt = f"""Check for CRITICAL issues only:
1. Position without stop loss
2. Connection lost >5 minutes  
3. Large loss >$500
4. Order stuck/failed
5. Bot not responding

LOG: {logs}

If critical issue found, respond: "ALERT: [specific issue]"
If all normal, respond: "OK"."""
        
        return self.query_ollama(prompt)
    
    def check_position_health(self):
        """Monitor open position health"""
        logs = self.get_recent_logs()
        
        prompt = f"""Check position health:
1. Current P&L
2. Distance from stop
3. Time in position
4. Unusual price movement

LOG: {logs}

Report issues only, else "Position healthy"."""
        
        return self.query_ollama(prompt)
    
    def send_alert(self, message):
        """Log alert (could extend to send email/SMS)"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        alert_msg = f"[{timestamp}] {message}"
        
        # Log to file
        with open(self.alert_file, 'a') as f:
            f.write(alert_msg + '\n')
        
        # Also print to console
        print(f"\n🚨 ALERT: {message}")
        
        # Could add email/SMS here later
        
    def run_continuous(self):
        """Run continuous monitoring"""
        print(f"🤖 Starting Continuous Monitor (checking every {self.check_interval/60} minutes)")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        
        check_count = 0
        
        try:
            while True:
                check_count += 1
                timestamp = datetime.now().strftime('%I:%M %p')
                
                print(f"\n[{timestamp}] Check #{check_count}")
                print("-" * 30)
                
                # Check critical issues
                critical_check = self.check_critical_issues()
                print(f"Critical Issues: {critical_check}")
                
                if "ALERT:" in critical_check:
                    self.send_alert(critical_check)
                
                # Check position health
                position_check = self.check_position_health()
                print(f"Position Health: {position_check}")
                
                if "issue" in position_check.lower() or "problem" in position_check.lower():
                    self.send_alert(f"Position Issue: {position_check}")
                
                # Sleep until next check
                print(f"\nNext check in {self.check_interval/60} minutes...")
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped by user")
            print(f"Total checks performed: {check_count}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Continuous Trading Monitor')
    parser.add_argument('--interval', type=int, default=300,
                      help='Check interval in seconds (default: 300)')
    
    args = parser.parse_args()
    
    monitor = ContinuousMonitor(check_interval=args.interval)
    monitor.run_continuous()

if __name__ == "__main__":
    main()