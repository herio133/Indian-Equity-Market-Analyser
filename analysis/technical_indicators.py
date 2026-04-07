import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from database.db_manager import DatabaseManager
from config.settings import (
    SMA_PERIODS, EMA_PERIODS, RSI_PERIOD, MACD_FAST, 
    MACD_SLOW, MACD_SIGNAL, BOLLINGER_BANDS_PERIOD
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TechnicalAnalysis:
    """Calculate technical analysis indicators"""
    
    def __init__(self, db=None):
        self.db = db or DatabaseManager()
    
    def get_price_data(self, stock_id, days=500):
        """Fetch price data from database"""
        query = '''
            SELECT price_date, close_price, volume
            FROM price_history
            WHERE stock_id = %s
            ORDER BY price_date ASC
            LIMIT %s
        '''
        data = self.db.execute_query(query, (stock_id, days))
        df = pd.DataFrame(data, columns=['date', 'close', 'volume'])
        df['date'] = pd.to_datetime(df['date'])
        return df.set_index('date')
    
    def calculate_sma(self, stock_id, period=20):
        """Calculate Simple Moving Average"""
        df = self.get_price_data(stock_id)
        df['sma'] = df['close'].rolling(window=period).mean()
        return df[['close', 'sma']]
    
    def calculate_ema(self, stock_id, period=12):
        """Calculate Exponential Moving Average"""
        df = self.get_price_data(stock_id)
        df['ema'] = df['close'].ewm(span=period, adjust=False).mean()
        return df[['close', 'ema']]
    
    def calculate_rsi(self, stock_id, period=14):
        """Calculate Relative Strength Index"""
        df = self.get_price_data(stock_id)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        df['rsi'] = rsi
        
        return df[['close', 'rsi']]
    
    def calculate_macd(self, stock_id):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        df = self.get_price_data(stock_id)
        
        ema_12 = df['close'].ewm(span=MACD_FAST, adjust=False).mean()
        ema_26 = df['close'].ewm(span=MACD_SLOW, adjust=False).mean()
        
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=MACD_SIGNAL, adjust=False).mean()
        histogram = macd_line - signal_line
        
        df['macd'] = macd_line
        df['signal'] = signal_line
        df['histogram'] = histogram
        
        return df[['close', 'macd', 'signal', 'histogram']]
    
    def calculate_bollinger_bands(self, stock_id, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        df = self.get_price_data(stock_id)
        
        sma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        
        df['upper_band'] = upper_band
        df['middle_band'] = sma
        df['lower_band'] = lower_band
        
        return df[['close', 'upper_band', 'middle_band', 'lower_band']]
    
    def calculate_atr(self, stock_id, period=14):
        """Calculate Average True Range"""
        query = '''
            SELECT price_date, high_price, low_price, close_price
            FROM price_history
            WHERE stock_id = %s
            ORDER BY price_date ASC
            LIMIT 500
        '''
        data = self.db.execute_query(query, (stock_id,))
        df = pd.DataFrame(data, columns=['date', 'high', 'low', 'close'])
        
        df['tr'] = np.maximum(
            df['high'] - df['low'],
            np.maximum(
                abs(df['high'] - df['close'].shift(1)),
                abs(df['low'] - df['close'].shift(1))
            )
        )
        
        df['atr'] = df['tr'].rolling(window=period).mean()
        return df[['close', 'atr']]
    
    def calculate_all_indicators(self, stock_id, save_to_db=True):
        """Calculate all technical indicators"""
        try:
            indicators = {}
            
            # SMA calculations
            for period in SMA_PERIODS:
                indicators[f'sma_{period}'] = self.calculate_sma(stock_id, period)
            
            # EMA calculations
            for period in EMA_PERIODS:
                indicators[f'ema_{period}'] = self.calculate_ema(stock_id, period)
            
            # RSI
            indicators['rsi'] = self.calculate_rsi(stock_id, RSI_PERIOD)
            
            # MACD
            indicators['macd'] = self.calculate_macd(stock_id)
            
            # Bollinger Bands
            indicators['bb'] = self.calculate_bollinger_bands(stock_id, BOLLINGER_BANDS_PERIOD)
            
            # ATR
            indicators['atr'] = self.calculate_atr(stock_id, 14)
            
            if save_to_db:
                self._save_indicators_to_db(stock_id, indicators)
            
            logger.info(f"Calculated all indicators for stock_id: {stock_id}")
            return indicators
        except Exception as e:
            logger.error(f"Error calculating indicators: {str(e)}")
            return {}
    
    def _save_indicators_to_db(self, stock_id, indicators):
        """Save calculated indicators to database"""
        try:
            # Combine all indicators into one DataFrame
            df = indicators['rsi'][['rsi']].copy()
            df['sma_20'] = indicators['sma_20']['sma']
            df['sma_50'] = indicators['sma_50']['sma']
            df['sma_200'] = indicators['sma_200']['sma']
            df['ema_12'] = indicators['ema_12']['ema']
            df['ema_26'] = indicators['ema_26']['ema']
            df['macd'] = indicators['macd']['macd']
            df['macd_signal'] = indicators['macd']['signal']
            df['bb_upper'] = indicators['bb']['upper_band']
            df['bb_middle'] = indicators['bb']['middle_band']
            df['bb_lower'] = indicators['bb']['lower_band']
            df['atr'] = indicators['atr']['atr']
            
            df = df.dropna()
            
            query = '''
                INSERT INTO technical_indicators 
                (stock_id, price_date, sma_20, sma_50, sma_200, ema_12, ema_26,
                 rsi_14, macd, macd_signal, bollinger_upper, bollinger_middle, 
                 bollinger_lower, atr_14)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                sma_20 = VALUES(sma_20), sma_50 = VALUES(sma_50), sma_200 = VALUES(sma_200)
            '''
            
            for date, row in df.iterrows():
                self.db.execute_insert(query, (
                    stock_id, date.date(), row['sma_20'], row['sma_50'], row['sma_200'],
                    row['ema_12'], row['ema_26'], row['rsi'], row['macd'], 
                    row['macd_signal'], row['bb_upper'], row['bb_middle'], 
                    row['bb_lower'], row['atr']
                ))
            
            logger.info(f"Saved indicators for stock_id: {stock_id}")
        except Exception as e:
            logger.error(f"Error saving indicators: {str(e)}")
