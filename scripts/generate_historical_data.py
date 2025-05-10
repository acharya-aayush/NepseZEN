"""
Script to generate historical data for the NEPSEZEN simulator

This script uses the data_gen module to create historical stock data
for the companies in companies.json
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator.data_gen import DataGenerator
import config

def main():
    """Main function to generate historical data"""
    print("Generating historical data for NEPSEZEN...")
    
    # Load company data
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    companies_file = os.path.join(data_dir, 'companies.json')
    
    with open(companies_file, 'r') as f:
        companies_data = json.load(f)
    
    print(f"Loaded {len(companies_data)} companies from {companies_file}")
    
    # Generate data for different time periods
    periods = [
        {'days': 30, 'name': '1month'},
        {'days': 90, 'name': '3months'},
        {'days': 180, 'name': '6months'},
        {'days': 365, 'name': '1year'}
    ]
    
    for period in periods:
        print(f"Generating {period['name']} data ({period['days']} days)...")
        
        # Create output directory if it doesn't exist
        historical_dir = os.path.join(data_dir, 'historical')
        os.makedirs(historical_dir, exist_ok=True)        # Initialize the data generator
        data_generator = DataGenerator(company_info=companies_data)
        
        # Initialize market factors with start date
        start_date = datetime.now() - timedelta(days=period['days'])
        data_generator.initialize_market_factors(
            start_date=start_date.strftime('%Y-%m-%d')
        )
          # Generate historical data
        # Use default volatility value or calculate from the max daily price change
        volatility = 0.015  # Default value
        if hasattr(config, 'MAX_DAILY_PRICE_CHANGE'):
            volatility = config.MAX_DAILY_PRICE_CHANGE / 2  # Conservative estimate
            
        historical_data = data_generator.generate_historical_data(
            num_days=period['days'],
            volatility=volatility
        )
          # Save to CSV
        output_file = os.path.join(historical_dir, f"{period['name']}.csv")
        
        # Reset index to include date and symbol columns
        if isinstance(historical_data.index, pd.MultiIndex):
            historical_data = historical_data.reset_index()
        
        # Convert date to string if it's datetime
        if 'date' in historical_data.columns and isinstance(historical_data['date'].iloc[0], (datetime, pd.Timestamp)):
            historical_data['date'] = historical_data['date'].dt.strftime('%Y-%m-%d')
            
        historical_data.to_csv(output_file, index=False)
        print(f"Saved {len(historical_data)} records to {output_file}")

if __name__ == "__main__":
    main()
