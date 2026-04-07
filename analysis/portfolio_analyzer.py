import pandas as pd
import numpy as np
from datetime import datetime
import logging
from database.db_manager import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortfolioAnalyzer:
    """Analyze portfolio performance and risk"""
    
    def __init__(self, db=None):
        self.db = db or DatabaseManager()
    
    def get_portfolio_holdings(self, portfolio_id):
        """Get current portfolio holdings"""
        query = '''
            SELECT 
                ph.holding_id,
                s.symbol,
                s.company_name,
                ph.quantity,
                ph.purchase_price,
                ph.purchase_date,
                ph.current_value
            FROM portfolio_holdings ph
            JOIN stocks s ON ph.stock_id = s.stock_id
            WHERE ph.portfolio_id = %s
        '''
        data = self.db.execute_query(query, (portfolio_id,))
        return pd.DataFrame(data, columns=[
            'holding_id', 'symbol', 'company_name', 'quantity',
            'purchase_price', 'purchase_date', 'current_value'
        ])
    
    def calculate_portfolio_value(self, portfolio_id):
        """Calculate total portfolio value"""
        df = self.get_portfolio_holdings(portfolio_id)
        if df.empty:
            return 0
        
        total_value = df['current_value'].sum()
        
        query = 'UPDATE portfolio SET total_value = %s, updated_at = NOW() WHERE portfolio_id = %s'
        self.db.execute_update(query, (total_value, portfolio_id))
        
        return total_value
    
    def calculate_portfolio_return(self, portfolio_id):
        """Calculate portfolio return percentage"""
        df = self.get_portfolio_holdings(portfolio_id)
        if df.empty:
            return 0, 0
        
        investment_value = (df['quantity'] * df['purchase_price']).sum()
        current_value = df['current_value'].sum()
        
        total_return = current_value - investment_value
        return_percentage = (total_return / investment_value * 100) if investment_value > 0 else 0
        
        return total_return, return_percentage
    
    def calculate_holding_performance(self, portfolio_id):
        """Calculate individual holding performance"""
        df = self.get_portfolio_holdings(portfolio_id)
        
        df['invested_value'] = df['quantity'] * df['purchase_price']
        df['gain_loss'] = df['current_value'] - df['invested_value']
        df['return_pct'] = (df['gain_loss'] / df['invested_value'] * 100).fillna(0)
        df['weight_pct'] = (df['current_value'] / df['current_value'].sum() * 100)
        
        return df[['symbol', 'quantity', 'purchase_price', 'current_value',
                   'gain_loss', 'return_pct', 'weight_pct']]
    
    def calculate_portfolio_beta(self, portfolio_id, benchmark_symbol='NIFTY50'):
        """Calculate portfolio beta relative to benchmark"""
        try:
            df = self.get_portfolio_holdings(portfolio_id)
            
            # Get benchmark returns
            benchmark_query = '''
                SELECT price_date, close_price FROM price_history
                WHERE stock_id = (SELECT stock_id FROM stocks WHERE symbol = %s)
                ORDER BY price_date DESC LIMIT 252
            '''
            benchmark_data = self.db.execute_query(benchmark_query, (benchmark_symbol,))
            benchmark_df = pd.DataFrame(benchmark_data, columns=['date', 'close'])
            benchmark_returns = benchmark_df['close'].pct_change()
            
            portfolio_returns = []
            for _, row in df.iterrows():
                stock_query = '''
                    SELECT price_date, close_price FROM price_history
                    WHERE stock_id = (SELECT stock_id FROM stocks WHERE symbol = %s)
                    ORDER BY price_date DESC LIMIT 252
                '''
                stock_data = self.db.execute_query(stock_query, (row['symbol'],))
                stock_df = pd.DataFrame(stock_data, columns=['date', 'close'])
                stock_returns = stock_df['close'].pct_change()
                portfolio_returns.append(stock_returns.values * row['weight_pct'] / 100)
            
            weighted_returns = np.array(portfolio_returns).sum(axis=0)
            
            covariance = np.cov(weighted_returns, benchmark_returns)[0][1]
            benchmark_variance = np.var(benchmark_returns)
            
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
            
            return beta
        except Exception as e:
            logger.error(f"Error calculating portfolio beta: {str(e)}")
            return 0
    
    def calculate_sharpe_ratio(self, portfolio_id, risk_free_rate=0.06):
        """Calculate Sharpe ratio"""
        try:
            df = self.get_portfolio_holdings(portfolio_id)
            
            # Calculate weighted returns
            portfolio_returns = []
            for _, row in df.iterrows():
                query = '''
                    SELECT close_price FROM price_history
                    WHERE stock_id = (SELECT stock_id FROM stocks WHERE symbol = %s)
                    ORDER BY price_date DESC LIMIT 252
                '''
                data = self.db.execute_query(query, (row['symbol'],))
                prices = [d[0] for d in data]
                returns = pd.Series(prices).pct_change().mean() * 252
                portfolio_returns.append(returns * row['weight_pct'] / 100)
            
            portfolio_return = sum(portfolio_returns)
            
            # Calculate volatility
            portfolio_std = 0.15  # Placeholder - calculate actual volatility
            
            sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_std
            
            return sharpe_ratio
        except Exception as e:
            logger.error(f"Error calculating Sharpe ratio: {str(e)}")
            return 0
    
    def get_diversification_metrics(self, portfolio_id):
        """Get portfolio diversification metrics"""
        df = self.calculate_holding_performance(portfolio_id)
        
        metrics = {
            'total_holdings': len(df),
            'top_3_weight': df.nlargest(3, 'weight_pct')['weight_pct'].sum(),
            'herfindahl_index': (df['weight_pct'] ** 2).sum(),
            'most_concentrated': df.loc[df['weight_pct'].idxmax()],
            'sector_concentration': df.groupby('symbol')['weight_pct'].sum()
        }
        
        return metrics
    
    def generate_portfolio_report(self, portfolio_id):
        """Generate comprehensive portfolio report"""
        try:
            portfolio_value = self.calculate_portfolio_value(portfolio_id)
            total_return, return_pct = self.calculate_portfolio_return(portfolio_id)
            holding_performance = self.calculate_holding_performance(portfolio_id)
            portfolio_beta = self.calculate_portfolio_beta(portfolio_id)
            sharpe_ratio = self.calculate_sharpe_ratio(portfolio_id)
            diversification = self.get_diversification_metrics(portfolio_id)
            
            report = {
                'timestamp': datetime.now(),
                'portfolio_value': portfolio_value,
                'total_return': total_return,
                'return_percentage': return_pct,
                'portfolio_beta': portfolio_beta,
                'sharpe_ratio': sharpe_ratio,
                'diversification': diversification,
                'holdings': holding_performance.to_dict()
            }
            
            logger.info(f"Generated portfolio report for portfolio_id: {portfolio_id}")
            return report
        except Exception as e:
            logger.error(f"Error generating portfolio report: {str(e)}")
            return {}
