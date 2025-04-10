# REIT Portfolio Tracker - Manage and Analyze US REIT Investments

![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.7%2B-brightgreen)
![REIT Tool](https://img.shields.io/badge/investment-US%20REITs-orange)
![AI Assisted](https://img.shields.io/badge/AI%20Assisted-Development-purple)

**Track, analyze and optimize your US Real Estate Investment Trust (REIT) portfolio with this comprehensive desktop application.**

> ⓘ **AI Development Note**: This application was developed with the assistance of artificial intelligence tools to enhance code quality, optimize algorithms, and improve user experience.

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

### Net Asset Value Analysis
![Portfolio Value Over Time](https://raw.githubusercontent.com/akossotchu/REIT-Portfolio-Tracker/refs/heads/screenshots/nav.png)

### Split / Reverse Split
![Portfolio Value Over Time](https://raw.githubusercontent.com/akossotchu/REIT-Portfolio-Tracker/refs/heads/screenshots/split.png)

## 🔧 Technical Details

### Data Sources

- **Stock Data**: Fetched automatically through the yfinance API
- **Consensus NAV Values**: Entered manually using data from sources like Seeking Alpha's [REIT reports](https://seekingalpha.com/article/4769493-the-state-of-reits-march-2025-edition)
- **Quality Scores**: Fetched from alreits.com

### AI-Assisted Development

This application incorporates several AI-assisted components:
- **Intelligent sector classification**: Automated REIT categorization using natural language processing
- **Optimized visualization algorithms**: Data presentation enhanced through machine learning techniques
- **Code quality improvements**: Structure and performance optimized with AI assistance
- **UI/UX enhancements**: Interface design refined with AI-driven recommendations

### Special Features

- **FIFO Accounting**: Calculates average cost basis and profit/loss using First-In-First-Out method
- **Stock Split Handling**: Properly adjusts holdings for stock splits and reverse splits
- **After-tax Income for International Investors**: Calculates estimated monthly income with tax adjustments (default 30% for Brazilian investors, customizable)

## ![PDF Report](https://raw.githubusercontent.com/akossotchu/REIT-Portfolio-Tracker/refs/heads/screenshots/pdf_report.png) PDF Report Generation

The REIT Portfolio Tracker can generate comprehensive PDF reports that provide a detailed analysis of your investment portfolio. These professional-quality reports include:

- Complete summary of portfolio value and performance
- Detailed holdings breakdown with current prices and metrics
- Allocation analysis with visual indicators to identify concentration risks
- Dividend growth tracking with 3-year and 5-year CAGR analysis
- NAV comparison showing premium/discount to consensus values
- After-tax income calculations for international investors

Perfect for record-keeping, sharing with advisors, or reviewing your investment strategy on a regular basis.

<p align="center">
  <a href="https://raw.githubusercontent.com/akossotchu/REIT-Portfolio-Tracker/refs/heads/screenshots/sample_report.pdf">Download Sample Report (PDF)</a>
</p>


## 🛠️ Advanced Usage

### Compiling to Executable

Create a standalone executable:

```
pip install pyinstaller
pyinstaller --name="REIT_Portfolio_Tracker" --windowed --icon=icon.ico --add-data="theme.py;." --add-data="split_dialog.py;." --add-data="nav.py;." --add-data="donate_dialog.py;." --add-data="transaction_history.py;." --add-data="data_visualization.py;." --add-data="sector_allocation.py;." --add-data="report_generator.py;." main.py
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
- Further AI integration for predictive analytics and automated portfolio optimization

## ❓ Troubleshooting

### Common Issues

1. **API Rate Limits**: If encountering errors with data fetching, wait a few minutes and try again
2. **Missing Data**: Some REITs may have incomplete data; manual entry is available
3. **Startup Issues**: Verify all dependencies are correctly installed

Need more help? [Open an issue](https://github.com/akossotchu/REIT-Portfolio-Tracker/issues) on GitHub

## 💎 Support This Project

If you find this application useful for managing your REIT investments, please consider making a Bitcoin donation to support continued development.

<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/64px-Bitcoin.svg.png" alt="Bitcoin Logo">
</p>

<p align="center">
  <strong>Bitcoin Address:</strong><br>
  <code>bc1qxqdxgf7ncc4ekz8ldq5cc5gukpykm6hfhjad0l</code>
</p>

<p align="center">
  <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=bc1qxqdxgf7ncc4ekz8ldq5cc5gukpykm6hfhjad0l" alt="Bitcoin Donation QR Code">
</p>

<p align="center">
  <em>Your support helps maintain and enhance this tool for all REIT investors</em>
</p>

## ⚠️ Disclaimer

This application is for informational purposes only and is not intended to provide investment advice. Always consult with a qualified financial advisor before making investment decisions.

## 📄 License

This project is open source and available under the MIT License.

---

### Related Keywords

US REIT tracking, REIT portfolio manager, dividend yield monitor, REIT investment tool, real estate investment trust software, REIT analysis application, dividend growth tracker, NAV premium discount calculator, REIT portfolio tracker, Python REIT app, AI-assisted investment tools

---

[View all features and documentation on GitHub](https://github.com/akossotchu/REIT-Portfolio-Tracker)
