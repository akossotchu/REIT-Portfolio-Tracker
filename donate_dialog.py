import os
import io
import qrcode
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                           QFrame, QApplication)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QPen, QBrush, QPainterPath, QFont
from PyQt5.QtCore import Qt, QSize, QRect
from theme import Theme


class DonateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Support This Project")
        self.setMinimumWidth(450)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.BACKGROUND};
            }}
            QLabel {{
                color: {Theme.TEXT_PRIMARY};
            }}
            QLabel#title {{
                font-size: 18px;
                font-weight: bold;
                color: {Theme.PRIMARY};
            }}
            QLabel#address {{
                font-family: monospace;
                background-color: #f5f5f5;
                padding: 10px;
                border-radius: 4px;
                selection-background-color: {Theme.SECONDARY};
            }}
        """)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Support REIT Portfolio Tracker")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        description = QLabel(
            "If you find this tool useful, please consider making a donation. "
            "Your support helps maintain and improve this application."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignCenter)
        layout.addWidget(description)
        
        # Bitcoin logo and QR code in a horizontal layout
        donation_layout = QHBoxLayout()
        
        # Create Bitcoin logo
        bitcoin_logo = self.create_bitcoin_logo()
        donation_layout.addWidget(bitcoin_logo)
        
        # Create QR code
        qr_label = self.create_qr_code("bc1qxqdxgf7ncc4ekz8ldq5cc5gukpykm6hfhjad0l")
        donation_layout.addWidget(qr_label)
        
        layout.addLayout(donation_layout)
        
        # Bitcoin address
        address_frame = QFrame()
        address_frame.setStyleSheet(f"background-color: white; border-radius: 8px; padding: 10px;")
        address_layout = QVBoxLayout(address_frame)
        
        address_title = QLabel("Bitcoin Address:")
        address_title.setStyleSheet("font-weight: bold;")
        address_layout.addWidget(address_title)
        
        address_label = QLabel("bc1qxqdxgf7ncc4ekz8ldq5cc5gukpykm6hfhjad0l")
        address_label.setObjectName("address")
        address_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        address_label.setCursor(Qt.IBeamCursor)
        address_layout.addWidget(address_label)
        
        copy_info = QLabel("Click the address to select it, then copy with Ctrl+C")
        copy_info.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 11px;")
        address_layout.addWidget(copy_info)
        
        layout.addWidget(address_frame)
        
        # Thank you message
        thanks = QLabel("Thank you for your support!")
        thanks.setAlignment(Qt.AlignCenter)
        thanks.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(thanks)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.setMinimumWidth(100)
        close_button.setMinimumHeight(36)
        close_button.clicked.connect(self.accept)
        close_button.setStyleSheet(f"""
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
        """)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def create_qr_code(self, data):
        """Create a QR code for the given data"""
        # Criar QR code com tamanho maior e borda menor
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,  # Melhor correção de erro
            box_size=10,  # Tamanho maior dos blocos
            border=2,     # Borda menor
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Criar a imagem usando PIL
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Converter a imagem PIL para um formato que o PyQt5 possa usar
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        # Carregar a imagem como QPixmap
        qr_pixmap = QPixmap()
        qr_pixmap.loadFromData(buffer.getvalue())
        
        # Criar QLabel com o QR code
        qr_label = QLabel()
        qr_label.setPixmap(qr_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        qr_label.setAlignment(Qt.AlignCenter)
        
        return qr_label
    
    def create_bitcoin_logo(self):
        """Create a Bitcoin logo with proper circle"""
        # Criar um QLabel para exibir o logo
        bitcoin_label = QLabel()
        bitcoin_label.setFixedSize(120, 120)
        
        # Criar um QPixmap para desenhar o logo
        pixmap = QPixmap(120, 120)
        pixmap.fill(Qt.transparent)  # Fundo transparente
        
        # Iniciar o painter
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)  # Para melhorar a qualidade
        
        # Definir cores
        bitcoin_orange = QColor("#F7931A")
        
        # Desenhar círculo de fundo
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bitcoin_orange))
        painter.drawEllipse(10, 10, 100, 100)
        
        # Configurar a fonte para o símbolo ₿
        font = QFont("Arial", 48, QFont.Bold)
        painter.setFont(font)
        
        # Desenhar símbolo ₿ em branco
        painter.setPen(QColor("white"))
        
        # Criar um retângulo para centralizar o texto
        text_rect = QRect(10, 10, 100, 100)
        painter.drawText(text_rect, Qt.AlignCenter, "₿")
        
        # Finalizar o painter
        painter.end()
        
        # Definir o pixmap como imagem do QLabel
        bitcoin_label.setPixmap(pixmap)
        bitcoin_label.setAlignment(Qt.AlignCenter)
        
        return bitcoin_label