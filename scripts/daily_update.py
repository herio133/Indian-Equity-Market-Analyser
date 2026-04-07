import schedule
import time
from datetime import datetime
import logging
from data_collection.nse_scraper import NSEScraper
from analysis.technical_indicators import TechnicalAnalysis
from database.db_manager import DatabaseManager
from config.settings import NIFTY_50_STOCKS, MARKET_OPEN_TIME, MARKET_CLOSE_TIME

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/daily_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DailyUpdateScheduler:
    """Scheduler for daily market data updates"""
    
    def __init__(self):
        self.scraper = NSEScraper()
        self.analysis = TechnicalAnalysis()
        self.db = DatabaseManager()
    
    def update_daily_data(self):
        """Update daily OHLCV data for all stocks"""
        try:
            logger.info("Starting daily data update...")
            
            # Fetch and save data
            self.scraper.fetch_daily_data(NIFTY_50_STOCKS)
            
            logger.info("Daily data update completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error in daily data update: {str(e)}")
            return False
    
    def calculate_daily_indicators(self):
        """Calculate technical indicators for all stocks"""
        try:
            logger.info("Calculating daily technical indicators...")
            
            query = 'SELECT stock_id FROM stocks WHERE symbol IN ({})'.format(
                ','.join(['%s'] * len(NIFTY_50_STOCKS))
            )
            stocks = self.db.execute_query(query, NIFTY_50_STOCKS)
            
            for stock in stocks:
                stock_id = stock[0]
                self.analysis.calculate_all_indicators(stock_id, save_to_db=True)
            
            logger.info("Daily indicator calculation completed")
            return True
        except Exception as e:
            logger.error(f"Error calculating indicators: {str(e)}")
            return False
    
    def generate_trading_signals(self):
        """Generate trading signals based on technical indicators"""
        try:
            logger.info("Generating trading signals...")
            
            query = '''
                SELECT ti.stock_id, s.symbol, ti.rsi_14, ti.macd, ti.macd_signal
                FROM technical_indicators ti
                JOIN stocks s ON ti.stock_id = s.stock_id
                WHERE ti.price_date = CURDATE()
                ORDER BY ti.stock_id
            '''
            
            signals = self.db.execute_query(query, ())
            
            for signal in signals:
                stock_id, symbol, rsi, macd, macd_signal = signal
                
                signal_type = self._determine_signal(rsi, macd, macd_signal)
                strength = self._calculate_signal_strength(rsi, macd, macd_signal)
                
                insert_query = '''
                    INSERT INTO trading_signals 
                    (stock_id, signal_date, signal_type, signal_strength)
                    VALUES (%s, CURDATE(), %s, %s)
                '''
                self.db.execute_insert(insert_query, (stock_id, signal_type, strength))
            
            logger.info(f"Generated {len(signals)} trading signals")
            return True
        except Exception as e:
            logger.error(f"Error generating signals: {str(e)}")
            return False
    
    def _determine_signal(self, rsi, macd, macd_signal):
        """Determine buy/sell/hold signal"""
        signals = []
        
        # RSI signals
        if rsi < 30:
            signals.append('BUY')
        elif rsi > 70:
            signals.append('SELL')
        
        # MACD signals
        if macd is not None and macd_signal is not None:
            if macd > macd_signal:
                signals.append('BUY')
            elif macd < macd_signal:
                signals.append('SELL')
        
        if not signals:
            return 'HOLD'
        
        buy_count = signals.count('BUY')
        sell_count = signals.count('SELL')
        
        if buy_count > sell_count:
            return 'BUY'
        elif sell_count > buy_count:
            return 'SELL'
        else:
            return 'HOLD'
    
    def _calculate_signal_strength(self, rsi, macd, macd_signal):
        """Calculate signal strength on scale of 1-5"""
        strength = 3  # Default HOLD
        
        if rsi is not None:
            if rsi < 20:
                strength += 1
            elif rsi < 30:
                strength += 1
            elif rsi > 80:
                strength -= 1
            elif rsi > 70:
                strength -= 1
        
        if macd is not None and macd_signal is not None:
            if macd > macd_signal:
                strength += 1
            else:
                strength -= 1
        
        return max(1, min(5, strength))
    
    def schedule_updates(self):
        """Schedule automatic updates"""
        # Daily EOD update at 4:00 PM IST
        schedule.every().day.at("16:00").do(self.update_daily_data)
        schedule.every().day.at("16:15").do(self.calculate_daily_indicators)
        schedule.every().day.at("16:30").do(self.generate_trading_signals)
        
        logger.info("Update schedule configured")
        
        # Keep scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)

def main():
    """Main entry point"""
    scheduler = DailyUpdateScheduler()
    
    # Run immediate update
    scheduler.update_daily_data()
    scheduler.calculate_daily_indicators()
    scheduler.generate_trading_signals()
    
    # Start scheduled updates
    scheduler.schedule_updates()

if __name__ == '__main__':
    main()
