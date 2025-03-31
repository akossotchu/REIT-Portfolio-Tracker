#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
REIT Portfolio Tracker
======================

A Python application with PyQt5 GUI to track and manage REIT investments.
Features:
- Track buy, sell, and no-cost acquisition transactions
- Calculate average prices using FIFO method
- Fetch dividend yields automatically
- Calculate yield on cost and other portfolio metrics
- Visualize portfolio performance and income
"""

import sys
import os
from reit_portfolio_app import PortfolioApp
from theme import Theme
from PyQt5.QtWidgets import QApplication, QSplashScreen, QProgressBar, QVBoxLayout, QLabel, QWidget
from PyQt5.QtCore import Qt, QTimer, QSize, QRect, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPixmap, QFont, QIcon, QPainter, QColor, QLinearGradient, QPen, QPainterPath

class CustomSplashScreen(QSplashScreen):
    def __init__(self):
        """Create a custom splash screen with gradient background and animations"""
        # Create the pixmap for the splash screen with a good size
        splash_pix = QPixmap(500, 300)
        super().__init__(splash_pix)
        
        # Main layout for content
        self.layout = QVBoxLayout()
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        
        # Add a progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: rgba(255, 255, 255, 80);
                border-radius: 2px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {Theme.ACCENT};
                border-radius: 2px;
            }}
        """)
        
        # Progress animation
        self.progress_animation = QPropertyAnimation(self.progress_bar, b"value")
        self.progress_animation.setDuration(3000)  # 3 seconds
        self.progress_animation.setStartValue(0)
        self.progress_animation.setEndValue(100)
        self.progress_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Set the window flags
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # Set the status message
        self.message = "Starting application..."
        
    def showEvent(self, event):
        """Start animations when splash is shown"""
        super().showEvent(event)
        self.progress_animation.start()
        
    def setProgress(self, value):
        """Set progress bar value"""
        self.progress_bar.setValue(value)
        
    def setMessage(self, message):
        """Update status message"""
        self.message = message
        self.repaint()
        
    def drawContents(self, painter):
        """Draw custom splash screen content"""
        # Create a gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(Theme.PRIMARY))
        gradient.setColorAt(1, QColor(Theme.SECONDARY))
        painter.fillRect(self.rect(), gradient)
        
        # Draw a subtle pattern or overlay
        painter.setOpacity(0.05)
        for i in range(0, self.width(), 20):
            painter.drawLine(i, 0, i, self.height())
        for i in range(0, self.height(), 20):
            painter.drawLine(0, i, self.width(), i)
        painter.setOpacity(1.0)
        
        # Draw app title
        painter.setPen(QColor("white"))
        title_font = QFont("Segoe UI", 24, QFont.Bold)
        painter.setFont(title_font)
        painter.drawText(QRect(0, 60, self.width(), 50), 
                         Qt.AlignCenter, "REIT Portfolio Tracker")
        
        # Draw subtitle
        subtitle_font = QFont("Segoe UI", 12)
        painter.setFont(subtitle_font)
        painter.drawText(QRect(0, 110, self.width(), 30), 
                         Qt.AlignCenter, "Smart Investment Management")
        
        # Draw a stylized chart icon
        painter.setPen(QPen(QColor(Theme.ACCENT), 3))
        chart_rect = QRect(self.width() // 2 - 40, 150, 80, 50)
        
        # Simple bar chart icon
        bar_width = 12
        space = 8
        heights = [30, 20, 40, 25, 35]
        start_x = chart_rect.x() + (chart_rect.width() - (len(heights) * bar_width + (len(heights) - 1) * space)) // 2
        
        for i, height in enumerate(heights):
            x = start_x + i * (bar_width + space)
            y = chart_rect.y() + chart_rect.height() - height
            bar_rect = QRect(x, y, bar_width, height)
            painter.fillRect(bar_rect, QColor(Theme.ACCENT))
        
        # Draw status message at bottom
        status_font = QFont("Segoe UI", 10)
        painter.setFont(status_font)
        painter.setPen(QColor("white"))
        painter.drawText(QRect(0, self.height() - 60, self.width(), 30), 
                         Qt.AlignCenter, self.message)
        
        # Draw progress bar
        progress_rect = QRect(50, self.height() - 30, self.width() - 100, 4)
        painter.fillRect(progress_rect, QColor(255, 255, 255, 80))
        
        # Draw progress
        progress_width = int((self.progress_bar.value() / 100) * (self.width() - 100))
        progress_fill_rect = QRect(50, self.height() - 30, progress_width, 4)
        painter.fillRect(progress_fill_rect, QColor(Theme.ACCENT))
        
        # Draw a subtle border
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)


def main():
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("REIT Portfolio Tracker")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show custom splash screen
    splash = CustomSplashScreen()
    splash.show()
    
    # Process events to display splash screen
    app.processEvents()
    
    # Create main application window
    main_window = PortfolioApp()
    
    # Update splash message after a delay
    QTimer.singleShot(1000, lambda: splash.setMessage("Loading portfolio data..."))
    QTimer.singleShot(2000, lambda: splash.setMessage("Setting up interface..."))
    QTimer.singleShot(2500, lambda: splash.setMessage("Almost there..."))
    
    # Hide splash and show main window
    QTimer.singleShot(3000, lambda: splash.finish(main_window))
    QTimer.singleShot(3000, main_window.show)
    
    # Force a data update after the window is shown
    QTimer.singleShot(4000, main_window.update_portfolio_data)
    
    # Start the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
