"""
Unit tests for the data generation module
"""

import sys
import os
import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator.data_gen import DataGenerator

class TestDataGeneration(unittest.TestCase):
    """Test cases for data generation"""
    
    def setUp(self):
        """Set up test data"""
        # Sample company data
        self.company_data = {
            'NABIL': {
                'company_name': 'Nabil Bank Limited',
                'sector': 'Commercial Bank',
                'price': {
                    'open': 1000,
                    'high': 1020,
                    'low': 990,
                    'close': 1010
                },
                'volume': 5000
            },
            'NLIC': {
                'company_name': 'Nepal Life Insurance Co. Ltd.',
                'sector': 'Insurance',
                'price': {
                    'open': 800,
                    'high': 820,
                    'low': 795,
                    'close': 815
                },
                'volume': 3000
            }
        }
        
        # Sample market parameters
        self.market_params = {
            'volatility': 0.02,
            'drift': 0.001,
            'volume_mean': 5000,
            'volume_std': 1000
        }
        
        # Sample sector trends
        self.sector_trends = {
            'Commercial Bank': {'trend': 0.002, 'volatility': 0.015},
            'Insurance': {'trend': -0.001, 'volatility': 0.02}
        }
          def test_data_generator_init(self):
        """Test DataGenerator initialization"""
        data_gen = DataGenerator(self.company_data)
        
        # Check that the DataGenerator is initialized with the company data
        self.assertEqual(data_gen.company_info, self.company_data)
        self.assertIsNone(data_gen.stock_data)
        
    def test_data_generator_historical(self):
        """Test historical data generation"""
        data_gen = DataGenerator(self.company_data)
        
        # Initialize market factors
        data_gen.initialize_market_factors(start_date="2023-01-01")
        
        # Generate 10 days of data
        data = data_gen.generate_historical_data(num_days=10, volatility=0.015)
        
        # Check that data is returned
        self.assertIsNotNone(data)
        self.assertIsInstance(data, pd.DataFrame)
        
        # Check columns
        required_columns = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            self.assertIn(col, data.columns)
            
        # Check number of rows (days × companies)
        expected_rows = 10 * len(self.company_data)
        self.assertEqual(len(data), expected_rows)
        
        # Check that all companies are included
        for symbol in self.company_data:
            self.assertIn(symbol, data['symbol'].unique())
        
        # Check DataFrame structure
        self.assertIsInstance(data, pd.DataFrame)
        
        # Check columns
        required_columns = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            self.assertIn(col, data.columns)
            
        # Check number of rows (days × companies)
        expected_rows = days * len(self.company_data)
        self.assertEqual(len(data), expected_rows)
        
        # Check that all companies are included
        for symbol in self.company_data:
            self.assertIn(symbol, data['symbol'].unique())
            
        # Check date range
        min_date = data['date'].min()
        max_date = data['date'].max()
        self.assertEqual(min_date, start_date)
        self.assertEqual(max_date, start_date + timedelta(days=days-1))
        
        # Check price ordering (high >= open, close and low <= open, close)
        self.assertTrue(all(data['high'] >= data['open']))
        self.assertTrue(all(data['high'] >= data['close']))
        self.assertTrue(all(data['low'] <= data['open']))
        self.assertTrue(all(data['low'] <= data['close']))

if __name__ == '__main__':
    unittest.main()
