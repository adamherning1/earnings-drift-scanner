class TieredDataService:
    """Smart data fetching to minimize costs"""
    
    def get_stock_data(self, symbol: str, tier: str = "basic"):
        if tier == "basic":
            # FREE - Yahoo Finance
            return self.get_yahoo_data(symbol)
            
        elif tier == "earnings":
            # PAID - Databento only for earnings events
            if self.has_recent_earnings(symbol):
                return self.get_databento_earnings(symbol)
            else:
                return self.get_yahoo_data(symbol)
                
        elif tier == "premium":
            # PAID - Full analysis for paying customers only
            return self.get_databento_full(symbol)
    
    def has_recent_earnings(self, symbol: str) -> bool:
        """Check if stock had earnings in last 5 days"""
        # This saves TONS of money
        return symbol in self.recent_earnings_list