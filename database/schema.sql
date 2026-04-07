-- Stock Master Table
CREATE TABLE IF NOT EXISTS stocks (
    stock_id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    pe_ratio DECIMAL(10, 2),
    pb_ratio DECIMAL(10, 2),
    dividend_yield DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_sector (sector)
);

-- Price History Table
CREATE TABLE IF NOT EXISTS price_history (
    price_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    price_date DATE NOT NULL,
    open_price DECIMAL(10, 2) NOT NULL,
    high_price DECIMAL(10, 2) NOT NULL,
    low_price DECIMAL(10, 2) NOT NULL,
    close_price DECIMAL(10, 2) NOT NULL,
    volume BIGINT,
    adjusted_close DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    UNIQUE KEY unique_stock_date (stock_id, price_date),
    INDEX idx_date (price_date),
    INDEX idx_stock_date (stock_id, price_date)
);

-- Intraday Data Table
CREATE TABLE IF NOT EXISTS intraday_data (
    intraday_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    volume BIGINT,
    bid DECIMAL(10, 2),
    ask DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    INDEX idx_stock_timestamp (stock_id, timestamp),
    INDEX idx_timestamp (timestamp)
);

-- Technical Indicators Table
CREATE TABLE IF NOT EXISTS technical_indicators (
    indicator_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    price_date DATE NOT NULL,
    sma_20 DECIMAL(10, 2),
    sma_50 DECIMAL(10, 2),
    sma_200 DECIMAL(10, 2),
    ema_12 DECIMAL(10, 2),
    ema_26 DECIMAL(10, 2),
    rsi_14 DECIMAL(10, 2),
    macd DECIMAL(10, 4),
    macd_signal DECIMAL(10, 4),
    macd_histogram DECIMAL(10, 4),
    bollinger_upper DECIMAL(10, 2),
    bollinger_middle DECIMAL(10, 2),
    bollinger_lower DECIMAL(10, 2),
    atr_14 DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    UNIQUE KEY unique_stock_date (stock_id, price_date),
    INDEX idx_stock_date (stock_id, price_date)
);

-- Fundamental Analysis Table
CREATE TABLE IF NOT EXISTS fundamentals (
    fundamental_id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    fiscal_quarter VARCHAR(10),
    fiscal_year INT,
    revenue BIGINT,
    profit BIGINT,
    eps DECIMAL(10, 2),
    roe DECIMAL(10, 2),
    roa DECIMAL(10, 2),
    debt_equity DECIMAL(10, 2),
    current_ratio DECIMAL(10, 2),
    quick_ratio DECIMAL(10, 2),
    operating_margin DECIMAL(10, 2),
    net_margin DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    UNIQUE KEY unique_stock_quarter (stock_id, fiscal_quarter, fiscal_year),
    INDEX idx_stock_year (stock_id, fiscal_year)
);

-- Portfolio Table
CREATE TABLE IF NOT EXISTS portfolio (
    portfolio_id INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_name VARCHAR(255) NOT NULL,
    total_value DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Portfolio Holdings Table
CREATE TABLE IF NOT EXISTS portfolio_holdings (
    holding_id INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_id INT NOT NULL,
    stock_id INT NOT NULL,
    quantity INT NOT NULL,
    purchase_price DECIMAL(10, 2) NOT NULL,
    purchase_date DATE NOT NULL,
    current_value DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolio(portfolio_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    INDEX idx_portfolio (portfolio_id),
    INDEX idx_stock (stock_id)
);

-- Trading Signals Table
CREATE TABLE IF NOT EXISTS trading_signals (
    signal_id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    signal_date DATE NOT NULL,
    signal_type VARCHAR(50),  -- 'BUY', 'SELL', 'HOLD'
    signal_strength INT,  -- 1-5 scale
    indicators_used VARCHAR(255),
    confidence_score DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    INDEX idx_stock_date (stock_id, signal_date)
);

-- Price Alerts Table
CREATE TABLE IF NOT EXISTS price_alerts (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    alert_type VARCHAR(50),  -- 'ABOVE', 'BELOW', 'CHANGE_PERCENT'
    alert_value DECIMAL(10, 2),
    is_triggered BOOLEAN DEFAULT FALSE,
    triggered_date DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    INDEX idx_stock_triggered (stock_id, is_triggered)
);

-- Data Update Log
CREATE TABLE IF NOT EXISTS update_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    update_type VARCHAR(50),
    stock_id INT,
    records_processed INT,
    status VARCHAR(20),  -- 'SUCCESS', 'FAILED', 'PARTIAL'
    error_message TEXT,
    started_at DATETIME,
    completed_at DATETIME,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE SET NULL,
    INDEX idx_status (status),
    INDEX idx_completed_at (completed_at)
);

-- Create indexes for better performance
CREATE INDEX idx_price_close ON price_history(close_price);
CREATE INDEX idx_volume ON price_history(volume);
CREATE INDEX idx_rsi ON technical_indicators(rsi_14);
CREATE INDEX idx_macd ON technical_indicators(macd);
