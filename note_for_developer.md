# Developer Notes for NEPSEZEN

## Author
Built by [Aayush Acharya](https://github.com/acharya-aayush) using Chat GPT, Claude, and GitHub Copilot.
- GitHub: [github.com/acharya-aayush](https://github.com/acharya-aayush)
- Instagram: [instagram.com/aayushacharya_gz](https://instagram.com/aayushacharya_gz)
- LinkedIn: [linkedin.com/in/acharyaaayush](https://linkedin.com/in/acharyaaayush)

## Project Structure and Architecture

NEPSEZEN follows a modular architecture to ensure maintainability and extensibility. The core components are:

1. **Simulator Core** (`simulator/main_builder.py`): The central simulation engine
2. **Data Generation** (`simulator/data_gen.py`): Realistic data creation and manipulation 
3. **Analytics Engine** (`analytics/analyzer.py`): Market analysis algorithms
4. **Filtering Module** (`analytics/filters.py`): Company screening functionality
5. **Technical Indicators** (`utils/indicators.py`): Trading indicators calculation
6. **Visualization** (`utils/visualizer.py`): Charts and graphical representation
7. **Dashboard** (`dashboard/dashboard.py`): User interface in Streamlit

## Known Issues & Areas for Improvement

### Data Generation Issues
- The data in `main.py` is completely out of proportion for Nepal's context
- Need better algorithms for realistic NEPSE simulation
- Consider implementing web scraping for authentic NEPSE data (idk if this is possible tbh)
- More accurate market event generation needed

### Code Indentation & Structure
- Some modules have indentation issues (especially in `main_builder.py`)
- Dashboard code could be more modular
- Streamlit components need better organization

### Testing Gaps
- Several tests need updating to match current implementation
- Need more comprehensive edge case testing

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use descriptive variable and function names (none of that single letter variable nonsense ok?)
- Include docstrings for all public functions, classes, and modules
- Keep functions focused on a single responsibility

### Error Handling

- Use appropriate exception handling for different error types
- Log errors with contextual information
- Provide user-friendly error messages for UI errors

### Performance Optimization

- Profile code to identify bottlenecks, especially in data processing
- Use vectorized operations where possible (NumPy/pandas)
- Consider lazy loading for large datasets
- Optimize visualization rendering for large datasets

### Testing

- Write unit tests for all modules, especially critical components
- Create integration tests for component interactions
- Test edge cases thoroughly (e.g., market circuit breakers, extreme volatility)

## Technical Debt and Known Issues

1. **Historical Data Generation**: The current approach to data generation could be more sophisticated to reflect real market patterns.
   - **Future Work**: Implement a more advanced model using statistical properties of actual NEPSE data.

2. **Dashboard Performance**: With large datasets, the dashboard may experience performance issues.
   - **Future Work**: Implement data aggregation and caching mechanisms.

3. **Circuit Breaker Logic**: The circuit breaker implementation is simplified.
   - **Future Work**: Enhance to match NEPSE's multi-tiered circuit breaker rules.

## Extensibility Points

### Adding New Technical Indicators

To add new indicators:

1. Add implementation to `utils/indicators.py`
2. Update the indicator configuration in `config.py`
3. Add visualization support in `utils/visualizer.py`
4. Create UI components in the dashboard

### Adding New Analytics

1. Implement new analytics function in `analytics/analyzer.py`
2. Add configuration parameters in `config.py` if necessary
3. Create visualization in `utils/visualizer.py`
4. Update dashboard to display the new analytics

### Adding New Simulation Factors

1. Define new market factors in `simulator/main_builder.py`
2. Update configuration in `config.py`
3. Integrate with the existing simulation logic

## Optimization Opportunities

1. **Parallelization**: Many simulations and analytics can be parallelized using multiprocessing.

2. **Caching**: Implement caching for frequently accessed data and computed results.

3. **Database Integration**: Replace file-based storage with a proper database for better performance with large datasets.

4. **Dashboard Optimizations**:
   - Lazy loading of components
   - Dynamic data aggregation based on zoom levels
   - Background processing of intensive calculations

## Future Development Roadmap

### Short-term (1-3 months)

- Enhance data generation with more realistic market patterns
- Implement portfolio optimization algorithms
- Add more technical indicators
- Improve test coverage

### Medium-term (3-6 months)

- Develop an API for headless operation
- Create a backtesting framework for strategy evaluation
- Implement machine learning models for market prediction
- Add support for news sentiment analysis

### Long-term (6+ months)

- Develop a real-time data integration with actual NEPSE data
- Create a distributed architecture for high-performance simulation
- Implement advanced risk management tools
- Develop mobile application interface

## Debugging Tips

1. Enable DEBUG level logging for more detailed information:
   ```python
   logging.basicConfig(level=logging.DEBUG)
   ```

2. Use the `--debug` flag when running the application:
   ```bash
   python main.py --mode dashboard --debug
   ```

3. Inspect generated data files to verify simulation accuracy:
   - Check `data/historical/` directory for generated historical data
   - Review simulation logs for unexpected behaviors

## Important Dependencies

- **pandas**: Used extensively for data manipulation
- **numpy**: Core numerical operations
- **plotly**: Interactive visualizations
- **streamlit**: Dashboard interface
- **scipy**: Statistical calculations

When updating dependencies, ensure compatibility is maintained and test thoroughly.

---

