"""
NEPSEZEN - Nepal Stock Exchange Simulator
Data Filtering Module

This module provides functions to filter companies based on various criteria,
such as sector, market cap, P/E ratio, and technical indicators.
"""

import pandas as pd
import numpy as np
import sys
import os
import logging
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from utils.indicators import calculate_rsi, calculate_macd

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def filter_by_sector(company_info, sector):
    """
    Filter companies by sector.
    
    Args:
        company_info (dict): Dictionary of company information
        sector (str or list): Sector(s) to filter by
        
    Returns:
        list: List of company symbols in the specified sector(s)
    """
    if isinstance(sector, str):
        sectors = [sector]
    else:
        sectors = sector
    
    filtered_companies = []
    for symbol, info in company_info.items():
        if 'sector' in info and info['sector'] in sectors:
            filtered_companies.append(symbol)
    
    logger.info(f"Filtered {len(filtered_companies)} companies in sector(s): {sectors}")
    return filtered_companies


def filter_by_market_cap(company_info, min_market_cap=None, max_market_cap=None):
    """
    Filter companies by market capitalization range.
    
    Args:
        company_info (dict): Dictionary of company information
        min_market_cap (float, optional): Minimum market cap value
        max_market_cap (float, optional): Maximum market cap value
        
    Returns:
        list: List of company symbols within the specified market cap range
    """
    filtered_companies = []
    for symbol, info in company_info.items():
        if 'market_cap' not in info:
            continue
        
        market_cap = info['market_cap']
        
        if min_market_cap is not None and market_cap < min_market_cap:
            continue
        
        if max_market_cap is not None and market_cap > max_market_cap:
            continue
        
        filtered_companies.append(symbol)
    
    logger.info(f"Filtered {len(filtered_companies)} companies by market cap range: "
                f"[{min_market_cap if min_market_cap is not None else 'min'}, "
                f"{max_market_cap if max_market_cap is not None else 'max'}]")
    
    return filtered_companies


def filter_by_pe_ratio(company_info, min_pe=None, max_pe=None):
    """
    Filter companies by P/E ratio range.
    
    Args:
        company_info (dict): Dictionary of company information
        min_pe (float, optional): Minimum P/E ratio
        max_pe (float, optional): Maximum P/E ratio
        
    Returns:
        list: List of company symbols within the specified P/E ratio range
    """
    filtered_companies = []
    for symbol, info in company_info.items():
        if 'pe_ratio' not in info or info['pe_ratio'] is None:
            continue
        
        pe_ratio = info['pe_ratio']
        
        if min_pe is not None and pe_ratio < min_pe:
            continue
        
        if max_pe is not None and pe_ratio > max_pe:
            continue
        
        filtered_companies.append(symbol)
    
    logger.info(f"Filtered {len(filtered_companies)} companies by P/E ratio range: "
                f"[{min_pe if min_pe is not None else 'min'}, "
                f"{max_pe if max_pe is not None else 'max'}]")
    
    return filtered_companies


def filter_by_eps(company_info, min_eps=None, max_eps=None):
    """
    Filter companies by EPS (Earnings Per Share) range.
    
    Args:
        company_info (dict): Dictionary of company information
        min_eps (float, optional): Minimum EPS value
        max_eps (float, optional): Maximum EPS value
        
    Returns:
        list: List of company symbols within the specified EPS range
    """
    filtered_companies = []
    for symbol, info in company_info.items():
        if 'eps' not in info or info['eps'] is None:
            continue
        
        eps = info['eps']
        
        if min_eps is not None and eps < min_eps:
            continue
        
        if max_eps is not None and eps > max_eps:
            continue
        
        filtered_companies.append(symbol)
    
    logger.info(f"Filtered {len(filtered_companies)} companies by EPS range: "
                f"[{min_eps if min_eps is not None else 'min'}, "
                f"{max_eps if max_eps is not None else 'max'}]")
    
    return filtered_companies


def filter_by_rsi(stock_data, min_rsi=None, max_rsi=None, period=None, as_of_date=None):
    """
    Filter companies by RSI (Relative Strength Index) range.
    
    Args:
        stock_data (pd.DataFrame): DataFrame with hierarchical index (date, symbol) and OHLCV columns
        min_rsi (float, optional): Minimum RSI value
        max_rsi (float, optional): Maximum RSI value
        period (int, optional): Period for RSI calculation, defaults to config value
        as_of_date (str, optional): Date to calculate RSI as of, defaults to latest date
        
    Returns:
        list: List of company symbols within the specified RSI range
    """
    if period is None:
        period = config.RSI_PERIOD
    
    filtered_companies = []
    
    # Get unique companies
    companies = stock_data.index.get_level_values(1).unique()
    
    for company in companies:
        try:
            # Get close prices for the company
            company_data = stock_data.xs(company, level=1)['close']
            
            # Calculate RSI
            rsi = calculate_rsi(company_data, period)
            
            # Get RSI as of specified date or latest date
            if as_of_date is not None:
                if as_of_date not in rsi.index:
                    continue
                rsi_value = rsi[as_of_date]
            else:
                # Get latest valid (non-NaN) RSI
                valid_rsi = rsi.dropna()
                if valid_rsi.empty:
                    continue
                rsi_value = valid_rsi.iloc[-1]
            
            # Check if RSI is within range
            if min_rsi is not None and rsi_value < min_rsi:
                continue
            
            if max_rsi is not None and rsi_value > max_rsi:
                continue
            
            filtered_companies.append(company)
        
        except Exception as e:
            logger.warning(f"Error calculating RSI for {company}: {str(e)}")
    
    logger.info(f"Filtered {len(filtered_companies)} companies by RSI range: "
                f"[{min_rsi if min_rsi is not None else 'min'}, "
                f"{max_rsi if max_rsi is not None else 'max'}]")
    
    return filtered_companies


def filter_by_volume(stock_data, min_volume=None, max_volume=None, 
                     avg_period=20, as_of_date=None):
    """
    Filter companies by trading volume range.
    
    Args:
        stock_data (pd.DataFrame): DataFrame with hierarchical index (date, symbol) and OHLCV columns
        min_volume (float, optional): Minimum volume value
        max_volume (float, optional): Maximum volume value
        avg_period (int, optional): Period for average volume calculation, defaults to 20
        as_of_date (str, optional): Date to calculate volume as of, defaults to latest date
        
    Returns:
        list: List of company symbols within the specified volume range
    """
    filtered_companies = []
    
    # Get unique companies
    companies = stock_data.index.get_level_values(1).unique()
    
    for company in companies:
        try:
            # Get volume data for the company
            company_data = stock_data.xs(company, level=1)['volume']
            
            # Calculate average volume
            avg_volume = company_data.rolling(window=avg_period).mean()
            
            # Get volume as of specified date or latest date
            if as_of_date is not None:
                if as_of_date not in avg_volume.index:
                    continue
                volume_value = avg_volume[as_of_date]
            else:
                # Get latest valid (non-NaN) volume
                valid_volume = avg_volume.dropna()
                if valid_volume.empty:
                    continue
                volume_value = valid_volume.iloc[-1]
            
            # Check if volume is within range
            if min_volume is not None and volume_value < min_volume:
                continue
            
            if max_volume is not None and volume_value > max_volume:
                continue
            
            filtered_companies.append(company)
        
        except Exception as e:
            logger.warning(f"Error calculating average volume for {company}: {str(e)}")
    
    logger.info(f"Filtered {len(filtered_companies)} companies by average volume range: "
                f"[{min_volume if min_volume is not None else 'min'}, "
                f"{max_volume if max_volume is not None else 'max'}]")
    
    return filtered_companies


def filter_by_price_change(stock_data, min_change=None, max_change=None,
                           start_date=None, end_date=None):
    """
    Filter companies by price change over a specified period.
    
    Args:
        stock_data (pd.DataFrame): DataFrame with hierarchical index (date, symbol) and OHLCV columns
        min_change (float, optional): Minimum price change percentage
        max_change (float, optional): Maximum price change percentage
        start_date (str, optional): Start date for calculating price change, defaults to earliest date
        end_date (str, optional): End date for calculating price change, defaults to latest date
        
    Returns:
        list: List of company symbols within the specified price change range
    """
    # Set default dates if not provided
    if start_date is None:
        start_date = stock_data.index.get_level_values(0).min()
    if end_date is None:
        end_date = stock_data.index.get_level_values(0).max()
    
    filtered_companies = []
    
    # Get unique companies
    companies = stock_data.index.get_level_values(1).unique()
    
    for company in companies:
        try:
            # Get close prices for the company
            idx = pd.IndexSlice
            company_data = stock_data.loc[idx[start_date:end_date, company], 'close']
            
            if company_data.empty or len(company_data) < 2:
                continue
            
            # Calculate price change percentage
            start_price = company_data.iloc[0]
            end_price = company_data.iloc[-1]
            price_change = (end_price / start_price - 1) * 100
            
            # Check if price change is within range
            if min_change is not None and price_change < min_change:
                continue
            
            if max_change is not None and price_change > max_change:
                continue
            
            filtered_companies.append(company)
        
        except Exception as e:
            logger.warning(f"Error calculating price change for {company}: {str(e)}")
    
    logger.info(f"Filtered {len(filtered_companies)} companies by price change range: "
                f"[{min_change if min_change is not None else 'min'}%, "
                f"{max_change if max_change is not None else 'max'}%] "
                f"from {start_date} to {end_date}")
    
    return filtered_companies


def filter_by_circuit_breakers(circuit_data, circuit_type=None, min_count=1):
    """
    Filter companies by circuit breaker events.
    
    Args:
        circuit_data (pd.DataFrame): DataFrame with date index, company columns, and circuit values
        circuit_type (str, optional): Type of circuit breaker ('Upper', 'Lower', or None for both)
        min_count (int, optional): Minimum number of circuit breaker events, defaults to 1
        
    Returns:
        list: List of company symbols with the specified circuit breaker events
    """
    filtered_companies = []
    
    for company in circuit_data.columns:
        if circuit_type:
            # Count specific circuit type
            count = (circuit_data[company] == circuit_type).sum()
        else:
            # Count any circuit (not 'None')
            count = (circuit_data[company] != 'None').sum()
        
        if count >= min_count:
            filtered_companies.append(company)
    
    circuit_str = circuit_type if circuit_type else "any"
    logger.info(f"Filtered {len(filtered_companies)} companies with at least {min_count} "
                f"{circuit_str} circuit breaker events")
    
    return filtered_companies


def filter_by_macd_signal(stock_data, signal_type='crossover', as_of_date=None):
    """
    Filter companies by MACD signal.
    
    Args:
        stock_data (pd.DataFrame): DataFrame with hierarchical index (date, symbol) and OHLCV columns
        signal_type (str): Type of MACD signal ('crossover', 'crossunder', 'positive', 'negative')
        as_of_date (str, optional): Date to check for MACD signal, defaults to latest date
        
    Returns:
        list: List of company symbols with the specified MACD signal
    """
    filtered_companies = []
    
    # Get unique companies
    companies = stock_data.index.get_level_values(1).unique()
    
    for company in companies:
        try:
            # Get close prices for the company
            company_data = stock_data.xs(company, level=1)['close']
            
            # Calculate MACD
            macd_line, signal_line, histogram = calculate_macd(company_data)
            
            # Get index for checking signal
            if as_of_date is not None:
                if as_of_date not in macd_line.index:
                    continue
                idx = macd_line.index.get_loc(as_of_date)
            else:
                # Use latest available data
                idx = -1
            
            # Check if we have enough data
            if len(macd_line) < 2 or len(signal_line) < 2:
                continue
            
            if idx == 0:
                # Need at least one prior data point
                continue
            
            # Check for the specified signal
            if signal_type == 'crossover':
                # MACD crossed above signal line
                if macd_line.iloc[idx-1] <= signal_line.iloc[idx-1] and macd_line.iloc[idx] > signal_line.iloc[idx]:
                    filtered_companies.append(company)
            
            elif signal_type == 'crossunder':
                # MACD crossed below signal line
                if macd_line.iloc[idx-1] >= signal_line.iloc[idx-1] and macd_line.iloc[idx] < signal_line.iloc[idx]:
                    filtered_companies.append(company)
            
            elif signal_type == 'positive':
                # MACD above signal line
                if macd_line.iloc[idx] > signal_line.iloc[idx]:
                    filtered_companies.append(company)
            
            elif signal_type == 'negative':
                # MACD below signal line
                if macd_line.iloc[idx] < signal_line.iloc[idx]:
                    filtered_companies.append(company)
        
        except Exception as e:
            logger.warning(f"Error checking MACD signal for {company}: {str(e)}")
    
    logger.info(f"Filtered {len(filtered_companies)} companies with MACD {signal_type} signal")
    
    return filtered_companies


def combine_filters(company_lists, operation='and'):
    """
    Combine multiple filtered company lists using logical operations.
    
    Args:
        company_lists (list): List of company symbol lists to combine
        operation (str): Logical operation to use ('and', 'or')
        
    Returns:
        list: Combined list of company symbols
    """
    if not company_lists:
        return []
    
    if len(company_lists) == 1:
        return company_lists[0]
    
    # Convert all lists to sets
    company_sets = [set(company_list) for company_list in company_lists]
    
    # Combine sets using the specified operation
    if operation.lower() == 'and':
        result = company_sets[0]
        for company_set in company_sets[1:]:
            result = result.intersection(company_set)
    elif operation.lower() == 'or':
        result = company_sets[0]
        for company_set in company_sets[1:]:
            result = result.union(company_set)
    else:
        logger.error(f"Unsupported operation: {operation}")
        return []
    
    logger.info(f"Combined {len(company_lists)} filter lists using '{operation}' "
                f"operation, resulting in {len(result)} companies")
    
    return list(result)


class CompanyFilterBuilder:
    """
    A builder class for creating and combining multiple company filters.
    """
    
    def __init__(self, stock_data=None, company_info=None):
        """
        Initialize the filter builder with stock data and company information.
        
        Args:
            stock_data (pd.DataFrame): DataFrame with hierarchical index (date, symbol) and OHLCV columns
            company_info (dict): Dictionary of company information
        """
        self.stock_data = stock_data
        self.company_info = company_info
        self.filters = []
    
    def by_sector(self, sector):
        """
        Add a sector filter.
        
        Args:
            sector (str or list): Sector(s) to filter by
            
        Returns:
            CompanyFilterBuilder: Self for method chaining
        """
        if self.company_info is None:
            logger.error("Company information not available for sector filter")
            return self
        
        self.filters.append(filter_by_sector(self.company_info, sector))
        return self
    
    def by_market_cap(self, min_market_cap=None, max_market_cap=None):
        """
        Add a market cap filter.
        
        Args:
            min_market_cap (float, optional): Minimum market cap value
            max_market_cap (float, optional): Maximum market cap value
            
        Returns:
            CompanyFilterBuilder: Self for method chaining
        """
        if self.company_info is None:
            logger.error("Company information not available for market cap filter")
            return self
        
        self.filters.append(filter_by_market_cap(self.company_info, min_market_cap, max_market_cap))
        return self
    
    def by_pe_ratio(self, min_pe=None, max_pe=None):
        """
        Add a P/E ratio filter.
        
        Args:
            min_pe (float, optional): Minimum P/E ratio
            max_pe (float, optional): Maximum P/E ratio
            
        Returns:
            CompanyFilterBuilder: Self for method chaining
        """
        if self.company_info is None:
            logger.error("Company information not available for P/E ratio filter")
            return self
        
        self.filters.append(filter_by_pe_ratio(self.company_info, min_pe, max_pe))
        return self
    
    def by_eps(self, min_eps=None, max_eps=None):
        """
        Add an EPS filter.
        
        Args:
            min_eps (float, optional): Minimum EPS value
            max_eps (float, optional): Maximum EPS value
            
        Returns:
            CompanyFilterBuilder: Self for method chaining
        """
        if self.company_info is None:
            logger.error("Company information not available for EPS filter")
            return self
        
        self.filters.append(filter_by_eps(self.company_info, min_eps, max_eps))
        return self
    
    def by_rsi(self, min_rsi=None, max_rsi=None, period=None, as_of_date=None):
        """
        Add an RSI filter.
        
        Args:
            min_rsi (float, optional): Minimum RSI value
            max_rsi (float, optional): Maximum RSI value
            period (int, optional): Period for RSI calculation, defaults to config value
            as_of_date (str, optional): Date to calculate RSI as of, defaults to latest date
            
        Returns:
            CompanyFilterBuilder: Self for method chaining
        """
        if self.stock_data is None:
            logger.error("Stock data not available for RSI filter")
            return self
        
        self.filters.append(filter_by_rsi(self.stock_data, min_rsi, max_rsi, period, as_of_date))
        return self
    
    def by_volume(self, min_volume=None, max_volume=None, avg_period=20, as_of_date=None):
        """
        Add a volume filter.
        
        Args:
            min_volume (float, optional): Minimum volume value
            max_volume (float, optional): Maximum volume value
            avg_period (int, optional): Period for average volume calculation, defaults to 20
            as_of_date (str, optional): Date to calculate volume as of, defaults to latest date
            
        Returns:
            CompanyFilterBuilder: Self for method chaining
        """
        if self.stock_data is None:
            logger.error("Stock data not available for volume filter")
            return self
        
        self.filters.append(filter_by_volume(self.stock_data, min_volume, max_volume, avg_period, as_of_date))
        return self
    
    def by_price_change(self, min_change=None, max_change=None, start_date=None, end_date=None):
        """
        Add a price change filter.
        
        Args:
            min_change (float, optional): Minimum price change percentage
            max_change (float, optional): Maximum price change percentage
            start_date (str, optional): Start date for calculating price change, defaults to earliest date
            end_date (str, optional): End date for calculating price change, defaults to latest date
            
        Returns:
            CompanyFilterBuilder: Self for method chaining
        """
        if self.stock_data is None:
            logger.error("Stock data not available for price change filter")
            return self
        
        self.filters.append(filter_by_price_change(
            self.stock_data, min_change, max_change, start_date, end_date))
        return self
    
    def by_macd_signal(self, signal_type='crossover', as_of_date=None):
        """
        Add a MACD signal filter.
        
        Args:
            signal_type (str): Type of MACD signal ('crossover', 'crossunder', 'positive', 'negative')
            as_of_date (str, optional): Date to check for MACD signal, defaults to latest date
            
        Returns:
            CompanyFilterBuilder: Self for method chaining
        """
        if self.stock_data is None:
            logger.error("Stock data not available for MACD signal filter")
            return self
        
        self.filters.append(filter_by_macd_signal(self.stock_data, signal_type, as_of_date))
        return self
    
    def by_circuit_breakers(self, circuit_data, circuit_type=None, min_count=1):
        """
        Add a circuit breaker filter.
        
        Args:
            circuit_data (pd.DataFrame): DataFrame with date index, company columns, and circuit values
            circuit_type (str, optional): Type of circuit breaker ('Upper', 'Lower', or None for both)
            min_count (int, optional): Minimum number of circuit breaker events, defaults to 1
            
        Returns:
            CompanyFilterBuilder: Self for method chaining
        """
        self.filters.append(filter_by_circuit_breakers(circuit_data, circuit_type, min_count))
        return self
    
    def build(self, operation='and'):
        """
        Combine all filters and return the final list of filtered companies.
        
        Args:
            operation (str): Logical operation to use when combining filters ('and', 'or')
            
        Returns:
            list: Final filtered list of company symbols
        """
        if not self.filters:
            logger.warning("No filters added, returning empty list")
            return []
        
        return combine_filters(self.filters, operation)
