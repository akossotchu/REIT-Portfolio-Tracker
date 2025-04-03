import sys
import os
import json
from datetime import datetime, timedelta, date
import requests
import yfinance as yf
import pandas as pd
from bs4 import BeautifulSoup
import qrcode
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem, 
                            QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, 
                            QLineEdit, QDialog, QDateEdit, QDoubleSpinBox, QSpinBox, 
                            QComboBox, QHeaderView, QMessageBox, QFrame, QToolBar, 
                            QAction, QMenu, QStatusBar, QFileDialog, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QThread, QUrl, QTimer, QSize, QRect, QPoint, QPropertyAnimation, QEasingCurve, QLocale
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QPalette, QDesktopServices, QLinearGradient, QPainter, QPen, QPainterPath
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QPalette, QDesktopServices, QLinearGradient, QPainter, QPen, QPainterPath
from theme import Theme
from split_dialog import SplitDialog
from nav import NAVDialog

# Constants
PORTFOLIO_FILE = "reit_portfolio.json"

class SplitDialog(QDialog):
    def __init__(self, parent=None, ticker=""):
        super().__init__(parent)
        self.setWindowTitle("Stock Split")
        self.setMinimumWidth(400)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.BACKGROUND};
            }}
            QLabel {{
                font-size: 13px;
                color: {Theme.TEXT_PRIMARY};
            }}
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
                border: 1px solid {Theme.BORDER};
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                min-height: 20px;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
                border: 1px solid {Theme.SECONDARY};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Stock Split / Reverse Split")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        layout.addWidget(title_label)
        
        # Form container with white background
        form_container = QFrame()
        form_container.setStyleSheet(f"""
            background-color: {Theme.CARD_BG};
            border-radius: 8px;
            padding: 15px;
        """)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(15)
        
        # Explanation label
        explanation = QLabel(
            "A stock split changes the number of shares and their price. "
            "For example, in a 2:1 split, 1 share becomes 2 shares at half the price."
        )
        explanation.setWordWrap(True)
        explanation.setStyleSheet(f"color: {Theme.TEXT_SECONDARY};")
        form_layout.addWidget(explanation)
        
        # Ticker selector
        ticker_layout = QHBoxLayout()
        ticker_layout.addWidget(QLabel("Ticker:"))
        self.ticker_edit = QLineEdit()
        self.ticker_edit.setText(ticker)
        self.ticker_edit.setMinimumHeight(36)
        self.ticker_edit.setPlaceholderText("Enter REIT ticker symbol")
        ticker_layout.addWidget(self.ticker_edit)
        form_layout.addLayout(ticker_layout)
        
        # Split ratio
        ratio_layout = QHBoxLayout()
        ratio_layout.addWidget(QLabel("Split Ratio:"))
        
        ratio_container = QHBoxLayout()
        ratio_container.setSpacing(5)
        
        self.new_shares_spin = QSpinBox()
        self.new_shares_spin.setMinimum(1)
        self.new_shares_spin.setMaximum(100)
        self.new_shares_spin.setValue(2)
        self.new_shares_spin.setMinimumHeight(36)
        
        ratio_container.addWidget(self.new_shares_spin)
        ratio_container.addWidget(QLabel(":"))
        
        self.old_shares_spin = QSpinBox()
        self.old_shares_spin.setMinimum(1)
        self.old_shares_spin.setMaximum(100)
        self.old_shares_spin.setValue(1)
        self.old_shares_spin.setMinimumHeight(36)
        
        ratio_container.addWidget(self.old_shares_spin)
        ratio_layout.addLayout(ratio_container)
        form_layout.addLayout(ratio_layout)
        
        # Add a date selector for the split date
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Split Date:"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setMinimumHeight(36)
        date_layout.addWidget(self.date_edit)
        form_layout.addLayout(date_layout)
        
        # Add form to main layout
        layout.addWidget(form_container)
        
        # Preview section
        preview_container = QFrame()
        preview_container.setStyleSheet(f"""
            background-color: {Theme.CARD_BG};
            border-radius: 8px;
            padding: 15px;
            margin-top: 10px;
        """)
        preview_layout = QVBoxLayout(preview_container)
        
        preview_title = QLabel("Effect Preview:")
        preview_title.setStyleSheet("font-weight: bold;")
        preview_layout.addWidget(preview_title)
        
        self.preview_label = QLabel(
            "2:1 split means: 10 shares at $100 → 20 shares at $50"
        )
        self.preview_label.setWordWrap(True)
        preview_layout.addWidget(self.preview_label)
        
        layout.addWidget(preview_container)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumWidth(100)
        self.cancel_button.setMinimumHeight(36)
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #f0f0f0;
                color: {Theme.TEXT_PRIMARY};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
        """)
        button_layout.addWidget(self.cancel_button)
        
        self.ok_button = QPushButton("Apply Split")
        self.ok_button.setMinimumWidth(100)
        self.ok_button.setMinimumHeight(36)
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.PRIMARY};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Theme.SECONDARY};
            }}
        """)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        
        # Connect signals for previews
        self.new_shares_spin.valueChanged.connect(self.update_preview)
        self.old_shares_spin.valueChanged.connect(self.update_preview)
        
        # Initial preview update
        self.update_preview()
    
    def update_preview(self):
        """Update the preview text based on current split ratio"""
        new_shares = self.new_shares_spin.value()
        old_shares = self.old_shares_spin.value()
        
        # Calculate the price factor
        price_factor = old_shares / new_shares
        
        # Set up example values
        example_shares = 10
        example_price = 100
        
        # Calculate new values
        new_example_shares = example_shares * (new_shares / old_shares)
        new_example_price = example_price * price_factor
        
        # Format the preview text
        if new_shares > old_shares:
            split_type = "split"
        elif new_shares < old_shares:
            split_type = "reverse split"
        else:
            split_type = "1:1 ratio (no effect)"
        
        preview_text = f"{new_shares}:{old_shares} {split_type} means: "\
                       f"{example_shares} shares at ${example_price:.2f} → "\
                       f"{new_example_shares:.2f} shares at ${new_example_price:.2f}"
        
        self.preview_label.setText(preview_text)
    
    def get_split_info(self):
        """Return the split information"""
        ticker = self.ticker_edit.text().strip().upper()
        new_shares = self.new_shares_spin.value()
        old_shares = self.old_shares_spin.value()
        split_date = self.date_edit.date().toPyDate()  # Get as datetime.date
        
        return {
            'ticker': ticker,
            'new_shares': new_shares,
            'old_shares': old_shares,
            'split_date': split_date
        }

# Custom button style with hover effect
class StyledButton(QPushButton):
    def __init__(self, text, parent=None, accent=False):
        super().__init__(text, parent)
        self.accent = accent
        self.setFont(QFont("Segoe UI", 9))
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(36)
        
        # Set initial style
        self.update_style()
        
    def update_style(self):
        if self.accent:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Theme.ACCENT};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #FF8C24;
                }}
                QPushButton:pressed {{
                    background-color: #E58535;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Theme.PRIMARY};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: {Theme.SECONDARY};
                }}
                QPushButton:pressed {{
                    background-color: #1E3A70;
                }}
            """)

# Modern card widget with shadow
class ModernCard(QFrame):
    def __init__(self, parent=None, clickable=False):
        super().__init__(parent)
        self.setFrameShape(QFrame.NoFrame)
        self.setObjectName("modernCard")
        self.setCursor(Qt.PointingHandCursor if clickable else Qt.ArrowCursor)
        
        # Set up shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        # Modern styling
        self.setStyleSheet(f"""
            #modernCard {{
                background-color: {Theme.CARD_BG};
                border-radius: 8px;
                padding: 0px;
                margin: 0px;
            }}
            #modernCard:hover {{
                background-color: #F8FAFD;
            }}
        """)

class StockDataFetcher(QThread):
    data_fetched = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker
        self.running = True
        
    def run(self):
        try:
            if not self.running:
                return
                    
            # Initialize variables
            current_price = None
            dividend_yield = None
            annual_dividend = None
            company_name = ""
            dividend_growth_3y = 0.0
            dividend_growth_5y = 0.0
                    
            # Use yfinance to get data for the ticker
            stock = yf.Ticker(self.ticker)
            
            if not self.running:
                return
            
            # Get basic information
            try:
                stock_info = stock.info
            except Exception as e:
                stock_info = {}
                print(f"Error getting information for {self.ticker}: {e}")
            
            # Get current price
            if 'regularMarketPrice' in stock_info:
                current_price = stock_info['regularMarketPrice']
            elif 'currentPrice' in stock_info:
                current_price = stock_info['currentPrice']
            elif 'previousClose' in stock_info:
                current_price = stock_info['previousClose']
                  
            # Get company name
            if 'shortName' in stock_info:
                company_name = stock_info['shortName']
            elif 'longName' in stock_info:
                company_name = stock_info['longName']
            
            # Get annual dividends
            if 'dividendRate' in stock_info and stock_info['dividendRate'] is not None:
                annual_dividend = stock_info['dividendRate']
            
            # Sempre calcular o dividend yield a partir do annual_dividend e current_price
            if annual_dividend is not None and current_price is not None and current_price > 0:
                dividend_yield = (annual_dividend / current_price) * 100
            else:
                # Fallback para quando não temos annual_dividend
                if 'dividendYield' in stock_info and stock_info['dividendYield'] is not None:
                    decimal_yield = stock_info['dividendYield']
                    if decimal_yield > 0 and decimal_yield < 1:
                        dividend_yield = decimal_yield * 100
                    else:
                        dividend_yield = decimal_yield
			
            if not self.running:
                return
            
            # Buscar dados históricos de dividendos
            try:
                # Obter histórico de dividendos
                dividend_history = stock.actions
                
                if not dividend_history.empty:
                    # Filtrar apenas os dividendos positivos
                    dividends = dividend_history[dividend_history['Dividends'] > 0]['Dividends']
                    
                    if not dividends.empty:
                        # Identificar se o pagamento é mensal ou trimestral
                        # Usamos o índice que contém as datas dos pagamentos
                        dates = dividends.index
                        
                        if len(dates) >= 12:  # Precisamos de pelo menos ~1 ano de dados
                            # Criar um DataFrame com a data e o valor do dividendo
                            dividend_df = pd.DataFrame({
                                'date': dates,
                                'dividend': dividends.values
                            })
                            
                            # Adicionar colunas para ano e mês
                            dividend_df['year'] = dividend_df['date'].dt.year
                            dividend_df['month'] = dividend_df['date'].dt.month
                            
                            # Detectar a frequência de pagamento
                            # Se temos pelo menos 10 meses diferentes com pagamentos no último ano,
                            # provavelmente é pagamento mensal, caso contrário, assumimos trimestral
                            last_year_dividends = dividend_df[dividend_df['date'] >= (dates[-1] - pd.DateOffset(years=1))]
                            unique_months = last_year_dividends['month'].nunique()
                            is_monthly = unique_months >= 10
                            
                            # Calcular dividendos anuais para cada ano agrupando por ano
                            annual_dividends = dividend_df.groupby('year')['dividend'].sum()
                            years = annual_dividends.index.tolist()
                            
                            # Para o CAGR de 3 anos
                            if len(years) >= 3:
                                # Pegar anos completos para comparação
                                current_year = years[-1]
                                three_years_ago = current_year - 3
                                
                                # Se o último ano está incompleto (estamos no meio do ano),
                                # usamos anualizados para o ano atual
                                if is_monthly:
                                    # Para pagamentos mensais
                                    current_year_months = dividend_df[dividend_df['year'] == current_year]['month'].nunique()
                                    if current_year_months < 12 and current_year_months > 0:
                                        # Anualizar dividendos para o ano atual
                                        current_year_div = annual_dividends[current_year] * (12 / current_year_months)
                                    else:
                                        current_year_div = annual_dividends[current_year]
                                else:
                                    # Para pagamentos trimestrais
                                    current_year_quarters = dividend_df[dividend_df['year'] == current_year]['month'].nunique()
                                    if current_year_quarters < 4 and current_year_quarters > 0:
                                        # Anualizar dividendos para o ano atual
                                        current_year_div = annual_dividends[current_year] * (4 / current_year_quarters)
                                    else:
                                        current_year_div = annual_dividends[current_year]
                                
                                # Encontrar o valor para 3 anos atrás
                                if three_years_ago in years:
                                    three_years_ago_div = annual_dividends[three_years_ago]
                                    # Calcular CAGR para 3 anos
                                    if three_years_ago_div > 0:
                                        dividend_growth_3y = ((current_year_div / three_years_ago_div) ** (1/3) - 1) * 100
                                
                            # Para o CAGR de 5 anos
                            if len(years) >= 5:
                                # Pegar anos completos para comparação
                                current_year = years[-1]
                                five_years_ago = current_year - 5
                                
                                # Usamos o mesmo valor anualizado para o ano atual
                                
                                # Encontrar o valor para 5 anos atrás
                                if five_years_ago in years:
                                    five_years_ago_div = annual_dividends[five_years_ago]
                                    # Calcular CAGR para 5 anos
                                    if five_years_ago_div > 0:
                                        dividend_growth_5y = ((current_year_div / five_years_ago_div) ** (1/5) - 1) * 100
            except Exception as div_error:
                print(f"Error fetching dividend history for {self.ticker}: {str(div_error)}")
            
            # Fallback for missing values
            if current_price is None:
                # Try to get at least the last closing price
                try:
                    hist = stock.history(period="1d")
                    if not hist.empty:
                        current_price = hist['Close'][-1]
                except:
                    pass
            
            # Final fallback for data that couldn't be obtained
            if dividend_yield is None or dividend_yield == 0:
                # REITs typically have yields between 2% and 8%
                # But we won't generate random values, just indicate that it wasn't possible to obtain
                dividend_yield = 0.0
                
            if current_price is None:
                current_price = 0.0
                
            if not self.running:
                return
                    
            # Ensure dividend yield is a percentage
            if dividend_yield > 100:
                dividend_yield = dividend_yield / 100  # Fix if incorrectly multiplied
                    
            # Debug to check values
            print(f"Ticker: {self.ticker}, Price: {current_price}, Dividend Yield: {dividend_yield}%, Annual Dividend: {annual_dividend}")
            print(f"Dividend Growth 3Y CAGR: {dividend_growth_3y:.2f}%, 5Y CAGR: {dividend_growth_5y:.2f}%")
                
            result = {
                'ticker': self.ticker,
                'price': current_price,
                'dividend_yield': dividend_yield,
                'company_name': company_name,
                'annual_dividend': annual_dividend,
                'dividend_growth_3y': dividend_growth_3y,
                'dividend_growth_5y': dividend_growth_5y
            }
            self.data_fetched.emit(result)
            
        except Exception as e:
            if self.running:
                self.error_occurred.emit(f"Error fetching data for {self.ticker}: {str(e)}")
    
    def stop(self):
        self.running = False

# Adicione depois da classe StockDataFetcher
class AlreitsScoreFetcher(QThread):
    score_fetched = pyqtSignal(str, int)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker
        self.running = True
        
    def run(self):
        try:
            if not self.running:
                return
                
            print(f"DEBUG - Buscando score para {self.ticker} em alreits.com")
			
            # URL para o REIT no site alreits
            url = f"https://alreits.com/reits/{self.ticker}"
            
            # Buscar a página
            print(f"  Fazendo requisição para: {url}")
            try:
                response = requests.get(url, timeout=10)
                print(f"  Status da resposta: {response.status_code}")
            except Exception as req_error:
                print(f"  Erro na requisição: {str(req_error)}")
                self.error_occurred.emit(f"Request error for {self.ticker}: {str(req_error)}")
                return
            
            if not self.running or response.status_code != 200:
                return
                
            # Analisar o HTML para extrair o score
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Encontrar o elemento que contém o score
            score_element = soup.find('p', class_='MuiTypography-root MuiTypography-body1 ScoreTotal__Score-sc-1cc8w4y-1 ka-Dica css-99u0rr')
            
            if score_element:
                # Extrair o número do score
                score_text = score_element.get_text().strip()
                try:
                    score = int(score_text)
                    if score > 0:  # Verificar se é um score válido
                        self.score_fetched.emit(self.ticker, score)
                    else:
                        self.error_occurred.emit(f"Invalid score value for {self.ticker}")
                except:
                    self.error_occurred.emit(f"Could not parse score for {self.ticker}")
            else:
                self.error_occurred.emit(f"Score element not found for {self.ticker}")
                
        except Exception as e:
            if self.running:
                self.error_occurred.emit(f"Error fetching alreits score for {self.ticker}: {str(e)}")
    
    def stop(self):
        self.running = False

class Transaction:
    def __init__(self, date, transaction_type, ticker, shares, price=0.0):
        # Ensure date is always a datetime.date object
        if isinstance(date, datetime) and not isinstance(date, date.__class__):
            self.date = date.date()
        else:
            self.date = date
        self.type = transaction_type  # "BUY", "SELL", "NO_COST"
        self.ticker = ticker
        self.shares = shares
        self.price = price
        
    def to_dict(self):
        return {
            'date': self.date.strftime('%Y-%m-%d'),
            'type': self.type,
            'ticker': self.ticker,
            'shares': self.shares,
            'price': self.price
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),  # Ensure it's date, not datetime
            transaction_type=data['type'],
            ticker=data['ticker'],
            shares=data['shares'],
            price=data['price']
        )

class Position:
    def __init__(self, ticker, name=""):
        self.ticker = ticker
        self.name = name
        self.transactions = []
        self.current_price = 0.0
        self.dividend_yield = 0.0
        self.annual_dividend = 0.0
        self.annual_income = 0.0
        self.alreits_score = 0
        self.consensus_nav = 0.0
        self.dividend_growth_3y = 0.0  # Nova propriedade
        self.dividend_growth_5y = 0.0  # Nova propriedade
        
    def normalize_transaction_dates(self):
        """Ensures all transaction dates are datetime.date type"""
        for transaction in self.transactions:
            if isinstance(transaction.date, datetime) and not isinstance(transaction.date, date.__class__):
                transaction.date = transaction.date.date()
                
    def add_transaction(self, transaction):
        # Ensure transaction date is a date object
        if isinstance(transaction.date, datetime) and not isinstance(transaction.date, date.__class__):
            transaction.date = transaction.date.date()
            
        self.transactions.append(transaction)
        self.transactions.sort(key=lambda x: x.date)
        
    def calculate_metrics(self):
        # Calculate shares and average cost using FIFO
        fifo_queue = []
        for transaction in self.transactions:
            if transaction.type == "BUY":
                fifo_queue.append((transaction.shares, transaction.price))
            elif transaction.type == "NO_COST":
                # No-cost acquisition reduces average price
                fifo_queue.append((transaction.shares, 0.0))
            elif transaction.type == "SELL":
                # Sell shares using FIFO
                shares_to_sell = transaction.shares
                while shares_to_sell > 0 and fifo_queue:
                    shares, price = fifo_queue[0]
                    if shares <= shares_to_sell:
                        shares_to_sell -= shares
                        fifo_queue.pop(0)
                    else:
                        fifo_queue[0] = (shares - shares_to_sell, price)
                        shares_to_sell = 0
        
        # Calculate remaining shares and total cost
        total_shares = sum(shares for shares, _ in fifo_queue)
        total_cost = sum(shares * price for shares, price in fifo_queue)
        
        # Calculate average cost
        average_cost = total_cost / total_shares if total_shares > 0 else 0
        
        # Calculate yield on cost correctly:
        # Yield on Cost = (Annual Dividend per Share / Average Cost per Share) * 100
        
        # If we have the annual dividend directly from the API
        # Nos cálculos do yield on cost e annual_income, 
        # usar sempre o annual_dividend se disponível, ou calcular pelo dividend_yield e preço
        if self.annual_dividend > 0:
            yield_on_cost = (self.annual_dividend / average_cost) * 100 if average_cost > 0 else 0
            self.annual_income = self.annual_dividend * total_shares
        else:
            # Calcular annual_dividend a partir do yield
            estimated_annual_dividend = (self.dividend_yield / 100) * self.current_price
            yield_on_cost = (estimated_annual_dividend / average_cost) * 100 if average_cost > 0 else 0
            self.annual_income = estimated_annual_dividend * total_shares
        
        # If yield on cost is very high (more than 100%), it's probably an error
        if yield_on_cost > 100:
            # Check if dividend yield is correct
            print(f"Alert: Very high Yield on Cost for {self.ticker}: {yield_on_cost}%")
            print(f"  Dividend Yield: {self.dividend_yield}%")
            print(f"  Annual Dividend: {self.annual_dividend}")
            print(f"  Current Price: {self.current_price}")
            print(f"  Average Cost: {average_cost}")
               
        # Calculate total position value
        position_value = self.current_price * total_shares
		
        # Calcular Premium/Discount se houver Consensus NAV
        premium_discount = 0.0
        if self.consensus_nav > 0:
            premium_discount = (1 - (self.current_price / self.consensus_nav)) * 100
		
        return {
            'shares': total_shares,
            'average_cost': average_cost,
            'total_cost': total_cost,
            'yield_on_cost': yield_on_cost,
            'annual_income': self.annual_income,
            'profit_loss': (self.current_price - average_cost) * total_shares,
			'position_value': position_value,  # New metric for total position value
			'premium_discount': premium_discount        
        }
    
    def to_dict(self):
        return {
            'ticker': self.ticker,
            'name': self.name,
            'transactions': [t.to_dict() for t in self.transactions],
            'current_price': self.current_price,
            'dividend_yield': self.dividend_yield,
            'annual_dividend': self.annual_dividend,
            'alreits_score': self.alreits_score,
            'consensus_nav': self.consensus_nav,
            'dividend_growth_3y': self.dividend_growth_3y,  # Adicionar ao dicionário
            'dividend_growth_5y': self.dividend_growth_5y   # Adicionar ao dicionário
        }
    
    @classmethod
    def from_dict(cls, data):
        position = cls(data['ticker'], data['name'])
        position.current_price = data.get('current_price', 0.0)
        position.dividend_yield = data.get('dividend_yield', 0.0)
        position.annual_dividend = data.get('annual_dividend', 0.0)
        position.alreits_score = data.get('alreits_score', 0)
        position.consensus_nav = data.get('consensus_nav', 0.0)
        position.dividend_growth_3y = data.get('dividend_growth_3y', 0.0)  # Recuperar do dicionário
        position.dividend_growth_5y = data.get('dividend_growth_5y', 0.0)  # Recuperar do dicionário
        position.transactions = [Transaction.from_dict(t) for t in data.get('transactions', [])]
        
        # Normalize date types to avoid comparison problems
        position.normalize_transaction_dates()
        
        return position

class Portfolio:
    def __init__(self):
        self.positions = {}  # ticker -> Position
        
    def add_position(self, position):
        self.positions[position.ticker] = position
        
    def remove_position(self, ticker):
        if ticker in self.positions:
            del self.positions[ticker]
            
    def get_position(self, ticker):
        return self.positions.get(ticker)
        
    def add_transaction(self, transaction):
        ticker = transaction.ticker
        if ticker not in self.positions:
            self.positions[ticker] = Position(ticker)
        self.positions[ticker].add_transaction(transaction)
        
    def calculate_portfolio_metrics(self):
        total_cost = 0
        total_value = 0
        total_annual_income = 0
        total_profit_loss = 0
        position_values = {}
        
        # Adicionar variáveis para cálculo de CAGR ponderado
        weighted_dg_3y_sum = 0
        weighted_dg_5y_sum = 0
        total_weight = 0
        
        for ticker, position in self.positions.items():
            metrics = position.calculate_metrics()
            shares = metrics['shares']
            if shares > 0:
                total_cost += metrics['total_cost']
                position_value = position.current_price * shares
                position_values[ticker] = position_value
                current_value = position.current_price * shares
                total_value += current_value
                total_annual_income += metrics['annual_income']
                total_profit_loss += metrics['profit_loss']
        
        # Calculate portfolio-wide metrics
        # Dividend yield is already a percentage, no need to multiply by 100
        portfolio_yield = (total_annual_income / total_value) * 100 if total_value > 0 else 0
        portfolio_yield_on_cost = (total_annual_income / total_cost) * 100 if total_cost > 0 else 0
        portfolio_beta = 1.03  # Placeholder - would need to calculate based on holdings
        
        # Calcular CAGR médio ponderado
        weighted_dg_3y = 0
        weighted_dg_5y = 0
        
        if total_value > 0:
            for ticker, position in self.positions.items():
                metrics = position.calculate_metrics()
                shares = metrics['shares']
                if shares > 0:
                    position_value = position.current_price * shares
                    weight = position_value / total_value
                    weighted_dg_3y += position.dividend_growth_3y * weight
                    weighted_dg_5y += position.dividend_growth_5y * weight
        
        return {
            'total_cost': total_cost,
            'total_value': total_value,
            'total_annual_income': total_annual_income,
            'portfolio_yield': portfolio_yield,
            'portfolio_yield_on_cost': portfolio_yield_on_cost,
            'position_values': position_values,
            'total_profit_loss': total_profit_loss,
            'weighted_dg_3y': weighted_dg_3y,
            'weighted_dg_5y': weighted_dg_5y
        }
        
    def to_dict(self):
        data = {
            'positions': {ticker: position.to_dict() for ticker, position in self.positions.items()}
       }
    
        # Preserve nav_data and nav_report_date if they exist in the file
        try:
            if os.path.exists(PORTFOLIO_FILE):
                with open(PORTFOLIO_FILE, 'r') as f:
                    existing_data = json.load(f)
                    # Copy existing nav data if present
                    if 'nav_data' in existing_data:
                        data['nav_data'] = existing_data['nav_data']
                    if 'nav_report_date' in existing_data:
                        data['nav_report_date'] = existing_data['nav_report_date']
        except:
            pass
        
        return data
    
    @classmethod
    def from_dict(cls, data):
        portfolio = cls()
        for ticker, position_data in data.get('positions', {}).items():
            portfolio.positions[ticker] = Position.from_dict(position_data)
        return portfolio
		
    def apply_stock_split(self, ticker, new_shares, old_shares, split_date):
        """
        Apply a stock split to a position in the portfolio
    
        Args:
            ticker (str): The ticker symbol
            new_shares (int): Number of new shares
            old_shares (int): Number of old shares
            split_date (datetime.date): The date of the split
        
        Returns:
            bool: True if successful, False otherwise
        """
        position = self.get_position(ticker)
        if not position:
            return False
    
        # Calculate the split ratio and price adjustment factor
        split_ratio = new_shares / old_shares
        price_factor = old_shares / new_shares
    
        # Get all transactions for this position
        for transaction in position.transactions:
            # Convert transaction date to datetime.date if it's a datetime.datetime
            if isinstance(transaction.date, datetime):
                transaction_date = transaction.date.date()
            else:
                transaction_date = transaction.date
            
            # Only adjust transactions that happened before the split date
            if transaction_date < split_date:
                # Adjust shares and price
                transaction.shares = transaction.shares * split_ratio
                transaction.price = transaction.price * price_factor
    
        # If the position has a current price, adjust it too
        if position.current_price > 0:
            position.current_price = position.current_price * price_factor
    
        return True
	
    def update_consensus_nav(self, nav_data):
        """Update Consensus NAV values for positions"""
        for ticker, nav_value in nav_data.items():
            position = self.get_position(ticker)
            if position:
                position.consensus_nav = nav_value

# Modern transaction dialog
class TransactionDialog(QDialog):
    def __init__(self, parent=None, transaction_type="BUY", ticker=""):
        super().__init__(parent)
        self.setWindowTitle(f"{transaction_type.capitalize()} Transaction")
        self.setMinimumWidth(400)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.BACKGROUND};
            }}
            QLabel {{
                font-size: 13px;
                color: {Theme.TEXT_PRIMARY};
            }}
            QDateEdit, QLineEdit, QDoubleSpinBox {{
                border: 1px solid {Theme.BORDER};
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                min-height: 20px;
            }}
            QDateEdit:focus, QLineEdit:focus, QDoubleSpinBox:focus {{
                border: 1px solid {Theme.SECONDARY};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title with transaction type
        title_label = QLabel(f"New {transaction_type.capitalize()} Transaction")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        layout.addWidget(title_label)
        
        # Form container with white background
        form_container = QFrame()
        form_container.setStyleSheet(f"""
            background-color: {Theme.CARD_BG};
            border-radius: 8px;
            padding: 15px;
        """)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(15)
        
        # Date selector
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date:"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setMinimumHeight(36)
        date_layout.addWidget(self.date_edit)
        form_layout.addLayout(date_layout)
        
        # Ticker with autocomplete (could be enhanced with actual ticker suggestions)
        ticker_layout = QHBoxLayout()
        ticker_layout.addWidget(QLabel("Ticker:"))
        self.ticker_edit = QLineEdit()
        self.ticker_edit.setText(ticker)
        self.ticker_edit.setMinimumHeight(36)
        self.ticker_edit.setPlaceholderText("Enter REIT ticker symbol")
        ticker_layout.addWidget(self.ticker_edit)
        form_layout.addLayout(ticker_layout)
        
        # Shares
        shares_layout = QHBoxLayout()
        shares_layout.addWidget(QLabel("Shares:"))
        self.shares_spin = QDoubleSpinBox()
        self.shares_spin.setMinimum(0.001)
        self.shares_spin.setMaximum(1000000)
        self.shares_spin.setValue(1)
        self.shares_spin.setDecimals(3)
        self.shares_spin.setMinimumHeight(36)
        self.shares_spin.setLocale(QLocale('en_US'))
        shares_layout.addWidget(self.shares_spin)
        form_layout.addLayout(shares_layout)
        
        # Price (not shown for NO_COST transactions)
        self.price_layout = QHBoxLayout()
        self.price_layout.addWidget(QLabel("Price:"))
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setMinimum(0.01)
        self.price_spin.setMaximum(1000000)
        self.price_spin.setValue(10.00)
        self.price_spin.setDecimals(2)
        self.price_spin.setPrefix("$ ")
        self.price_spin.setMinimumHeight(36)
        self.price_spin.setLocale(QLocale('en_US'))
        self.price_layout.addWidget(self.price_spin)
        if transaction_type != "NO_COST":
            form_layout.addLayout(self.price_layout)
            
        # Add form to main layout
        layout.addWidget(form_container)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumWidth(100)
        self.cancel_button.setMinimumHeight(36)
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #f0f0f0;
                color: {Theme.TEXT_PRIMARY};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
        """)
        button_layout.addWidget(self.cancel_button)
        
        self.ok_button = QPushButton("Confirm")
        self.ok_button.setMinimumWidth(100)
        self.ok_button.setMinimumHeight(36)
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.PRIMARY};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Theme.SECONDARY};
            }}
        """)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        
        self.transaction_type = transaction_type
        
        # If it's a BUY transaction, give the OK button an accent color
        if transaction_type == "BUY":
            self.ok_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Theme.ACCENT};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #FF8C24;
                }}
            """)
        # If it's a SELL transaction, make the button red
        elif transaction_type == "SELL":
            self.ok_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Theme.DANGER};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #C53030;
                }}
            """)
    
    def get_transaction(self):
        # Get the date as a datetime.date object (without time component)
        date = self.date_edit.date().toPyDate()  # This returns a datetime.date
        ticker = self.ticker_edit.text().strip().upper()
        shares = self.shares_spin.value()
        price = self.price_spin.value() if self.transaction_type != "NO_COST" else 0.0
        
        return Transaction(
            date=date,
            transaction_type=self.transaction_type,
            ticker=ticker,
            shares=shares,
            price=price
        )

class PortfolioApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.portfolio = Portfolio()
        self.fetcher_threads = []  # Store references to thread objects
        self.show_alreits_score = False
        self.valid_alreits_scores_found = False
        self.init_ui()
        self.load_portfolio()
        self.update_portfolio_data()
        
    def fetch_alreits_scores(self):
        """Busca os scores do alreits para todos os REITs no portfólio"""
        print("DEBUG - Iniciando fetch_alreits_scores")
        # Pare threads existentes
        for fetcher in getattr(self, 'alreits_fetchers', []):
            fetcher.stop()
            fetcher.wait()
    
        self.alreits_fetchers = []
		
        # Resetar flag que indica se scores foram encontrados
        self.valid_alreits_scores_found = False  # Adicione esta linha
        print("  Resetando valid_alreits_scores_found para False")
    
        for ticker in self.portfolio.positions:
            # Crie uma thread para buscar o score deste ticker
            fetcher = AlreitsScoreFetcher(ticker)
            fetcher.score_fetched.connect(self.update_alreits_score)
            fetcher.error_occurred.connect(self.show_error_message)
            self.alreits_fetchers.append(fetcher)
            fetcher.start()
			
        # Aumentar o tempo de espera para 10 segundos
        QTimer.singleShot(10000, self.check_score_column_visibility)
        print("  Timer de 10 segundos iniciado para check_score_column_visibility")
    
    def update_alreits_score(self, ticker, score):
        """Atualiza o score do alreits para um ticker específico"""
        print(f"DEBUG - update_alreits_score: ticker={ticker}, score={score}")
		
        if score > 0:  # Apenas considere scores válidos
            print(f"  Score é válido, atualizando valid_alreits_scores_found para True")
            self.valid_alreits_scores_found = True  # Adicione esta linha
		
        position = self.portfolio.get_position(ticker)
        if position:
            position.alreits_score = score
            self.save_portfolio()
        
            # Atualiza a interface para este ticker
            for row in range(self.holdings_table.rowCount()):
                if self.holdings_table.item(row, 0).text() == ticker:
                    score_item = QTableWidgetItem(f"{score}")
                    score_item.setTextAlignment(Qt.AlignCenter)
                    
                    # Colorir com base no score
                    if score >= 80:
                        score_item.setForeground(QColor(Theme.SUCCESS))
                    elif score >= 50:
                        score_item.setForeground(QColor(Theme.ACCENT))
                    else:
                        score_item.setForeground(QColor(Theme.DANGER))
                
                    self.holdings_table.setItem(row, 12, score_item)
                    break    
	
    def check_score_column_visibility(self):
        """Verifica se algum score válido foi encontrado e atualiza a visibilidade da coluna"""
        print("DEBUG - check_score_column_visibility sendo executado!")
        old_visibility = self.show_alreits_score
    
        # Verificar se algum score válido foi encontrado
        self.show_alreits_score = self.valid_alreits_scores_found
    	
        # Adicione estas linhas de diagnóstico
        print(f"DEBUG - check_score_column_visibility:")
        print(f"  valid_alreits_scores_found: {self.valid_alreits_scores_found}")
        print(f"  show_alreits_score (antigo): {old_visibility}")
        print(f"  show_alreits_score (novo): {self.show_alreits_score}")
    
        # Se mudou o estado de visibilidade, atualize a coluna
        if old_visibility != self.show_alreits_score:
            if self.show_alreits_score:
                print("  Mostrando coluna de score")
                self.holdings_table.setColumnHidden(12, False)  # Atualizar índice para 12
            else:
                print("  Ocultando coluna de score")
                self.holdings_table.setColumnHidden(12, True)  # Atualizar índice para 12
	
    def get_usd_to_brl_rate(self):
        """Obtém a cotação atual do dólar para real brasileiro"""
        # Primeiro, tenta obter pela API
        try:
            response = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
            if response.status_code == 200:
                data = response.json()
                rate = data['rates'].get('BRL')
                if rate and rate > 0:
                    print(f"Cotação USD/BRL obtida via API: {rate}")
                    return rate
        except Exception as e:
            print(f"Erro ao obter cotação do dólar via API: {str(e)}")
    
        # Se falhar, tenta usar yfinance como backup
        try:
            # Ticker USDBRL=X representa a cotação do dólar em reais
            ticker = yf.Ticker("USDBRL=X")
            data = ticker.history(period="1d")
            
            if not data.empty:
                # Obtém o último preço de fechamento
                rate = data['Close'].iloc[-1]
                if rate and rate > 0:
                    print(f"Cotação USD/BRL obtida via yfinance: {rate}")
                    return rate
        except Exception as e:
            print(f"Erro ao obter cotação do dólar via yfinance: {str(e)}")
    
        # Valor padrão caso ambos os métodos falhem
        default_rate = 5.0
        print(f"Usando taxa padrão USD/BRL: {default_rate}")
        return default_rate
	
    def init_ui(self):
        self.setWindowTitle("REIT Portfolio Tracker")
        self.setMinimumSize(1350, 800)
        
        # Set app-wide stylesheet
        self.setStyleSheet(f"""
            QMainWindow, QDialog {{
                background-color: {Theme.BACKGROUND};
                color: {Theme.TEXT_PRIMARY};
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }}
            QLabel {{
                color: {Theme.TEXT_PRIMARY};
            }}
            QTableWidget {{
                background-color: white;
                alternate-background-color: #F5F7FA;
                border: 1px solid {Theme.BORDER};
                border-radius: 6px;
                gridline-color: #E5E9F0;
                selection-background-color: {Theme.SECONDARY};
                selection-color: white;
            }}
            QTableWidget::item {{
                padding: 6px;
            }}
            QHeaderView::section {{
                background-color: #E5E9F0;
                color: {Theme.TEXT_PRIMARY};
                padding: 6px;
                border: 1px solid {Theme.BORDER};
                font-weight: bold;
            }}
            QLineEdit {{
                border: 1px solid {Theme.BORDER};
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }}
            QLineEdit:focus {{
                border: 1px solid {Theme.SECONDARY};
            }}
            QStatusBar {{
                background-color: white;
                color: {Theme.TEXT_SECONDARY};
            }}
            QMenu {{
                background-color: white;
                border: 1px solid {Theme.BORDER};
                border-radius: 4px;
            }}
            QMenu::item {{
                padding: 8px 24px;
            }}
            QMenu::item:selected {{
                background-color: {Theme.SECONDARY};
                color: white;
            }}
            QToolBar {{
                background-color: {Theme.PRIMARY};
                border: none;
                spacing: 10px;
                padding: 5px;
            }}
        """)
        
        # Create modern toolbar
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(18, 18))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Create app title in toolbar
        title_label = QLabel("REIT Portfolio Tracker")
        title_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: white;
            margin-left: 10px;
            margin-right: 20px;
        """)
        toolbar.addWidget(title_label)
             
        # Style the toolbar actions
        toolbar.setStyleSheet(f"""
            QToolBar {{
                background-color: {Theme.PRIMARY};
                border: none;
                spacing: 10px;
                padding: 10px;
            }}
            QToolButton {{
                background-color: transparent;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }}
            QToolButton:hover {{
                background-color: {Theme.SECONDARY};
            }}
        """)
        
        
        # Create main widget
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Criar duas linhas de cards em vez de uma única linha
        # Primeira linha de cards
        top_cards_layout = QHBoxLayout()
        top_cards_layout.setSpacing(15)
        main_layout.addLayout(top_cards_layout)
        
        # Segunda linha de cards
        bottom_cards_layout = QHBoxLayout()
        bottom_cards_layout.setSpacing(15)
        main_layout.addLayout(bottom_cards_layout)
        
        # Create modern summary cards
        self.portfolio_yield_card = self.create_modern_summary_card("PORTFOLIO YIELD", "4.31%", "yield")
        self.yield_on_cost_card = self.create_modern_summary_card("YIELD ON COST", "4.61%", "cost")
        self.annual_income_card = self.create_modern_summary_card("ANNUAL INCOME", "$103", "income")
        self.monthly_income_brl_card = self.create_modern_summary_card("NET MONTHLY INCOME (BRL)", "R$ 0", "income", clickable=True)
        self.portfolio_value_card = self.create_modern_summary_card("PORTFOLIO VALUE", "$1,000", "portfolio", clickable=True)
        
        # Criar os novos cards de crescimento de dividendos
        self.dg_3y_card = self.create_modern_summary_card("PORTFOLIO DG 3y CAGR", "0.00%", "yield")
        self.dg_5y_card = self.create_modern_summary_card("PORTFOLIO DG 5y CAGR", "0.00%", "yield")
        
        # Adicionar cards à primeira linha na ordem especificada com o mesmo stretch factor para cada um
        top_cards_layout.addWidget(self.portfolio_yield_card, 1)  # Adicionando stretch factor 1
        top_cards_layout.addWidget(self.yield_on_cost_card, 1)
        top_cards_layout.addWidget(self.annual_income_card, 1)
        top_cards_layout.addWidget(self.monthly_income_brl_card, 1)
        
        # Adicionar cards à segunda linha na ordem especificada com o mesmo stretch factor
        bottom_cards_layout.addWidget(self.dg_3y_card, 1)
        bottom_cards_layout.addWidget(self.dg_5y_card, 1)
        bottom_cards_layout.addWidget(self.portfolio_value_card, 1)     
        
        # Search bar with modern styling
        search_widget = QWidget()
        search_widget.setStyleSheet(f"""
            background-color: white;
            border-radius: 6px;
        """)
        search_layout = QHBoxLayout(search_widget)
        search_layout.setContentsMargins(10, 5, 10, 5)
        
        search_icon_label = QLabel()
        search_icon = self.get_icon("search")
        if not search_icon.isNull():
            search_icon_label.setPixmap(search_icon.pixmap(16, 16))
        else:
            search_icon_label.setText("🔍")
        search_layout.addWidget(search_icon_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search holdings")
        self.search_edit.setStyleSheet("""
            border: none;
            padding: 8px;
            font-size: 13px;
        """)
        self.search_edit.textChanged.connect(self.filter_holdings)
        search_layout.addWidget(self.search_edit)
        
        # Create a horizontal layout for search and actions
        search_actions_layout = QHBoxLayout()
        search_actions_layout.addWidget(search_widget, 1)  # 1 is the stretch factor
        
        # Modern action button
        self.actions_button = StyledButton("Actions ▼")
        actions_menu = QMenu(self)
        
        view_history_action = QAction("View Transaction History", self)
        view_history_action.triggered.connect(self.show_transaction_history)
        actions_menu.addAction(view_history_action)
        
        view_analytics_action = QAction("View Analytics", self)
        view_analytics_action.triggered.connect(self.show_portfolio_analytics)
        actions_menu.addAction(view_analytics_action)
        
        actions_menu.addSeparator()
        
        export_action = QAction("Export Portfolio", self)
        export_action.triggered.connect(self.export_portfolio)
        actions_menu.addAction(export_action)
        
        self.actions_button.setMenu(actions_menu)
        search_actions_layout.addWidget(self.actions_button)
        
        main_layout.addLayout(search_actions_layout)
        
        # Create modern table
        self.holdings_table = QTableWidget()
        self.holdings_table.setColumnCount(13)  # Updated to include Percentage column
        self.holdings_table.setHorizontalHeaderLabels([
            "Ticker", "Shares", "Price", "Position Value", "Average Cost", 
            "Profit/Loss", "Dividend Yield", "Yield on Cost", 
            "Annual Income", "Percentage (%)", "DG 3y CAGR", "DG 5y CAGR", "Score by alreits"  # Added Percentage column
        ])
        
        # Modern table styling
        self.holdings_table.setShowGrid(True)
        self.holdings_table.setAlternatingRowColors(True)
        self.holdings_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.holdings_table.verticalHeader().setVisible(False)
        self.holdings_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.holdings_table.customContextMenuRequested.connect(self.show_holdings_context_menu)
        self.holdings_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.holdings_table.setStyleSheet("""
            QTableWidget {
                border-radius: 8px;
                padding: 5px;
            }
            QTableWidget::item {
                padding: 10px 5px;
            }
        """)
        
        main_layout.addWidget(self.holdings_table)
        
        # Create status bar with modern styling
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Portfolio loaded")
        
        # Set up menu bar with modern styling
        menubar = self.menuBar()
        menubar.setStyleSheet(f"""
            QMenuBar {{
                background-color: {Theme.PRIMARY};
                color: white;
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 8px 12px;
            }}
            QMenuBar::item:selected {{
                background-color: {Theme.SECONDARY};
            }}
        """)
        
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Portfolio", self)
        new_action.triggered.connect(self.new_portfolio)
        file_menu.addAction(new_action)
        
        load_action = QAction("Load Portfolio", self)
        load_action.triggered.connect(self.load_portfolio_dialog)
        file_menu.addAction(load_action)
        
        save_action = QAction("Save Portfolio", self)
        save_action.triggered.connect(self.save_portfolio)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        transactions_menu = menubar.addMenu("Transactions")
        
        buy_action = QAction("Buy", self)
        buy_action.triggered.connect(lambda: self.add_transaction("BUY"))
        transactions_menu.addAction(buy_action)
        
        sell_action = QAction("Sell", self)
        sell_action.triggered.connect(lambda: self.add_transaction("SELL"))
        transactions_menu.addAction(sell_action)
        
        no_cost_action = QAction("No-cost Acquisition", self)
        no_cost_action.triggered.connect(lambda: self.add_transaction("NO_COST"))
        transactions_menu.addAction(no_cost_action)
        
        transactions_menu.addSeparator()
        split_action = QAction("Apply Stock Split", self)
        split_action.triggered.connect(lambda: self.apply_stock_split())
        transactions_menu.addAction(split_action)
		
        # Analytics menu
        analytics_menu = menubar.addMenu("Analytics")
        
        portfolio_analytics_action = QAction("Portfolio Performance", self)
        portfolio_analytics_action.triggered.connect(self.show_portfolio_analytics)
        analytics_menu.addAction(portfolio_analytics_action)
        
        transaction_history_action = QAction("Transaction History", self)
        transaction_history_action.triggered.connect(self.show_transaction_history)
        analytics_menu.addAction(transaction_history_action)
		

        nav_data_action = QAction("NAV Data", self)
        nav_data_action.triggered.connect(self.show_nav_analysis)
        analytics_menu.addAction(nav_data_action)
        
        # Refresh menu
        refresh_menu = menubar.addMenu("Actions")
		
        refresh_action = QAction("Refresh Data", self)
        refresh_action.triggered.connect(self.update_portfolio_data)
        refresh_menu.addAction(refresh_action)
		
        # Add separator
        refresh_menu.addSeparator()
        
        # Add Report Export action
        export_report_action = QAction("Export Report", self)
        export_report_action.triggered.connect(self.export_portfolio_report)
        refresh_menu.addAction(export_report_action)
		
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
		
        # Donate menu
        donate_menu = menubar.addMenu("Donate")
        donate_action = QAction("Support this Project", self)
        donate_action.triggered.connect(self.show_donate_dialog)
        donate_menu.addAction(donate_action)
		
        self.holdings_table.setColumnHidden(12, True)
        
    def create_modern_summary_card(self, title, value, icon_type, clickable=False):
        card = ModernCard(clickable=clickable)
        
        # Estabelecer tamanho mínimo para evitar cards muito pequenos
        card.setMinimumWidth(200)
		
        # Use vertical layout for better spacing
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)
        
        # Create header layout
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        # Add icon based on type
        icon_label = QLabel()
        icon = self.get_icon(icon_type)
        if not icon.isNull():
            icon_label.setPixmap(icon.pixmap(24, 24))
        else:
            # Use text emoji as fallback if icon not found
            fallback_icons = {
                "yield": "📊",
                "cost": "💰",
                "income": "💵",
                "portfolio": "📈"
            }
            icon_label.setText(fallback_icons.get(icon_type, "$"))
            icon_label.setStyleSheet("font-size: 18px;")
        
        header_layout.addWidget(icon_label)
        
        # Add title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            color: {Theme.TEXT_SECONDARY};
            font-size: 12px;
            font-weight: bold;
        """)
        header_layout.addWidget(title_label, 1)  # 1 is stretch factor
        layout.addLayout(header_layout)
        
        # Add value
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {Theme.TEXT_PRIMARY};
            padding-top: 5px;
        """)
        layout.addWidget(value_label)
        
        # Store value label to update later
        card.value_label = value_label
        
        # Add an indicator bar at bottom (optional visual enhancement)
        indicator = QFrame()
        indicator.setFixedHeight(4)
        indicator.setFixedWidth(60)
        indicator.setStyleSheet(f"""
            background-color: {Theme.ACCENT};
            border-radius: 2px;
        """)
        layout.addWidget(indicator, 0, Qt.AlignLeft)
        
        # Make card clickable if specified
        if clickable:
            card.setCursor(Qt.PointingHandCursor)
            card.mousePressEvent = lambda e: self.handle_card_click(title, card)
        
        return card
        
    def handle_card_click(self, title, card):
        """Handle clicks on card widgets"""
        if title == "PORTFOLIO VALUE":
            self.show_portfolio_sector_allocation()
        elif title == "NET MONTHLY INCOME (BRL)":
            QMessageBox.information(
                self,
                "NET MONTHLY INCOME (BRL)",
                "The value of the annual income is converted to Brazilian reais based on the current USD/BRL exchange rate and then divided by 12 to determine the monthly amount. After this calculation, a 30% tax is applied, resulting in the final net amount to be received."
            )
        # Add other card handlers here if needed
    
    def get_icon(self, name):
        """Get an icon from the theme or return a default icon if not found"""
        icon = QIcon.fromTheme(name)
        if icon.isNull():
            # Fallback icons (can add more cases as needed)
            if name == "view-refresh":
                return QIcon()  # Empty icon as fallback
            elif name == "list-add":
                return QIcon()
            elif name == "list-remove":
                return QIcon()
            elif name == "document-new":
                return QIcon()
            elif name == "chart-line":
                return QIcon()
            elif name == "document-history":
                return QIcon()
            elif name == "search":
                return QIcon()
            elif name == "yield":
                return QIcon()
            elif name == "cost":
                return QIcon()
            elif name == "income":
                return QIcon()
            elif name == "portfolio":
                return QIcon()
            else:
                return QIcon()
        return icon
        
    def show_error_message(self, message):
        """Show error message in status bar and log to console"""
        self.statusBar.showMessage(message, 5000)  # Show for 5 seconds
        print(f"ERROR: {message}")  # Log to console for debugging
        
    def update_position_data(self, data):
        ticker = data['ticker']
        price = data['price']
        dividend_yield = data['dividend_yield']
        company_name = data.get('company_name', '')
        annual_dividend = data.get('annual_dividend', 0.0)
        dividend_growth_3y = data.get('dividend_growth_3y', 0.0)
        dividend_growth_5y = data.get('dividend_growth_5y', 0.0)
        
        position = self.portfolio.get_position(ticker)
        if position:
            position.current_price = price
            # Atualizar o dividend_yield com base no preço atual e no annual_dividend
            if annual_dividend > 0 and price > 0:
                position.dividend_yield = (annual_dividend / price) * 100
            else:
                # Fallback para o valor fornecido pela API
                position.dividend_yield = dividend_yield
            
            # Update company name if empty
            if not position.name and company_name:
                position.name = company_name
            
            # Update other fields if needed
            if annual_dividend:
                position.annual_dividend = annual_dividend
                
            # Atualizar campos de crescimento de dividendos
            position.dividend_growth_3y = dividend_growth_3y
            position.dividend_growth_5y = dividend_growth_5y
            
            self.save_portfolio()
            
            # Get updated portfolio metrics for percentage calculation
            portfolio_metrics = self.portfolio.calculate_portfolio_metrics()
            total_portfolio_value = portfolio_metrics['total_value']
            
            # Update UI for just this position
            for row in range(self.holdings_table.rowCount()):
                if self.holdings_table.item(row, 0).text() == ticker:
                    # Update price cell
                    price_item = QTableWidgetItem(f"${price:.2f}")
                    price_item.setTextAlignment(Qt.AlignCenter)
                    self.holdings_table.setItem(row, 2, price_item)
                    
                    # Update other metrics
                    metrics = position.calculate_metrics()
                    
                    # Update position value
                    position_value = metrics['position_value']
                    value_item = QTableWidgetItem(f"${position_value:.2f}")
                    value_item.setTextAlignment(Qt.AlignCenter)
                    value_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
                    self.holdings_table.setItem(row, 3, value_item)
                    
                    # Update dividend yield cell
                    div_yield_item = QTableWidgetItem(f"{position.dividend_yield:.2f}%")
                    div_yield_item.setTextAlignment(Qt.AlignCenter)
                    self.holdings_table.setItem(row, 6, div_yield_item)
                    
                    # Update profit/loss
                    profit_loss = metrics['profit_loss']
                    pl_item = QTableWidgetItem(f"${profit_loss:.2f}")
                    pl_item.setTextAlignment(Qt.AlignCenter)
                    if profit_loss < 0:
                        pl_item.setForeground(QColor(Theme.DANGER))
                    else:
                        pl_item.setForeground(QColor(Theme.SUCCESS))
                    self.holdings_table.setItem(row, 5, pl_item)
                    
                    # Update yield on cost
                    yoc = metrics['yield_on_cost']
                    yoc_item = QTableWidgetItem(f"{yoc:.2f}%")
                    yoc_item.setTextAlignment(Qt.AlignCenter)
                    self.holdings_table.setItem(row, 7, yoc_item)
                    
                    # Update annual income
                    annual_income = metrics['annual_income']
                    income_item = QTableWidgetItem(f"${annual_income:.2f}")
                    income_item.setTextAlignment(Qt.AlignCenter)
                    self.holdings_table.setItem(row, 8, income_item)
                    
                    # Update percentage column
                    percentage = (position_value / total_portfolio_value * 100) if total_portfolio_value > 0 else 0
                    percentage_item = QTableWidgetItem(f"{percentage:.2f}%")
                    percentage_item.setTextAlignment(Qt.AlignCenter)
                    self.holdings_table.setItem(row, 9, percentage_item)
                    
                    # Update DG 3y CAGR
                    dg_3y_item = QTableWidgetItem(f"{dividend_growth_3y:.2f}%")
                    dg_3y_item.setTextAlignment(Qt.AlignCenter)
                    # Colorir com base no crescimento
                    if dividend_growth_3y > 5:
                        dg_3y_item.setForeground(QColor(Theme.SUCCESS))
                    elif dividend_growth_3y <= 0:
                        dg_3y_item.setForeground(QColor(Theme.DANGER))
                    elif dividend_growth_3y > 0:
                        dg_3y_item.setForeground(QColor(Theme.ACCENT))
                    self.holdings_table.setItem(row, 10, dg_3y_item)
                    
                    # Update DG 5y CAGR
                    dg_5y_item = QTableWidgetItem(f"{dividend_growth_5y:.2f}%")
                    dg_5y_item.setTextAlignment(Qt.AlignCenter)
                    # Colorir com base no crescimento
                    if dividend_growth_5y > 5:
                        dg_5y_item.setForeground(QColor(Theme.SUCCESS))
                    elif dividend_growth_5y <= 0:
                        dg_5y_item.setForeground(QColor(Theme.DANGER))
                    elif dividend_growth_5y > 0:
                        dg_5y_item.setForeground(QColor(Theme.ACCENT))
                    self.holdings_table.setItem(row, 11, dg_5y_item)
                    
                    # Apply background color based on row number for consistent styling
                    bg_color = QColor("#FFFFFF") if row % 2 == 0 else QColor("#F5F7FA")
                    for col in range(self.holdings_table.columnCount()):
                        item = self.holdings_table.item(row, col)
                        if item:
                            item.setBackground(bg_color)
                    
                    break
            
            # Also update summary cards
            self.update_summary_cards()
    
    def update_portfolio_data(self):
        """Atualiza todos os dados do portfólio, incluindo preços e dividend yields"""
        self.statusBar.showMessage("Atualizando dados do portfólio...")
        self.fetch_stock_data()
        self.fetch_alreits_scores()
		
        # Programar uma atualização da interface após um pequeno atraso para dar tempo às threads terminarem
        QTimer.singleShot(2000, self.refresh_ui)
    
    def refresh_ui(self):
        """Atualiza a interface do usuário com os dados mais recentes"""
        print("Refreshing UI - Checking column visibility")
        self.update_holdings_table()
        self.update_summary_cards()
        
        # Garantir que as colunas de DG CAGR estejam visíveis
        self.holdings_table.setColumnHidden(10, False)  # DG 3y CAGR
        self.holdings_table.setColumnHidden(11, False)  # DG 5y CAGR
        
        # Aplicar configuração de visibilidade para a coluna de score
        self.holdings_table.setColumnHidden(12, not self.show_alreits_score)
        
        self.statusBar.showMessage("Dados do portfólio atualizados", 3000)
        
    def fetch_stock_data(self):
        # Stop any existing threads
        for fetcher in self.fetcher_threads:
            fetcher.stop()
            fetcher.wait()  # Wait for thread to finish
            
        self.fetcher_threads = []  # Clear the list
        
        for ticker in self.portfolio.positions:
            # Create a thread to fetch data for this ticker
            fetcher = StockDataFetcher(ticker)
            fetcher.data_fetched.connect(self.update_position_data)
            fetcher.error_occurred.connect(self.show_error_message)
            self.fetcher_threads.append(fetcher)  # Store the reference
            fetcher.start()
    
    def update_holdings_table(self):
        self.holdings_table.setRowCount(0)
		
		# Primeiro calcular o valor total do portfólio para referência
        portfolio_metrics = self.portfolio.calculate_portfolio_metrics()
        total_portfolio_value = portfolio_metrics['total_value']
        
        row = 0
        for ticker, position in self.portfolio.positions.items():
            metrics = position.calculate_metrics()
            shares = metrics['shares']
            
            if shares <= 0:
                continue
                
            self.holdings_table.insertRow(row)
            
            # Ticker
            ticker_item = QTableWidgetItem(ticker)
            ticker_item.setTextAlignment(Qt.AlignCenter)
            ticker_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
            self.holdings_table.setItem(row, 0, ticker_item)
            
            # Shares
            shares_item = QTableWidgetItem(f"{int(shares) if shares.is_integer() else shares}")
            shares_item.setTextAlignment(Qt.AlignCenter)
            self.holdings_table.setItem(row, 1, shares_item)
            
            # Current Price
            price_item = QTableWidgetItem(f"${position.current_price:.2f}")
            price_item.setTextAlignment(Qt.AlignCenter)
            self.holdings_table.setItem(row, 2, price_item)
                      
            # Average Cost
            avg_cost = metrics['average_cost']
            avg_cost_item = QTableWidgetItem(f"${avg_cost:.2f}")
            avg_cost_item.setTextAlignment(Qt.AlignCenter)
            self.holdings_table.setItem(row, 4, avg_cost_item)
            
            # Profit/Loss
            profit_loss = metrics['profit_loss']
            pl_item = QTableWidgetItem(f"${profit_loss:.2f}")
            pl_item.setTextAlignment(Qt.AlignCenter)
            pl_item.setForeground(QColor("red") if profit_loss < 0 else QColor("green"))
            self.holdings_table.setItem(row, 5, pl_item)
            
            # Dividend Yield - usando o valor já calculado na posição
            div_yield = position.dividend_yield
            div_yield_item = QTableWidgetItem(f"{div_yield:.2f}%")    
            div_yield_item.setTextAlignment(Qt.AlignCenter)
            self.holdings_table.setItem(row, 6, div_yield_item)
            
            # Yield on Cost - já é porcentagem, exibir diretamente
            # Garantir que estamos exibindo o valor correto (não multiplicado por 100)
            yoc = metrics['yield_on_cost'] 
            yoc_item = QTableWidgetItem(f"{yoc:.2f}%")
            yoc_item.setTextAlignment(Qt.AlignCenter)
            self.holdings_table.setItem(row, 7, yoc_item)
            
            # Annual Income
            annual_income = metrics['annual_income']
            income_item = QTableWidgetItem(f"${annual_income:.2f}")
            income_item.setTextAlignment(Qt.AlignCenter)
            self.holdings_table.setItem(row, 8, income_item)
			
            # Update position value
            position_value = metrics['position_value']
            value_item = QTableWidgetItem(f"${position_value:.2f}")
            value_item.setTextAlignment(Qt.AlignCenter)
            self.holdings_table.setItem(row, 3, value_item)
			
			# Porcentagem do portfolio
            position_value = metrics['position_value']
            percentage = (position_value / total_portfolio_value * 100) if total_portfolio_value > 0 else 0
            percentage_item = QTableWidgetItem(f"{percentage:.2f}%")
            percentage_item.setTextAlignment(Qt.AlignCenter)
            self.holdings_table.setItem(row, 9, percentage_item)
			
            # DG 3y CAGR
            dg_3y = position.dividend_growth_3y
            dg_3y_item = QTableWidgetItem(f"{dg_3y:.2f}%")
            dg_3y_item.setTextAlignment(Qt.AlignCenter)
            # Colorir com base no crescimento (verde para positivo, vermelho para negativo)
            if dg_3y > 5:
                dg_3y_item.setForeground(QColor(Theme.SUCCESS))
            elif dg_3y <= 0:
                dg_3y_item.setForeground(QColor(Theme.DANGER))
            elif dg_3y > 0:
                dg_3y_item.setForeground(QColor(Theme.ACCENT))
            self.holdings_table.setItem(row, 10, dg_3y_item)
            
            # DG 5y CAGR
            dg_5y = position.dividend_growth_5y
            dg_5y_item = QTableWidgetItem(f"{dg_5y:.2f}%")
            dg_5y_item.setTextAlignment(Qt.AlignCenter)
            # Colorir com base no crescimento
            if dg_5y > 5:
                dg_5y_item.setForeground(QColor(Theme.SUCCESS))
            elif dg_5y <= 0:
                dg_5y_item.setForeground(QColor(Theme.DANGER))
            elif dg_5y > 0:
                dg_5y_item.setForeground(QColor(Theme.ACCENT))
            self.holdings_table.setItem(row, 11, dg_5y_item)
            
            # Adicionar a coluna de score
            score = position.alreits_score
            score_item = QTableWidgetItem(f"{score}")
            score_item.setTextAlignment(Qt.AlignCenter)
            # Colorir com base no score
            if score >= 80:
                score_item.setForeground(QColor(Theme.SUCCESS))
            elif score >= 50:
                score_item.setForeground(QColor(Theme.ACCENT))
            else:
                score_item.setForeground(QColor(Theme.DANGER))
            self.holdings_table.setItem(row, 12, score_item)
			
            row += 1
    
    def update_summary_cards(self):
        metrics = self.portfolio.calculate_portfolio_metrics()
        
        # Update cards
        self.portfolio_yield_card.value_label.setText(f"{metrics['portfolio_yield']:.2f}%")
        self.yield_on_cost_card.value_label.setText(f"{metrics['portfolio_yield_on_cost']:.2f}%")
        self.annual_income_card.value_label.setText(f"${metrics['total_annual_income']:.2f}")
    
        # Calculate profit/loss and format it
        profit_loss = metrics['total_profit_loss']
        profit_loss_color = Theme.SUCCESS if profit_loss > 0 else Theme.DANGER
    
        # Format main value with profit/loss
        main_value = f"${metrics['total_value']:,.2f}"
        pl_display = f" ({'+' if profit_loss > 0 else ''} ${abs(profit_loss):.2f})"
    
        # Create HTML structure with just the main value and profit/loss
        full_text = f"{main_value}<span style='font-size:14px; color:{profit_loss_color};'>{pl_display}</span>"
        
        # Set rich text to the value label
        self.portfolio_value_card.value_label.setText(full_text)
        self.portfolio_value_card.value_label.setTextFormat(Qt.RichText)
        
        # Calculate monthly income in BRL
        usd_brl_rate = self.get_usd_to_brl_rate()
        monthly_income_usd = metrics['total_annual_income'] / 12
        monthly_income_brl = monthly_income_usd * usd_brl_rate * 0.7
    
        # Update monthly income BRL card
        self.monthly_income_brl_card.value_label.setText(f"R$ {monthly_income_brl:.2f}")
        
        # Atualizar novos cards de crescimento de dividendos
        self.dg_3y_card.value_label.setText(f"{metrics['weighted_dg_3y']:.2f}%")
        self.dg_5y_card.value_label.setText(f"{metrics['weighted_dg_5y']:.2f}%")
        
        # Definir cores para os cards de DG baseado no valor
        dg_3y_value = metrics['weighted_dg_3y']
        if dg_3y_value > 5:
            self.dg_3y_card.value_label.setStyleSheet(f"""
                font-size: 24px;
                font-weight: bold;
                color: {Theme.SUCCESS};
                padding-top: 5px;
            """)
        elif dg_3y_value <= 0:
            self.dg_3y_card.value_label.setStyleSheet(f"""
                font-size: 24px;
                font-weight: bold;
                color: {Theme.DANGER};
                padding-top: 5px;
            """)
        else:
            self.dg_3y_card.value_label.setStyleSheet(f"""
                font-size: 24px;
                font-weight: bold;
                color: {Theme.TEXT_PRIMARY};
                padding-top: 5px;
            """)
            
        dg_5y_value = metrics['weighted_dg_5y']
        if dg_5y_value > 5:
            self.dg_5y_card.value_label.setStyleSheet(f"""
                font-size: 24px;
                font-weight: bold;
                color: {Theme.SUCCESS};
                padding-top: 5px;
            """)
        elif dg_5y_value <= 0:
            self.dg_5y_card.value_label.setStyleSheet(f"""
                font-size: 24px;
                font-weight: bold;
                color: {Theme.DANGER};
                padding-top: 5px;
            """)
        else:
            self.dg_5y_card.value_label.setStyleSheet(f"""
                font-size: 24px;
                font-weight: bold;
                color: {Theme.TEXT_PRIMARY};
                padding-top: 5px;
            """)
    
    def filter_holdings(self):
        search_text = self.search_edit.text().lower()
        
        for row in range(self.holdings_table.rowCount()):
            ticker = self.holdings_table.item(row, 0).text().lower()
            
            if search_text in ticker:
                self.holdings_table.setRowHidden(row, False)
            else:
                self.holdings_table.setRowHidden(row, True)
    
    def show_holdings_context_menu(self, position):
        # Get the selected row
        row = self.holdings_table.currentRow()
        if row < 0:
            return
            
        # Get the ticker
        ticker = self.holdings_table.item(row, 0).text()
        
        # Create menu
        menu = QMenu(self)
        
        # Add actions
        buy_action = QAction(f"Buy more {ticker}", self)
        buy_action.triggered.connect(lambda: self.add_transaction("BUY", ticker))
        menu.addAction(buy_action)
        
        sell_action = QAction(f"Sell {ticker}", self)
        sell_action.triggered.connect(lambda: self.add_transaction("SELL", ticker))
        menu.addAction(sell_action)
        
        no_cost_action = QAction(f"Add No-cost Acquisition for {ticker}", self)
        no_cost_action.triggered.connect(lambda: self.add_transaction("NO_COST", ticker))
        menu.addAction(no_cost_action)
        
        menu.addSeparator()
        
        view_history_action = QAction(f"View {ticker} Transactions", self)
        view_history_action.triggered.connect(lambda: self.show_specific_transactions(ticker))
        menu.addAction(view_history_action)
		
        menu.addSeparator()
    
        apply_split_action = QAction(f"Apply Stock Split to {ticker}", self)
        apply_split_action.triggered.connect(lambda: self.apply_stock_split(ticker))
        menu.addAction(apply_split_action)
        
        # Show menu
        menu.exec_(self.holdings_table.viewport().mapToGlobal(position))
    
    def show_specific_transactions(self, ticker):
        from transaction_history import TransactionHistoryDialog
        
        dialog = TransactionHistoryDialog(self, self.portfolio)
        # Set the filter to the specified ticker
        ticker_index = dialog.ticker_combo.findText(ticker)
        if ticker_index >= 0:
            dialog.ticker_combo.setCurrentIndex(ticker_index)
        dialog.transaction_deleted.connect(self.delete_transaction)
        dialog.exec_()
    
    def add_transaction(self, transaction_type="BUY", ticker=""):
        dialog = TransactionDialog(self, transaction_type, ticker)
        if dialog.exec_():
            transaction = dialog.get_transaction()
            if not transaction.ticker:
                QMessageBox.warning(self, "Invalid Ticker", "Please enter a valid ticker symbol.")
                return
                
            self.portfolio.add_transaction(transaction)
            self.save_portfolio()
            self.update_portfolio_data()
            self.statusBar.showMessage(f"{transaction_type} transaction added for {transaction.ticker}")
    
    def delete_transaction(self, index, ticker):
        position = self.portfolio.get_position(ticker)
        if position and 0 <= index < len(position.transactions):
            # Remove the transaction
            position.transactions.pop(index)
            
            # Check if position is now empty
            if not position.transactions:
                self.portfolio.remove_position(ticker)
                
            # Save and update
            self.save_portfolio()
            self.update_portfolio_data()
            self.statusBar.showMessage(f"Transaction deleted for {ticker}")
    
    def new_portfolio(self):
        reply = QMessageBox.question(
            self, 
            "New Portfolio", 
            "Are you sure you want to create a new portfolio? This will delete your current portfolio.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.portfolio = Portfolio()
            self.save_portfolio()
            self.update_portfolio_data()
            self.statusBar.showMessage("New portfolio created")
    
    def load_portfolio(self):
        if os.path.exists(PORTFOLIO_FILE):
            try:
                with open(PORTFOLIO_FILE, 'r') as f:
                    data = json.load(f)
                    self.portfolio = Portfolio.from_dict(data)
                    
                    # Carregar dados de NAV (se existirem)
                    if 'nav_data' in data:
                        self.nav_data = data['nav_data']
                        self.nav_report_date = data.get('nav_report_date', '')
                    
                        # Atualizar valores de NAV para cada posição
                        for ticker, nav_value in self.nav_data.items():
                            position = self.portfolio.get_position(ticker)
                            if position:
                                position.consensus_nav = nav_value
                    
                self.statusBar.showMessage("Portfolio loaded successfully")
            except Exception as e:
                self.statusBar.showMessage(f"Error loading portfolio: {str(e)}")
                # Create a backup of the corrupted file
                if os.path.exists(PORTFOLIO_FILE):
                    backup_file = f"{PORTFOLIO_FILE}.bak"
                    try:
                        os.rename(PORTFOLIO_FILE, backup_file)
                        self.statusBar.showMessage(f"Corrupted file backed up as {backup_file}")
                    except:
                        pass
        else:
            # Criar um portfólio vazio, sem amostras
            self.create_sample_portfolio()
            self.save_portfolio()
    
    def load_portfolio_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Load Portfolio", 
            "", 
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self.portfolio = Portfolio.from_dict(data)
                self.update_portfolio_data()
                self.statusBar.showMessage(f"Portfolio loaded from {file_path}")
            except Exception as e:
                self.statusBar.showMessage(f"Error loading portfolio: {str(e)}")
    
    def save_portfolio(self):
        try:
            # Get existing data to preserve nav_data
            existing_data = {}
            if os.path.exists(PORTFOLIO_FILE):
                try:
                    with open(PORTFOLIO_FILE, 'r') as f:
                        existing_data = json.load(f)
                except:
                    pass
        
            # Get portfolio data
            portfolio_data = self.portfolio.to_dict()
        
            # Preserve nav_data if it exists in file
            if 'nav_data' in existing_data:
                portfolio_data['nav_data'] = existing_data['nav_data']
            if 'nav_report_date' in existing_data:
                portfolio_data['nav_report_date'] = existing_data['nav_report_date']
        
            # Save back to file
            with open(PORTFOLIO_FILE, 'w') as f:
                json.dump(portfolio_data, f, indent=2)
            self.statusBar.showMessage("Portfolio saved")
        except Exception as e:
            self.statusBar.showMessage(f"Error saving portfolio: {str(e)}")
    
    def export_portfolio(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Portfolio", 
            "reit_portfolio_export.csv", 
            "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    # Write header
                    f.write("Ticker,Shares,Current Price,Average Cost,Profit/Loss,Dividend Yield,Yield on Cost,Annual Income\n")
                    
                    # Write each position
                    for ticker, position in self.portfolio.positions.items():
                        metrics = position.calculate_metrics()
                        shares = metrics['shares']
                        
                        if shares > 0:
                            f.write(f"{ticker},{shares:.2f},{position.current_price:.2f}," +
                                    f"{metrics['average_cost']:.2f},{metrics['profit_loss']:.2f}," +
                                    f"{position.dividend_yield:.2f},{metrics['yield_on_cost']:.2f}," +
                                    f"{metrics['annual_income']:.2f}\n")
                            
                self.statusBar.showMessage(f"Portfolio exported to {file_path}")
            except Exception as e:
                self.statusBar.showMessage(f"Error exporting portfolio: {str(e)}")
    
    def create_sample_portfolio(self):
        # Cria um portfólio vazio em vez de preencher com amostras
        # O objeto Portfolio já foi inicializado no construtor da classe PortfolioApp
        # Não precisa fazer nada aqui, apenas deixar o portfólio vazio
        self.statusBar.showMessage("New empty portfolio created")
            
    def show_portfolio_sector_allocation(self):
        """Show sector allocation pie chart"""
        try:
            # Verificar se o portfólio tem posições
            if not self.portfolio.positions:
                QMessageBox.warning(self, "Sem Dados", "Seu portfólio está vazio. Adicione transações primeiro.")
                return
            
            # Verificar se temos dados válidos
            has_valid_data = False
            for ticker, position in self.portfolio.positions.items():
                metrics = position.calculate_metrics()
                if metrics['shares'] > 0:
                    has_valid_data = True
                    break
            
            if not has_valid_data:
                QMessageBox.warning(self, "Sem Dados", "Não há posições com ações no seu portfólio.")
                return
            
            # Mostrar cursor de espera
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            from sector_allocation import SectorAllocationDialog
            
            dialog = SectorAllocationDialog(self, self.portfolio)
            
            # Restaurar cursor normal
            QApplication.restoreOverrideCursor()
            
            dialog.exec_()
        except Exception as e:
            # Restaurar cursor normal em caso de erro
            QApplication.restoreOverrideCursor()
            
            print(f"Erro ao mostrar alocação setorial: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erro", f"Falha ao exibir o gráfico de alocação setorial: {str(e)}")
    
    def show_portfolio_analytics(self):
        """Mostra o diálogo de análise do portfólio"""
        try:
            # Verificar se o portfólio tem posições
            if not self.portfolio.positions:
                QMessageBox.warning(self, "Sem Dados", "Seu portfólio está vazio. Adicione transações primeiro.")
                return
            
            # Verificar se temos dados válidos
            has_valid_data = False
            for ticker, position in self.portfolio.positions.items():
                metrics = position.calculate_metrics()
                if metrics['shares'] > 0:
                    has_valid_data = True
                    break
            
            if not has_valid_data:
                QMessageBox.warning(self, "Sem Dados", "Não há posições com ações no seu portfólio.")
                return
            
            # Mostrar cursor de espera
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            from data_visualization import PortfolioAnalyticsDialog
            
            dialog = PortfolioAnalyticsDialog(self, self.portfolio)
            
            # Restaurar cursor normal
            QApplication.restoreOverrideCursor()
            
            dialog.exec_()
        except Exception as e:
            # Restaurar cursor normal em caso de erro
            QApplication.restoreOverrideCursor()
            
            print(f"Erro ao mostrar análise do portfólio: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erro", f"Falha ao abrir a análise do portfólio: {str(e)}")
    
    def show_transaction_history(self):
        """Mostra o histórico de transações"""
        try:
            from transaction_history import TransactionHistoryDialog
            
            dialog = TransactionHistoryDialog(self, self.portfolio)
            dialog.transaction_deleted.connect(self.delete_transaction)
            dialog.exec_()
        except Exception as e:
            print(f"Erro ao mostrar histórico de transações: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erro", f"Falha ao abrir o histórico de transações: {str(e)}")

    # Adicione esta função com as outras funções de diálogo (como show_portfolio_analytics)
    def show_nav_analysis(self):
        """Show NAV data analysis dialog"""
        try:
            # Verificar se o portfólio tem posições
            if not self.portfolio.positions:
                QMessageBox.warning(self, "Sem Dados", "Seu portfólio está vazio. Adicione transações primeiro.")
                return
        
            # Verificar se temos dados válidos
            has_valid_data = False
            for ticker, position in self.portfolio.positions.items():
                metrics = position.calculate_metrics()
                if metrics['shares'] > 0:
                    has_valid_data = True
                    break
        
            if not has_valid_data:
                QMessageBox.warning(self, "Sem Dados", "Não há posições com ações no seu portfólio.")
                return
        
            # Mostrar cursor de espera
            QApplication.setOverrideCursor(Qt.WaitCursor)
        
            dialog = NAVDialog(self, self.portfolio)
        
            # Restaurar cursor normal
            QApplication.restoreOverrideCursor()
        
            dialog.exec_()
        except Exception as e:
            # Restaurar cursor normal em caso de erro
            QApplication.restoreOverrideCursor()
        
            print(f"Erro ao mostrar análise NAV: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erro", f"Falha ao abrir a análise NAV: {str(e)}")


    def apply_stock_split(self, ticker=""):
        """Show dialog to apply a stock split to a specific ticker"""
        dialog = SplitDialog(self, ticker)
    
        if dialog.exec_():
            split_info = dialog.get_split_info()
        
            # Validate inputs
            ticker = split_info['ticker']
            if not ticker:
                QMessageBox.warning(self, "Invalid Ticker", "Please enter a valid ticker symbol.")
                return
                
            # Check if ticker exists in portfolio
            position = self.portfolio.get_position(ticker)
            if not position:
                QMessageBox.warning(
                    self, 
                    "Ticker Not Found", 
                    f"Ticker {ticker} not found in your portfolio. Please add a position first."
                )
                return
            
            # Confirm with user
            new_shares = split_info['new_shares']
            old_shares = split_info['old_shares']
        
            message = f"Apply a {new_shares}:{old_shares} "
            if new_shares > old_shares:
                message += "split"
            elif new_shares < old_shares:
                message += "reverse split"
            else:
                message += "adjustment (no effect)"
            
            message += f" to {ticker}?\n\nThis will adjust all transactions and current prices."
        
            reply = QMessageBox.question(
                self, 
                "Confirm Stock Split", 
                message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
        
            if reply == QMessageBox.Yes:
                # Apply the split
                success = self.portfolio.apply_stock_split(
                    ticker,
                    split_info['new_shares'],
                    split_info['old_shares'],
                    split_info['split_date']
                )
            
                if success:
                    # Save and update
                    self.save_portfolio()
                    self.update_portfolio_data()
                
                    status_message = f"Applied {new_shares}:{old_shares} "
                    if new_shares > old_shares:
                        status_message += "split"
                    elif new_shares < old_shares:
                        status_message += "reverse split"
                    else:
                        status_message += "adjustment"
                    
                    status_message += f" to {ticker}"
                    self.statusBar.showMessage(status_message)
                
                    QMessageBox.information(
                        self,
                        "Stock Split Applied",
                        f"Successfully applied {new_shares}:{old_shares} adjustment to {ticker}."
                    )
                else:
                    QMessageBox.warning(
                        self,
                       "Error",
                        f"Failed to apply stock split to {ticker}."
                    )   
    def export_portfolio_report(self):
        """Export a comprehensive portfolio report in PDF format"""
        # Import reportlab here to avoid issues if the dependency is not installed
        try:
            import reportlab
        except ImportError:
            QMessageBox.critical(
                self,
                "Missing Dependency",
                "This feature requires the reportlab and matplotlib packages.\n\n"
                "Please install them using pip:\n"
                "pip install reportlab matplotlib"
            )
            return
            
        # Importar o diálogo de seleção de seções
        from report_generator import ReportSectionsDialog
        
        # Mostrar diálogo de seleção de seções
        sections_dialog = ReportSectionsDialog(self)
        if not sections_dialog.exec_():
            return  # Usuário cancelou
            
        # Obter seções selecionadas
        selected_sections = sections_dialog.get_selected_sections()
        
        # Ask user where to save the report
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Portfolio Report", 
            "reit_portfolio_report.pdf", 
            "PDF Files (*.pdf)"
        )
        
        if not file_path:
            return  # User cancelled
            
        try:
            # Show wait cursor
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            # Import here to avoid circular imports
            from report_generator import PortfolioReportGenerator
            
            # Create report generator
            report_generator = PortfolioReportGenerator(self.portfolio, self)
            
            # Generate the report with selected sections
            report_generator.generate_report(file_path, selected_sections)
            
            # Restore cursor
            QApplication.restoreOverrideCursor()
            
            self.statusBar.showMessage(f"Portfolio report exported to {file_path}")
            
            # Ask if user wants to open the report
            reply = QMessageBox.question(
                self, 
                "Open Report", 
                f"Report saved to {file_path}. Would you like to open it now?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # Open the report with default PDF viewer
                if sys.platform == 'win32':
                    os.startfile(file_path)
                elif sys.platform == 'darwin':  # macOS
                    os.system(f'open "{file_path}"')
                else:  # Linux
                    os.system(f'xdg-open "{file_path}"')
                    
        except Exception as e:
            # Restore cursor in case of error
            QApplication.restoreOverrideCursor()
            
            error_message = f"Error exporting portfolio report: {str(e)}"
            self.statusBar.showMessage(error_message)
            
            print(error_message)
            import traceback
            traceback.print_exc()
            
            QMessageBox.critical(self, "Error", f"Failed to export portfolio report:\n\n{str(e)}")
    
    def show_about(self):
        QMessageBox.about(
            self,
            "About REIT Portfolio Tracker",
            """
            <h1>REIT Portfolio Tracker</h1>
            <p>A Python application to track and analyze your REIT investments.</p>
            <p>Features:</p>
            <ul>
                <li>Track buy, sell, and no-cost acquisition transactions</li>
                <li>Calculate average price using FIFO method</li>
                <li>Automatically fetch dividend yields</li>
                <li>Calculate portfolio metrics such as yield on cost and dividend growth</li>
                <li>Visualize portfolio performance and income</li>
                <li>View and manage transaction history</li>
                <li>Track premium/discount compared to NAV (manual input)</li>
                <li>Fetches the score values from the site alreits.com.</li>
                <li>Generate professional report</li>
            </ul>
            """
        )
    
    def show_donate_dialog(self):
        """Show a dialog for donations"""
        try:
            # Import here to avoid circular imports
            from donate_dialog import DonateDialog
            
            dialog = DonateDialog(self)
            dialog.exec_()
        except Exception as e:
            print(f"Error showing donation dialog: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to open donation dialog: {str(e)}")
	
    def closeEvent(self, event):
        # Stop all threads
        for fetcher in self.fetcher_threads:
            fetcher.stop()
            fetcher.wait()  # Wait for thread to finish
            
        # Save portfolio before closing
        self.save_portfolio()
        event.accept()
