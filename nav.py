import os
import sys
import json
from datetime import datetime
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QMessageBox, QProgressBar, QFrame, QFormLayout, QDateEdit,
                             QDoubleSpinBox)
from PyQt5.QtCore import Qt, QDate, QLocale
from PyQt5.QtGui import QFont, QColor
from theme import Theme

# Constante para o arquivo de portfólio
PORTFOLIO_FILE = "reit_portfolio.json"

class NAVDialog(QDialog):
    def __init__(self, parent=None, portfolio=None):
        super().__init__(parent)
        self.portfolio = portfolio
        self.nav_data = {}
        self.report_date = datetime.now().strftime('%d/%m/%Y')
        
        self.setWindowTitle("REIT NAV Analysis")
        self.setMinimumSize(800, 600)
        self.load_nav_data()
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Title
        title_label = QLabel("REIT NAV Analysis")
        title_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {Theme.TEXT_PRIMARY};
        """)
        main_layout.addWidget(title_label)
        
        # Report date input section
        date_frame = QFrame()
        date_frame.setStyleSheet(f"""
            background-color: {Theme.CARD_BG};
            border-radius: 8px;
            padding: 15px;
        """)
        date_layout = QHBoxLayout(date_frame)
        
        date_layout.addWidget(QLabel("Report Date:"))
        
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        
        # Set the date to today or existing date
        try:
            if self.report_date:
                qdate = QDate.fromString(self.report_date, "dd/MM/yyyy")
                if qdate.isValid():
                    self.date_edit.setDate(qdate)
                else:
                    self.date_edit.setDate(QDate.currentDate())
            else:
                self.date_edit.setDate(QDate.currentDate())
        except:
            self.date_edit.setDate(QDate.currentDate())
            
        self.date_edit.dateChanged.connect(self.date_changed)
        date_layout.addWidget(self.date_edit)
        
        main_layout.addWidget(date_frame)
        
        # Instructions
        instruction_label = QLabel(
            "Enter Consensus NAV values for each ticker in your portfolio. "
            "These values will be saved and used to calculate Premium/Discount metrics."
        )
        instruction_label.setWordWrap(True)
        instruction_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY};")
        main_layout.addWidget(instruction_label)
        
        # Table for NAV input
        self.nav_table = QTableWidget()
        self.nav_table.setColumnCount(4)
        self.nav_table.setHorizontalHeaderLabels([
            "Ticker", "Current Price ($)", "Consensus NAV ($)", "Premium/Discount"
        ])
        
        # Table styling
        self.nav_table.setShowGrid(True)
        self.nav_table.setAlternatingRowColors(True)
        self.nav_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.nav_table.verticalHeader().setVisible(False)
        self.nav_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: white;
                alternate-background-color: #F5F7FA;
                border: 1px solid {Theme.BORDER};
                border-radius: 6px;
                gridline-color: #E5E9F0;
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QHeaderView::section {{
                background-color: #E5E9F0;
                color: {Theme.TEXT_PRIMARY};
                padding: 8px;
                border: 1px solid {Theme.BORDER};
                font-weight: bold;
            }}
        """)
        
        # Habilitar ordenação da tabela
        self.nav_table.setSortingEnabled(True)
        
        # Conectar o evento de clique no cabeçalho
        self.nav_table.horizontalHeader().sectionClicked.connect(self.header_clicked)
		
        main_layout.addWidget(self.nav_table)
        
        # Populate table with portfolio data
        self.update_nav_table()
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save NAV Data")
        self.save_button.setMinimumWidth(120)
        self.save_button.setMinimumHeight(36)
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.clicked.connect(self.save_nav_data)
        self.save_button.setStyleSheet(f"""
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
        button_layout.addWidget(self.save_button)
        
        button_layout.addStretch()
        
        self.close_button = QPushButton("Close")
        self.close_button.setMinimumWidth(100)
        self.close_button.setMinimumHeight(36)
        self.close_button.clicked.connect(self.reject)
        self.close_button.setStyleSheet(f"""
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
        button_layout.addWidget(self.close_button)
        
        main_layout.addLayout(button_layout)
    
    def load_nav_data(self):
        """Load existing NAV data from the portfolio file"""
        try:
            if os.path.exists(PORTFOLIO_FILE):
                with open(PORTFOLIO_FILE, 'r') as f:
                    data = json.load(f)
                    
                # Extract NAV data and report date if they exist
                if 'nav_data' in data:
                    self.nav_data = data['nav_data']
                if 'nav_report_date' in data:
                    self.report_date = data['nav_report_date']
                    
                print(f"Loaded NAV data for {len(self.nav_data)} tickers")
        except Exception as e:
            print(f"Error loading NAV data: {str(e)}")
    
    def update_nav_table(self):
        """Populate table with tickers from portfolio"""
        if not self.portfolio:
            return
                
        # Clear table
        self.nav_table.setRowCount(0)
        
        # Coletar dados para ordenação
        all_data = []
        
        # Coletar dados do portfolio
        for ticker, position in self.portfolio.positions.items():
            # Skip positions with no shares
            metrics = position.calculate_metrics()
            if metrics['shares'] <= 0:
                continue
                    
            # Current Price
            current_price = position.current_price
                
            # Consensus NAV (get existing value or default to 0.0)
            nav_value = self.nav_data.get(ticker, 0.0)
                
            # Calculate Premium/Discount
            premium_discount = 0.0
            if nav_value > 0:
                # Fórmula: ((current_price / nav_value) - 1) * 100
                premium_discount = ((current_price / nav_value) - 1) * 100
                    
            all_data.append({
                'ticker': ticker,
                'price': current_price,
                'nav_value': nav_value,
                'premium_discount': premium_discount
            })
        
        # Ordenar por Premium/Discount (do valor mais negativo para o mais positivo)
        all_data.sort(key=lambda x: x['premium_discount'])
        
        # Preencher a tabela com dados ordenados
        for idx, item in enumerate(all_data):
            ticker = item['ticker']
            current_price = item['price']
            nav_value = item['nav_value']
            premium_discount = item['premium_discount']
            
            # Inserir nova linha
            row = self.nav_table.rowCount()
            self.nav_table.insertRow(row)
            
            # Ticker (non-editable)
            ticker_item = QTableWidgetItem(ticker)
            ticker_item.setTextAlignment(Qt.AlignCenter)
            ticker_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
            ticker_item.setFlags(ticker_item.flags() & ~Qt.ItemIsEditable)
            self.nav_table.setItem(row, 0, ticker_item)
            
            # Current Price (non-editable)
            price_item = QTableWidgetItem(f"${current_price:.2f}")
            price_item.setTextAlignment(Qt.AlignCenter)
            price_item.setFlags(price_item.flags() & ~Qt.ItemIsEditable)
            self.nav_table.setItem(row, 1, price_item)
            
            # Consensus NAV (editable)
            nav_editor = QDoubleSpinBox()
            nav_editor.setMinimum(0.0)
            nav_editor.setMaximum(2000.0)
            nav_editor.setValue(nav_value)
            nav_editor.setPrefix("$ ")
            nav_editor.setDecimals(2)
            nav_editor.setSingleStep(0.5)
            nav_editor.setLocale(QLocale('en_US'))
            nav_editor.setStyleSheet("""
                border: none;
                background-color: transparent;
            """)
            nav_editor.valueChanged.connect(lambda value, t=ticker: self.nav_value_changed(t, value))
            self.nav_table.setCellWidget(row, 2, nav_editor)
            
            # Premium/Discount (calculated, non-editable)
            if nav_value > 0:
                premium_str = f"{premium_discount:.2f}%"
                
                # Add + sign for positive premium
                if premium_discount > 0:
                    premium_str = f"+{premium_str}"
                    
                premium_item = QTableWidgetItem(premium_str)
                premium_item.setTextAlignment(Qt.AlignCenter)
                
                # Color based on premium/discount
                if premium_discount < 0:  # Trading at discount (valor negativo com a nova fórmula)
                    premium_item.setForeground(QColor(Theme.SUCCESS))
                else:  # Trading at premium (valor positivo com a nova fórmula)
                    premium_item.setForeground(QColor(Theme.DANGER))
            else:
                premium_item = QTableWidgetItem("N/A")
                premium_item.setTextAlignment(Qt.AlignCenter)
                
            premium_item.setFlags(premium_item.flags() & ~Qt.ItemIsEditable)
            self.nav_table.setItem(row, 3, premium_item)
            
            # Apply alternating row colors
            bg_color = QColor("#FFFFFF") if row % 2 == 0 else QColor("#F5F7FA")
            for col in range(self.nav_table.columnCount()):
                item = self.nav_table.item(row, col)
                if item:
                    item.setBackground(bg_color)
    
    def nav_value_changed(self, ticker, value):
        """Handle changes to NAV values"""
        self.nav_data[ticker] = value
        self.update_premium_discount(ticker)
    
    def update_premium_discount(self, ticker):
        """Update the Premium/Discount calculation for a specific ticker"""
        # Find the row for this ticker
        for row in range(self.nav_table.rowCount()):
            ticker_item = self.nav_table.item(row, 0)
            if ticker_item and ticker_item.text() == ticker:
                # Get current price
                price_text = self.nav_table.item(row, 1).text()
                current_price = float(price_text.replace('$', ''))
                
                # Get NAV value
                nav_editor = self.nav_table.cellWidget(row, 2)
                nav_value = nav_editor.value()
                
                # Calculate Premium/Discount
                if nav_value > 0:
                    premium_discount = ((current_price / nav_value) - 1) * 100
                    premium_str = f"{premium_discount:.2f}%"
                    
                    # Add + sign for premium (discount)
                    if premium_discount > 0:
                        premium_str = f"+{premium_str}"
                        
                    premium_item = QTableWidgetItem(premium_str)
                    premium_item.setTextAlignment(Qt.AlignCenter)
                    
                    # Color based on premium/discount
                    if premium_discount < 0:  # Trading at discount (positive value)
                        premium_item.setForeground(QColor(Theme.SUCCESS))
                    else:  # Trading at premium (negative value)
                        premium_item.setForeground(QColor(Theme.DANGER))
                else:
                    premium_item = QTableWidgetItem("N/A")
                    premium_item.setTextAlignment(Qt.AlignCenter)
                    
                premium_item.setFlags(premium_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
                self.nav_table.setItem(row, 3, premium_item)
                break
    
    def header_clicked(self, section):
        """Handle clicks on table header sections"""
        # Verificar se clicou na coluna Premium/Discount (índice 3)
        if section == 3:
            print("Clicou no cabeçalho Premium/Discount - iniciando nova ordenação")
            
            # Coletar dados do portfolio e valores NAV atuais
            all_data = []
            
            # Primeiro, salvar os valores NAV atuais da tabela
            for row in range(self.nav_table.rowCount()):
                ticker_item = self.nav_table.item(row, 0)
                if ticker_item:
                    ticker = ticker_item.text()
                    nav_widget = self.nav_table.cellWidget(row, 2)
                    if nav_widget:
                        nav_value = nav_widget.value()
                        self.nav_data[ticker] = nav_value
            
            # Agora, gerar a tabela do zero usando os dados do portfolio
            for ticker, position in self.portfolio.positions.items():
                # Skip positions with no shares
                metrics = position.calculate_metrics()
                if metrics['shares'] <= 0:
                    continue
                    
                # Current Price
                current_price = position.current_price
                
                # Consensus NAV (get existing value or default to 0.0)
                nav_value = self.nav_data.get(ticker, 0.0)
                
                # Calculate Premium/Discount - FÓRMULA ALTERADA AQUI
                premium_discount = 0.0
                if nav_value > 0:
                    # Nova fórmula: ((current_price / nav_value) - 1) * 100
                    premium_discount = ((current_price / nav_value) - 1) * 100
                    
                all_data.append({
                    'ticker': ticker,
                    'price': current_price,
                    'nav_value': nav_value,
                    'premium_discount': premium_discount
                })
            
            # Ordenar por Premium/Discount (do valor mais negativo para o mais positivo)
            all_data.sort(key=lambda x: x['premium_discount'])
        
            
            # Limpar tabela e desativar ordenação
            self.nav_table.setRowCount(0)
            self.nav_table.setSortingEnabled(False)
            
            # Preencher a tabela com dados ordenados
            for idx, item in enumerate(all_data):
                ticker = item['ticker']
                current_price = item['price']
                nav_value = item['nav_value']
                premium_discount = item['premium_discount']  # Valor original mantido
                
                # Inserir nova linha
                row = self.nav_table.rowCount()
                self.nav_table.insertRow(row)
                
                # Ticker (non-editable)
                ticker_item = QTableWidgetItem(ticker)
                ticker_item.setTextAlignment(Qt.AlignCenter)
                ticker_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
                ticker_item.setFlags(ticker_item.flags() & ~Qt.ItemIsEditable)
                self.nav_table.setItem(row, 0, ticker_item)
                
                # Current Price (non-editable)
                price_item = QTableWidgetItem(f"${current_price:.2f}")
                price_item.setTextAlignment(Qt.AlignCenter)
                price_item.setFlags(price_item.flags() & ~Qt.ItemIsEditable)
                self.nav_table.setItem(row, 1, price_item)
                
                # Consensus NAV (editable)
                nav_editor = QDoubleSpinBox()
                nav_editor.setMinimum(0.0)
                nav_editor.setMaximum(2000.0)
                nav_editor.setValue(nav_value)
                nav_editor.setPrefix("$ ")
                nav_editor.setDecimals(2)
                nav_editor.setSingleStep(0.5)
                nav_editor.setLocale(QLocale('en_US'))
                nav_editor.setStyleSheet("""
                    border: none;
                    background-color: transparent;
                """)
                nav_editor.valueChanged.connect(lambda value, t=ticker: self.nav_value_changed(t, value))
                self.nav_table.setCellWidget(row, 2, nav_editor)
                
                # Premium/Discount (calculated, non-editable)
                if nav_value > 0:
                    premium_str = f"{premium_discount:.2f}%"
                    
                    # Add + sign for positive premium
                    if premium_discount > 0:
                        premium_str = f"+{premium_str}"
                        
                    premium_item = QTableWidgetItem(premium_str)
                    premium_item.setTextAlignment(Qt.AlignCenter)
                    
                    # Color based on premium/discount - LÓGICA ALTERADA AQUI
                    if premium_discount < 0:  # Trading at discount (valor negativo com a nova fórmula)
                        premium_item.setForeground(QColor(Theme.SUCCESS))
                    else:  # Trading at premium (valor positivo com a nova fórmula)
                        premium_item.setForeground(QColor(Theme.DANGER))
                else:
                    premium_item = QTableWidgetItem("N/A")
                    premium_item.setTextAlignment(Qt.AlignCenter)
                    
                premium_item.setFlags(premium_item.flags() & ~Qt.ItemIsEditable)
                self.nav_table.setItem(row, 3, premium_item)
                
                # Apply alternating row colors
                bg_color = QColor("#FFFFFF") if row % 2 == 0 else QColor("#F5F7FA")
                for col in range(self.nav_table.columnCount()):
                    item = self.nav_table.item(row, col)
                    if item:
                        item.setBackground(bg_color)
            
            # Manter a ordenação desativada após a recriação
            self.nav_table.setSortingEnabled(False)
        
        print(f"Ordenação concluída - {len(all_data)} linhas")
    
    def reorder_table(self, sorted_data):
        """Reorder the table based on the sorted data"""
        # Criar uma tabela temporária com os mesmos dados, mas na ordem desejada
        tmp_table = []
        for row_idx in range(self.nav_table.rowCount()):
            row_data = {}
            
            # Item 0: Ticker
            ticker_item = self.nav_table.item(row_idx, 0)
            row_data['ticker'] = ticker_item.clone() if ticker_item else None
            
            # Item 1: Price
            price_item = self.nav_table.item(row_idx, 1)
            row_data['price'] = price_item.clone() if price_item else None
            
            # Item 2: NAV (QDoubleSpinBox)
            spinbox = self.nav_table.cellWidget(row_idx, 2)
            row_data['nav_value'] = spinbox.value() if spinbox else 0.0
            
            # Item 3: Premium/Discount
            premium_item = self.nav_table.item(row_idx, 3)
            row_data['premium'] = premium_item.clone() if premium_item else None
            
            # Ticker for saving
            ticker = ticker_item.text() if ticker_item else ""
            row_data['ticker_text'] = ticker
            
            tmp_table.append(row_data)
        
        # Reorganizar com base na ordenação
        for new_idx, (old_idx, ticker, _) in enumerate(sorted_data):
            # Item 0: Ticker
            if tmp_table[old_idx]['ticker']:
                self.nav_table.setItem(new_idx, 0, tmp_table[old_idx]['ticker'])
            
            # Item 1: Price
            if tmp_table[old_idx]['price']:
                self.nav_table.setItem(new_idx, 1, tmp_table[old_idx]['price'])
            
            # Item 3: Premium
            if tmp_table[old_idx]['premium']:
                self.nav_table.setItem(new_idx, 3, tmp_table[old_idx]['premium'])
            
            # Item 2: NAV (QDoubleSpinBox)
            nav_value = tmp_table[old_idx]['nav_value']
            
            # Recriar o spinbox
            nav_editor = QDoubleSpinBox()
            nav_editor.setMinimum(0.0)
            nav_editor.setMaximum(2000.0)
            nav_editor.setValue(nav_value)
            nav_editor.setPrefix("$ ")
            nav_editor.setDecimals(2)
            nav_editor.setSingleStep(0.5)
            nav_editor.setLocale(QLocale('en_US'))
            nav_editor.setStyleSheet("""
                border: none;
                background-color: transparent;
            """)
            nav_editor.valueChanged.connect(lambda value, t=ticker: self.nav_value_changed(t, value))
            self.nav_table.setCellWidget(new_idx, 2, nav_editor)
            
            # Atualizar o nav_data para este ticker
            ticker_text = tmp_table[old_idx]['ticker_text']
            if ticker_text:
                self.nav_data[ticker_text] = nav_value
            
        # Aplicar cores alternadas de linha
        for row in range(self.nav_table.rowCount()):
            bg_color = QColor("#FFFFFF") if row % 2 == 0 else QColor("#F5F7FA")
            for col in range(self.nav_table.columnCount()):
                item = self.nav_table.item(row, col)
                if item:
                    item.setBackground(bg_color)    
	    
    def date_changed(self, qdate):
        """Handle changes to the report date"""
        self.report_date = qdate.toString("dd/MM/yyyy")
    
    def save_nav_data(self):
        """Save NAV data to portfolio file"""
        try:
            print("Salvando NAV data...")
            print(f"NAV data: {self.nav_data}")
        
            # Load existing portfolio data
            if os.path.exists(PORTFOLIO_FILE):
                print(f"Arquivo encontrado: {PORTFOLIO_FILE}")
                with open(PORTFOLIO_FILE, 'r') as f:
                    data = json.load(f)
            
                # Add or update NAV data
                data['nav_data'] = self.nav_data
                data['nav_report_date'] = self.report_date
            
                # Save back to file
                with open(PORTFOLIO_FILE, 'w') as f:
                    json.dump(data, f, indent=2)
            
                print("Dados salvos com sucesso!")
                self.accept()  # Aceitar o diálogo
                QMessageBox.information(self, "Success", "NAV data saved successfully!")
            else:
                print(f"Arquivo não encontrado: {PORTFOLIO_FILE}")
                QMessageBox.warning(self, "File Not Found", "Portfolio file not found. Please save your portfolio first.")
        
        except Exception as e:
            print(f"Erro ao salvar: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to save NAV data: {str(e)}")


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    # Dummy portfolio for testing
    class Position:
        def __init__(self, ticker, name=""):
            self.ticker = ticker
            self.name = name
            self.current_price = 0.0
            
        def calculate_metrics(self):
            return {'shares': 10}  # Dummy value
    
    class Portfolio:
        def __init__(self):
            self.positions = {}
            
        def add_position(self, position):
            self.positions[position.ticker] = position
    
    app = QApplication(sys.argv)
    
    # Create dummy portfolio
    portfolio = Portfolio()
    
    for ticker, price in [
        ("AMT", 216.23),
        ("EPRT", 31.73),
        ("EXR", 143.80),
        ("MAA", 161.27),
        ("O", 55.80),
        ("PLD", 108.42),
        ("STAG", 34.02),
        ("TRNO", 62.69)
    ]:
        pos = Position(ticker)
        pos.current_price = price
        portfolio.add_position(pos)
    
    dialog = NAVDialog(portfolio=portfolio)
    dialog.exec_()
    
    sys.exit(0)
