"""
NEPSEZEN - Nepal Stock Exchange Simulator
Main entry point for the NEPSEZEN application

This script provides a command-line interface to run the NEPSEZEN simulator
in different modes (dashboard, simulation, etc.)
"""

import os
import sys
import argparse
import logging
from datetime import datetime
import subprocess
import importlib.util

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("nepsezen.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        # Try to import key libraries
        import pandas as pd
        import numpy as np
        import matplotlib
        import plotly
        import streamlit
        
        logger.info("All core dependencies are installed")
        return True
    except ImportError as e:
        logger.error(f"Missing dependency: {str(e)}")
        logger.info("Please install all dependencies with: pip install -r requirements.txt")
        return False

def run_dashboard():
    """Run the Streamlit dashboard"""
    logger.info("Starting NEPSEZEN dashboard...")
    
    # Construct the path to the dashboard script
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard", "dashboard.py")
    
    if not os.path.exists(dashboard_path):
        logger.error(f"Dashboard file not found at {dashboard_path}")
        return False
    
    # Run Streamlit
    cmd = [sys.executable, "-m", "streamlit", "run", dashboard_path]
    
    try:
        logger.info(f"Running command: {' '.join(cmd)}")
        subprocess.run(cmd)
        return True
    except Exception as e:
        logger.error(f"Error running dashboard: {str(e)}")
        return False

def run_simulation(days=30, save_results=True):
    """Run a historical market simulation without the dashboard"""
    logger.info(f"Running NEPSEZEN simulation for {days} days...")
    
    try:
        # Import the main simulation module
        from simulator.main_builder import MarketSimulation
        
        # Initialize simulation
        simulation = MarketSimulation()
        
        # Load company data
        success = simulation.load_company_data()
        if not success:
            logger.error("Failed to load company data")
            return False
        
        # Initialize with historical data
        success = simulation.initialize_simulation(historical_days=365)
        if not success:
            logger.error("Failed to initialize simulation")
            return False
        
        # Run simulation
        result = simulation.run_historical_simulation(days, save_results)
        
        if result is not None:
            logger.info(f"Simulation completed successfully for {days} trading days")
            
            # Run analysis
            analysis = simulation.run_market_analysis()
            
            # Print summary
            if analysis and 'summary' in analysis:
                summary = analysis['summary']
                logger.info("=== Market Summary ===")
                
                if 'market_breadth' in summary:
                    breadth = summary['market_breadth']
                    logger.info(f"Market Breadth: {breadth.get('advancing', 0)} advancing, "
                                f"{breadth.get('declining', 0)} declining, "
                                f"{breadth.get('unchanged', 0)} unchanged")
                
                if 'sector_metrics' in summary:
                    sectors = summary['sector_metrics']
                    logger.info(f"Best Sector: {sectors.get('best_sector', 'Unknown')}")
                    logger.info(f"Worst Sector: {sectors.get('worst_sector', 'Unknown')}")
                    logger.info(f"Market Return: {sectors.get('market_return', 0)*100:.2f}%")
            
            return True
        else:
            logger.error("Simulation failed")
            return False
    except Exception as e:
        logger.error(f"Error running simulation: {str(e)}")
        return False

def run_realtime_simulation(minutes=60, update_interval=5, volatility=1.0):
    """Run a real-time market simulation without the dashboard"""
    logger.info(f"Running NEPSEZEN real-time simulation for {minutes} minutes...")
    
    try:
        # Import the main simulation module
        from simulator.main_builder import MarketSimulation
        import time
        
        # Initialize simulation
        simulation = MarketSimulation()
        
        # Load company data
        success = simulation.load_company_data()
        if not success:
            logger.error("Failed to load company data")
            return False
        
        # Initialize with historical data
        success = simulation.initialize_simulation(historical_days=30)
        if not success:
            logger.error("Failed to initialize simulation")
            return False
        
        # Start real-time simulation
        success = simulation.start_realtime_simulation(update_interval, volatility)
        if not success:
            logger.error("Failed to start real-time simulation")
            return False
        
        logger.info(f"Real-time simulation started with {update_interval}s updates")
        
        # Run for specified duration
        elapsed_time = 0
        try:
            while elapsed_time < minutes * 60:
                time.sleep(update_interval)
                elapsed_time += update_interval
                
                # Get market status
                if simulation.mode == "realtime" and simulation.realtime_simulator:
                    status = simulation.realtime_simulator.get_market_status()
                    
                    # Print status every minute
                    if elapsed_time % 60 == 0:
                        logger.info(f"Minute {elapsed_time//60}/{minutes}: "
                                    f"Advancing: {status['advancing']}, "
                                    f"Declining: {status['declining']}, "
                                    f"Volume: {status['total_volume']:,}")
                
                # Check if market closed
                if simulation.mode == "realtime" and not simulation.realtime_simulator.market_open:
                    logger.info("Market has closed")
                    break
        
        except KeyboardInterrupt:
            logger.info("Simulation interrupted by user")
        
        # Stop simulation
        simulation.stop_realtime_simulation()
        logger.info("Real-time simulation completed")
        
        # Save results
        simulation.save_historical_data()
        simulation.save_company_info()
        
        return True
    except Exception as e:
        logger.error(f"Error running real-time simulation: {str(e)}")
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="NEPSEZEN - Nepal Stock Exchange Simulator")
    
    # Define command-line arguments
    parser.add_argument('mode', choices=['dashboard', 'simulation', 'realtime'],
                        help='Mode to run (dashboard, simulation, or realtime)')
    
    parser.add_argument('--days', type=int, default=30,
                        help='Number of days to simulate (for simulation mode)')
    
    parser.add_argument('--minutes', type=int, default=60,
                        help='Number of minutes to run real-time simulation (for realtime mode)')
    
    parser.add_argument('--interval', type=int, default=5,
                        help='Update interval in seconds (for realtime mode)')
    
    parser.add_argument('--volatility', type=float, default=1.0,
                        help='Market volatility factor (for realtime mode)')
    
    parser.add_argument('--no-save', action='store_true',
                        help='Do not save simulation results')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Print welcome message
    print("\n" + "=" * 50)
    print(" NEPSEZEN - Nepal Stock Exchange Simulator")
    print("=" * 50 + "\n")
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Run selected mode
    if args.mode == 'dashboard':
        success = run_dashboard()
    elif args.mode == 'simulation':
        success = run_simulation(args.days, not args.no_save)
    elif args.mode == 'realtime':
        success = run_realtime_simulation(args.minutes, args.interval, args.volatility)
    else:
        parser.print_help()
        return 1
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
