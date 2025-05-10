# NEPSEZEN - Nepal Stock Exchange Simulator

![NEPSEZEN](https://via.placeholder.com/800x200/0077B6/FFFFFF?text=NEPSEZEN)

## Overview

NEPSEZEN is a comprehensive stock market simulation and analytics platform designed specifically for the Nepal Stock Exchange (NEPSE). The platform provides a realistic market environment for investors, analysts, and students to practice trading strategies, analyze market patterns, and understand the dynamics of the Nepalese stock market. 

Built by [Aayush Acharya](https://github.com/acharya-aayush), this project focuses on NEPSE overview and simulation capabilities.

## Key Features

- **Market Simulation**: Realistic simulation of the Nepal Stock Exchange with configurable market parameters
- **Technical Indicators**: Advanced technical analysis tools including RSI, MACD, and Bollinger Bands
- **Interactive Visualizations**: Dynamic charts for price movements, volume analysis, and sector performance
- **Portfolio Management**: Track investments, execute trades, and analyze performance
- **Real-time Analytics**: Market-wide analytics, sector-specific trends, and company performance metrics
- **Circuit Breaker Analysis**: Simulation of market circuit breaker mechanisms
- **Customizable Dashboard**: Modular interface with configurable views

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup Steps

1. Clone the repository:
```bash
git clone https://github.com/acharya-aayush/nepsezen.git
cd nepsezen
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py --mode dashboard
```

## Usage

### Dashboard Mode

Launch the interactive Streamlit dashboard:

```bash
python main.py --mode dashboard
```

### Simulation Mode

Run market simulation without dashboard:

```bash
python main.py --mode simulate --days 30
```

### Data Generation Mode

Generate sample historical data:

```bash
python main.py --mode generate --days 365
```

## Contributing

We welcome contributions to NEPSEZEN! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Known Issues and Future Improvements

### Current Limitations
- The data generation in `main.py` produces values that are out of proportion for Nepal's market context
- Better data generator is needed for more realistic simulation
- Consider web scraping real NEPSE data in future versions
- Some simulation parameters may need fine-tuning for authentic NEPSE behavior
- Dashboard has some visualization limitations that could be improved

### Future Roadmap
- Implement web scraping for real NEPSE data
- Create more accurate data generation algorithms
- Add user authentication for saving preferences
- Develop mobile-responsive dashboard
- Improve technical indicator accuracy

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Nepal Stock Exchange (NEPSE) for public data and market specifications
- Financial analysts and traders who provided domain expertise
- Open source community for various libraries used in this project
- AI assistants (ChatGPT, Claude, GitHub Copilot) for development support

## Contact

For questions and feedback, please contact:
- GitHub: [github.com/acharya-aayush](https://github.com/acharya-aayush)
- Instagram: [instagram.com/aayushacharya_gz](https://instagram.com/aayushacharya_gz)
- LinkedIn: [linkedin.com/in/acharyaaayush](https://linkedin.com/in/acharyaaayush)

---

> **Aayush's Corner:** This README do be hitting different tho. Straight up created this simulator with zero cap and all vibes. If you're not investing in NEPSE, you're missing out fr fr. Major shoutout to the AI and frnds who helped make this a whole mood. ✌️
