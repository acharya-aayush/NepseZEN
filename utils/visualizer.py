"""
NEPSEZEN - Nepal Stock Exchange Simulator
Data Visualization Module

This module provides functions for visualizing stock market data,
including candlestick charts, indicator plots, and volume analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from utils.indicators import calculate_rsi, calculate_bollinger_bands, calculate_macd


def plot_candlestick_chart(df, title='Stock Price', volume=True, figsize=(12, 8)):
    """
    Create a matplotlib candlestick chart with optional volume.
    
    Args:
        df (pd.DataFrame): DataFrame with 'open', 'high', 'low', 'close', and optionally 'volume' columns
        title (str, optional): Chart title, defaults to 'Stock Price'
        volume (bool, optional): Whether to include volume subplot, defaults to True
        figsize (tuple, optional): Figure size, defaults to (12, 8)
        
    Returns:
        plt.Figure: The matplotlib figure object
    """
    # Create figure and primary axis
    fig = plt.figure(figsize=figsize)
    
    if volume:
        # Create subplots for price and volume
        ax1 = plt.subplot2grid((5, 1), (0, 0), rowspan=3)
        ax2 = plt.subplot2grid((5, 1), (3, 0), rowspan=1, sharex=ax1)
        
        # Format dates on x-axis
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        
        # Plot candlestick chart
        for i in range(len(df)):
            # Green candle
            if df['close'].iloc[i] >= df['open'].iloc[i]:
                ax1.plot([df.index[i], df.index[i]], [df['low'].iloc[i], df['high'].iloc[i]], 'g-')
                ax1.plot([df.index[i], df.index[i]], [df['open'].iloc[i], df['close'].iloc[i]], 'g-', linewidth=4)
            # Red candle
            else:
                ax1.plot([df.index[i], df.index[i]], [df['low'].iloc[i], df['high'].iloc[i]], 'r-')
                ax1.plot([df.index[i], df.index[i]], [df['open'].iloc[i], df['close'].iloc[i]], 'r-', linewidth=4)
        
        # Plot volume
        ax2.bar(df.index, df['volume'], color='blue', alpha=0.5)
        ax2.set_ylabel('Volume')
        
        # Set title and labels
        ax1.set_title(title)
        ax1.set_ylabel('Price')
        ax1.grid(True)
        ax2.grid(True)
        
        # Format x-axis
        plt.xticks(rotation=45)
        plt.tight_layout()
        
    else:
        ax1 = plt.gca()
        
        # Format dates on x-axis
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        
        # Plot candlestick chart
        for i in range(len(df)):
            # Green candle
            if df['close'].iloc[i] >= df['open'].iloc[i]:
                ax1.plot([df.index[i], df.index[i]], [df['low'].iloc[i], df['high'].iloc[i]], 'g-')
                ax1.plot([df.index[i], df.index[i]], [df['open'].iloc[i], df['close'].iloc[i]], 'g-', linewidth=4)
            # Red candle
            else:
                ax1.plot([df.index[i], df.index[i]], [df['low'].iloc[i], df['high'].iloc[i]], 'r-')
                ax1.plot([df.index[i], df.index[i]], [df['open'].iloc[i], df['close'].iloc[i]], 'r-', linewidth=4)
        
        # Set title and labels
        ax1.set_title(title)
        ax1.set_ylabel('Price')
        ax1.grid(True)
        
        # Format x-axis
        plt.xticks(rotation=45)
        plt.tight_layout()
    
    return fig


def plot_interactive_candlestick(df, title='Stock Price', include_volume=True, include_rsi=False, include_bb=False, include_macd=False):
    """
    Create an interactive Plotly candlestick chart with optional indicators.
    
    Args:
        df (pd.DataFrame): DataFrame with 'open', 'high', 'low', 'close', and optionally 'volume' columns
        title (str, optional): Chart title, defaults to 'Stock Price'
        include_volume (bool, optional): Whether to include volume subplot, defaults to True
        include_rsi (bool, optional): Whether to include RSI indicator, defaults to False
        include_bb (bool, optional): Whether to include Bollinger Bands, defaults to False
        include_macd (bool, optional): Whether to include MACD indicator, defaults to False
        
    Returns:
        plotly.graph_objects.Figure: The Plotly figure object
    """
    # Calculate how many rows we need for subplots
    row_count = 1
    if include_volume:
        row_count += 1
    if include_rsi:
        row_count += 1
    if include_macd:
        row_count += 1
    
    # Create subplot specs
    row_heights = []
    specs = []
    for i in range(row_count):
        if i == 0:  # Main price chart
            row_heights.append(0.5)
        elif i == row_count - 1 and include_volume:  # Volume is last if included
            row_heights.append(0.2)
        else:  # Other indicators
            row_heights.append(0.3)
        specs.append([{"secondary_y": True}])
    
    # Create figure with subplots
    fig = make_subplots(rows=row_count, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, subplot_titles=None,
                        row_heights=row_heights, specs=specs)
    
    # Add candlestick chart
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'], 
        high=df['high'],
        low=df['low'], 
        close=df['close'],
        name="Price"
    ), row=1, col=1)
    
    # Add Bollinger Bands if requested
    if include_bb:
        upper_band, middle_band, lower_band = calculate_bollinger_bands(df['close'])
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=upper_band, 
            name="Upper Bollinger Band",
            line=dict(color='rgba(250, 0, 0, 0.5)'),
            legendgroup='Bollinger'
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=middle_band, 
            name="Middle Bollinger Band",
            line=dict(color='rgba(0, 0, 250, 0.5)'),
            legendgroup='Bollinger'
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=lower_band, 
            name="Lower Bollinger Band",
            line=dict(color='rgba(250, 0, 0, 0.5)'),
            legendgroup='Bollinger',
            fill='tonexty',
            fillcolor='rgba(255, 255, 255, 0.1)'
        ), row=1, col=1)
    
    # Current row counter for adding subplots
    current_row = 2
    
    # Add RSI if requested
    if include_rsi:
        rsi = calculate_rsi(df['close'])
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=rsi, 
            name="RSI",
            line=dict(color='purple', width=1)
        ), row=current_row, col=1)
        
        # Add overbought/oversold lines
        fig.add_trace(go.Scatter(
            x=df.index,
            y=[70] * len(df.index),
            name="Overbought",
            line=dict(color='red', width=1, dash='dash'),
            legendgroup='RSI_lines'
        ), row=current_row, col=1)
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=[30] * len(df.index),
            name="Oversold",
            line=dict(color='green', width=1, dash='dash'),
            legendgroup='RSI_lines'
        ), row=current_row, col=1)
        
        current_row += 1
    
    # Add MACD if requested
    if include_macd:
        macd_line, signal_line, macd_histogram = calculate_macd(df['close'])
        
        # Add MACD line and signal line
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=macd_line, 
            name="MACD",
            line=dict(color='blue', width=1)
        ), row=current_row, col=1)
        
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=signal_line, 
            name="Signal",
            line=dict(color='red', width=1)
        ), row=current_row, col=1)
        
        # Add MACD histogram
        colors = ['green' if val >= 0 else 'red' for val in macd_histogram]
        fig.add_trace(go.Bar(
            x=df.index, 
            y=macd_histogram, 
            name="Histogram",
            marker_color=colors
        ), row=current_row, col=1)
        
        current_row += 1
    
    # Add volume if requested
    if include_volume:
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['volume'],
            name="Volume",
            marker=dict(color='rgba(0, 0, 255, 0.3)')
        ), row=current_row, col=1)
    
    # Update layout
    fig.update_layout(
        title=title,
        height=config.DEFAULT_CHART_HEIGHT,
        width=config.DEFAULT_CHART_WIDTH,
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=50, t=85, b=50),
    )
    
    # Update candlestick colors
    fig.update_traces(
        increasing_line_color='green',
        decreasing_line_color='red',
        selector=dict(type='candlestick')
    )
    
    return fig


def plot_sector_performance(sector_returns, title="Sector Performance"):
    """
    Create a bar chart of sector performance.
    
    Args:
        sector_returns (dict): Dictionary of sector names and their returns
        title (str, optional): Chart title, defaults to "Sector Performance"
        
    Returns:
        plotly.graph_objects.Figure: The Plotly figure object
    """
    # Convert dictionary to dataframe
    df = pd.DataFrame(list(sector_returns.items()), columns=['Sector', 'Return'])
    
    # Sort by return
    df = df.sort_values('Return', ascending=False)
    
    # Assign colors based on return value
    colors = ['green' if r >= 0 else 'red' for r in df['Return']]
    
    # Create bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['Sector'],
        y=df['Return'] * 100,  # Convert to percentage
        marker_color=colors,
        text=df['Return'] * 100,
        texttemplate='%{text:.2f}%',
        textposition='outside'
    ))
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Sector",
        yaxis_title="Return (%)",
        height=500,
        width=config.DEFAULT_CHART_WIDTH
    )
    
    return fig


def plot_volume_heatmap(df, companies, title="Trading Volume Heatmap"):
    """
    Create a heatmap of trading volumes across multiple companies.
    
    Args:
        df (pd.DataFrame): DataFrame with date index and company volumes as columns
        companies (list): List of company symbols to include
        title (str, optional): Chart title, defaults to "Trading Volume Heatmap"
        
    Returns:
        plotly.graph_objects.Figure: The Plotly figure object
    """
    # Filter for specified companies
    volume_df = df[companies]
    
    # Normalize volumes for better visualization
    volume_norm = volume_df.div(volume_df.max()).fillna(0)
    
    # Create heatmap
    fig = px.imshow(
        volume_norm.T,
        labels=dict(x="Date", y="Company", color="Normalized Volume"),
        x=volume_norm.index,
        y=companies,
        aspect="auto"
    )
    
    # Update layout
    fig.update_layout(
        title=title,
        height=600,
        width=config.DEFAULT_CHART_WIDTH
    )
    
    return fig


def plot_portfolio_performance(portfolio_history, benchmark=None, title="Portfolio Performance"):
    """
    Create a line chart of portfolio performance with optional benchmark comparison.
    
    Args:
        portfolio_history (pd.DataFrame): DataFrame with date index and portfolio value
        benchmark (pd.DataFrame, optional): DataFrame with date index and benchmark value
        title (str, optional): Chart title, defaults to "Portfolio Performance"
        
    Returns:
        plotly.graph_objects.Figure: The Plotly figure object
    """
    fig = go.Figure()
    
    # Add portfolio performance line
    fig.add_trace(go.Scatter(
        x=portfolio_history.index,
        y=portfolio_history['value'],
        name="Portfolio",
        line=dict(color='blue', width=2)
    ))
    
    # Add benchmark if provided
    if benchmark is not None:
        fig.add_trace(go.Scatter(
            x=benchmark.index,
            y=benchmark['value'],
            name="Benchmark",
            line=dict(color='gray', width=2, dash='dash')
        ))
    
    # Calculate and display return
    initial_value = portfolio_history['value'].iloc[0]
    final_value = portfolio_history['value'].iloc[-1]
    total_return = (final_value / initial_value - 1) * 100
    
    # Update layout
    fig.update_layout(
        title=f"{title} (Return: {total_return:.2f}%)",
        xaxis_title="Date",
        yaxis_title="Value (NPR)",
        height=500,
        width=config.DEFAULT_CHART_WIDTH,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def plot_circuit_breakers(circuit_data, title="Circuit Breaker Events"):
    """
    Create a visualization of circuit breaker events.
    
    Args:
        circuit_data (pd.DataFrame): DataFrame with date index, company symbols as columns, and circuit values
        title (str, optional): Chart title, defaults to "Circuit Breaker Events"
        
    Returns:
        plotly.graph_objects.Figure: The Plotly figure object
    """
    # Melt the dataframe to long format
    melted_df = pd.melt(
        circuit_data.reset_index(), 
        id_vars=['index'], 
        var_name='Company', 
        value_name='Circuit'
    )
    melted_df = melted_df.rename(columns={'index': 'Date'})
    
    # Filter for only circuit breaker events
    melted_df = melted_df[melted_df['Circuit'] != 'None']
    
    # Create color map
    color_map = {'Upper': 'green', 'Lower': 'red'}
    
    # Create scatter plot
    fig = px.scatter(
        melted_df,
        x='Date',
        y='Company',
        color='Circuit',
        color_discrete_map=color_map,
        size_max=10,
        title=title
    )
    
    # Update layout
    fig.update_layout(
        height=600,
        width=config.DEFAULT_CHART_WIDTH,
        yaxis=dict(categoryorder='category ascending'),
        xaxis_title="Date",
        yaxis_title="Company"
    )
    
    return fig


def plot_company_comparison(df, companies, metric='close', title="Company Comparison"):
    """
    Create a line chart comparing a metric across multiple companies.
    
    Args:
        df (pd.DataFrame): DataFrame with hierarchical index of (date, company) and columns of metrics
        companies (list): List of company symbols to include
        metric (str, optional): Metric to compare, defaults to 'close'
        title (str, optional): Chart title, defaults to "Company Comparison"
        
    Returns:
        plotly.graph_objects.Figure: The Plotly figure object
    """
    fig = go.Figure()
    
    # Filter for companies and normalize to first day = 100
    for company in companies:
        company_data = df.xs(company, level=1)[metric]
        normalized_data = company_data / company_data.iloc[0] * 100
        
        fig.add_trace(go.Scatter(
            x=normalized_data.index,
            y=normalized_data,
            name=company,
            mode='lines'
        ))
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title=f"Normalized {metric.capitalize()} Price (Base=100)",
        height=500,
        width=config.DEFAULT_CHART_WIDTH,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def plot_rsi_distribution(rsi_values, title="RSI Distribution"):
    """
    Create a histogram of RSI values across companies.
    
    Args:
        rsi_values (pd.Series): Series of RSI values for different companies
        title (str, optional): Chart title, defaults to "RSI Distribution"
        
    Returns:
        plotly.graph_objects.Figure: The Plotly figure object
    """
    fig = go.Figure()
    
    # Add histogram
    fig.add_trace(go.Histogram(
        x=rsi_values,
        marker_color='blue',
        opacity=0.7,
        nbinsx=20
    ))
    
    # Add vertical lines for overbought and oversold thresholds
    fig.add_shape(
        type="line",
        x0=30, x1=30, y0=0, y1=1,
        yref="paper",
        line=dict(color="green", width=2, dash="dash")
    )
    
    fig.add_shape(
        type="line",
        x0=70, x1=70, y0=0, y1=1,
        yref="paper",
        line=dict(color="red", width=2, dash="dash")
    )
    
    # Add annotations
    fig.add_annotation(
        x=30, y=0.95, yref="paper",
        text="Oversold (30)",
        showarrow=False,
        bgcolor="rgba(255,255,255,0.8)"
    )
    
    fig.add_annotation(
        x=70, y=0.95, yref="paper",
        text="Overbought (70)",
        showarrow=False,
        bgcolor="rgba(255,255,255,0.8)"
    )
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="RSI Value",
        yaxis_title="Number of Companies",
        height=500,
        width=config.DEFAULT_CHART_WIDTH,
        bargap=0.1
    )
    
    return fig
