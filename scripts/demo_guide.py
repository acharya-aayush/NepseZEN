"""
Demo script for recording a NEPSEZEN demonstration video

This script provides step-by-step guidance for creating a video demonstration
of the NEPSEZEN platform's key features.
"""

import os
import sys
import time
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def print_section(title):
    """Print a section header for the demo"""
    print("\n" + "="*80)
    print(f" {title} ".center(80, "="))
    print("="*80 + "\n")
    time.sleep(1)

def wait_for_input(message="Press Enter to continue..."):
    """Wait for user input to continue the demo"""
    input(f"\n{message}\n")

def demo_flow():
    """Main demo flow script"""
    # Introduction
    print_section("NEPSEZEN - Nepal Stock Exchange Simulator Demo")
    print("""
Welcome to the NEPSEZEN demonstration. This script will guide you through
recording a comprehensive video demo of the platform's key features.

Please ensure:
1. You have a screen recording software ready
2. The simulator has been properly set up
3. Historical data has been generated
4. The dashboard is accessible
    """)
    wait_for_input("Press Enter to start the demo script...")
    
    # Start the demo
    print_section("1. Launch the Dashboard")
    print("""
Step 1: Launch the NEPSEZEN dashboard by running:
    
    python main.py --mode dashboard
    
Wait for the dashboard to load completely in your browser.
Explain that NEPSEZEN is a comprehensive stock market simulation 
platform focused on the Nepal Stock Exchange.
    """)
    wait_for_input()
    
    # Market Overview
    print_section("2. Market Overview Tab")
    print("""
Step 2: On the Market Overview tab:

- Highlight the market summary metrics (index value, volume, advances/declines)
- Show the interactive market index chart
- Demonstrate changing the time period (1D, 1W, 1M, 3M, 6M, 1Y)
- Point out the sector performance visualization
- Show the volume heatmap and explain its significance
- Discuss the top gainers and losers section
    """)
    wait_for_input()
    
    # Stock Analysis
    print_section("3. Stock Analysis Tab")
    print("""
Step 3: Navigate to the Stock Analysis tab:

- Select a bank stock (e.g., NABIL) from the dropdown
- Show the interactive candlestick chart
- Add a technical indicator (e.g., RSI) and explain its significance
- Add another indicator (e.g., Bollinger Bands)
- Demonstrate the zoom and pan features of the chart
- Show the historical performance metrics
- Point out the circuit breaker status (if applicable)
    """)
    wait_for_input()
    
    # Portfolio Management
    print_section("4. Portfolio Management Tab")
    print("""
Step 4: Navigate to the Portfolio Management tab:

- Show the current portfolio composition
- Demonstrate creating a new portfolio or reset the existing one
- Execute a buy order for a stock (e.g., buy 100 shares of NABIL)
- Execute a sell order for another stock (if available)
- Show the portfolio performance chart
- Point out the profit/loss calculation
- Demonstrate the portfolio analytics features
    """)
    wait_for_input()
    
    # Analytics Dashboard
    print_section("5. Analytics Dashboard Tab")
    print("""
Step 5: Navigate to the Analytics Dashboard tab:

- Show the correlation matrix between different stocks
- Demonstrate sector allocation analysis
- Point out the circuit breaker analysis visualization
- Show the volatility comparison chart
- Explain how these analytics can help investors
    """)
    wait_for_input()
    
    # Simulation Controls
    print_section("6. Simulation Controls Tab")
    print("""
Step 6: Navigate to the Simulation Controls tab:

- Show the simulation configuration options
- Adjust a parameter (e.g., volatility)
- Run a short simulation (e.g., 5 market days)
- Show how the change affected the market behavior
- Demonstrate the news and events feature (if implemented)
- Explain how the simulation can be used for scenario analysis
    """)
    wait_for_input()
    
    # Conclusion
    print_section("7. Conclusion and Key Features Recap")
    print("""
Step 7: Conclude the demo:

- Summarize the key features demonstrated:
  * Realistic market simulation
  * Technical analysis capabilities
  * Interactive visualizations
  * Portfolio management
  * Advanced analytics
  * Customization options
  
- Highlight the educational value of the platform
- Mention potential use cases (investors, students, financial institutions)
- Direct viewers to documentation for more information
    """)
    
    print("\nDemo script completed!")

if __name__ == "__main__":
    demo_flow()
