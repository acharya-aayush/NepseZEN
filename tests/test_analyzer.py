"""
Unit tests for the market analyzer module
"""

import sys
import os
import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics.analyzer import MarketAnalyzer

class TestMarketAnalyzer(unittest.TestCase):
    """Test cases for the market analyzer"""
    
    def setUp(self):
        """Set up test data"""
        # Create sample market data
        dates = pd.date_range(start='2023-01-01', periods=30)
        symbols = ['NABIL', 'NLIC', 'NRIC', 'EBL', 'ADBL']
        
        # Create a DataFrame with price and volume data
        data = []
        
        for symbol in symbols:
            for date in dates:
                # Generate some random price data
                open_price = np.random.uniform(100, 500)
                close_price = open_price * (1 + np.random.uniform(-0.05, 0.05))
                high_price = max(open_price, close_price) * (1 + np.random.uniform(0, 0.03))
                low_price = min(open_price, close_price) * (1 - np.random.uniform(0, 0.03))
                volume = np.random.randint(1000, 10000)
                
                data.append({
                    'date': date,
                    'symbol': symbol,
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': close_price,
                    'volume': volume
                })
        
        self.market_data = pd.DataFrame(data)
        
        # Create company data
        self.company_data = {
            'NABIL': {'company_name': 'Nabil Bank Limited', 'sector': 'Commercial Bank'},
            'NLIC': {'company_name': 'Nepal Life Insurance Co. Ltd.', 'sector': 'Insurance'},
            'NRIC': {'company_name': 'Nepal Reinsurance Company Ltd.', 'sector': 'Insurance'},
            'EBL': {'company_name': 'Everest Bank Limited', 'sector': 'Commercial Bank'},
            'ADBL': {'company_name': 'Agricultural Development Bank Ltd', 'sector': 'Development Bank'}
        }
          # Set up the market data index properly
        self.market_data.set_index(['date', 'symbol'], inplace=True)
        
        # Create the analyzer
        self.analyzer = MarketAnalyzer(self.market_data, self.company_data)
        
    def test_get_market_summary(self):
        """Test market summary calculation"""
        summary = self.analyzer.get_market_summary(date=datetime.now().date())
        
        # Check that summary contains required fields
        self.assertIn('total_volume', summary)
        self.assertIn('advances', summary)
        self.assertIn('declines', summary)
        self.assertIn('unchanged', summary)
        self.assertIn('market_index', summary)
        
    def test_get_sector_performance(self):
        """Test sector performance calculation"""
        sector_perf = self.analyzer.get_sector_performance()
        
        # Check that all sectors are included
        sectors = set(info['sector'] for info in self.company_data.values())
        for sector in sectors:
            self.assertIn(sector, sector_perf.index)
            
        # Check that performance contains required columns
        self.assertIn('return', sector_perf.columns)
        self.assertIn('volume', sector_perf.columns)
        
    def test_get_top_gainers_losers(self):
        """Test top gainers and losers calculation"""
        gainers = self.analyzer.get_top_gainers(limit=3)
        losers = self.analyzer.get_top_losers(limit=3)
        
        # Check result sizes
        self.assertTrue(len(gainers) <= 3)
        self.assertTrue(len(losers) <= 3)
        
        # Check that gainers have positive returns
        if not gainers.empty:
            self.assertTrue(all(gainers['return'] >= 0))
            
        # Check that losers have negative returns
        if not losers.empty:
            self.assertTrue(all(losers['return'] <= 0))
        
    def test_get_volume_leaders(self):
        """Test volume leaders calculation"""
        leaders = self.analyzer.get_volume_leaders(limit=3)
        
        # Check result size
        self.assertTrue(len(leaders) <= 3)
        
        # Check that volume is sorted in descending order
        if not leaders.empty:
            volumes = leaders['volume'].values
            self.assertTrue(all(volumes[i] >= volumes[i+1] for i in range(len(volumes)-1)))
        
    def test_get_price_range(self):
        """Test price range calculation"""
        price_range = self.analyzer.get_price_range('NABIL')
        
        # Check that price range contains required fields
        self.assertIn('52w_high', price_range)
        self.assertIn('52w_low', price_range)
        self.assertIn('current', price_range)
        
        # Current price should be within 52-week range
        self.assertTrue(price_range['52w_low'] <= price_range['current'] <= price_range['52w_high'])
        
    def test_calculate_correlation_matrix(self):
        """Test correlation matrix calculation"""
        corr_matrix = self.analyzer.calculate_correlation_matrix(['NABIL', 'EBL'])
        
        # Check matrix dimensions
        self.assertEqual(corr_matrix.shape, (2, 2))
        
        # Diagonal should be 1
        np.testing.assert_almost_equal(np.diag(corr_matrix), np.ones(2))
        
        # Matrix should be symmetric
        np.testing.assert_almost_equal(corr_matrix, corr_matrix.T)

if __name__ == '__main__':
    unittest.main()
