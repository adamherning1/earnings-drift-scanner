#!/usr/bin/env python3
"""
Run MGC Trading Bot - Fixed for asyncio issues
"""

from ib_insync import *
import logging
from datetime import datetime, time
import time as time_module
from config import *

# Setup logging with encoding fix
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('mgc_bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point"""
    logger.info("Starting MGC Trading Bot...")
    
    # Create IB connection
    ib = IB()
    
    try:
        # Connect to IB Gateway
        logger.info(f"Connecting to IB Gateway at {IB_HOST}:{IB_PORT}...")
        ib.connect(IB_HOST, IB_PORT, clientId=IB_CLIENT_ID)
        logger.info("✅ Connected successfully!")
        
        # Setup contract
        contract = Future(SYMBOL, CONTRACT_MONTH, EXCHANGE)
        ib.qualifyContracts(contract)
        logger.info(f"Contract qualified: {contract.localSymbol}")
        
        # Request delayed market data (for paper account)
        ib.reqMarketDataType(3)  # 3 = Delayed
        ticker = ib.reqMktData(contract, genericTickList='', snapshot=False, regulatorySnapshot=False)
        ib.sleep(2)  # Let data flow in
        
        logger.info("Bot is monitoring MGC market...")
        logger.info("=" * 60)
        
        # Main monitoring loop
        while True:
            # Get current position
            positions = ib.positions()
            mgc_position = None
            for pos in positions:
                if pos.contract.localSymbol == contract.localSymbol:
                    mgc_position = pos
                    break
            
            # Display market info
            if ticker.marketPrice():
                logger.info(f"MGC Price: ${ticker.marketPrice():.2f} | "
                          f"Bid: ${ticker.bid:.2f} | Ask: ${ticker.ask:.2f} | "
                          f"Volume: {ticker.volume}")
                
                if mgc_position:
                    logger.info(f"Position: {mgc_position.position} contracts @ "
                              f"${mgc_position.avgCost:.2f} | "
                              f"P&L: ${float(mgc_position.unrealizedPnL):.2f}")
                else:
                    logger.info("Position: No active position")
            
            # Check if market is open
            now = datetime.now()
            if now.weekday() < 5 and time(6, 30) <= now.time() <= time(13, 0):  # PST times
                logger.info(f"Market OPEN - Ready to trade")
            else:
                logger.info(f"Market CLOSED - Monitoring only")
            
            logger.info("-" * 60)
            
            # Update dashboard status
            try:
                import json
                status = {
                    "connected": True,
                    "account": ib.managedAccounts()[0] if ib.managedAccounts() else "N/A",
                    "net_liquidation": "N/A",
                    "net_liquidation_value": 0,
                    "daily_pnl": 0,
                    "unrealized_pnl": float(mgc_position.unrealizedPnL) if mgc_position else 0,
                    "positions": 1 if mgc_position else 0,
                    "timestamp": datetime.now().isoformat(),
                    "message": "MGC Bot Running",
                    "mgc_price": ticker.marketPrice() if ticker.marketPrice() else 0
                }
                
                # Get account values
                for av in ib.accountValues():
                    if av.tag == 'NetLiquidation':
                        status["net_liquidation"] = f"${float(av.value):,.2f}"
                        status["net_liquidation_value"] = float(av.value)
                    elif av.tag == 'DailyPnL':
                        status["daily_pnl"] = float(av.value)
                
                with open('../trading_status.json', 'w') as f:
                    json.dump(status, f)
            except Exception as e:
                logger.error(f"Error updating status: {e}")
            
            # Sleep for 30 seconds
            ib.sleep(30)
            
    except KeyboardInterrupt:
        logger.info("\nShutdown signal received...")
    except Exception as e:
        logger.error(f"Bot error: {e}", exc_info=True)
    finally:
        # Clean disconnect
        logger.info("Disconnecting from IB Gateway...")
        if ib.isConnected():
            ib.disconnect()
        logger.info("Bot stopped.")

if __name__ == "__main__":
    main()