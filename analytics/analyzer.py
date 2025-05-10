"""
NEPSEZEN - Nepal Stock Exchange Simulator
Core Analysis Module

This module provides functions and classes for analyzing stock market data,
including RSI calculation, circuit breaker detection, volume analysis, and sector analysis.
"""

import pandas as pd
import numpy as np
import sys
import os
import logging
from datetime import datetime, timedelta
from collections import defaultdict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from utils.indicators import (
    calculate_rsi, detect_circuit_breaker_events, is_volume_spike,
    calculate_macd, calculate_bollinger_bands
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MarketAnalyzer:
    """
    Class for analyzing market data, detecting patterns, and calculating indicators.
    """
    
    def __init__(self, stock_data=None, company_info=None):
        """
        Initialize the MarketAnalyzer with stock data and company information.
        
        Args:
            stock_data (pd.DataFrame): DataFrame with hierarchical index (date, symbol) and OHLCV columns
            company_info (dict): Dictionary mapping company symbols to their information
        """
        self.stock_data = stock_data
        self.company_info = company_info
        self.analysis_results = {}
        
        # Initialize storage for specific analyses
        self.rsi_values = {}
        self.circuit_breakers = {}
        self.volume_spikes = {}
        self.sector_performance = {}
        
        if stock_data is not None:
            logger.info(f"MarketAnalyzer initialized with {len(stock_data.index.get_level_values(1).unique())} companies")
        else:
            logger.info("MarketAnalyzer initialized without data")
    
    def get_top_gainers(self, n=10):
        """
        Get the top n gainers (companies with highest percent change).
        
        Args:
            n (int): Number of companies to return
            
        Returns:
            dict: Dictionary mapping symbols to percent change
        """
        if self.stock_data is None:
            logger.warning("No stock data available")
            return {}
        
        try:
            # Get the latest date in the data
            latest_date = self.stock_data.index.get_level_values('date').max()
            
            # Get all records for the latest date
            latest_data = self.stock_data.xs(latest_date, level='date')
            
            # Calculate percent change
            latest_data['pct_change'] = ((latest_data['close'] - latest_data['open']) / latest_data['open']) * 100
            
            # Sort by percent change in descending order
            sorted_by_change = latest_data.sort_values('pct_change', ascending=False)
            
            # Get top n
            top_n = sorted_by_change.head(n)
            
            # Return as dictionary
            return dict(zip(top_n.index.get_level_values('symbol'), top_n['pct_change']))
        except Exception as e:
            logger.error(f"Error getting top gainers: {str(e)}")
            return {}
    
    def get_top_losers(self, n=10):
        """
        Get the top n losers (companies with lowest percent change).
        
        Args:
            n (int): Number of companies to return
            
        Returns:
            dict: Dictionary mapping symbols to percent change
        """
        if self.stock_data is None:
            logger.warning("No stock data available")
            return {}
        
        try:
            # Get the latest date in the data
            latest_date = self.stock_data.index.get_level_values('date').max()
            
            # Get all records for the latest date
            latest_data = self.stock_data.xs(latest_date, level='date')
            
            # Calculate percent change
            latest_data['pct_change'] = ((latest_data['close'] - latest_data['open']) / latest_data['open']) * 100
            
            # Sort by percent change in ascending order
            sorted_by_change = latest_data.sort_values('pct_change', ascending=True)
            
            # Get top n
            top_n = sorted_by_change.head(n)
            
            # Return as dictionary
            return dict(zip(top_n.index.get_level_values('symbol'), top_n['pct_change']))
        except Exception as e:
            logger.error(f"Error getting top losers: {str(e)}")
            return {}
    
    def get_volume_leaders(self, n=10):
        """
        Get the top n companies by trading volume.
        
        Args:
            n (int): Number of companies to return
            
        Returns:
            dict: Dictionary mapping symbols to volume
        """
        if self.stock_data is None:
            logger.warning("No stock data available")
            return {}
        
        try:
            # Get the latest date in the data
            latest_date = self.stock_data.index.get_level_values('date').max()
            
            # Get all records for the latest date
            latest_data = self.stock_data.xs(latest_date, level='date')
            
            # Sort by volume in descending order
            sorted_by_volume = latest_data.sort_values('volume', ascending=False)
            
            # Get top n
            top_n = sorted_by_volume.head(n)
            
            # Return as dictionary
            return dict(zip(top_n.index.get_level_values('symbol'), top_n['volume']))
        except Exception as e:
            logger.error(f"Error getting volume leaders: {str(e)}")
            return {}
    
    def get_market_summary(self):
        """
        Generate a summary of the market based on the latest analysis.
        
        Returns:
            dict: Dictionary with market summary metrics
        """
        if not self.analysis_results:
            logger.warning("No analysis results available. Run comprehensive analysis first.")
            return {}
        
        summary = {}
        
        # Calculate market breadth (advancing vs. declining stocks)
        if self.stock_data is not None:
            try:
                # Get the latest two trading days
                dates = sorted(self.stock_data.index.get_level_values('date').unique())[-2:]
                if len(dates) >= 2:
                    prev_date, curr_date = dates
                    
                    advancing = 0
                    declining = 0
                    unchanged = 0
                    
                    # Get unique companies
                    companies = self.stock_data.index.get_level_values('symbol').unique()
                    
                    for company in companies:
                        try:
                            # Get close prices for the company
                            idx = pd.IndexSlice
                            prev_price = self.stock_data.loc[idx[prev_date, company], 'close'].iloc[0]
                            curr_price = self.stock_data.loc[idx[curr_date, company], 'close'].iloc[0]
                            
                            # Compare prices
                            if curr_price > prev_price:
                                advancing += 1
                            elif curr_price < prev_price:
                                declining += 1
                            else:
                                unchanged += 1
                        except:
                            pass
                    
                    summary['market_breadth'] = {
                        'advancing': advancing,
                        'declining': declining,
                        'unchanged': unchanged,
                        'total': advancing + declining + unchanged,
                        'advance_decline_ratio': advancing / declining if declining > 0 else float('inf')
                    }
            except Exception as e:
                logger.error(f"Error calculating market breadth: {str(e)}")
        
        # Add RSI distribution
        if 'rsi' in self.analysis_results:
            rsi_values = list(self.analysis_results['rsi'].values())
            if rsi_values:
                summary['rsi_metrics'] = {
                    'mean': np.mean(rsi_values),
                    'median': np.median(rsi_values),
                    'std': np.std(rsi_values),
                    'min': min(rsi_values),
                    'max': max(rsi_values)
                }
        
        # Add sector performance
        if 'sector_performance' in self.analysis_results:
            summary['sector_metrics'] = {
                'best_sector': max(self.analysis_results['sector_performance'].items(), 
                                    key=lambda x: x[1])[0],
                'worst_sector': min(self.analysis_results['sector_performance'].items(), 
                                     key=lambda x: x[1])[0],
                'market_return': np.mean(list(self.analysis_results['sector_performance'].values()))
            }
        
        # Add circuit breaker information
        if 'upper_circuit_counts' in self.analysis_results and 'lower_circuit_counts' in self.analysis_results:
            summary['circuit_metrics'] = {
                'total_upper_circuits': sum(self.analysis_results['upper_circuit_counts'].values()),
                'total_lower_circuits': sum(self.analysis_results['lower_circuit_counts'].values()),
                'companies_hit_upper': len(self.analysis_results['upper_circuit_counts']),
                'companies_hit_lower': len(self.analysis_results['lower_circuit_counts'])
            }
        
        # Add volume information
        if 'volume_spike_counts' in self.analysis_results:
            summary['volume_metrics'] = {
                'total_spikes': sum(self.analysis_results['volume_spike_counts'].values()),
                'companies_with_spikes': len(self.analysis_results['volume_spike_counts'])
            }
        
        return summary
