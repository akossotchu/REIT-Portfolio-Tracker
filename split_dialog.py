from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit, 
                           QSpinBox, QPushButton, QDateEdit)
from PyQt5.QtCore import Qt, QDate, pyqtSignal

# Importe as constantes de tema do novo arquivo de tema
from theme import Theme

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
