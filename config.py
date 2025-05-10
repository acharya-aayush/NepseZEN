"""
NEPSEZEN - Nepal Stock Exchange Simulator
Configuration Settings Module
"""

import os
from pathlib import Path

# Path configurations
BASE_DIR = Path(__file__).parent
DATA_DIR = os.path.join(BASE_DIR, 'data')
COMPANIES_DATA_FILE = os.path.join(DATA_DIR, 'companies.json')
HISTORICAL_DATA_DIR = os.path.join(DATA_DIR, 'historical')

# Simulation configurations
DEFAULT_SIMULATION_DAYS = 30
TRADING_DAYS_PER_YEAR = 252  # Number of trading days in a year
TRADING_HOURS = {
    'start': '10:00',  # Market opens at 10:00 AM
    'end': '15:00'     # Market closes at 3:00 PM
}

# Market parameters
MAX_DAILY_PRICE_CHANGE = 0.1  # Maximum 10% daily change by default
CIRCUIT_BREAKER_THRESHOLD = {
    'upper': 0.1,      # +10% upper circuit
    'lower': -0.1      # -10% lower circuit
}

# Technical indicators parameters
RSI_PERIOD = 14  # Default period for RSI calculation
RSI_OVERBOUGHT = 70  # RSI threshold for overbought condition
RSI_OVERSOLD = 30  # RSI threshold for oversold condition

# Market events probabilities 
MARKET_EVENT_PROBABILITY = 0.2  # 20% chance of a market event each day
SECTOR_EVENT_PROBABILITY = 0.15  # 15% chance of a sector-specific event each day
COMPANY_EVENT_PROBABILITY = 0.05  # 5% chance of a company-specific event

# Market event impact levels
EVENT_IMPACT = {
    'low': 0.01,       # 1% impact
    'medium': 0.03,    # 3% impact
    'high': 0.05       # 5% impact
}

# Dashboard settings
DASHBOARD_REFRESH_RATE = 5  # Refresh dashboard every 5 seconds
DEFAULT_CHART_HEIGHT = 600
DEFAULT_CHART_WIDTH = 1000

# Portfolio simulation settings
INITIAL_PORTFOLIO_BALANCE = 1000000  # Initial balance of NPR 1,000,000
TRANSACTION_FEE_PERCENTAGE = 0.005   # 0.5% transaction fee

# Future API integration settings
API_KEYS = {
    'future_nepse_api': '',  # Placeholder for future API key
}

# Database settings (for future implementation)
DATABASE_CONFIG = {
    'type': 'file',  # Options: 'file', 'mongodb', 'sql'
    'connection_string': '',
}
