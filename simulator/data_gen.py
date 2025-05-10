"""
NEPSEZEN - Nepal Stock Exchange Simulator
Data Generation Module

This module generates historical and simulated market data for the NEPSE companies.
It creates realistic price movements based on market factors, sector trends, and company events.
"""

import pandas as pd
import numpy as np
import json
import os
import sys
import logging
from datetime import datetime, timedelta
import random
from collections import defaultdict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from utils.indicators import calculate_rsi

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataGenerator:
    """
    Class for generating realistic stock market data based on company information.
    """
    
    def __init__(self, company_info=None):
        """
        Initialize the DataGenerator with company information.
        
        Args:
            company_info (dict, optional): Dictionary of company information
        """
        self.company_info = company_info
        self.stock_data = None
        self.current_date = None
        self.market_sentiment = 0  # -1 to 1, where -1 is bearish, 1 is bullish
        self.sector_trends = {}
        self.company_events = {}
        self.trading_day_counter = 0
        
        # Initialize random seed for reproducibility
        random.seed(42)
        np.random.seed(42)
        
        logger.info("DataGenerator initialized")
    
    def load_company_info(self, file_path):
        """
        Load company information from a JSON file.
        
        Args:
            file_path (str): Path to the JSON file
            
        Returns:
            bool: True if loading successful, False otherwise
        """
        try:
            with open(file_path, 'r') as f:
                self.company_info = json.load(f)
            
            logger.info(f"Loaded information for {len(self.company_info)} companies from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading company information: {str(e)}")
            return False
    
    def initialize_market_factors(self, initial_sentiment=None, start_date=None):
        """
        Initialize market factors like overall sentiment and sector trends.
        
        Args:
            initial_sentiment (float, optional): Initial market sentiment (-1.0 to 1.0)
            start_date (str, optional): Start date for the simulation
        """
        # Set initial market sentiment
        if initial_sentiment is not None:
            self.market_sentiment = max(-1.0, min(1.0, initial_sentiment))  # Clamp between -1 and 1
        else:
            self.market_sentiment = random.uniform(-0.5, 0.5)
        
        # Set start date
        if start_date:
            self.current_date = pd.Timestamp(start_date)
        else:
            # Use a year ago as default start date
            self.current_date = pd.Timestamp.now() - pd.DateOffset(days=365)
        
        # Reset trading day counter
        self.trading_day_counter = 0
        
        # Initialize sector trends
        if self.company_info:
            sectors = set()
            for _, info in self.company_info.items():
                if 'sector' in info:
                    sectors.add(info['sector'])
            
            self.sector_trends = {
                sector: random.uniform(-0.5, 0.5) for sector in sectors
            }
        
        logger.info(f"Market factors initialized with sentiment {self.market_sentiment:.2f} "
                    f"and {len(self.sector_trends)} sector trends")
    
    def generate_historical_data(self, num_days=365, volatility=0.015):
        """
        Generate historical stock data for all companies.
        
        Args:
            num_days (int, optional): Number of trading days to generate, defaults to 365
            volatility (float, optional): Base volatility for price changes, defaults to 0.015
            
        Returns:
            pd.DataFrame: DataFrame with hierarchical index (date, symbol) and OHLCV columns
        """
        if not self.company_info:
            logger.error("No company information available. Load company info first.")
            return None
        
        # Initialize market factors if not done already
        if self.market_sentiment is None:
            self.initialize_market_factors()
        
        # Create a list to store all daily data
        all_data = []
        
        # Set first day as starting point
        current_date = self.current_date
        trading_days = 0
        
        logger.info(f"Generating {num_days} days of historical data starting from {current_date.strftime('%Y-%m-%d')}")
        
        # Generate data for each day
        while trading_days < num_days:
            # Skip weekends
            if current_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                current_date += timedelta(days=1)
                continue
            
            # Update market factors for the day
            self._update_market_factors()
            
            # Generate events occasionally
            if random.random() < config.MARKET_EVENT_PROBABILITY:
                self._generate_market_event()
            
            if random.random() < config.SECTOR_EVENT_PROBABILITY:
                self._generate_sector_event()
            
            # Generate data for each company
            daily_data = self._generate_daily_data(current_date, volatility)
            all_data.extend(daily_data)
            
            # Move to next day and increment counter
            current_date += timedelta(days=1)
            trading_days += 1
            self.trading_day_counter += 1
        
        # Update current date
        self.current_date = current_date
        
        # Create a DataFrame from all data
        columns = ['open', 'high', 'low', 'close', 'volume']
        df = pd.DataFrame(all_data, columns=['date', 'symbol'] + columns)
        
        # Set hierarchical index
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index(['date', 'symbol'])
        
        self.stock_data = df
        logger.info(f"Generated historical data with {len(df)} entries for {len(self.company_info)} companies")
        
        return df
    
    def _update_market_factors(self):
        """
        Update market sentiment and sector trends for the next trading day.
        """
        # Update overall market sentiment with some randomness
        sentiment_change = np.random.normal(0, 0.05)
        self.market_sentiment = max(-1.0, min(1.0, self.market_sentiment + sentiment_change))
        
        # Update sector trends
        for sector in self.sector_trends:
            # Sector trends are influenced by overall market but have their own momentum
            sector_change = np.random.normal(0, 0.08)
            market_influence = self.market_sentiment * 0.3
            self.sector_trends[sector] = max(-1.0, min(1.0, 
                                            self.sector_trends[sector] + sector_change + market_influence))
    
    def _generate_market_event(self):
        """
        Generate a random market-wide event that affects all stocks.
        """
        # Define possible market events
        events = [
            "Central Bank Changes Interest Rates",
            "Government Fiscal Policy Announcement",
            "Major Economic Data Release",
            "International Market Influence",
            "Foreign Investment Policy Change",
            "Currency Value Fluctuation"
        ]
        
        event = random.choice(events)
        impact = random.choice(list(config.EVENT_IMPACT.values()))
        if random.random() < 0.5:
            impact = -impact  # 50% chance of negative impact
        
        logger.info(f"Market Event: {event} with impact {impact:.2%}")
        
        # Adjust market sentiment based on event
        self.market_sentiment += impact * 2
        self.market_sentiment = max(-1.0, min(1.0, self.market_sentiment))
    
    def _generate_sector_event(self):
        """
        Generate a random event that affects a specific sector.
        """
        if not self.sector_trends:
            return
        
        # Choose a random sector
        sector = random.choice(list(self.sector_trends.keys()))
        
        # Define possible sector events
        events_by_sector = {
            "Commercial Bank": [
                "Banking Regulation Change",
                "Interest Rate Policy Shift",
                "Merger Announcement",
                "Credit Growth Report"
            ],
            "Life Insurance": [
                "Insurance Regulation Update",
                "Claim Settlement Rate Change",
                "New Insurance Product Launch",
                "Reinsurance Agreement"
            ],
            "Non-Life Insurance": [
                "Property Insurance Demand Change",
                "Natural Disaster Impact",
                "Regulatory Capital Requirements",
                "Insurance Premium Adjustment"
            ],
            "Finance": [
                "Microfinance Regulation",
                "Loan Portfolio Quality Report",
                "Credit Rating Change",
                "Liquidity Requirements"
            ],
            "Energy": [
                "Energy Policy Update",
                "Hydropower Project Announcement",
                "Electricity Demand Forecast",
                "Transmission Infrastructure Investment"
            ],
            "Aviation": [
                "Fuel Price Changes",
                "Airport Expansion Project",
                "Tourism Trend Impact",
                "Route Expansion Announcement"
            ],
            "Agriculture": [
                "Monsoon Season Forecast",
                "Crop Production Report",
                "Fertilizer Subsidy Change",
                "Agricultural Export Policy"
            ],
            "Construction": [
                "Infrastructure Development Plan",
                "Building Material Price Change",
                "Construction Permit Process Update",
                "Real Estate Market Report"
            ],
            "Manufacturing": [
                "Raw Material Price Fluctuation",
                "Export Incentives Change",
                "Labor Law Amendment",
                "Factory Output Report"
            ],
            "Telecommunications": [
                "Spectrum Allocation Decision",
                "Internet Penetration Report",
                "Telecom Tariff Regulation",
                "Network Infrastructure Investment"
            ],
            "Hospitality": [
                "Tourism Season Forecast",
                "Hotel Occupancy Rates",
                "International Tourism Policy",
                "Travel Advisory Change"
            ],
            "Conglomerate": [
                "Corporate Restructuring",
                "Diversification Strategy",
                "Holdings Adjustment",
                "Group Performance Report"
            ],
            "Investment Fund": [
                "Investment Strategy Update",
                "Fund Performance Report",
                "Asset Allocation Change",
                "Regulatory Compliance Update"
            ]
        }
        
        # Default events for sectors not explicitly defined
        default_events = [
            "Regulatory Change",
            "Industry Report Release",
            "Market Trend Shift",
            "Corporate Announcement"
        ]
        
        # Get events for the selected sector
        sector_events = events_by_sector.get(sector, default_events)
        event = random.choice(sector_events)
        
        # Determine impact
        impact = random.choice(list(config.EVENT_IMPACT.values()))
        if random.random() < 0.5:
            impact = -impact  # 50% chance of negative impact
        
        logger.info(f"Sector Event: {event} in {sector} sector with impact {impact:.2%}")
        
        # Adjust sector trend based on event
        self.sector_trends[sector] += impact * 3
        self.sector_trends[sector] = max(-1.0, min(1.0, self.sector_trends[sector]))
    
    def _generate_company_event(self, symbol):
        """
        Generate a random event for a specific company.
        
        Args:
            symbol (str): Company symbol
            
        Returns:
            float: Impact of the event on the company's stock price
        """
        # Define possible company events
        events = [
            "Quarterly Earnings Report",
            "Management Change",
            "New Product Launch",
            "Regulatory Action",
            "Legal Issue",
            "Dividend Announcement",
            "Merger or Acquisition Talks",
            "Insider Trading News",
            "Major Contract Gain/Loss",
            "Analyst Rating Change"
        ]
        
        event = random.choice(events)
        impact = random.choice(list(config.EVENT_IMPACT.values()))
        if random.random() < 0.6:  # 60% chance of positive impact for company-specific events
            impact = abs(impact)
        else:
            impact = -abs(impact)
        
        logger.debug(f"Company Event: {event} for {symbol} with impact {impact:.2%}")
        
        # Store event for potential UI display
        self.company_events[symbol] = {
            'event': event,
            'impact': impact,
            'day': self.trading_day_counter
        }
        
        return impact
    
    def _generate_daily_data(self, date, volatility):
        """
        Generate daily data for all companies for the given date.
        
        Args:
            date (datetime): Date to generate data for
            volatility (float): Base volatility for price changes
            
        Returns:
            list: List of daily data dictionaries for all companies
        """
        daily_data = []
        
        for symbol, info in self.company_info.items():
            # Get current price or use initial price
            prev_close = None
            
            if self.stock_data is not None:
                try:
                    # Try to get the previous close price for this company
                    prev_data = self.stock_data.xs(symbol, level=1).iloc[-1]
                    prev_close = prev_data['close']
                except (KeyError, IndexError):
                    prev_close = None
            
            if prev_close is None:
                # Use initial price from company info or a default value
                if 'price' in info and 'close' in info['price']:
                    prev_close = info['price']['close']
                else:
                    prev_close = random.uniform(500, 1500)  # Default price range
            
            # Calculate base price change factors
            company_volatility = volatility * random.uniform(0.7, 1.3)  # Vary volatility by company
            
            # Market factor: overall market sentiment
            market_factor = self.market_sentiment * 0.3  # Market sentiment has 30% influence
            
            # Sector factor: specific sector trend
            sector_factor = 0
            if 'sector' in info and info['sector'] in self.sector_trends:
                sector_factor = self.sector_trends[info['sector']] * 0.4  # Sector has 40% influence
            
            # Company factor: company-specific events and randomness
            company_factor = 0
            # 5% chance of company event
            if random.random() < config.COMPANY_EVENT_PROBABILITY:
                company_factor += self._generate_company_event(symbol)
            
            # Add randomness specific to the company
            company_factor += np.random.normal(0, company_volatility)
            
            # Circuit breaker check and combined daily change
            combined_factor = market_factor + sector_factor + company_factor
            
            # Apply circuit breaker logic if needed
            if combined_factor > config.CIRCUIT_BREAKER_THRESHOLD['upper']:
                combined_factor = config.CIRCUIT_BREAKER_THRESHOLD['upper']
                circuit_status = "Upper"
            elif combined_factor < config.CIRCUIT_BREAKER_THRESHOLD['lower']:
                combined_factor = config.CIRCUIT_BREAKER_THRESHOLD['lower']
                circuit_status = "Lower"
            else:
                circuit_status = "None"
            
            # Calculate new price
            daily_change = prev_close * combined_factor
            close_price = max(prev_close + daily_change, prev_close * 0.1)  # Ensure price doesn't go too low
            
            # Generate OHLC data
            price_range = max(close_price * company_volatility, 1)  # Ensure some price range
            open_price = prev_close * (1 + np.random.normal(0, company_volatility * 0.5))
            high_price = max(open_price, close_price) + abs(np.random.normal(0, price_range * 0.3))
            low_price = min(open_price, close_price) - abs(np.random.normal(0, price_range * 0.3))
            
            # Ensure high >= open/close >= low
            high_price = max(high_price, open_price, close_price)
            low_price = min(low_price, open_price, close_price)
            low_price = max(low_price, 0.1)  # Ensure price is positive
            
            # Generate trading volume
            base_volume = info.get('volume', 500000)  # Use provided volume or default
            volume_factor = 1.0
            
            # Higher volume on larger price moves
            volume_factor *= (1 + abs(combined_factor) * 5)
            
            # Higher volume on circuit breaker events
            if circuit_status != "None":
                volume_factor *= 1.5
            
            # Add randomness to volume
            volume_factor *= random.uniform(0.7, 1.3)
            
            # Calculate final volume
            volume = int(base_volume * volume_factor)
            
            # Create daily data record
            daily_record = {
                'date': date.strftime('%Y-%m-%d'),
                'symbol': symbol,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume
            }
            
            # Update company info with latest price and circuit status
            if self.company_info is not None and symbol in self.company_info:
                self.company_info[symbol]['price'] = {
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': close_price
                }
                self.company_info[symbol]['volume'] = volume
                self.company_info[symbol]['circuit_status'] = circuit_status
            
            daily_data.append(daily_record)
        
        return daily_data
    
    def save_historical_data(self, file_path):
        """
        Save generated historical data to HDF5 format.
        
        Args:
            file_path (str): Path to save the data file
            
        Returns:
            bool: True if saving successful, False otherwise
        """
        if self.stock_data is None:
            logger.error("No stock data available to save")
            return False
        
        try:
            self.stock_data.to_hdf(file_path, key='stock_data')
            logger.info(f"Historical data saved to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving historical data: {str(e)}")
            return False
    
    def load_historical_data(self, file_path):
        """
        Load historical data from HDF5 format.
        
        Args:
            file_path (str): Path to the data file
            
        Returns:
            bool: True if loading successful, False otherwise
        """
        try:
            self.stock_data = pd.read_hdf(file_path, key='stock_data')
            # Update current date to the last date in the data
            self.current_date = self.stock_data.index.get_level_values(0).max()
            logger.info(f"Historical data loaded from {file_path} up to {self.current_date}")
            return True
        except Exception as e:
            logger.error(f"Error loading historical data: {str(e)}")
            return False
    
    def save_company_info(self, file_path):
        """
        Save company information to a JSON file.
        
        Args:
            file_path (str): Path to save the JSON file
            
        Returns:
            bool: True if saving successful, False otherwise
        """
        if self.company_info is None:
            logger.error("No company information available to save")
            return False
        
        try:
            with open(file_path, 'w') as f:
                json.dump(self.company_info, f, indent=4)
            logger.info(f"Company information saved to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving company information: {str(e)}")
            return False
    
    def generate_next_day(self, volatility=0.015):
        """
        Generate data for the next trading day.
        
        Args:
            volatility (float, optional): Base volatility for price changes, defaults to 0.015
            
        Returns:
            pd.DataFrame: DataFrame with the next day's data
        """
        # Move to next trading day
        next_date = self.current_date + timedelta(days=1)
        while next_date.weekday() >= 5:  # Skip weekends
            next_date += timedelta(days=1)
        
        # Update market factors
        self._update_market_factors()
        
        # Generate events occasionally
        if random.random() < config.MARKET_EVENT_PROBABILITY:
            self._generate_market_event()
        
        if random.random() < config.SECTOR_EVENT_PROBABILITY:
            self._generate_sector_event()
        
        # Generate data for all companies
        daily_data = self._generate_daily_data(next_date, volatility)
        
        # Create a DataFrame from the data
        columns = ['open', 'high', 'low', 'close', 'volume']
        df = pd.DataFrame(daily_data, columns=['date', 'symbol'] + columns)
        
        # Set hierarchical index
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index(['date', 'symbol'])
        
        # Append to existing stock data if available
        if self.stock_data is not None:
            self.stock_data = pd.concat([self.stock_data, df])
        else:
            self.stock_data = df
        
        # Update current date and counter
        self.current_date = next_date
        self.trading_day_counter += 1
        
        logger.info(f"Generated next day data for {len(daily_data)} companies on {next_date.strftime('%Y-%m-%d')}")
        
        return df
    
    def generate_multiple_days(self, num_days=5, volatility=0.015):
        """
        Generate data for multiple trading days.
        
        Args:
            num_days (int, optional): Number of trading days to generate, defaults to 5
            volatility (float, optional): Base volatility for price changes, defaults to 0.015
            
        Returns:
            pd.DataFrame: DataFrame with data for all generated days
        """
        all_data = []
        
        for _ in range(num_days):
            next_day_data = self.generate_next_day(volatility)
            all_data.append(next_day_data)
        
        # Combine all days
        if all_data:
            combined_df = pd.concat(all_data)
            logger.info(f"Generated data for {num_days} trading days")
            return combined_df
        else:
            logger.warning("No data generated")
            return None
    
    def get_latest_company_data(self):
        """
        Get the latest data for all companies.
        
        Returns:
            dict: Dictionary with latest data for each company
        """
        if self.stock_data is None:
            logger.error("No stock data available")
            return {}
        
        latest_data = {}
        latest_date = self.stock_data.index.get_level_values(0).max()
        
        for symbol in self.company_info.keys():
            try:
                company_latest = self.stock_data.xs((latest_date, symbol))
                
                # Calculate RSI
                company_history = self.stock_data.xs(symbol, level=1)['close']
                rsi = calculate_rsi(company_history).iloc[-1]
                
                latest_data[symbol] = {
                    'date': latest_date.strftime('%Y-%m-%d'),
                    'open': float(company_latest['open']),
                    'high': float(company_latest['high']),
                    'low': float(company_latest['low']),
                    'close': float(company_latest['close']),
                    'volume': int(company_latest['volume']),
                    'rsi': float(rsi) if not np.isnan(rsi) else None
                }
            except:
                # Company might not have data for the latest date
                pass
        
        return latest_data


class RealTimeSimulator:
    """
    Class for simulating real-time market data during trading hours.
    """
    
    def __init__(self, stock_data=None, company_info=None):
        """
        Initialize the real-time simulator with stock data and company information.
        
        Args:
            stock_data (pd.DataFrame): DataFrame with historical stock data
            company_info (dict): Dictionary of company information
        """
        self.stock_data = stock_data
        self.company_info = company_info
        self.current_date = None
        self.market_open = False
        self.current_minute = 0
        self.trading_minutes = 300  # 5 hours = 300 minutes
        self.intraday_data = {}
        self.last_update_time = None
        
        # Initialize random seed
        random.seed(42)
        np.random.seed(42)
        
        logger.info("RealTimeSimulator initialized")
    
    def set_current_date(self, date=None):
        """
        Set the current date for simulation.
        
        Args:
            date (str or datetime, optional): Date to set, defaults to today
        """
        if date is None:
            self.current_date = pd.Timestamp.now().normalize()
        else:
            self.current_date = pd.Timestamp(date).normalize()
        
        # Reset intraday data
        self.intraday_data = {}
        self.current_minute = 0
        self.market_open = False
        
        logger.info(f"Current date set to {self.current_date.strftime('%Y-%m-%d')}")
    
    def open_market(self):
        """
        Open the market for trading.
        
        Returns:
            dict: Initial price data for all companies
        """
        self.market_open = True
        self.current_minute = 0
        self.last_update_time = pd.Timestamp.now()
        
        # Initialize intraday data with opening prices
        self.intraday_data = {}
        
        # Get previous day's closing prices or use company info
        for symbol, info in self.company_info.items():
            prev_close = None
            
            if self.stock_data is not None:
                try:
                    # Try to get the previous close price for this company
                    company_data = self.stock_data.xs(symbol, level=1)
                    prev_close = company_data.iloc[-1]['close']
                except (KeyError, IndexError):
                    prev_close = None
            
            if prev_close is None:
                # Use price from company info
                if 'price' in info and 'close' in info['price']:
                    prev_close = info['price']['close']
                else:
                    prev_close = random.uniform(500, 1500)
            
            # Generate opening price with small random change
            open_price = prev_close * (1 + np.random.normal(0, 0.01))
            
            # Initialize company's intraday data
            self.intraday_data[symbol] = {
                'open': open_price,
                'high': open_price,
                'low': open_price,
                'last': open_price,
                'volume': 0,
                'prices': [open_price],
                'times': [0],
                'volumes': [0],
                'prev_close': prev_close
            }
        
        logger.info(f"Market opened for {self.current_date.strftime('%Y-%m-%d')}")
        
        return {symbol: data['open'] for symbol, data in self.intraday_data.items()}
    
    def close_market(self):
        """
        Close the market and finalize daily data.
        
        Returns:
            pd.DataFrame: DataFrame with the day's final data
        """
        if not self.market_open:
            logger.warning("Market is not open")
            return None
        
        self.market_open = False
        
        # Create final daily data
        daily_data = []
        for symbol, data in self.intraday_data.items():
            daily_record = {
                'date': self.current_date.strftime('%Y-%m-%d'),
                'symbol': symbol,
                'open': data['open'],
                'high': data['high'],
                'low': data['low'],
                'close': data['last'],
                'volume': data['volume']
            }
            daily_data.append(daily_record)
            
            # Update company info with latest price
            if self.company_info is not None and symbol in self.company_info:
                self.company_info[symbol]['price'] = {
                    'open': data['open'],
                    'high': data['high'],
                    'low': data['low'],
                    'close': data['last']
                }
                self.company_info[symbol]['volume'] = data['volume']
        
        # Create a DataFrame from the data
        columns = ['open', 'high', 'low', 'close', 'volume']
        df = pd.DataFrame(daily_data, columns=['date', 'symbol'] + columns)
        
        # Set hierarchical index
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index(['date', 'symbol'])
        
        # Append to existing stock data if available
        if self.stock_data is not None:
            self.stock_data = pd.concat([self.stock_data, df])
        else:
            self.stock_data = df
        
        logger.info(f"Market closed for {self.current_date.strftime('%Y-%m-%d')}")
        
        return df
    
    def update_prices(self, minutes_elapsed=1, volatility_factor=1.0):
        """
        Update prices for all companies based on simulated market activity.
        
        Args:
            minutes_elapsed (int, optional): Number of minutes since last update, defaults to 1
            volatility_factor (float, optional): Factor to adjust volatility, defaults to 1.0
            
        Returns:
            dict: Updated price data for all companies
        """
        if not self.market_open:
            logger.error("Market is not open")
            return {}
        
        # Update current minute
        self.current_minute += minutes_elapsed
        if self.current_minute >= self.trading_minutes:
            logger.info("Trading hours completed")
            return self.close_market()
        
        self.last_update_time = pd.Timestamp.now()
        
        # Market-wide factors for this update
        market_factor = np.random.normal(0, 0.001 * volatility_factor)
        
        # Create sector factors
        sector_factors = {}
        for symbol, info in self.company_info.items():
            if 'sector' in info:
                sector = info['sector']
                if sector not in sector_factors:
                    sector_factors[sector] = np.random.normal(0, 0.002 * volatility_factor)
        
        # Update each company's price
        for symbol, data in self.intraday_data.items():
            # Get company sector
            sector = self.company_info.get(symbol, {}).get('sector', None)
            sector_factor = sector_factors.get(sector, 0) if sector else 0
            
            # Company-specific factor
            company_factor = np.random.normal(0, 0.003 * volatility_factor)
            
            # Combined price change factor
            change_factor = market_factor + sector_factor + company_factor
            
            # Calculate new price
            prev_price = data['last']
            new_price = prev_price * (1 + change_factor)
            
            # Generate random volume for this update
            base_volume = self.company_info.get(symbol, {}).get('volume', 1000)
            volume_increment = int(random.uniform(0, base_volume * 0.01 * minutes_elapsed))
            
            # Increase volume for larger price moves
            volume_increment *= (1 + abs(change_factor) * 20)
            
            # Update intraday data
            data['last'] = new_price
            data['high'] = max(data['high'], new_price)
            data['low'] = min(data['low'], new_price)
            data['volume'] += volume_increment
            
            # Add to price and volume history
            data['prices'].append(new_price)
            data['times'].append(self.current_minute)
            data['volumes'].append(volume_increment)
        
        logger.debug(f"Updated prices at minute {self.current_minute}")
        
        # Return current prices for all companies
        return {symbol: {
            'price': data['last'],
            'change': data['last'] - data['prev_close'],
            'change_pct': (data['last'] - data['prev_close']) / data['prev_close'] * 100,
            'high': data['high'],
            'low': data['low'],
            'volume': data['volume']
        } for symbol, data in self.intraday_data.items()}
    
    def get_intraday_data(self, symbol=None):
        """
        Get intraday data for a specific company or all companies.
        
        Args:
            symbol (str, optional): Company symbol, defaults to None (all companies)
            
        Returns:
            dict: Dictionary with intraday data
        """
        if not self.intraday_data:
            logger.warning("No intraday data available")
            return {}
        
        if symbol is not None:
            if symbol in self.intraday_data:
                return {symbol: self.intraday_data[symbol]}
            else:
                logger.warning(f"No data available for symbol {symbol}")
                return {}
        else:
            return self.intraday_data
    
    def get_market_status(self):
        """
        Get current market status information.
        
        Returns:
            dict: Dictionary with market status information
        """
        # Calculate market-wide metrics
        if not self.intraday_data:
            return {
                'date': self.current_date.strftime('%Y-%m-%d') if self.current_date else None,
                'is_open': self.market_open,
                'minute': self.current_minute,
                'total_minutes': self.trading_minutes,
                'time_elapsed_pct': 0,
                'advancing': 0,
                'declining': 0,
                'unchanged': 0,
                'total_volume': 0
            }
        
        # Count advancing and declining stocks
        advancing = 0
        declining = 0
        unchanged = 0
        total_volume = 0
        
        for symbol, data in self.intraday_data.items():
            price_change = data['last'] - data['prev_close']
            if price_change > 0:
                advancing += 1
            elif price_change < 0:
                declining += 1
            else:
                unchanged += 1
            
            total_volume += data['volume']
        
        return {
            'date': self.current_date.strftime('%Y-%m-%d') if self.current_date else None,
            'is_open': self.market_open,
            'minute': self.current_minute,
            'total_minutes': self.trading_minutes,
            'time_elapsed_pct': (self.current_minute / self.trading_minutes) * 100,
            'advancing': advancing,
            'declining': declining,
            'unchanged': unchanged,
            'total_volume': total_volume
        }
