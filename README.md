# REIT Portfolio Tracker

## Overview

REIT Portfolio Tracker is a comprehensive desktop application built with Python and PyQt5, designed to help investors manage and analyze their Real Estate Investment Trust (REIT) portfolios. The application provides real-time data tracking, performance analytics, and customizable reporting features to facilitate informed investment decisions.

## Key Features

- **Transaction Management**: Track buy, sell, and no-cost acquisition transactions with detailed history.
- **Real-time Data**: Automatically fetch current prices and dividend yields for REITs.
- **Portfolio Analytics**: Visualize portfolio performance, income projections, and sector allocation.
- **NAV Analysis**: Track premium/discount compared to Consensus NAV values.
- **Dividend Growth Tracking**: Monitor 3-year and 5-year dividend growth CAGR for individual REITs and the overall portfolio.
- **REIT Quality Score**: Fetch quality scores from alreits.com for better investment decisions.
- **Export Capabilities**: Generate professional PDF reports and export data to CSV.
- **After-tax Income Calculations**: Calculate estimated monthly income after taxes.

## Technical Details

### Libraries and Dependencies

The application relies on several Python libraries:

- **PyQt5**: For the graphical user interface.
- **yfinance**: To fetch real-time stock data.
- **pandas**: For data manipulation and analysis.
- **requests & BeautifulSoup4**: For web scraping additional data.
- **qrcode & pillow**: For generating QR codes for the donation feature.
- **reportlab & matplotlib**: For generating PDF reports and data visualization.

### Data Sources

- **Stock Data**: Fetched automatically through the yfinance API.
- **Consensus NAV Values**: Entered manually by the user. These values can be obtained from various sources such as monthly REIT reports on Seeking Alpha (e.g., [The State of REITs: March 2025 Edition](https://seekingalpha.com/article/4769493-the-state-of-reits-march-2025-edition)).
- **Quality Scores**: Fetched from alreits.com.

### Special Features Explained

- **After-tax Monthly Income (BRL)**: This feature is specifically designed for Brazilian investors, calculating the estimated monthly income in Brazilian Reais after applying a standard 30% tax rate. This can be modified according to the user's specific tax situation or country of residence.

- **FIFO Accounting**: The application uses the First-In-First-Out method to calculate average cost basis and profit/loss.

- **Stock Split Handling**: Special functionality to properly adjust holdings for stock splits and reverse splits.

## Installation

### Requirements

- Python 3.7+
- Required packages can be installed via pip:
```
pip install -r requirements.txt
```

### Building from Source

For developers who want to build the application from source:

1. Clone the repository
2. Install requirements
3. Run `main.py` to start the application

### Running the Application

The application is initialized through the `main.py` file, which serves as the entry point:

```
python main.py
```

### Compiling to Executable

To create a standalone executable:

```
pip install pyinstaller
pyinstaller --name="REIT_Portfolio_Tracker" --windowed --icon=icon.ico --add-data="theme.py;." --add-data="split_dialog.py;." --add-data="nav.py;." --add-data="donate_dialog.py;." --add-data="transaction_history.py;." --add-data="data_visualization.py;." --add-data="sector_allocation.py;." --add-data="report_generator.py;." main.py
```

## Support This Project

<div align="center">

![Bitcoin](https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/64px-Bitcoin.svg.png)

If you find this application useful for managing your REIT investments, please consider making a Bitcoin donation to support continued development and maintenance.

**Bitcoin Address:**  
**bc1qxqdxgf7ncc4ekz8ldq5cc5gukpykm6hfhjad0l**

<img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=bc1qxqdxgf7ncc4ekz8ldq5cc5gukpykm6hfhjad0l" alt="Bitcoin Donation QR Code">

*Your support helps maintain and enhance this tool for REIT investors*

</div>

## License

This project is open source and available under the MIT License.

## Disclaimer

This application is for informational purposes only and is not intended to provide investment advice. Always consult with a qualified financial advisor before making investment decisions.

## Contributing

We welcome contributions to the REIT Portfolio Tracker project! Here's how you can contribute:

1. **Bug Reports**: If you find a bug, please open an issue with detailed steps to reproduce it.
2. **Feature Requests**: Have an idea for a new feature? Open an issue to discuss it.
3. **Code Contributions**: Submit a pull request with your changes. Please follow these guidelines:
   - Write clean, well-documented code
   - Include tests when applicable
   - Follow the existing code style
   - Create focused, single-purpose pull requests

## Development Setup

To set up a development environment:

1. Fork and clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Make your changes
5. Test your changes thoroughly
6. Submit a pull request

## Project Structure

- **main.py**: Entry point for the application
- **reit_portfolio_app.py**: Main application file containing the core UI and program logic
- **theme.py**: Contains theme constants and styling information
- **split_dialog.py**: Dialog for handling stock splits
- **nav.py**: Implementation of NAV analysis features
- **donate_dialog.py**: Bitcoin donation dialog
- **transaction_history.py**: Transaction history view implementation
- **data_visualization.py**: Portfolio analytics visualization
- **sector_allocation.py**: Sector allocation charts and analytics
- **report_generator.py**: PDF report generation functionality

## Customization

Users can customize various aspects of the application:

- **Tax Rates**: The after-tax income calculation uses a default 30% tax rate for Brazilian investors, but this can be modified in the code to match your specific situation.
- **Currency Conversion**: Exchange rates are fetched automatically but can be manually adjusted if needed.
- **Data Sources**: Advanced users can modify the code to use alternative data sources.

## Future Development Plans

- Integration with additional data sources
- Support for more international markets and tax systems
- Enhanced data visualization and analytics
- Mobile companion app
- Cloud synchronization for multi-device access

## Known Limitations

- The application currently supports US-listed REITs most effectively
- Some features rely on third-party websites that may change their structure
- Performance may degrade with very large portfolios (hundreds of positions)

## Troubleshooting

### Common Issues

1. **API Errors**: If you encounter errors related to data fetching, it may be due to API rate limits. Try again after a few minutes.

2. **Missing Data**: Some REITs may have incomplete data. In these cases, you can manually enter the missing information.

3. **Startup Issues**: If the application fails to start, check if all dependencies are correctly installed.

### Getting Help

If you need assistance beyond what's covered in this documentation, you can:
- Open an issue on GitHub
- Contact the maintainers directly
- Check the Wiki for additional documentation

## Acknowledgments

- This project utilizes yfinance, which provides Yahoo Finance data
- Special thanks to all contributors who have helped improve this application
- The application incorporates ideas and feedback from the REIT investment community

## Final Notes

The REIT Portfolio Tracker is designed to be a helpful tool for investors, but remember that all investment decisions should be based on thorough research and possibly consultation with financial professionals. The application is continually evolving, and your feedback helps make it better for everyone.

Thank you for using and supporting REIT Portfolio Tracker!
