"""
Simple Streamlit dashboard for NEPSEZEN
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys

# Define simple market analysis function inline to avoid import issues
def simple_market_analysis(stock_data, company_info):
    """
    Perform basic market analysis
    
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

def main():
    # Load sample data
    try:
        stock_data = pd.read_csv('data/historical/1month.csv')
        # Convert string dates to datetime
        stock_data['date'] = pd.to_datetime(stock_data['date'])
        # Set multi-index
        stock_data = stock_data.set_index(['date', 'symbol'])
        
        # Set page title
        st.set_page_config(page_title='NEPSEZEN Dashboard', layout='wide')
        
        # Page header
        st.title('NEPSEZEN - Nepal Stock Exchange Dashboard')
        
        # Perform simple analysis
        analysis = simple_market_analysis(stock_data, {})
        
        # Market breadth
        st.header('Market Overview')
        if analysis and 'market_breadth' in analysis:
            col1, col2, col3 = st.columns(3)
            breadth = analysis['market_breadth']
            with col1:
                st.metric('Advances', breadth.get('advances', 0))
            with col2:
                st.metric('Declines', breadth.get('declines', 0))
            with col3:
                st.metric('Unchanged', breadth.get('unchanged', 0))
        
        # Market return
        if analysis and 'market_avg' in analysis:
            market_avg = analysis['market_avg']
            st.metric('Market Average Return', f"{market_avg.get('return', 0):.2f}%")
        
        # Top gainers and losers
        if analysis and 'top_gainers' in analysis and 'top_losers' in analysis:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader('Top Gainers')
                gainers_df = pd.DataFrame({
                    'Symbol': list(analysis['top_gainers'].keys()),
                    'Return (%)': list(analysis['top_gainers'].values())
                })
                if not gainers_df.empty:
                    gainers_df['Return (%)'] = gainers_df['Return (%)'].apply(lambda x: f"{x:.2f}%")
                    st.dataframe(gainers_df)
            
            with col2:
                st.subheader('Top Losers')
                losers_df = pd.DataFrame({
                    'Symbol': list(analysis['top_losers'].keys()),
                    'Return (%)': list(analysis['top_losers'].values())
                })
                if not losers_df.empty:
                    losers_df['Return (%)'] = losers_df['Return (%)'].apply(lambda x: f"{x:.2f}%")
                    st.dataframe(losers_df)
                    
        # Volume leaders
        if analysis and 'volume_leaders' in analysis:
            st.subheader('Volume Leaders')
            volume_df = pd.DataFrame({
                'Symbol': list(analysis['volume_leaders'].keys()),
                'Volume': list(analysis['volume_leaders'].values())
            })
            if not volume_df.empty:
                volume_df['Volume'] = volume_df['Volume'].apply(lambda x: f"{x:,.0f}")
                st.dataframe(volume_df)
                
        # If sector performance exists
        if analysis and 'sector_performance' in analysis:
            st.subheader('Sector Performance')
            sector_df = pd.DataFrame({
                'Sector': list(analysis['sector_performance'].keys()),
                'Return (%)': list(analysis['sector_performance'].values())
            })
            sector_df = sector_df.sort_values('Return (%)', ascending=False)
            sector_df['Return (%)'] = sector_df['Return (%)'].apply(lambda x: f"{x:.2f}%")
            st.dataframe(sector_df)

    except Exception as e:
        st.error(f'Error loading data: {str(e)}')

if __name__ == "__main__":
    main()
