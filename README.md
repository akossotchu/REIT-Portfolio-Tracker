# REIT Portfolio Tracker - Manage and Analyze US REIT Investments

![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.7%2B-brightgreen)
![REIT Tool](https://img.shields.io/badge/investment-US%20REITs-orange)

**Track, analyze and optimize your US Real Estate Investment Trust (REIT) portfolio with this comprehensive desktop application.**

## 🏢 REIT Portfolio Management Made Easy

REIT Portfolio Tracker is a powerful Python desktop application that helps investors manage their US REIT investments. The application offers real-time data tracking, performance analytics, dividend yield monitoring, and premium/discount to NAV analysis to support informed investment decisions.

![REIT Portfolio Tracker Screenshot](https://raw.githubusercontent.com/akossotchu/REIT-Portfolio-Tracker/refs/heads/screenshots/screenshot.png)

### Why REIT Portfolio Tracker?

- **Complete transaction tracking** - Buy, sell and no-cost acquisition management
- **Automatic data updates** - Real-time prices and dividend yields
- **Dividend growth analysis** - 3-year and 5-year CAGR calculations
- **Income projections** - Dividend income forecasting with tax calculations
- **NAV comparison** - Track premium/discount to consensus NAV
- **Quality scoring** - Integration with alreits.com scores

## 📊 Key Features

- **Transaction Management**: Track buy, sell, and no-cost acquisition transactions with detailed history
- **Real-time Data**: Automatically fetch current prices and dividend yields for US REITs
- **Portfolio Analytics**: Visualize performance, income projections, and sector allocation
- **NAV Analysis**: Track premium/discount compared to Consensus NAV values
- **Dividend Growth Tracking**: Monitor 3-year and 5-year dividend growth CAGR
- **REIT Quality Score**: Fetch quality scores for better investment decisions
- **Export Capabilities**: Generate professional PDF reports and export data to CSV
- **After-tax Income Calculations**: Calculate estimated monthly income after taxes

## 🚀 Getting Started

### Installation Requirements

- Python 3.7+
- Required packages can be installed via pip:
```
pip install -r requirements.txt
```
See the [requirements.txt](https://github.com/akossotchu/REIT-Portfolio-Tracker/blob/main/requirements.txt) file for all dependencies.

### Quick Start

1. Clone the repository
   ```
   git clone https://github.com/akossotchu/REIT-Portfolio-Tracker.git
   ```
2. Install requirements
   ```
   pip install -r requirements.txt
   ```
3. Run the application
   ```
   python main.py
   ```

## 📱 Screenshots and Features

### Portfolio Allocation
![Portfolio Allocation](https://raw.githubusercontent.com/akossotchu/REIT-Portfolio-Tracker/refs/heads/screenshots/allocation.png)

### Dividend Income Analysis
![Dividend Analysis](https://raw.githubusercontent.com/akossotchu/REIT-Portfolio-Tracker/refs/heads/screenshots/dividend_income.PNG)

### Portfolio Value Over Time
![Portfolio Value Over Time](https://raw.githubusercontent.com/akossotchu/REIT-Portfolio-Tracker/refs/heads/screenshots/portfolio.png)

### New Transaction & Transaction History
![New Transaction](https://raw.githubusercontent.com/akossotchu/REIT-Portfolio-Tracker/refs/heads/screenshots/transaction.png)

![Transaction History](https://raw.githubusercontent.com/akossotchu/REIT-Portfolio-Tracker/refs/heads/screenshots/transaction_history.png)

### Net Asset Value Analysis*
![Portfolio Value Over Time](https://raw.githubusercontent.com/akossotchu/REIT-Portfolio-Tracker/refs/heads/screenshots/nav.png)

### Split / Reverse Split
![Portfolio Value Over Time](https://raw.githubusercontent.com/akossotchu/REIT-Portfolio-Tracker/refs/heads/screenshots/split.png)

## 🔧 Technical Details

### Data Sources

- **Stock Data**: Fetched automatically through the yfinance API
- **Consensus NAV Values**: Entered manually using data from sources like Seeking Alpha's [REIT reports](https://seekingalpha.com/article/4769493-the-state-of-reits-march-2025-edition)
- **Quality Scores**: Fetched from alreits.com

### Special Features

- **FIFO Accounting**: Calculates average cost basis and profit/loss using First-In-First-Out method
- **Stock Split Handling**: Properly adjusts holdings for stock splits and reverse splits
- **After-tax Income for International Investors**: Calculates estimated monthly income with tax adjustments (default 30% for Brazilian investors, customizable)

## 🛠️ Advanced Usage

### Compiling to Executable

Create a standalone executable:

```
pip install pyinstaller
pyinstaller --name="REIT Portfolio Tracker" --windowed --onefile --icon=icon.ico --hidden-import=yfinance --hidden-import=pandas --hidden-import=numpy --hidden-import=matplotlib --hidden-import=scipy main.py
```

### Project Structure

- [**main.py**](https://github.com/akossotchu/REIT-Portfolio-Tracker/blob/main/main.py): Entry point for the application
- [**reit_portfolio_app.py**](https://github.com/akossotchu/REIT-Portfolio-Tracker/blob/main/reit_portfolio_app.py): Main application with UI and program logic
- [**theme.py**](https://github.com/akossotchu/REIT-Portfolio-Tracker/blob/main/theme.py): Theme constants and styling information
- [**split_dialog.py**](https://github.com/akossotchu/REIT-Portfolio-Tracker/blob/main/split_dialog.py): Dialog for handling stock splits
- [**nav.py**](https://github.com/akossotchu/REIT-Portfolio-Tracker/blob/main/nav.py): NAV analysis features
- [**donate_dialog.py**](https://github.com/akossotchu/REIT-Portfolio-Tracker/blob/main/donate_dialog.py): Bitcoin donation dialog
- [**transaction_history.py**](https://github.com/akossotchu/REIT-Portfolio-Tracker/blob/main/transaction_history.py): Transaction history implementation
- [**data_visualization.py**](https://github.com/akossotchu/REIT-Portfolio-Tracker/blob/main/data_visualization.py): Portfolio analytics visualization
- [**sector_allocation.py**](https://github.com/akossotchu/REIT-Portfolio-Tracker/blob/main/sector_allocation.py): Sector allocation analytics
- [**report_generator.py**](https://github.com/akossotchu/REIT-Portfolio-Tracker/blob/main/report_generator.py): PDF report generation

## 📈 Future Development

- Additional data source integrations
- Support for more international markets and tax systems
- Enhanced visualization and analytics
- Mobile companion app
- Cloud synchronization

## ❓ Troubleshooting

### Common Issues

1. **API Rate Limits**: If encountering errors with data fetching, wait a few minutes and try again
2. **Missing Data**: Some REITs may have incomplete data; manual entry is available
3. **Startup Issues**: Verify all dependencies are correctly installed

Need more help? [Open an issue](https://github.com/akossotchu/REIT-Portfolio-Tracker/issues) on GitHub

## 💎 Support This Project

<div align="center">

![Bitcoin](https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/64px-Bitcoin.png)

If you find this application useful for managing your REIT investments, please consider making a Bitcoin donation to support continued development.

**Bitcoin Address:**  
**bc1qxqdxgf7ncc4ekz8ldq5cc5gukpykm6hfhjad0l**

<img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=bc1qxqdxgf7ncc4ekz8ldq5cc5gukpykm6hfhjad0l" alt="Bitcoin Donation QR Code">

</div>

## ⚠️ Disclaimer

This application is for informational purposes only and is not intended to provide investment advice. Always consult with a qualified financial advisor before making investment decisions.

## 📄 License

This project is open source and available under the MIT License.

---

### Related Keywords

US REIT tracking, REIT portfolio manager, dividend yield monitor, REIT investment tool, real estate investment trust software, REIT analysis application, dividend growth tracker, NAV premium discount calculator, REIT portfolio tracker, Python REIT app

---

[View all features and documentation on GitHub](https://github.com/akossotchu/REIT-Portfolio-Tracker)
