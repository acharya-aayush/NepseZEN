"""
NEPSEZEN - Nepal Stock Exchange Simulator
Streamlit Dashboard for NEPSEZEN

This module provides an interactive dashboard for visualizing and interacting 
with the NEPSE market simulation.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
import sys
import json
import time
import threading

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from simulator.main_builder import MarketSimulation, PortfolioManager
from analytics.analyzer import MarketAnalyzer
from utils.visualizer import (
    plot_interactive_candlestick, plot_sector_performance,
    plot_volume_heatmap, plot_portfolio_performance, plot_circuit_breakers
)

# Initialize session state
if 'simulation' not in st.session_state:
    st.session_state.simulation = MarketSimulation()
    st.session_state.loaded = False
    st.session_state.realtime_running = False
    st.session_state.current_tab = "Overview"
    st.session_state.selected_company = None
    st.session_state.portfolio_manager = None


def load_simulation_data():
    """Load simulation data and initialize components"""
    simulation = st.session_state.simulation
    
    # Check if already loaded
    if st.session_state.loaded:
        return True
    
    # Load company data
    with st.spinner("Loading company data..."):
        success = simulation.load_company_data()
        if not success:
            st.error("Failed to load company data. Please check the file path.")
            return False
    
    # Initialize simulation
    with st.spinner("Initializing market simulation..."):
        success = simulation.initialize_simulation(historical_days=365)
        if not success:
            st.error("Failed to initialize simulation. Please check the logs.")
            return False
    
    # Initialize portfolio manager
    st.session_state.portfolio_manager = PortfolioManager(simulation)
    
    # Create a demo portfolio
    if st.session_state.portfolio_manager:
        st.session_state.portfolio_manager.create_portfolio("Demo Portfolio")
    
    st.session_state.loaded = True
    return True


def render_overview_tab():
    """Render the market overview tab"""
    st.header("NEPSE Market Overview")
    
    simulation = st.session_state.simulation
    
    # Market status
    market_status = simulation.get_market_status()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Mode", market_status.get('mode', 'Historical'))
        if 'latest_date' in market_status:
            st.metric("Latest Date", market_status.get('latest_date'))
    
    with col2:
        st.metric("Total Companies", market_status.get('companies', 0))
        
    with col3:
        st.metric("Trading Days", market_status.get('trading_days', 0))
      # Run simplified market analysis if not done already
    if 'analysis_results' not in st.session_state:
        with st.spinner("Running market analysis..."):
            # Use simple_analyze directly
            try:
                from dashboard.simple_analyze import simple_market_analysis
                if hasattr(simulation, 'data_generator') and simulation.data_generator.stock_data is not None:
                    st.session_state.analysis_results = simple_market_analysis(
                        simulation.data_generator.stock_data, 
                        simulation.company_info
                    )
                else:
                    st.error("No market data available for analysis")
                    st.session_state.analysis_results = None
            except Exception as e:
                st.error(f"Error analyzing market data: {str(e)}")
                st.session_state.analysis_results = None
    
    analysis = st.session_state.analysis_results
    
    # Market Summary
    if analysis and 'market_breadth' in analysis:
        st.subheader("Market Breadth")
        breadth = analysis['market_breadth']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Advancing", breadth.get('advances', 0))
        with col2:
            st.metric("Declining", breadth.get('declines', 0))
        with col3:
            st.metric("Unchanged", breadth.get('unchanged', 0))
      # Sector Performance
    if analysis and 'sector_performance' in analysis:
        st.subheader("Sector Performance")
        sector_perf = analysis['sector_performance']
        
        # Create sector performance chart
        try:
            fig = plot_sector_performance(sector_perf)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error plotting sector performance: {str(e)}")
            
            # Show as simple table instead
            sector_df = pd.DataFrame({
                'Sector': list(sector_perf.keys()),
                'Performance (%)': list(sector_perf.values())
            }).sort_values('Performance (%)', ascending=False)
            
            st.dataframe(sector_df)
        st.plotly_chart(fig, use_container_width=True)
      # Top Gainers and Losers
    if analysis and 'top_gainers' in analysis and 'top_losers' in analysis:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top Gainers")
            gainers_df = pd.DataFrame({
                'Symbol': list(analysis['top_gainers'].keys()),
                'Return (%)': list(analysis['top_gainers'].values())
            })
            if not gainers_df.empty:
                gainers_df['Return (%)'] = gainers_df['Return (%)'].apply(lambda x: f"{x:.2f}%")
                st.dataframe(gainers_df, use_container_width=True)
        
        with col2:
            st.subheader("Top Losers")
            losers_df = pd.DataFrame({
                'Symbol': list(analysis['top_losers'].keys()),
                'Return (%)': list(analysis['top_losers'].values())
            })
            if not losers_df.empty:
                losers_df['Return (%)'] = losers_df['Return (%)'].apply(lambda x: f"{x:.2f}%")
                st.dataframe(losers_df, use_container_width=True)
      # Volume Leaders 
    if analysis and 'volume_leaders' in analysis:
        st.subheader("Volume Leaders")
        volume_df = pd.DataFrame({
            'Symbol': list(analysis['volume_leaders'].keys()),
            'Volume': list(analysis['volume_leaders'].values())
        })
        if not volume_df.empty:
            volume_df['Volume'] = volume_df['Volume'].apply(lambda x: f"{x:,.0f}")
            st.dataframe(volume_df, use_container_width=True)
        fig.add_vline(x=30, line_dash="dash", line_color="green",
                      annotation_text="Oversold (30)", annotation_position="top")
        fig.add_vline(x=70, line_dash="dash", line_color="red",
                      annotation_text="Overbought (70)", annotation_position="top")
        
        st.plotly_chart(fig, use_container_width=True)


def render_stocks_tab():
    """Render the individual stocks tab"""
    st.header("Stock Analysis")
    
    simulation = st.session_state.simulation
    
    # Get company list for selection
    companies = simulation.get_company_list(with_details=True)
    
    # Create a selectbox for company selection
    company_options = [(f"{symbol} - {info['name']}") for symbol, info in companies.items()]
    selected_option = st.selectbox("Select a company", company_options, index=0)
    
    # Extract symbol from selected option
    selected_symbol = selected_option.split(" - ")[0]
    st.session_state.selected_company = selected_symbol
    
    # Get company details
    company_info = companies.get(selected_symbol, {})
    
    # Display company info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sector", company_info.get('sector', 'Unknown'))
        
    with col2:
        if company_info.get('latest_price'):
            st.metric("Latest Price", f"NPR {company_info['latest_price']:.2f}")
            
    with col3:
        if company_info.get('pe_ratio'):
            st.metric("P/E Ratio", f"{company_info['pe_ratio']:.2f}")
    
    # Get stock data for the selected company
    stock_data = simulation.get_stock_data(selected_symbol)
    
    if stock_data is not None:
        # Date range selection
        st.subheader("Historical Data")
        
        # Get min and max dates
        min_date = stock_data.index.min().date()
        max_date = stock_data.index.max().date()
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
        with col2:
            end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
        
        # Filter data by date range
        filtered_data = stock_data.loc[(stock_data.index >= pd.Timestamp(start_date)) & 
                                       (stock_data.index <= pd.Timestamp(end_date))]
        
        # Display interactive chart
        chart_options = st.multiselect(
            "Chart Indicators",
            ["Volume", "RSI", "Bollinger Bands", "MACD"],
            default=["Volume"]
        )
        
        include_volume = "Volume" in chart_options
        include_rsi = "RSI" in chart_options
        include_bb = "Bollinger Bands" in chart_options
        include_macd = "MACD" in chart_options
        
        fig = plot_interactive_candlestick(
            filtered_data, 
            title=f"{selected_symbol} - Stock Price",
            include_volume=include_volume,
            include_rsi=include_rsi,
            include_bb=include_bb,
            include_macd=include_macd
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display data table
        if st.checkbox("Show Data Table"):
            st.dataframe(filtered_data, use_container_width=True)
    else:
        st.warning(f"No data available for {selected_symbol}")


def render_portfolio_tab():
    """Render the portfolio management tab"""
    st.header("Portfolio Management")
    
    portfolio_manager = st.session_state.portfolio_manager
    if not portfolio_manager:
        st.error("Portfolio manager not initialized")
        return
    
    # Portfolio selection or creation
    portfolio_names = list(portfolio_manager.portfolios.keys())
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if portfolio_names:
            selected_portfolio = st.selectbox("Select Portfolio", portfolio_names)
        else:
            st.info("No portfolios found")
            selected_portfolio = None
    
    with col2:
        create_new = st.button("Create New Portfolio")
    
    if create_new:
        with st.form("new_portfolio_form"):
            portfolio_name = st.text_input("Portfolio Name")
            initial_balance = st.number_input("Initial Balance (NPR)", value=1000000.0, step=10000.0)
            submit = st.form_submit_button("Create")
            
            if submit and portfolio_name:
                portfolio_manager.create_portfolio(portfolio_name, initial_balance)
                st.success(f"Portfolio '{portfolio_name}' created!")
                st.experimental_rerun()
    
    # Display selected portfolio
    if selected_portfolio:
        portfolio = portfolio_manager.get_portfolio(selected_portfolio)
        
        # Portfolio overview
        st.subheader("Portfolio Overview")
        
        latest_value = portfolio.get('latest_value', {})
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Cash", f"NPR {portfolio['cash']:,.2f}")
        
        with col2:
            holdings_value = latest_value.get('holdings', 0)
            st.metric("Holdings Value", f"NPR {holdings_value:,.2f}")
        
        with col3:
            total_value = latest_value.get('total', portfolio['cash'])
            st.metric("Total Value", f"NPR {total_value:,.2f}")
        
        with col4:
            if 'created_at' in portfolio:
                st.metric("Created On", portfolio['created_at'][:10])
        
        # Performance chart
        full_portfolio = portfolio_manager.get_portfolio(selected_portfolio, with_history=True)
        if 'history' in full_portfolio and len(full_portfolio['history']) > 1:
            history_df = pd.DataFrame(full_portfolio['history'])
            history_df['date'] = pd.to_datetime(history_df['date'])
            history_df = history_df.set_index('date')
            
            fig = plot_portfolio_performance(history_df, title=f"Portfolio Performance - {selected_portfolio}")
            st.plotly_chart(fig, use_container_width=True)
        
        # Holdings table
        st.subheader("Current Holdings")
        
        if portfolio['holdings']:
            holdings_data = []
            for symbol, holding in portfolio['holdings'].items():
                holdings_data.append({
                    'Symbol': symbol,
                    'Shares': holding['shares'],
                    'Average Cost': f"NPR {holding['average_price']:,.2f}",
                    'Current Price': f"NPR {holding.get('current_price', 0):,.2f}",
                    'Market Value': f"NPR {holding.get('current_value', 0):,.2f}",
                    'Profit/Loss': f"NPR {holding.get('profit_loss', 0):,.2f}",
                    'Return': f"{holding.get('profit_loss_pct', 0):,.2f}%"
                })
            
            st.dataframe(pd.DataFrame(holdings_data), use_container_width=True)
        else:
            st.info("No holdings in this portfolio")
        
        # Trading interface
        st.subheader("Trade Stocks")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Buy Stocks")
            
            with st.form("buy_form"):
                # Get company list for selection
                companies = st.session_state.simulation.get_company_list(with_details=True)
                company_options = [(f"{symbol} - {info['name']}") for symbol, info in companies.items()]
                
                buy_company = st.selectbox("Select Company", company_options, key="buy_company")
                buy_symbol = buy_company.split(" - ")[0]
                buy_quantity = st.number_input("Quantity", min_value=1, value=100, step=10, key="buy_quantity")
                
                # Get current price
                current_price = companies.get(buy_symbol, {}).get('latest_price', 0)
                st.text(f"Current Price: NPR {current_price:,.2f}")
                st.text(f"Total Cost: NPR {current_price * buy_quantity:,.2f}")
                
                buy_submit = st.form_submit_button("Buy")
                
                if buy_submit:
                    result = portfolio_manager.buy_stock(selected_portfolio, buy_symbol, buy_quantity)
                    if result:
                        st.success(f"Bought {buy_quantity} shares of {buy_symbol}")
                        st.experimental_rerun()
                    else:
                        st.error("Transaction failed. Check portfolio balance or stock availability.")
        
        with col2:
            st.subheader("Sell Stocks")
            
            with st.form("sell_form"):
                # Only show holdings
                holding_options = [(f"{symbol} - {holding['shares']} shares") 
                                 for symbol, holding in portfolio['holdings'].items()]
                
                if holding_options:
                    sell_option = st.selectbox("Select Holding", holding_options, key="sell_holding")
                    sell_symbol = sell_option.split(" - ")[0]
                    
                    max_shares = portfolio['holdings'][sell_symbol]['shares']
                    sell_quantity = st.number_input("Quantity", min_value=1, max_value=max_shares, 
                                                    value=min(100, max_shares), step=10, key="sell_quantity")
                    
                    # Get current price
                    current_price = portfolio['holdings'][sell_symbol].get('current_price', 0)
                    st.text(f"Current Price: NPR {current_price:,.2f}")
                    st.text(f"Total Value: NPR {current_price * sell_quantity:,.2f}")
                    
                    sell_submit = st.form_submit_button("Sell")
                    
                    if sell_submit:
                        result = portfolio_manager.sell_stock(selected_portfolio, sell_symbol, sell_quantity)
                        if result:
                            st.success(f"Sold {sell_quantity} shares of {sell_symbol}")
                            st.experimental_rerun()
                        else:
                            st.error("Transaction failed.")
                else:
                    st.info("No holdings to sell")
                    st.form_submit_button("Sell", disabled=True)
        
        # Transaction history
        if st.checkbox("Show Transaction History"):
            st.subheader("Transaction History")
            
            full_portfolio = portfolio_manager.get_portfolio(selected_portfolio, with_history=True)
            if 'transactions' in full_portfolio and full_portfolio['transactions']:
                transactions_df = pd.DataFrame(full_portfolio['transactions'])
                # Sort by timestamp in descending order
                transactions_df = transactions_df.sort_values('timestamp', ascending=False)
                st.dataframe(transactions_df, use_container_width=True)
            else:
                st.info("No transactions recorded")


def render_analytics_tab():
    """Render the advanced analytics tab"""
    st.header("Advanced Analytics")
    
    simulation = st.session_state.simulation
    
    # Analytics type selection
    analytics_type = st.selectbox(
        "Select Analytics Type", 
        ["Sector Analysis", "Circuit Breakers", "Volume Analysis", "RSI Screening"]
    )
    
    if analytics_type == "Sector Analysis":
        st.subheader("Sector Analysis")
        
        # Get sector list
        sectors = simulation.get_sector_list()
        
        # Show sector distribution
        fig = px.pie(
            values=list(sectors.values()),
            names=list(sectors.keys()),
            title="Companies by Sector",
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Sector performance
        if 'analysis_results' in st.session_state and 'sector_performance' in st.session_state.analysis_results:
            sector_perf = st.session_state.analysis_results['sector_performance']
            
            # Show sector performance bar chart
            fig = plot_sector_performance(sector_perf, title="Sector Performance")
            st.plotly_chart(fig, use_container_width=True)
        
    elif analytics_type == "Circuit Breakers":
        st.subheader("Circuit Breaker Analysis")
        
        if 'analysis_results' in st.session_state and 'circuit_breakers' in st.session_state.analysis_results:
            circuit_data = st.session_state.analysis_results['circuit_breakers']
            
            # Show circuit breaker stats
            if 'upper_circuit_counts' in st.session_state.analysis_results and 'lower_circuit_counts' in st.session_state.analysis_results:
                upper = st.session_state.analysis_results['upper_circuit_counts']
                lower = st.session_state.analysis_results['lower_circuit_counts']
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Upper Circuit Events", sum(upper.values()))
                    st.metric("Companies with Upper Circuit", len(upper))
                
                with col2:
                    st.metric("Lower Circuit Events", sum(lower.values()))
                    st.metric("Companies with Lower Circuit", len(lower))
                
                # Plot circuit breaker events
                fig = plot_circuit_breakers(circuit_data, title="Circuit Breaker Events")
                st.plotly_chart(fig, use_container_width=True)
                
                # Show companies with most circuit breakers
                st.subheader("Companies with Most Circuit Breakers")
                
                # Combine upper and lower circuit counts
                all_circuits = {}
                for symbol, count in upper.items():
                    all_circuits[symbol] = {'symbol': symbol, 'upper': count, 'lower': 0}
                
                for symbol, count in lower.items():
                    if symbol in all_circuits:
                        all_circuits[symbol]['lower'] = count
                    else:
                        all_circuits[symbol] = {'symbol': symbol, 'upper': 0, 'lower': count}
                
                # Convert to dataframe
                circuit_df = pd.DataFrame(list(all_circuits.values()))
                circuit_df['total'] = circuit_df['upper'] + circuit_df['lower']
                circuit_df = circuit_df.sort_values('total', ascending=False).head(10)
                
                # Display table
                st.dataframe(circuit_df[['symbol', 'upper', 'lower', 'total']], use_container_width=True)
        
    elif analytics_type == "Volume Analysis":
        st.subheader("Volume Analysis")
        
        # Date range selection
        stock_data = simulation.get_stock_data()
        if stock_data is not None:
            # Get min and max dates
            min_date = stock_data.index.get_level_values(0).min().date()
            max_date = stock_data.index.get_level_values(0).max().date()
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date, key="vol_start")
            with col2:
                end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date, key="vol_end")
            
            # Filter data by date range
            idx = pd.IndexSlice
            filtered_data = stock_data.loc[idx[pd.Timestamp(start_date):pd.Timestamp(end_date), :], :]
            
            # Top 10 companies by volume
            st.subheader("Top Companies by Trading Volume")
            
            # Calculate total volume by company
            volume_by_company = filtered_data.groupby(level=1)['volume'].sum().sort_values(ascending=False)
            top_10_volume = volume_by_company.head(10)
            
            # Plot bar chart
            fig = px.bar(
                x=top_10_volume.index,
                y=top_10_volume.values,
                labels={'x': 'Company', 'y': 'Total Volume'},
                title="Top 10 Companies by Trading Volume"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Volume heatmap for top companies
            st.subheader("Volume Heatmap for Top Companies")
            
            # Prepare data for heatmap
            top_companies = volume_by_company.head(10).index.tolist()
            
            # Create pivot table with dates and companies
            volume_pivot = filtered_data.loc[idx[:, top_companies], 'volume'].unstack(level=1)
            
            fig = plot_volume_heatmap(volume_pivot, top_companies, title="Trading Volume Heatmap")
            st.plotly_chart(fig, use_container_width=True)
    
    elif analytics_type == "RSI Screening":
        st.subheader("RSI Screening")
        
        if 'analysis_results' in st.session_state and 'rsi' in st.session_state.analysis_results:
            rsi_values = st.session_state.analysis_results['rsi']
            
            # RSI range selection
            col1, col2 = st.columns(2)
            with col1:
                min_rsi = st.slider("Minimum RSI", min_value=0, max_value=100, value=0)
            with col2:
                max_rsi = st.slider("Maximum RSI", min_value=0, max_value=100, value=100)
            
            # Filter companies by RSI range
            filtered_companies = {}
            for symbol, rsi in rsi_values.items():
                if min_rsi <= rsi <= max_rsi:
                    filtered_companies[symbol] = rsi
            
            # Sort by RSI
            sorted_companies = sorted(filtered_companies.items(), key=lambda x: x[1])
            
            # Show filtered companies
            st.subheader(f"Companies with RSI between {min_rsi} and {max_rsi}")
            st.text(f"Found {len(sorted_companies)} companies")
            
            if sorted_companies:
                # Create dataframe for display
                company_info = simulation.get_company_list(with_details=True)
                
                data = []
                for symbol, rsi in sorted_companies:
                    name = company_info.get(symbol, {}).get('name', 'Unknown')
                    sector = company_info.get(symbol, {}).get('sector', 'Unknown')
                    price = company_info.get(symbol, {}).get('latest_price', 0)
                    
                    data.append({
                        'Symbol': symbol,
                        'Company': name,
                        'Sector': sector,
                        'Latest Price': price,
                        'RSI': rsi
                    })
                
                # Display as dataframe
                st.dataframe(pd.DataFrame(data), use_container_width=True)


def render_simulation_tab():
    """Render the simulation controls tab"""
    st.header("Simulation Controls")
    
    simulation = st.session_state.simulation
    
    # Display current simulation state
    market_status = simulation.get_market_status()
    st.subheader("Current Simulation Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Mode", market_status.get('mode', 'Historical'))
    
    with col2:
        latest_date = market_status.get('latest_date', 'Not started')
        st.metric("Current Date", latest_date)
    
    with col3:
        is_running = st.session_state.realtime_running
        st.metric("Simulation Running", "Yes" if is_running else "No")
    
    # Historical simulation controls
    st.subheader("Historical Simulation")
    
    with st.form("historical_simulation"):
        days = st.number_input("Number of Trading Days", min_value=1, max_value=252, value=30)
        save_data = st.checkbox("Save Generated Data", value=True)
        submit_historical = st.form_submit_button("Run Historical Simulation")
    
    if submit_historical:
        with st.spinner(f"Running historical simulation for {days} days..."):
            result = simulation.run_historical_simulation(days, save_data)
            
            if result is not None:
                st.success(f"Historical simulation completed for {days} trading days")
                # Refresh analysis results
                st.session_state.analysis_results = simulation.run_market_analysis()
                st.experimental_rerun()
            else:
                st.error("Failed to run historical simulation")
    
    # Real-time simulation controls
    st.subheader("Real-time Simulation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        interval_seconds = st.number_input("Update Interval (seconds)", min_value=1, max_value=30, value=5)
    
    with col2:
        volatility = st.slider("Market Volatility", min_value=0.5, max_value=3.0, value=1.0, step=0.1)
    
    with col3:
        if not st.session_state.realtime_running:
            start_btn = st.button("Start Real-time Simulation")
            if start_btn:
                # Register callbacks
                def price_update_callback(data):
                    # This function will be called when prices are updated
                    pass
                
                def market_close_callback(data):
                    # This function will be called when market closes
                    st.session_state.realtime_running = False
                    # Refresh analysis results
                    st.session_state.analysis_results = simulation.run_market_analysis()
                
                simulation.register_callback('price_update', price_update_callback)
                simulation.register_callback('market_close', market_close_callback)
                
                # Start simulation
                success = simulation.start_realtime_simulation(interval_seconds, volatility)
                if success:
                    st.session_state.realtime_running = True
                    st.success("Real-time simulation started")
                    st.experimental_rerun()
                else:
                    st.error("Failed to start real-time simulation")
        else:
            stop_btn = st.button("Stop Real-time Simulation")
            if stop_btn:
                success = simulation.stop_realtime_simulation()
                if success:
                    st.session_state.realtime_running = False
                    st.success("Real-time simulation stopped")
                    st.experimental_rerun()
                else:
                    st.error("Failed to stop real-time simulation")
    
    if st.session_state.realtime_running:
        st.info("Real-time simulation is running. The market data is being updated automatically.")
        
        # Show real-time market status
        if simulation.mode == "realtime" and simulation.realtime_simulator:
            status = simulation.realtime_simulator.get_market_status()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Time Elapsed", f"{status['minute']} min / {status['total_minutes']} min")
                progress = status['time_elapsed_pct'] / 100
                st.progress(progress)
            
            with col2:
                st.metric("Advancing", status['advancing'])
            
            with col3:
                st.metric("Declining", status['declining'])
            
            with col4:
                st.metric("Total Volume", f"{status['total_volume']:,}")
    
    # Data management
    st.subheader("Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        save_btn = st.button("Save Current Data")
        if save_btn:
            success_data = simulation.save_historical_data()
            success_info = simulation.save_company_info()
            
            if success_data and success_info:
                st.success("Data saved successfully")
            else:
                st.error("Error saving data")
    
    with col2:
        load_btn = st.button("Reload Simulation")
        if load_btn:
            st.session_state.loaded = False
            success = load_simulation_data()
            if success:
                st.success("Simulation reloaded successfully")
                # Refresh analysis results
                st.session_state.analysis_results = simulation.run_market_analysis()
                st.experimental_rerun()
            else:
                st.error("Failed to reload simulation")


def main():
    # Set page config
    st.set_page_config(
        page_title="NEPSEZEN - NEPSE Simulator",
        page_icon="📈",
        layout="wide"
    )
    
    # Display title
    st.title("NEPSEZEN - Nepal Stock Exchange Simulator")
    
    # Ensure simulation is loaded
    if not st.session_state.loaded:
        load_simulation_data()
    
    # Main tabs
    tabs = ["Overview", "Stocks", "Portfolio", "Analytics", "Simulation"]
    selected_tab = st.sidebar.selectbox("Navigation", tabs, index=tabs.index(st.session_state.current_tab))
    st.session_state.current_tab = selected_tab
    
    # Render selected tab
    if selected_tab == "Overview":
        render_overview_tab()
    elif selected_tab == "Stocks":
        render_stocks_tab()
    elif selected_tab == "Portfolio":
        render_portfolio_tab()
    elif selected_tab == "Analytics":
        render_analytics_tab()
    elif selected_tab == "Simulation":
        render_simulation_tab()
    
    # Sidebar - About
    st.sidebar.header("About NEPSEZEN")
    st.sidebar.info(
        "NEPSEZEN is a full-featured stock market simulation and analytics platform "
        "tailored for the Nepal Stock Exchange (NEPSE). It provides realistic "
        "market simulation, technical analysis, interactive charts, and portfolio "
        "management capabilities."
    )
    
    # Sidebar - Documentation links
    st.sidebar.header("Documentation")
    if st.sidebar.button("View README"):
        st.sidebar.markdown("README.md contents would open here")
    
    if st.sidebar.button("Developer Notes"):
        st.sidebar.markdown("Developer notes would open here")
    
    # Sidebar - Version info
    st.sidebar.header("Version Info")
    st.sidebar.text("NEPSEZEN v1.0.0")
    st.sidebar.text(f"Last updated: {datetime.now().strftime('%Y-%m-%d')}")


if __name__ == "__main__":
    main()
