import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
from bs4 import BeautifulSoup
from config.settings import NSE_API_BASE_URL, MAX_REQUESTS_PER_MINUTE
from database.db_manager import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NSEScraper:
    """Scrapes data from National Stock Exchange (NSE)"""
    
    def __init__(self):
        self.base_url = NSE_API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.db = DatabaseManager()
    
    def fetch_stock_list(self):
        """Fetch list of stocks from NSE"""
        try:
            url = f'{self.base_url}allStocks'
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Fetched {len(data['records']['data'])} stocks from NSE")
            return data['records']['data']
        except Exception as e:
            logger.error(f"Error fetching stock list: {str(e)}")
            return []
    
    def fetch_daily_data(self, symbols, date=None):
        """Fetch daily OHLCV data for given symbols"""
        if date is None:
            date = datetime.now().strftime('%d-%b-%Y')
        
        results = []
        for symbol in symbols:
            try:
                data = self._fetch_symbol_data(symbol, date)
                if data:
                    results.append(data)
                    self._save_to_database(symbol, data)
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {str(e)}")
        
        return results
    
    def _fetch_symbol_data(self, symbol, date):
        """Fetch individual symbol data"""
        try:
            url = f'{self.base_url}quote-equity?symbol={symbol}'
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'priceInfo' in data:
                price_info = data['priceInfo']
                return {
                    'symbol': symbol,
                    'date': date,
                    'open': price_info.get('open', 0),
                    'high': price_info.get('high', 0),
                    'low': price_info.get('low', 0),
                    'close': price_info.get('close', 0),
                    'volume': price_info.get('volume', 0),
                    'previous_close': price_info.get('previousClose', 0)
                }
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def _save_to_database(self, symbol, data):
        """Save fetched data to database"""
        try:
            # Insert or update stock
            stock_query = '''
                SELECT stock_id FROM stocks WHERE symbol = %s
            '''
            result = self.db.execute_query(stock_query, (symbol,))
            
            if not result:
                insert_stock = '''
                    INSERT INTO stocks (symbol, company_name) VALUES (%s, %s)
                '''
                stock_id = self.db.execute_insert(insert_stock, (symbol, symbol))
            else:
                stock_id = result[0][0]
            
            # Insert price data
            price_query = '''
                INSERT INTO price_history 
                (stock_id, price_date, open_price, high_price, low_price, close_price, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                open_price = VALUES(open_price),
                high_price = VALUES(high_price),
                low_price = VALUES(low_price),
                close_price = VALUES(close_price),
                volume = VALUES(volume)
            '''
            
            self.db.execute_insert(price_query, (
                stock_id, data['date'], data['open'], data['high'],
                data['low'], data['close'], data['volume']
            ))
            
            logger.info(f"Saved data for {symbol} on {data['date']}")
        except Exception as e:
            logger.error(f"Error saving data for {symbol}: {str(e)}")
    
    def fetch_historical_data(self, symbol, start_date, end_date):
        """Fetch historical data for a symbol"""
        try:
            url = f'{self.base_url}historical?symbol={symbol}&from={start_date}&to={end_date}'
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return None
    
    def fetch_corporate_actions(self, symbol):
        """Fetch corporate actions (dividends, splits, etc.)"""
        try:
            url = f'{self.base_url}corporateActions?symbol={symbol}'
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching corporate actions for {symbol}: {str(e)}")
            return None
