#!/usr/bin/env python3
"""
Simplified MGC Trading Bot - Skip learning on first run
"""

from ib_insync import *
import asyncio
import logging
from datetime import datetime, time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import *

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleMGCBot:
    def __init__(self):
        self.ib = IB()
        self.running = True
        self.contract = None
        self.position_size = POSITION_SIZE
        
    def connect(self):
        """Connect to IB Gateway"""
        try:
            logger.info(f"Connecting to IB Gateway at {IB_HOST}:{IB_PORT}")
            self.ib.connect(IB_HOST, IB_PORT, clientId=IB_CLIENT_ID)
            logger.info("Connected to IB Gateway successfully")
            
            # Create contract
            self.contract = Future(SYMBOL, CONTRACT_MONTH, EXCHANGE)
            self.ib.qualifyContracts(self.contract)
            logger.info(f"Contract qualified: {self.contract.localSymbol}")
            return True
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    async def check_market(self):
        """Simple market check"""
        # Get current price
        ticker = self.ib.reqMktData(self.contract)
        await asyncio.sleep(2)  # Wait for data
        
        if ticker.marketPrice():
            logger.info(f"Current MGC price: ${ticker.marketPrice()}")
            logger.info(f"Bid: ${ticker.bid} | Ask: ${ticker.ask}")
            logger.info(f"Volume: {ticker.volume}")
        else:
            logger.info("Waiting for market data...")
    
    async def run(self):
        """Main loop"""
        logger.info("Bot is running - monitoring MGC market...")
        
        while self.running:
            try:
                # Check if within trading hours (ET)
                now = datetime.now()
                current_time = now.time()
                
                # Convert to ET (simplified - you may need better timezone handling)
                if time(9, 30) <= current_time <= time(15, 45):
                    await self.check_market()
                else:
                    logger.info(f"Outside trading hours. Current time: {current_time}")
                
                # Wait before next check
                await asyncio.sleep(30)
                
            except KeyboardInterrupt:
                logger.info("Stopping bot...")
                self.running = False
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5)
    
    def stop(self):
        """Stop the bot"""
        logger.info("Disconnecting from IB...")
        if self.ib.isConnected():
            self.ib.disconnect()
        logger.info("Bot stopped")

async def main():
    bot = SimpleMGCBot()
    
    if not bot.connect():
        logger.error("Failed to connect!")
        return
    
    try:
        await bot.run()
    finally:
        bot.stop()

if __name__ == "__main__":
    asyncio.run(main())