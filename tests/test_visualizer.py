"""
Unit tests for the visualization module
"""

import sys
import os
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.visualizer import (
    plot_interactive_candlestick, plot_sector_performance,
    plot_volume_heatmap, plot_portfolio_performance, plot_circuit_breakers
)

class TestVisualizer(unittest.TestCase):
    """Test cases for the visualization module"""
    
    def setUp(self):
        """Set up test data"""
        # Create sample date range
        dates = pd.date_range(start='2023-01-01', periods=30)
        
        # Create sample price data
        price_data = []
        for i, date in enumerate(dates):
            # Generate some price patterns
            base_price = 100 + i * 0.5  # Slight upward trend
            price_data.append({
                'date': date,
                'symbol': 'NABIL',
                'open': base_price * (1 + np.random.uniform(-0.01, 0.01)),
                'high': base_price * (1 + np.random.uniform(0.01, 0.03)),
                'low': base_price * (1 - np.random.uniform(0.01, 0.03)),
                'close': base_price * (1 + np.random.uniform(-0.01, 0.01)),
                'volume': np.random.randint(1000, 10000)
            })
        
        self.price_data = pd.DataFrame(price_data)
        
        # Create sample sector data
        sectors = ['Commercial Bank', 'Insurance', 'Hydropower', 'Microfinance', 'Development Bank']
        sector_data = []
        
        for sector in sectors:
            sector_data.append({
                'sector': sector,
                'return': np.random.uniform(-0.05, 0.05),
                'volume': np.random.randint(10000, 100000),
                'market_cap': np.random.randint(1000000, 10000000)
            })
            
        self.sector_data = pd.DataFrame(sector_data)
        
        # Create sample portfolio data
        dates = pd.date_range(start='2023-01-01', periods=30)
        portfolio_data = []
        
        value = 100000  # Starting value
        for date in dates:
            # Random daily change
            daily_return = np.random.uniform(-0.02, 0.025)
            value = value * (1 + daily_return)
            
            portfolio_data.append({
                'date': date,
                'value': value,
                'daily_return': daily_return,
                'cash': value * np.random.uniform(0.1, 0.3),
                'invested': value * np.random.uniform(0.7, 0.9)
            })
            
        self.portfolio_data = pd.DataFrame(portfolio_data)
        
        # Create sample circuit breaker data
        circuit_data = []
        for i in range(5):
            date = datetime(2023, 1, 1) + timedelta(days=i*5)
            circuit_data.append({
                'date': date,
                'symbol': f'STOCK{i+1}',
                'type': np.random.choice(['upper', 'lower']),
                'price': np.random.uniform(100, 500),
                'change_percent': np.random.uniform(0.08, 0.15)
            })
            
        self.circuit_data = pd.DataFrame(circuit_data)
        
    def test_plot_interactive_candlestick(self):
        """Test candlestick chart generation"""
        fig = plot_interactive_candlestick(self.price_data, 'NABIL')
        
        # Check that a figure is returned
        self.assertIsNotNone(fig)
        
        # Check figure type
        import plotly.graph_objects as go
        self.assertIsInstance(fig, go.Figure)
          def test_plot_sector_performance(self):
        """Test sector performance chart generation"""
        # The function expects a DataFrame with 'return' column
        self.sector_data.rename(columns={'return': 'Return'}, inplace=True)
        
        fig = plot_sector_performance(self.sector_data)
        
        # Check that a figure is returned
        self.assertIsNotNone(fig)
        
        # Check figure type
        import plotly.graph_objects as go
        self.assertIsInstance(fig, go.Figure)
        
    def test_plot_volume_heatmap(self):
        """Test volume heatmap generation"""
        # First create multi-symbol data
        symbols = ['NABIL', 'NLIC', 'SBL', 'NBL', 'NRIC']
        multi_data = []
        
        for symbol in symbols:
            for date in pd.date_range(start='2023-01-01', periods=10):
                multi_data.append({
                    'date': date,
                    'symbol': symbol,
                    'volume': np.random.randint(1000, 10000)
                })
                
        multi_df = pd.DataFrame(multi_data)
        
        # Test the function
        fig = plot_volume_heatmap(multi_df, companies=symbols)
        
        # Check that a figure is returned
        self.assertIsNotNone(fig)
        
        # Check figure type
        import plotly.graph_objects as go
        self.assertIsInstance(fig, go.Figure)
        
    def test_plot_portfolio_performance(self):
        """Test portfolio performance chart generation"""
        fig = plot_portfolio_performance(self.portfolio_data)
        
        # Check that a figure is returned
        self.assertIsNotNone(fig)
        
        # Check figure type
        import plotly.graph_objects as go
        self.assertIsInstance(fig, go.Figure)
        
    def test_plot_circuit_breakers(self):
        """Test circuit breaker visualization"""
        fig = plot_circuit_breakers(self.circuit_data)
        
        # Check that a figure is returned
        self.assertIsNotNone(fig)
        
        # Check figure type
        import plotly.graph_objects as go
        self.assertIsInstance(fig, go.Figure)

if __name__ == '__main__':
    unittest.main()
