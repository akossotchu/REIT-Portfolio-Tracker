import sys
from datetime import datetime
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
                            QTableWidgetItem, QPushButton, QHeaderView, QLabel,
                            QComboBox, QApplication)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QTimer
from PyQt5.QtGui import QColor

class TransactionHistoryDialog(QDialog):
    transaction_deleted = pyqtSignal(int, str)  # index, ticker
    
    def __init__(self, parent=None, portfolio=None):
        super().__init__(parent)
        self.setWindowTitle("Transaction History")
        self.setMinimumSize(800, 500)
        self.portfolio = portfolio
        
        # Create UI
        self.init_ui()
        self.load_transactions()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filter by ticker:"))
        self.ticker_combo = QComboBox()
        self.ticker_combo.addItem("All")
        if self.portfolio:
            for ticker in sorted(self.portfolio.positions.keys()):
                self.ticker_combo.addItem(ticker)
        self.ticker_combo.currentTextChanged.connect(self.filter_transactions)
        filter_layout.addWidget(self.ticker_combo)
        
        filter_layout.addWidget(QLabel("Filter by type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["All", "BUY", "SELL", "NO_COST"])
        self.type_combo.currentTextChanged.connect(self.filter_transactions)
        filter_layout.addWidget(self.type_combo)
        
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Transactions table
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(6)
        self.transactions_table.setHorizontalHeaderLabels([
            "Date", "Ticker", "Type", "Shares", "Price", "Total Cost"
        ])
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.transactions_table.verticalHeader().setVisible(False)
        layout.addWidget(self.transactions_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_transaction)
        button_layout.addWidget(self.delete_button)
        
        button_layout.addStretch()
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def load_transactions(self):
        self.transactions = []
        self.transactions_table.setRowCount(0)
        
        if not self.portfolio:
            return
            
        # Collect all transactions from all positions
        for ticker, position in self.portfolio.positions.items():
            for i, transaction in enumerate(position.transactions):
                self.transactions.append((i, ticker, transaction))
        
        # Sort by date, newest first
        self.transactions.sort(key=lambda x: x[2].date, reverse=True)
        
        # Add to table
        self.add_transactions_to_table(self.transactions)
            
    def add_transactions_to_table(self, transactions):
        self.transactions_table.setRowCount(0)
        
        for row, (idx, ticker, transaction) in enumerate(transactions):
            self.transactions_table.insertRow(row)
            
            # Date
            date_item = QTableWidgetItem(transaction.date.strftime('%Y-%m-%d'))
            date_item.setTextAlignment(Qt.AlignCenter)
            self.transactions_table.setItem(row, 0, date_item)
            
            # Ticker
            ticker_item = QTableWidgetItem(ticker)
            ticker_item.setTextAlignment(Qt.AlignCenter)
            self.transactions_table.setItem(row, 1, ticker_item)
            
            # Type
            type_item = QTableWidgetItem(transaction.type)
            type_item.setTextAlignment(Qt.AlignCenter)
            if transaction.type == "BUY":
                type_item.setForeground(QColor("green"))
            elif transaction.type == "SELL":
                type_item.setForeground(QColor("red"))
            else:
                type_item.setForeground(QColor("blue"))
            self.transactions_table.setItem(row, 2, type_item)
            
            # Shares
            shares_item = QTableWidgetItem(f"{transaction.shares:.3f}")
            shares_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.transactions_table.setItem(row, 3, shares_item)
            
            # Price
            price_item = QTableWidgetItem(f"${transaction.price:.2f}")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.transactions_table.setItem(row, 4, price_item)
            
            # Total
            total = transaction.price * transaction.shares
            total_item = QTableWidgetItem(f"${total:.2f}")
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.transactions_table.setItem(row, 5, total_item)
            
            # Store the transaction index
            for col in range(6):
                item = self.transactions_table.item(row, col)
                item.setData(Qt.UserRole, (idx, ticker))
    
    def filter_transactions(self):
        ticker_filter = self.ticker_combo.currentText()
        type_filter = self.type_combo.currentText()
        
        filtered_transactions = []
        
        for idx, ticker, transaction in self.transactions:
            if (ticker_filter == "All" or ticker == ticker_filter) and \
               (type_filter == "All" or transaction.type == type_filter):
                filtered_transactions.append((idx, ticker, transaction))
        
        self.add_transactions_to_table(filtered_transactions)
    
    def delete_transaction(self):
        selected_rows = self.transactions_table.selectedIndexes()
        if not selected_rows:
            return
            
        # Get unique rows
        rows = set(index.row() for index in selected_rows)
        
        # Collect transaction indices and tickers
        to_delete = []
        for row in rows:
            idx_ticker = self.transactions_table.item(row, 0).data(Qt.UserRole)
            to_delete.append(idx_ticker)
        
        # Signal to parent to delete these transactions
        for idx, ticker in to_delete:
            self.transaction_deleted.emit(idx, ticker)
        
        # Reload transactions
        self.load_transactions()
        self.filter_transactions()

if __name__ == "__main__":
    # Test the dialog
    app = QApplication(sys.argv)
    dialog = TransactionHistoryDialog()
    dialog.show()
    sys.exit(app.exec_())