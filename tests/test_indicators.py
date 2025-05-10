"""
Unit tests for the technical indicators module
"""

import sys
import os
import unittest
import numpy as np
import pandas as pd

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.indicators import (
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_volume_profile, detect_support_resistance,
    calculate_average_volume, is_volume_spike
)

class TestIndicators(unittest.TestCase):
    """Test cases for technical indicators calculations"""
    
    def setUp(self):
        # Create sample price data for testing
        self.prices = pd.Series([
            100, 102, 104, 103, 105, 107, 108, 107, 105, 104,
            105, 107, 108, 110, 111, 112, 111, 109, 110, 111,
            113, 114, 115, 116, 115, 114, 113, 115, 117, 118
        ])
        
    def test_rsi_calculation(self):
        """Test RSI calculation with known values"""
        rsi = calculate_rsi(self.prices, period=14)
        
        # RSI should be between 0 and 100
        self.assertTrue(all((0 <= x <= 100) for x in rsi.dropna()))
        
        # For our sample data with an upward trend, RSI should be above 50
        self.assertTrue(rsi.iloc[-1] > 50)
        
        # Check NaN values for the first period-1 entries
        self.assertEqual(rsi.isna().sum(), 14)
        
    def test_macd_calculation(self):
        """Test MACD calculation"""
        macd, signal, histogram = calculate_macd(
            self.prices, fast_period=12, slow_period=26, signal_period=9
        )
        
        # MACD should be the difference between fast and slow EMAs
        self.assertFalse(macd.isna().all())
        
        # Signal line should have more NaN values due to additional smoothing
        self.assertTrue(signal.isna().sum() > macd.isna().sum())
        
        # Histogram should be MACD minus signal
        np.testing.assert_almost_equal(
            histogram.dropna().values, 
            (macd - signal).dropna().values
        )
        
    def test_bollinger_bands(self):
        """Test Bollinger Bands calculation"""
        upper, middle, lower = calculate_bollinger_bands(
            self.prices, window=20, num_std_dev=2
        )
        
        # Middle band should be SMA
        sma = self.prices.rolling(window=20).mean()
        pd.testing.assert_series_equal(middle, sma)
        
        # Upper band should be higher than middle band
        self.assertTrue(all(upper.dropna() > middle.dropna()))
        
        # Lower band should be lower than middle band
        self.assertTrue(all(lower.dropna() < middle.dropna()))
        
        # Distance from middle to upper and lower should be the same
        np.testing.assert_almost_equal(
            (upper - middle).dropna().values,
            (middle - lower).dropna().values
        )
          def test_volume_profile(self):
        """Test Volume Profile calculation"""
        # Create sample volume data
        volumes = pd.Series([1000, 1200, 800, 1500, 2000, 1800, 1600, 1400, 1300, 1900] * 3)
        
        # Calculate volume profile
        profile = calculate_volume_profile(self.prices, volumes, bins=5)
        
        # Check that profile is returned
        self.assertIsNotNone(profile)
        
        # Check that profile has the right number of bins
        self.assertEqual(len(profile), 5)
        
    def test_support_resistance(self):
        """Test Support and Resistance detection"""
        supports, resistances = detect_support_resistance(self.prices, window=5, threshold=0.01)
        
        # Check that supports and resistances are returned
        self.assertIsNotNone(supports)
        self.assertIsNotNone(resistances)
        
        # Both should be lists
        self.assertIsInstance(supports, list)
        self.assertIsInstance(resistances, list)

if __name__ == '__main__':
    unittest.main()
