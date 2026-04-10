#!/usr/bin/env python3
"""IB Gateway Manager - Keeps Gateway running 24/7"""

import subprocess
import psutil
import time
import json
import logging
from datetime import datetime, time as dt_time
import asyncio
import win32com.client
import pyautogui
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GatewayManager:
    """Manages IB Gateway lifecycle - auto-start, login, restart"""
    
    def __init__(self, config_file='gateway_config.json'):
        self.config = self._load_config(config_file)
        self.gateway_path = self.config.get('gateway_path', r'C:\Jts\ibgateway.exe')
        self.restart_time = dt_time(23, 45)  # 11:45 PM ET
        self.check_interval = 60  # Check every minute
        self.login_timeout = 120  # 2 minutes for login
        self.running = False
        
    def _load_config(self, config_file):
        """Load configuration (credentials stored securely)"""
        default_config = {
            'username': '',
            'password': '',
            'trading_mode': 'paper',  # 'paper' or 'live'
            'gateway_path': r'C:\Jts\ibgateway.exe',
            'java_path': r'C:\Program Files\Java\jre1.8.0_202\bin\java.exe',
            'auto_restart_time': '23:45',
            'host': '192.168.0.58',
            'port': 4002
        }
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                default_config.update(config)
        except FileNotFoundError:
            # Create config file with defaults
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created {config_file} - Please add your IB credentials")
        
        return default_config
    
    def save_config(self):
        """Save configuration"""
        with open('gateway_config.json', 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def is_gateway_running(self):
        """Check if IB Gateway is running"""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'ibgateway' in proc.info['name'].lower() or 'java' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.cmdline())
                    if 'ibgateway' in cmdline.lower():
                        return True, proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False, None
    
    def is_gateway_connected(self):
        """Check if Gateway is actually connected and responsive"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.config['host'], self.config['port']))
            sock.close()
            return result == 0
        except:
            return False
    
    def kill_gateway(self):
        """Kill any existing Gateway processes"""
        killed = False
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'ibgateway' in proc.info['name'].lower() or 'java' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.cmdline())
                    if 'ibgateway' in cmdline.lower():
                        logger.info(f"Killing Gateway process {proc.info['pid']}")
                        proc.terminate()
                        proc.wait(timeout=10)
                        killed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if killed:
            time.sleep(5)  # Wait for processes to fully terminate
    
    def start_gateway(self):
        """Start IB Gateway"""
        logger.info("Starting IB Gateway...")
        
        # Kill any existing instances first
        self.kill_gateway()
        
        # Start Gateway
        try:
            subprocess.Popen([self.gateway_path])
            logger.info("Gateway process started")
            time.sleep(10)  # Wait for window to appear
            return True
        except Exception as e:
            logger.error(f"Failed to start Gateway: {e}")
            return False
    
    def auto_login(self):
        """Automate Gateway login using pyautogui"""
        logger.info("Attempting auto-login...")
        
        try:
            # Wait for login window
            time.sleep(5)
            
            # Find and click username field
            username_field = pyautogui.locateOnScreen('images/username_field.png', confidence=0.8)
            if username_field:
                pyautogui.click(username_field)
                pyautogui.hotkey('ctrl', 'a')  # Select all
                pyautogui.typewrite(self.config['username'])
                logger.info("Entered username")
            
            # Tab to password field
            pyautogui.press('tab')
            pyautogui.typewrite(self.config['password'])
            logger.info("Entered password")
            
            # Select trading mode
            if self.config['trading_mode'] == 'paper':
                # Click paper trading button
                paper_button = pyautogui.locateOnScreen('images/paper_trading.png', confidence=0.8)
                if paper_button:
                    pyautogui.click(paper_button)
            
            # Click login
            login_button = pyautogui.locateOnScreen('images/login_button.png', confidence=0.8)
            if login_button:
                pyautogui.click(login_button)
                logger.info("Clicked login button")
            else:
                # Fallback: press Enter
                pyautogui.press('enter')
            
            # Wait for login to complete
            time.sleep(30)
            
            # Check if connected
            if self.is_gateway_connected():
                logger.info("Gateway login successful!")
                return True
            else:
                logger.warning("Gateway started but not accepting connections")
                return False
                
        except Exception as e:
            logger.error(f"Auto-login failed: {e}")
            return False
    
    def simple_login_sequence(self):
        """Simplified login without image recognition"""
        logger.info("Using simplified login sequence...")
        
        try:
            # Wait for Gateway window
            time.sleep(10)
            
            # Type username (assuming focus is on username field)
            pyautogui.typewrite(self.config['username'], interval=0.1)
            
            # Tab to password
            pyautogui.press('tab')
            time.sleep(0.5)
            
            # Type password
            pyautogui.typewrite(self.config['password'], interval=0.1)
            
            # Tab to trading mode and select paper
            pyautogui.press('tab')
            pyautogui.press('tab')
            if self.config['trading_mode'] == 'paper':
                pyautogui.press('down')  # Select paper trading
            
            # Press Enter to login
            time.sleep(1)
            pyautogui.press('enter')
            
            logger.info("Login sequence completed, waiting for connection...")
            
            # Wait and check connection
            for i in range(60):  # Wait up to 60 seconds
                time.sleep(1)
                if self.is_gateway_connected():
                    logger.info("Gateway connected successfully!")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Simple login failed: {e}")
            return False
    
    def ensure_gateway_running(self):
        """Ensure Gateway is running and connected"""
        running, pid = self.is_gateway_running()
        
        if running and self.is_gateway_connected():
            logger.info(f"Gateway is running (PID: {pid}) and connected")
            return True
        
        if running and not self.is_gateway_connected():
            logger.warning("Gateway running but not connected, restarting...")
            self.kill_gateway()
        
        # Start Gateway
        if self.start_gateway():
            # Try auto-login
            if self.simple_login_sequence():
                return True
            else:
                logger.error("Auto-login failed - manual intervention may be required")
                return False
        
        return False
    
    def check_restart_time(self):
        """Check if it's time for daily restart"""
        now = datetime.now().time()
        
        # Check if we're within 1 minute of restart time
        if (self.restart_time.hour == now.hour and 
            abs(self.restart_time.minute - now.minute) <= 1):
            return True
        
        return False
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("Starting Gateway Manager...")
        self.running = True
        last_restart_date = None
        
        while self.running:
            try:
                # Check if daily restart is needed
                if self.check_restart_time() and datetime.now().date() != last_restart_date:
                    logger.info("Daily restart time reached")
                    self.kill_gateway()
                    await asyncio.sleep(30)  # Wait for IB servers
                    self.ensure_gateway_running()
                    last_restart_date = datetime.now().date()
                
                # Regular health check
                elif not self.is_gateway_connected():
                    logger.warning("Gateway not connected, attempting to fix...")
                    self.ensure_gateway_running()
                
                # Log status
                else:
                    logger.debug("Gateway healthy")
                
                await asyncio.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("Stopping Gateway Manager...")
                self.running = False
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
                await asyncio.sleep(10)
    
    def stop(self):
        """Stop the manager"""
        self.running = False

def setup_credentials():
    """Interactive setup for credentials"""
    print("\n=== IB Gateway Manager Setup ===")
    print("Please enter your IB credentials (stored locally):\n")
    
    username = input("IB Username: ")
    password = input("IB Password: ")
    mode = input("Trading mode (paper/live) [paper]: ").lower() or 'paper'
    
    config = {
        'username': username,
        'password': password,
        'trading_mode': mode,
        'gateway_path': r'C:\Jts\ibgateway.exe',
        'host': '192.168.0.58',
        'port': 4002
    }
    
    with open('gateway_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\nConfiguration saved to gateway_config.json")
    print("Gateway Manager is ready to maintain 24/7 operation!")

async def main():
    """Run the Gateway Manager"""
    # Check if config exists
    if not os.path.exists('gateway_config.json'):
        setup_credentials()
    
    manager = GatewayManager()
    
    # Check credentials
    if not manager.config.get('username') or not manager.config.get('password'):
        print("\nNo credentials found. Running setup...")
        setup_credentials()
        manager = GatewayManager()  # Reload config
    
    print("\n" + "="*50)
    print("   IB GATEWAY MANAGER - 24/7 OPERATION")
    print("="*50)
    print(f"Host: {manager.config['host']}")
    print(f"Port: {manager.config['port']}")
    print(f"Mode: {manager.config['trading_mode'].upper()}")
    print(f"Daily restart: {manager.config['auto_restart_time']}")
    print("="*50 + "\n")
    
    # Ensure Gateway is running before we start monitoring
    manager.ensure_gateway_running()
    
    # Start monitoring
    try:
        await manager.monitor_loop()
    except KeyboardInterrupt:
        print("\nGateway Manager stopped.")

if __name__ == "__main__":
    asyncio.run(main())