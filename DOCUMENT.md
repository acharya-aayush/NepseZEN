# NEPSEZEN - Technical Documentation


## Architecture Overview

NEPSEZEN is built on a modular architecture with several key components, primarily focused on NEPSE overview and simulation:

```
nepsezen/
├── config.py                # Core configuration settings
├── main.py                  # Command-line entry point
├── requirements.txt         # Project dependencies
├── data/                    # Data storage directory
│   ├── companies.json       # Company information
│   └── historical/          # Historical market data
├── dashboard/               # Streamlit dashboard components
│   └── dashboard.py         # Main dashboard interface
├── utils/                   # Utility modules
│   ├── indicators.py        # Technical indicators calculation
│   └── visualizer.py        # Data visualization utilities
├── analytics/               # Market analysis modules
│   ├── analyzer.py          # Market analysis logic
│   └── filters.py           # Company filtering functions
└── simulator/               # Simulation engine
    ├── data_gen.py          # Data generation utilities
    └── main_builder.py      # Simulation coordinator
```

## Core Components

### 1. Simulation Engine

The simulation engine is the heart of NEPSEZEN, responsible for:

- Generating realistic market data
- Simulating market behaviors including volatility patterns
- Processing buy/sell orders
- Applying circuit breaker rules
- Managing market timing and sessions

Implementation: `simulator/main_builder.py`

### 2. Technical Indicators

The platform includes a comprehensive suite of technical indicators:

- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Moving Averages (Simple, Exponential)
- Volume indicators

Implementation: `utils/indicators.py`

### 3. Analytics Engine

The analytics engine processes market data to provide insights:

- Sector performance analysis
- Market breadth indicators
- Volatility measures
- Circuit breaker events
- Correlation analysis

Implementation: `analytics/analyzer.py`

### 4. Filtering System

The filtering system allows for screening stocks based on various criteria:

- Price thresholds
- Volume requirements
- Technical indicator values
- Fundamental metrics
- Circuit breaker status

Implementation: `analytics/filters.py`

### 5. Visualization

The visualization module creates interactive charts:

- Candlestick charts
- Volume profiles
- Performance comparisons
- Heatmaps and treemaps
- Portfolio performance

Implementation: `utils/visualizer.py`

### 6. User Interface

The Streamlit-based dashboard provides:

- Market overview tab
- Individual stock analysis
- Portfolio management
- Analytics dashboards
- Simulation controls

Implementation: `dashboard/dashboard.py`

## Data Model

### Company Data Structure

```json
{
  "SYMBOL": {
    "company_name": "String",
    "sector": "String",
    "listed_shares": "Number",
    "paid_up_value": "Number",
    "total_paid_up_capital": "Number",
    "market_cap": "Number",
    "price": {
      "open": "Number",
      "high": "Number",
      "low": "Number",
      "close": "Number"
    },
    "volume": "Number",
    "eps": "Number",
    "pe_ratio": "Number",
    "circuit_status": "String"
  }
}
```

### Historical Data Structure

Historical data is stored in CSV format with the following columns:

- Date
- Symbol
- Open
- High
- Low
- Close
- Volume

## Configuration Parameters

NEPSEZEN can be customized through various configuration parameters in `config.py`:

### Market Parameters

- Trading hours
- Circuit breaker thresholds
- Trading days
- Tick sizes

### Simulation Parameters

- Volatility factors
- Market event probabilities
- Sector interdependence
- Liquidity factors

### Technical Indicator Parameters

- RSI periods
- MACD parameters (fast, slow, signal)
- Bollinger Bands standard deviations

## Running the Application

### Command Line Interface

The application can be run in different modes using the command-line interface:

```bash
# Dashboard mode
python main.py --mode dashboard

# Simulation mode
python main.py --mode simulate --days 30

# Data generation mode
python main.py --mode generate --days 365

# Backtesting mode
python main.py --mode backtest --strategy momentum --start-date 2022-01-01 --end-date 2022-12-31
```

### Environment Variables

- `NEPSEZEN_DATA_DIR`: Custom data directory location
- `NEPSEZEN_LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING)
- `NEPSEZEN_CONFIG`: Path to custom configuration file

## Performance Considerations

- The simulation engine is optimized for realistic market behavior rather than absolute speed
- For large datasets, consider utilizing the batch processing options
- Visualization rendering may be intensive for long time periods with many companies

## Known Issues

- Data values don't reflect realistic Nepal market conditions
- Generated data in `main.py` is completely out of proportion for Nepal's market context
- Better data generator is needed for authentic NEPSE simulation
- Web scraping real NEPSE data would provide more accurate results
- Some dashboard visualizations may not render properly with certain data formats
- Indentation issues in some modules (particularly `main_builder.py`)
- Test files need updating to match current implementation

## Development Guidelines

- All new features should maintain the modular architecture
- Implement thorough error handling and logging
- Write unit tests for new functionality
- Follow PEP 8 style guidelines
- Document all public functions and classes

## Author
Built by [Aayush Acharya](https://github.com/acharya-aayush)
- GitHub: [github.com/acharya-aayush](https://github.com/acharya-aayush)
- Instagram: [instagram.com/aayushacharya_gz](https://instagram.com/aayushacharya_gz)
- LinkedIn: [linkedin.com/in/acharyaaayush](https://linkedin.com/in/acharyaaayush)
