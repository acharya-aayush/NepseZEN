"""
NEPSEZEN - Nepal Stock Exchange Simulator
Demo Script

This script demonstrates key features of the NEPSEZEN simulator.
"""

import os
import sys
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics.analyzer import MarketAnalyzer
from simulator.data_gen import DataGenerator
from utils.indicators import calculate_rsi, calculate_macd, calculate_bollinger_bands
from utils.visualizer import (
    plot_candlestick_chart, plot_sector_performance, plot_volume_heatmap,
    plot_interactive_candlestick
)
import config

def load_company_data():
    """Load company information"""
    companies_file = os.path.join(config.DATA_DIR, 'companies.json')
    if os.path.exists(companies_file):
        with open(companies_file, 'r') as f:
            import json
            return json.load(f)
    return {}

def load_historical_data(period='1month'):
    """Load historical market data"""
    file_path = os.path.join(config.DATA_DIR, 'historical', f'{period}.csv')
    if os.path.exists(file_path):
        data = pd.read_csv(file_path)
        # Add date and symbol columns if they don't exist
        if 'date' not in data.columns:
            # Create a date range starting from today and going back
            end_date = datetime.now()
            if period == '1month':
                days = 30
            elif period == '3months':
                days = 90
            elif period == '6months':
                days = 180
            else:  # 1year
                days = 365
            
            start_date = end_date - timedelta(days=days)
            # Create a date range excluding weekends
            date_range = []
            current = start_date
            while len(date_range) < len(data) // len(set(data.index)) if 'symbol' in data.columns else 10:
                if current.weekday() < 5:  # Monday to Friday
                    date_range.append(current)
                current += timedelta(days=1)
            
            # Add date column
            num_companies = len(data) // len(date_range)
            all_dates = []
            for d in date_range:
                all_dates.extend([d] * num_companies)
            data['date'] = all_dates[:len(data)]
        
        # Add symbol column if it doesn't exist
        if 'symbol' not in data.columns:
            # Create default symbols
            symbols = [f'STOCK{i+1}' for i in range(len(data) // len(set(data['date'])) if 'date' in data.columns else 10)]
            all_symbols = []
            # Repeat symbols for each date
            for _ in range(len(set(data['date'])) if 'date' in data.columns else 1):
                all_symbols.extend(symbols)
            data['symbol'] = all_symbols[:len(data)]
        
        # Convert date column to datetime
        data['date'] = pd.to_datetime(data['date'])
        return data
    return pd.DataFrame()

def demo_market_overview():
    """Demonstrate market overview analysis"""
    print("\n" + "=" * 50)
    print("DEMO: Market Overview Analysis")
    print("=" * 50)
    
    # Load data
    company_data = load_company_data()
    market_data = load_historical_data('1month')
    
    if market_data.empty:
        print("No historical data found. Please run the data generation script first.")
        return
    
    print(f"Loaded data for {len(company_data)} companies and {len(market_data)} market records.")
    
    # Set up market data for analyzer
    market_data_indexed = market_data.set_index(['date', 'symbol'])
    
    # Create analyzer
    analyzer = MarketAnalyzer(market_data_indexed, company_data)
    
    # Get latest date
    latest_date = market_data['date'].max()
    
    # Print some analysis
    print(f"\nMarket Summary for {latest_date.strftime('%Y-%m-%d')}:")
    summary = analyzer.get_market_summary()
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    print("\nTop 5 Gainers:")
    gainers = analyzer.get_top_gainers(5)
    for i, (symbol, pct) in enumerate(gainers.items(), 1):
        print(f"  {i}. {symbol}: {pct:.2f}%")
    
    print("\nTop 5 Losers:")
    losers = analyzer.get_top_losers(5)
    for i, (symbol, pct) in enumerate(losers.items(), 1):
        print(f"  {i}. {symbol}: {pct:.2f}%")
    
    print("\nTop 5 Volume Leaders:")
    leaders = analyzer.get_volume_leaders(5)
    for i, (symbol, vol) in enumerate(leaders.items(), 1):
        print(f"  {i}. {symbol}: {vol:,.0f}")
    
    return analyzer, market_data, company_data

def demo_technical_indicators():
    """Demonstrate technical indicators"""
    print("\n" + "=" * 50)
    print("DEMO: Technical Analysis Indicators")
    print("=" * 50)
    
    # Load data
    market_data = load_historical_data('3months')
    
    if market_data.empty:
        print("No historical data found. Please run the data generation script first.")
        return
    
    # Get data for a specific company
    symbol = "NABIL"  # Example company
    company_data = market_data[market_data['symbol'] == symbol].sort_values('date')
    
    if len(company_data) == 0:
        available_symbols = market_data['symbol'].unique()
        if len(available_symbols) > 0:
            symbol = available_symbols[0]
            company_data = market_data[market_data['symbol'] == symbol].sort_values('date')
            print(f"Symbol NABIL not found, using {symbol} instead.")
        else:
            print("No company data available.")
            return
    
    # Extract price series
    close_prices = company_data['close']
    
    print(f"\nTechnical Analysis for {symbol}:")
    
    # Calculate RSI
    rsi = calculate_rsi(close_prices)
    latest_rsi = rsi.iloc[-1] if not rsi.empty else None
    print(f"  Latest RSI: {latest_rsi:.2f}")
    
    # Calculate MACD
    macd_line, signal_line, histogram = calculate_macd(close_prices)
    latest_macd = macd_line.iloc[-1] if not macd_line.empty else None
    latest_signal = signal_line.iloc[-1] if not signal_line.empty else None
    print(f"  Latest MACD: {latest_macd:.4f}")
    print(f"  Latest MACD Signal: {latest_signal:.4f}")
    
    # Calculate Bollinger Bands
    upper, middle, lower = calculate_bollinger_bands(close_prices)
    latest_upper = upper.iloc[-1] if not upper.empty else None
    latest_middle = middle.iloc[-1] if not middle.empty else None
    latest_lower = lower.iloc[-1] if not lower.empty else None
    print(f"  Bollinger Bands:")
    print(f"    Upper: {latest_upper:.2f}")
    print(f"    Middle: {latest_middle:.2f}")
    print(f"    Lower: {latest_lower:.2f}")
    
    # Trading signals
    print("\nTrading Signals:")
    
    # RSI signals
    if latest_rsi < 30:
        print("  RSI indicates OVERSOLD condition - Potential BUY signal")
    elif latest_rsi > 70:
        print("  RSI indicates OVERBOUGHT condition - Potential SELL signal")
    else:
        print("  RSI is NEUTRAL")
    
    # MACD signals
    if latest_macd > latest_signal:
        print("  MACD is BULLISH (above signal line)")
    else:
        print("  MACD is BEARISH (below signal line)")
    
    # Bollinger Band signals
    current_price = close_prices.iloc[-1]
    if current_price < latest_lower:
        print("  Price is BELOW lower Bollinger Band - Potential oversold condition")
    elif current_price > latest_upper:
        print("  Price is ABOVE upper Bollinger Band - Potential overbought condition")
    else:
        print("  Price is WITHIN Bollinger Bands")
    
    return company_data

def demo_simulation():
    """Demonstrate market simulation"""
    print("\n" + "=" * 50)
    print("DEMO: Market Simulation")
    print("=" * 50)
    
    # Load company information
    company_data = load_company_data()
    
    if not company_data:
        print("No company data found. Unable to run simulation.")
        return
    
    # Initialize data generator
    data_gen = DataGenerator(company_info=company_data)
    
    # Initialize market factors
    data_gen.initialize_market_factors()
    
    # Simulate 5 trading days
    print("\nSimulating 5 trading days...\n")
    for i in range(5):
        # Generate next day's data
        day_data = data_gen.generate_next_day(volatility=0.015)
          # Show summary
        date = day_data.index.get_level_values('date')[0].strftime('%Y-%m-%d')
        advances = (day_data['close'] > day_data['open']).sum()
        declines = (day_data['close'] < day_data['open']).sum()
        unchanged = len(day_data) - advances - declines
        
        print(f"Day {i+1} ({date}):")
        print(f"  Advances: {advances}")
        print(f"  Declines: {declines}")
        print(f"  Unchanged: {unchanged}")
        
        # Calculate market return
        market_return = ((day_data['close'] - day_data['open']) / day_data['open']).mean() * 100
        print(f"  Market Return: {market_return:.2f}%")
          # Show top gainer
        day_data['return'] = (day_data['close'] - day_data['open']) / day_data['open'] * 100
        top_gainer_idx = day_data['return'].idxmax()
        top_gainer_symbol = top_gainer_idx[1] if isinstance(top_gainer_idx, tuple) else "Unknown"
        top_gainer_return = day_data['return'].max()
        print(f"  Top Gainer: {top_gainer_symbol} ({top_gainer_return:.2f}%)")
        
        # Show top loser
        top_loser_idx = day_data['return'].idxmin()
        top_loser_symbol = top_loser_idx[1] if isinstance(top_loser_idx, tuple) else "Unknown"
        top_loser_return = day_data['return'].min()
        print(f"  Top Loser: {top_loser_symbol} ({top_loser_return:.2f}%)")
        
        print()
        time.sleep(1)  # Pause for readability
    
    return data_gen

def demo_custom_scenario():
    """Demonstrate custom market scenario"""
    print("\n" + "=" * 50)
    print("DEMO: Custom Market Scenario")
    print("=" * 50)
    
    # Load company information
    company_data = load_company_data()
    
    if not company_data:
        print("No company data found. Unable to run custom scenario.")
        return
    
    # Initialize data generator with specific sentiment
    data_gen = DataGenerator(company_info=company_data)
    
    # Set initial market conditions
    print("\nScenario: Market Crash Followed by Recovery\n")
      # Day 1: Strong negative sentiment
    data_gen.initialize_market_factors(initial_sentiment=-0.8)
    day1_data = data_gen.generate_next_day(volatility=0.02)
    date1 = day1_data.index.get_level_values('date')[0].strftime('%Y-%m-%d')
    market_return1 = ((day1_data['close'] - day1_data['open']) / day1_data['open']).mean() * 100
    print(f"Day 1 ({date1}) - Market Crash:")
    print(f"  Market sentiment: Very Negative (-0.8)")
    print(f"  Market Return: {market_return1:.2f}%")
    print(f"  Advances: {(day1_data['close'] > day1_data['open']).sum()}")
    print(f"  Declines: {(day1_data['close'] < day1_data['open']).sum()}")
    print()
    time.sleep(1)
      # Day 2: Continued negative sentiment
    data_gen.market_sentiment = -0.5
    day2_data = data_gen.generate_next_day(volatility=0.025)
    date2 = day2_data.index.get_level_values('date')[0].strftime('%Y-%m-%d')
    market_return2 = ((day2_data['close'] - day2_data['open']) / day2_data['open']).mean() * 100
    print(f"Day 2 ({date2}) - Continued Decline:")
    print(f"  Market sentiment: Negative (-0.5)")
    print(f"  Market Return: {market_return2:.2f}%")
    print(f"  Advances: {(day2_data['close'] > day2_data['open']).sum()}")
    print(f"  Declines: {(day2_data['close'] < day2_data['open']).sum()}")
    print()
    time.sleep(1)
      # Day 3: Neutral sentiment (market stabilizes)
    data_gen.market_sentiment = 0.0
    day3_data = data_gen.generate_next_day(volatility=0.015)
    date3 = day3_data.index.get_level_values('date')[0].strftime('%Y-%m-%d')
    market_return3 = ((day3_data['close'] - day3_data['open']) / day3_data['open']).mean() * 100
    print(f"Day 3 ({date3}) - Market Stabilizes:")
    print(f"  Market sentiment: Neutral (0.0)")
    print(f"  Market Return: {market_return3:.2f}%")
    print(f"  Advances: {(day3_data['close'] > day3_data['open']).sum()}")
    print(f"  Declines: {(day3_data['close'] < day3_data['open']).sum()}")
    print()
    time.sleep(1)
      # Day 4: Positive sentiment begins (recovery)
    data_gen.market_sentiment = 0.4
    day4_data = data_gen.generate_next_day(volatility=0.018)
    date4 = day4_data.index.get_level_values('date')[0].strftime('%Y-%m-%d')
    market_return4 = ((day4_data['close'] - day4_data['open']) / day4_data['open']).mean() * 100
    print(f"Day 4 ({date4}) - Recovery Begins:")
    print(f"  Market sentiment: Positive (0.4)")
    print(f"  Market Return: {market_return4:.2f}%")
    print(f"  Advances: {(day4_data['close'] > day4_data['open']).sum()}")
    print(f"  Declines: {(day4_data['close'] < day4_data['open']).sum()}")
    print()
    time.sleep(1)
      # Day 5: Strong positive sentiment (strong recovery)
    data_gen.market_sentiment = 0.7
    day5_data = data_gen.generate_next_day(volatility=0.02)
    date5 = day5_data.index.get_level_values('date')[0].strftime('%Y-%m-%d')
    market_return5 = ((day5_data['close'] - day5_data['open']) / day5_data['open']).mean() * 100
    print(f"Day 5 ({date5}) - Strong Recovery:")
    print(f"  Market sentiment: Very Positive (0.7)")
    print(f"  Market Return: {market_return5:.2f}%")
    print(f"  Advances: {(day5_data['close'] > day5_data['open']).sum()}")
    print(f"  Declines: {(day5_data['close'] < day5_data['open']).sum()}")
    print()
    
    # Overall scenario summary
    print("Scenario Summary:")
    print(f"  5-Day Cumulative Return: {market_return1+market_return2+market_return3+market_return4+market_return5:.2f}%")
    print(f"  Crisis Depth: {min(market_return1, market_return2, market_return3, market_return4, market_return5):.2f}%")
    print(f"  Recovery High: {max(market_return1, market_return2, market_return3, market_return4, market_return5):.2f}%")
    
    return data_gen

def main():
    """Main demo function"""
    print("\n" + "=" * 50)
    print("NEPSEZEN - Nepal Stock Exchange Simulator Demo")
    print("=" * 50)
    
    print("\nThis demo showcases key features of the NEPSEZEN simulator.")
    
    # Check if data exists
    if not os.path.exists(os.path.join(config.DATA_DIR, 'historical', '1month.csv')):
        print("\nWARNING: Historical data files not found.")
        print("Please run the data generation script first:")
        print("  python -m scripts.generate_historical_data")
        return 1
    
    try:
        # Show menu
        while True:
            print("\n" + "-" * 50)
            print("DEMO MENU")
            print("-" * 50)
            print("1. Market Overview Analysis")
            print("2. Technical Indicators")
            print("3. Market Simulation")
            print("4. Custom Market Scenario")
            print("0. Exit Demo")
            
            choice = input("\nEnter choice (0-4): ")
            
            if choice == '0':
                break
            elif choice == '1':
                demo_market_overview()
            elif choice == '2':
                demo_technical_indicators()
            elif choice == '3':
                demo_simulation()
            elif choice == '4':
                demo_custom_scenario()
            else:
                print("Invalid choice. Please try again.")
        
        print("\nThank you for exploring NEPSEZEN!")
        return 0
            
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
        return 0
    except Exception as e:
        print(f"\nError running demo: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
