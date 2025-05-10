"""
Simple market analysis functions for the NEPSEZEN dashboard
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def simple_market_analysis(stock_data, company_info):
    """
    Perform basic market analysis without requiring the full analyzer
    
    Args:
        stock_data (pd.DataFrame): DataFrame with hierarchical index (date, symbol) and OHLCV columns
        company_info (dict): Dictionary with company information
    
    Returns:
        dict: Dictionary with analysis results
    """
    results = {}
    
    # Get latest data
    latest_date = stock_data.index.get_level_values('date').max()
    latest_data = stock_data.xs(latest_date, level='date').copy()
    
    # Add percent change
    latest_data['pct_change'] = ((latest_data['close'] - latest_data['open']) / latest_data['open']) * 100
    
    # Get top gainers
    top_gainers = latest_data.sort_values('pct_change', ascending=False).head(10)
    results['top_gainers'] = dict(zip(top_gainers.index.get_level_values('symbol'), top_gainers['pct_change']))
    
    # Get top losers
    top_losers = latest_data.sort_values('pct_change', ascending=True).head(10)
    results['top_losers'] = dict(zip(top_losers.index.get_level_values('symbol'), top_losers['pct_change']))
    
    # Get volume leaders
    volume_leaders = latest_data.sort_values('volume', ascending=False).head(10)
    results['volume_leaders'] = dict(zip(volume_leaders.index.get_level_values('symbol'), volume_leaders['volume']))
    
    # Calculate market breadth
    advances = (latest_data['pct_change'] > 0).sum()
    declines = (latest_data['pct_change'] < 0).sum()
    unchanged = len(latest_data) - advances - declines
    
    results['market_breadth'] = {
        'advances': advances,
        'declines': declines,
        'unchanged': unchanged,
        'total': len(latest_data),
        'advance_decline_ratio': advances / declines if declines > 0 else float('inf')
    }
    
    # Calculate market average
    results['market_avg'] = {
        'return': latest_data['pct_change'].mean(),
        'volume': latest_data['volume'].mean()
    }
    
    # Calculate sector performance if sector info available
    if company_info:
        sector_returns = {}
        sector_companies = {}
        
        for symbol, data in latest_data.iterrows():
            if symbol in company_info and 'sector' in company_info[symbol]:
                sector = company_info[symbol]['sector']
                if sector not in sector_returns:
                    sector_returns[sector] = []
                    sector_companies[sector] = []
                
                sector_returns[sector].append(data['pct_change'])
                sector_companies[sector].append(symbol)
        
        # Calculate average return by sector
        sector_performance = {}
        for sector, returns in sector_returns.items():
            sector_performance[sector] = sum(returns) / len(returns)
        
        results['sector_performance'] = sector_performance
        results['sector_companies'] = sector_companies
    
    return results
