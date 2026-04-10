#!/usr/bin/env python3
"""
Simple startup script for MGC Trading Bot
Handles the async/sync connection issues
"""

import asyncio
import logging
import sys
from trading_bot import MGCTradingBot

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point"""
    logger.info("Starting MGC Trading Bot...")
    
    # Create the bot
    bot = MGCTradingBot()
    
    # Connect synchronously
    if not bot.connect():
        logger.error("Failed to connect to IB Gateway")
        sys.exit(1)
    
    # Run the async strategy loop
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(bot.run_strategy_loop())
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Bot error: {e}", exc_info=True)
    finally:
        bot.stop()
        logger.info("Bot stopped")

if __name__ == "__main__":
    main()