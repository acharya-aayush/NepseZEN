"""
NEPSEZEN - Nepal Stock Exchange Simulator
Technical Indicators Calculation Module

This module provides functions for calculating various technical indicators
used in stock market analysis, such as RSI, MACD, and Bollinger Bands.
"""

import numpy as np
import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def calculate_rsi(prices, periods=None):
    """
    Calculate the Relative Strength Index (RSI) for a given price series.
    
    Args:
        prices (list/Series): A list or pandas Series of price data
        periods (int, optional): The number of periods to use for RSI calculation, defaults to config.RSI_PERIOD
        
    Returns:
        pandas.Series: RSI values for the given price series
    """
    if periods is None:
        periods = config.RSI_PERIOD
        
    # Convert to pandas Series if input is a list
    if not isinstance(prices, pd.Series):
        prices = pd.Series(prices)
        
    # Calculate price changes
    delta = prices.diff()
    
    # Separate gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Calculate average gain and loss over the specified period
    avg_gain = gain.rolling(window=periods).mean()
    avg_loss = loss.rolling(window=periods).mean()
    
    # Calculate RS (Relative Strength)
    rs = avg_gain / avg_loss
    
    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_macd(prices, fast_period=12, slow_period=26, signal_period=9):
    """
    Calculate the Moving Average Convergence Divergence (MACD) for a given price series.
    
    Args:
        prices (list/Series): A list or pandas Series of price data
        fast_period (int, optional): The period for the fast EMA, defaults to 12
        slow_period (int, optional): The period for the slow EMA, defaults to 26
        signal_period (int, optional): The period for the signal line, defaults to 9
        
    Returns:
        tuple: (MACD line, Signal line, MACD histogram)
    """
    # Convert to pandas Series if input is a list
    if not isinstance(prices, pd.Series):
        prices = pd.Series(prices)
        
    # Calculate fast and slow EMAs
    ema_fast = prices.ewm(span=fast_period, adjust=False).mean()
    ema_slow = prices.ewm(span=slow_period, adjust=False).mean()
    
    # Calculate MACD line
    macd_line = ema_fast - ema_slow
    
    # Calculate Signal line
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    
    # Calculate MACD histogram
    macd_histogram = macd_line - signal_line
    
    return macd_line, signal_line, macd_histogram


def calculate_bollinger_bands(prices, window=20, num_std=2):
    """
    Calculate Bollinger Bands for a given price series.
    
    Args:
        prices (list/Series): A list or pandas Series of price data
        window (int, optional): The moving average window, defaults to 20
        num_std (int, optional): Number of standard deviations for the bands, defaults to 2
        
    Returns:
        tuple: (Upper band, Middle band, Lower band)
    """
    # Convert to pandas Series if input is a list
    if not isinstance(prices, pd.Series):
        prices = pd.Series(prices)
    
    # Calculate middle band (simple moving average)
    middle_band = prices.rolling(window=window).mean()
    
    # Calculate standard deviation
    std = prices.rolling(window=window).std()
    
    # Calculate upper and lower bands
    upper_band = middle_band + (std * num_std)
    lower_band = middle_band - (std * num_std)
    
    return upper_band, middle_band, lower_band


def calculate_volume_profile(prices, volumes, bins=10):
    """
    Calculate Volume Profile to analyze volume distribution across price levels.
    
    Args:
        prices (list/Series): A list or pandas Series of price data
        volumes (list/Series): A list or pandas Series of volume data
        bins (int, optional): The number of price levels to divide into, defaults to 10
        
    Returns:
        tuple: (Price levels, Volume at each level)
    """
    # Convert to pandas Series if input is a list
    if not isinstance(prices, pd.Series):
        prices = pd.Series(prices)
    if not isinstance(volumes, pd.Series):
        volumes = pd.Series(volumes)
    
    # Calculate price range
    min_price = prices.min()
    max_price = prices.max()
    
    # Create price levels
    price_levels = np.linspace(min_price, max_price, bins + 1)
    
    # Initialize volume at each price level
    volume_profile = np.zeros(bins)
    
    # Iterate through each price and volume
    for price, volume in zip(prices, volumes):
        # Find which bin this price belongs to
        bin_index = int((price - min_price) / (max_price - min_price) * bins)
        if bin_index == bins:  # Edge case for max price
            bin_index = bins - 1
        
        # Add volume to the appropriate bin
        volume_profile[bin_index] += volume
    
    return price_levels, volume_profile


def detect_support_resistance(prices, window=10, threshold=0.02):
    """
    Detect support and resistance levels in a price series.
    
    Args:
        prices (list/Series): A list or pandas Series of price data
        window (int, optional): The window size to use for peak detection, defaults to 10
        threshold (float, optional): The threshold percentage difference to consider a level, defaults to 0.02 (2%)
        
    Returns:
        tuple: (Support levels, Resistance levels)
    """
    # Convert to pandas Series if input is a list
    if not isinstance(prices, pd.Series):
        prices = pd.Series(prices)
    
    # Initialize lists for support and resistance levels
    support_levels = []
    resistance_levels = []
    
    # Function to check if a point is a local minimum or maximum
    def is_min_max(data, index, window, is_max=True):
        if index - window < 0 or index + window >= len(data):
            return False
        
        window_data = data[index-window:index+window+1]
        if is_max:
            return data[index] == max(window_data)
        else:
            return data[index] == min(window_data)
    
    # Iterate through prices to find local minima and maxima
    for i in range(window, len(prices) - window):
        if is_min_max(prices, i, window, is_max=False):
            support_levels.append((i, prices[i]))
        elif is_min_max(prices, i, window, is_max=True):
            resistance_levels.append((i, prices[i]))
    
    # Filter support and resistance levels based on threshold
    filtered_support = []
    filtered_resistance = []
    
    # Group similar support levels
    support_levels.sort(key=lambda x: x[1])
    for i, (idx, price) in enumerate(support_levels):
        if i == 0 or abs(price - support_levels[i-1][1]) / price > threshold:
            filtered_support.append((idx, price))
            
    # Group similar resistance levels
    resistance_levels.sort(key=lambda x: x[1])
    for i, (idx, price) in enumerate(resistance_levels):
        if i == 0 or abs(price - resistance_levels[i-1][1]) / price > threshold:
            filtered_resistance.append((idx, price))
    
    return filtered_support, filtered_resistance


def calculate_average_volume(volumes, periods=20):
    """
    Calculate average volume over a specified period.
    
    Args:
        volumes (list/Series): A list or pandas Series of volume data
        periods (int, optional): The number of periods to average over, defaults to 20
        
    Returns:
        pandas.Series: Average volume values
    """
    # Convert to pandas Series if input is a list
    if not isinstance(volumes, pd.Series):
        volumes = pd.Series(volumes)
        
    # Calculate moving average of volume
    avg_volume = volumes.rolling(window=periods).mean()
    
    return avg_volume


def is_volume_spike(volumes, threshold=2.0, periods=20):
    """
    Detect volume spikes based on a threshold multiple of average volume.
    
    Args:
        volumes (list/Series): A list or pandas Series of volume data
        threshold (float, optional): Multiple of average volume to consider a spike, defaults to 2.0
        periods (int, optional): The number of periods to average over, defaults to 20
        
    Returns:
        pandas.Series: Boolean series indicating volume spikes
    """
    # Convert to pandas Series if input is a list
    if not isinstance(volumes, pd.Series):
        volumes = pd.Series(volumes)
        
    # Calculate average volume
    avg_volume = calculate_average_volume(volumes, periods)
    
    # Identify volume spikes
    volume_spikes = volumes > (avg_volume * threshold)
    
    return volume_spikes


def detect_circuit_breaker_events(prices, threshold=None):
    """
    Detect circuit breaker events based on price changes exceeding thresholds.
    
    Args:
        prices (list/Series): A list or pandas Series of price data
        threshold (dict, optional): Dictionary with 'upper' and 'lower' thresholds, defaults to config values
        
    Returns:
        tuple: (Upper circuit events, Lower circuit events)
    """
    if threshold is None:
        threshold = config.CIRCUIT_BREAKER_THRESHOLD
        
    # Convert to pandas Series if input is a list
    if not isinstance(prices, pd.Series):
        prices = pd.Series(prices)
    
    # Calculate daily returns
    returns = prices.pct_change()
    
    # Detect upper and lower circuit breaker events
    upper_circuit = returns > threshold['upper']
    lower_circuit = returns < threshold['lower']
    
    return upper_circuit, lower_circuit
