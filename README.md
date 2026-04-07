# Indian Equity Market Analyser

An end-to-end financial data analysis platform for Indian equity markets using Python, SQLite/MySQL, and Power BI dashboards.

## Features
- Real-time stock data collection from multiple sources
- Financial metrics calculation and analysis
- Time-series data management with SQLite/MySQL
- Power BI integration for interactive dashboards
- Portfolio analysis and risk assessment
- Technical and fundamental analysis indicators

## Project Structure
```
indian-equity-market-analyser/
├── data_collection/
│   ├── __init__.py
│   ├── nse_scraper.py
│   ├── bse_scraper.py
│   └── api_connector.py
├── database/
│   ├── __init__.py
│   ├── db_manager.py
│   ├── schema.sql
│   └── migrations/
├── analysis/
│   ├── __init__.py
│   ├── technical_indicators.py
│   ├── fundamental_analysis.py
│   └── portfolio_analyzer.py
├── powerbi/
│   ├── powerbi_connector.py
│   ├── data_export.py
│   └── dashboards/
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── credentials.example.json
├── scripts/
│   ├── daily_update.py
│   ├── backfill_data.py
│   └── generate_reports.py
├── tests/
│   ├── __init__.py
│   ├── test_data_collection.py
│   ├── test_analysis.py
│   └── test_database.py
├── requirements.txt
├── setup.py
└── .gitignore

## Installation

### Prerequisites
- Python 3.8+
- MySQL 5.7+ or SQLite3
- Power BI Desktop (for dashboard creation)

### Setup Steps

1. Clone the repository
```bash
git clone https://github.com/herio133/indian-equity-market-analyser.git
cd indian-equity-market-analyser
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure database
```bash
cp config/credentials.example.json config/credentials.json
# Edit credentials.json with your database details
```

5. Initialize database
```bash
python -c "from database.db_manager import DatabaseManager; DatabaseManager.init_db()"
```

## Usage

### Collect Data
```python
from data_collection.nse_scraper import NSEScraper
scraper = NSEScraper()
scraper.fetch_daily_data(['RELIANCE', 'TCS', 'INFY'])
```

### Perform Analysis
```python
from analysis.technical_indicators import TechnicalAnalysis
from database.db_manager import DatabaseManager

db = DatabaseManager()
analysis = TechnicalAnalysis(db)
signals = analysis.calculate_sma('RELIANCE', period=20)
```

### Export to Power BI
```bash
python powerbi/data_export.py --output powerbi_data.csv
```

## Database Schema

Key tables:
- `stocks`: Stock master data (symbol, name, sector, etc.)
- `price_history`: Daily OHLCV data
- `fundamentals`: Quarterly financial metrics
- `technical_indicators`: Calculated indicators
- `portfolio`: Portfolio holdings and performance

## API Sources
- NSE (National Stock Exchange)
- BSE (Bombay Stock Exchange)
- yfinance for supplementary data
- Economic calendars

## Power BI Dashboards

Included dashboards:
- Market Overview
- Stock Performance Tracker
- Portfolio Analysis
- Risk Assessment
- Technical Analysis Charts
- Fundamental Comparison

## Data Update Schedule
- Intraday: Every 15 minutes (market hours)
- EOD: 6:00 PM IST
- Weekly: Sunday 8:00 PM IST
- Monthly: First day of month

## Contributing
Pull requests are welcome. For major changes, please open an issue first.

## License
NO License

## Support
For issues and questions, please open a GitHub issue.

---

**Last Updated**: 2026-04-07
