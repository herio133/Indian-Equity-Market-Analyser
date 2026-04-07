import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')  # 'sqlite' or 'mysql'
DATABASE_NAME = os.getenv('DATABASE_NAME', 'equity_market.db')
DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
DATABASE_USER = os.getenv('DATABASE_USER', 'root')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', '')
DATABASE_PORT = int(os.getenv('DATABASE_PORT', 3306))

# Data Collection Settings
NSE_API_BASE_URL = 'https://www.nseindia.com/api/'
BSE_API_BASE_URL = 'https://www.bseindia.com/api/'
YFINANCE_TIMEOUT = 30

# Stock Symbols
NIFTY_50_STOCKS = [
    'RELIANCE', 'TCS', 'INFY', 'HDFC', 'WIPRO', 'LT', 'AXISBANK',
    'MARUTI', 'BAJAJFINSV', 'HDFCBANK', 'ITC', 'SBIN', 'SUNPHARMA',
    'ASIANPAINT', 'ADANIGREEN', 'ADANIPORTS', 'POWERGRID', 'ULTRAMECH',
    'HINDALCO', 'JSWSTEEL', 'TATAMOTORS', 'BHARTIARTL', 'INDIGO', 'BPCL',
    'HCLTECH', 'DRREDDY', 'TECHM', 'DIVISLAB', 'BAJAJHLDNG', 'NTPC',
    'COAL', 'TATASTEEL', 'ONGC', 'GAIL', 'IOC', 'EICHERMOT', 'APOLLOHOSP',
    'CIPLA', 'BIOCON', 'LTIM', 'LUPIN', 'PIDILITIND', 'COLPAL'
]

# Technical Analysis Parameters
SMA_PERIODS = [20, 50, 200]
EMA_PERIODS = [12, 26]
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BOLLINGER_BANDS_PERIOD = 20
BOLLINGER_BANDS_STD = 2

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = 'logs/equity_analyser.log'

# Scheduler Settings
UPDATE_INTERVAL_MINUTES = 15
EOD_UPDATE_TIME = '18:00'  # IST
MARKET_OPEN_TIME = '09:15'  # IST
MARKET_CLOSE_TIME = '15:30'  # IST

# Power BI Settings
POWERBI_WORKSPACE_ID = os.getenv('POWERBI_WORKSPACE_ID', '')
POWERBI_DATASET_ID = os.getenv('POWERBI_DATASET_ID', '')
POWERBI_CLIENT_ID = os.getenv('POWERBI_CLIENT_ID', '')
POWERBI_CLIENT_SECRET = os.getenv('POWERBI_CLIENT_SECRET', '')
POWERBI_TENANT_ID = os.getenv('POWERBI_TENANT_ID', '')

# API Rate Limiting
MAX_REQUESTS_PER_MINUTE = 100
RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 5

# Data Retention (in days)
PRICE_DATA_RETENTION = 5 * 365  # 5 years
INTRADAY_DATA_RETENTION = 30  # 30 days

# Risk Management
DEFAULT_PORTFOLIO_SIZE = 10000000  # Default portfolio value in INR
MAX_SINGLE_POSITION = 0.15  # 15% max position size
MIN_DIVERSIFICATION = 5  # Minimum number of stocks
