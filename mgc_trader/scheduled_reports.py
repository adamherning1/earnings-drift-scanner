#!/usr/bin/env python3
"""
Scheduled Trading Reports - Run via cron
Generates AI-powered reports at specific times
"""

import subprocess
from datetime import datetime
import json
import os

class ReportGenerator:
    def __init__(self):
        self.ollama_model = "llama3"
        self.reports_dir = "trading_reports"
        
        # Create reports directory
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
    
    def query_ollama(self, prompt):
        """Query Ollama"""
        try:
            # Escape quotes in prompt
            prompt = prompt.replace('"', '\\"')
            cmd = f'echo "{prompt}" | ollama run {self.ollama_model}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "Query failed"
    
    def morning_report(self):
        """Generate morning pre-market report"""
        # Get end of yesterday's logs
        logs = subprocess.run("tail -200 adaptive_bot.log", shell=True, capture_output=True, text=True).stdout
        
        prompt = f"""Generate morning trading report:
1. Yesterday's final P&L
2. Overnight positions (if any)
3. Expected market bias today
4. System health check
5. Recommendations

LOG: {logs}"""
        
        report = self.query_ollama(prompt)
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f"{self.reports_dir}/morning_report_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(f"MORNING TRADING REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}\n")
            f.write("=" * 50 + "\n\n")
            f.write(report)
            
        return report
    
    def midday_report(self):
        """Generate midday performance report"""
        logs = subprocess.run("tail -500 adaptive_bot.log", shell=True, capture_output=True, text=True).stdout
        
        prompt = f"""Generate midday trading report:
1. Morning session P&L
2. Number of trades taken
3. Win/loss ratio so far
4. Current positions
5. Market conditions assessment

LOG: {logs}"""
        
        report = self.query_ollama(prompt)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f"{self.reports_dir}/midday_report_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(f"MIDDAY TRADING REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}\n")
            f.write("=" * 50 + "\n\n")
            f.write(report)
            
        return report
    
    def end_of_day_report(self):
        """Generate comprehensive EOD report"""
        # Get full day's logs
        logs = subprocess.run("grep $(date +%Y-%m-%d) adaptive_bot.log | tail -1000", 
                            shell=True, capture_output=True, text=True).stdout
        
        prompt = f"""Generate detailed END OF DAY trading report:

1. SUMMARY
   - Total P&L
   - Total trades
   - Win rate
   - Largest win/loss

2. TRADE ANALYSIS
   - Best performing strategy
   - Worst performing trades
   - Average hold time

3. TECHNICAL ISSUES
   - Any connection problems
   - Failed orders
   - System errors

4. MARKET ANALYSIS
   - Dominant market regime
   - Bias accuracy

5. RECOMMENDATIONS
   - What worked well
   - What needs improvement
   - Tomorrow's outlook

LOG: {logs}

Format as professional report."""
        
        report = self.query_ollama(prompt)
        
        timestamp = datetime.now().strftime('%Y%m%d')
        filename = f"{self.reports_dir}/eod_report_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(f"END OF DAY TRADING REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}\n")
            f.write("=" * 50 + "\n\n")
            f.write(report)
            
        return report
    
    def weekly_summary(self):
        """Generate weekly performance summary"""
        # This would need more sophisticated log parsing
        prompt = """Generate weekly trading summary based on daily reports:
1. Week's total P&L
2. Best and worst days
3. Total trades and win rate
4. Strategy performance comparison
5. Key learnings
6. Next week's plan"""
        
        report = self.query_ollama(prompt)
        
        timestamp = datetime.now().strftime('%Y%m%d')
        filename = f"{self.reports_dir}/weekly_report_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(f"WEEKLY TRADING SUMMARY\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}\n")
            f.write("=" * 50 + "\n\n")
            f.write(report)
            
        return report

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate Trading Reports')
    parser.add_argument('report_type', 
                      choices=['morning', 'midday', 'eod', 'weekly'],
                      help='Type of report to generate')
    
    args = parser.parse_args()
    
    generator = ReportGenerator()
    
    print(f"🤖 Generating {args.report_type} report using local AI...")
    
    if args.report_type == 'morning':
        report = generator.morning_report()
    elif args.report_type == 'midday':
        report = generator.midday_report()
    elif args.report_type == 'eod':
        report = generator.end_of_day_report()
    elif args.report_type == 'weekly':
        report = generator.weekly_summary()
    
    print("\n" + "=" * 50)
    print(report)
    print("=" * 50)
    print(f"\n✅ Report saved to trading_reports/")
    print(f"💰 Cost: $0 (saved ~$5-10)")

if __name__ == "__main__":
    main()