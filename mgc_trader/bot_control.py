#!/usr/bin/env python3
"""
MGC Bot Master Control - One script to rule them all
Combines monitoring, control, and reporting
"""

import subprocess
import os
import sys
from datetime import datetime
import time

class BotController:
    def __init__(self):
        self.bot_script = "adaptive_trading_bot.py"
        self.ollama_model = "llama3"
        
    def print_header(self, title):
        """Print formatted header"""
        print(f"\n{'=' * 60}")
        print(f"🤖 {title}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
        print('=' * 60)
    
    def check_bot_running(self):
        """Check if bot is running"""
        try:
            # Windows command to check if Python process is running our bot
            cmd = f'tasklist | findstr python | findstr {self.bot_script}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return len(result.stdout) > 0
        except:
            return False
    
    def start_bot(self):
        """Start the trading bot"""
        if self.check_bot_running():
            print("Bot is already running!")
            return False
        
        print("Starting trading bot...")
        # Start bot in new window
        subprocess.Popen(f'start cmd /k python {self.bot_script}', shell=True)
        time.sleep(3)
        
        if self.check_bot_running():
            print("✅ Bot started successfully!")
            return True
        else:
            print("❌ Failed to start bot")
            return False
    
    def stop_bot(self):
        """Stop the trading bot"""
        if not self.check_bot_running():
            print("Bot is not running")
            return True
            
        print("Stopping bot...")
        # Windows command to kill Python processes running our bot
        cmd = f'taskkill /F /FI "WINDOWTITLE eq *{self.bot_script}*"'
        subprocess.run(cmd, shell=True)
        
        time.sleep(2)
        if not self.check_bot_running():
            print("✅ Bot stopped successfully")
            return True
        else:
            print("❌ Failed to stop bot")
            return False
    
    def restart_bot(self):
        """Restart the trading bot"""
        print("Restarting bot...")
        self.stop_bot()
        time.sleep(2)
        self.start_bot()
    
    def run_monitor(self, monitor_type='status'):
        """Run monitoring check"""
        cmd = f'python monitor_suite.py {monitor_type}'
        subprocess.run(cmd, shell=True)
    
    def emergency_check(self):
        """Run emergency checks using local AI"""
        self.print_header("EMERGENCY CHECK")
        
        # Run alert check
        subprocess.run('python alert_check.py', shell=True)
        
        # Check if intervention needed
        print("\n" + "-" * 40)
        subprocess.run('python monitor_suite.py intervene', shell=True)
    
    def generate_report(self, report_type='eod'):
        """Generate trading report"""
        cmd = f'python scheduled_reports.py {report_type}'
        subprocess.run(cmd, shell=True)
    
    def dashboard(self):
        """Show full dashboard"""
        self.print_header("TRADING BOT DASHBOARD")
        
        # Bot status
        print("\n📊 BOT STATUS:")
        print("-" * 30)
        if self.check_bot_running():
            print("✅ Bot is RUNNING")
        else:
            print("❌ Bot is STOPPED")
        
        # Run full monitoring suite
        print("\n")
        self.run_monitor('all')
        
    def interactive_menu(self):
        """Interactive control menu"""
        while True:
            self.print_header("BOT CONTROL MENU")
            print("""
1. 📊 Dashboard (full status)
2. 🔍 Quick Status
3. ⚠️  Emergency Check
4. 📈 Generate Report
5. ▶️  Start Bot
6. ⏹️  Stop Bot
7. 🔄 Restart Bot
8. 🔁 Continuous Monitor
9. 📝 View Positions
0. 🚪 Exit

💰 All monitoring uses FREE local AI (Ollama)
            """)
            
            choice = input("\nSelect option (0-9): ").strip()
            
            if choice == '1':
                self.dashboard()
            elif choice == '2':
                subprocess.run('python quick_status.py', shell=True)
            elif choice == '3':
                self.emergency_check()
            elif choice == '4':
                report_type = input("Report type (morning/midday/eod/weekly): ").strip()
                if report_type in ['morning', 'midday', 'eod', 'weekly']:
                    self.generate_report(report_type)
            elif choice == '5':
                self.start_bot()
            elif choice == '6':
                self.stop_bot()
            elif choice == '7':
                self.restart_bot()
            elif choice == '8':
                print("\nStarting continuous monitor (Ctrl+C to stop)...")
                subprocess.run('python continuous_monitor.py', shell=True)
            elif choice == '9':
                self.run_monitor('position')
            elif choice == '0':
                print("\nExiting bot control...")
                break
            else:
                print("\nInvalid choice!")
            
            input("\nPress Enter to continue...")

def main():
    controller = BotController()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'start':
            controller.start_bot()
        elif command == 'stop':
            controller.stop_bot()
        elif command == 'restart':
            controller.restart_bot()
        elif command == 'status':
            controller.run_monitor('status')
        elif command == 'dashboard':
            controller.dashboard()
        elif command == 'emergency':
            controller.emergency_check()
        elif command == 'menu':
            controller.interactive_menu()
        else:
            print("Usage: python bot_control.py [start|stop|restart|status|dashboard|emergency|menu]")
    else:
        # Default to interactive menu
        controller.interactive_menu()

if __name__ == "__main__":
    main()