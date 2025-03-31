import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton,
                            QApplication, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

class MplCanvas(FigureCanvas):
    def __init__(self, width=8, height=8, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)

class SectorAllocationDialog(QDialog):
    def __init__(self, parent=None, portfolio=None):
        super().__init__(parent)
        self.setWindowTitle("REIT Portfolio Allocation by Sector")
        self.setMinimumSize(800, 600)
        self.portfolio = portfolio
        
        # Define sectors for common REITs
        self.reit_sectors = {
            # Cell tower and data center REITs
            "AMT": "Infrastructure",
            "CCI": "Infrastructure",
            "EQIX": "Data Centers",
            "DLR": "Data Centers",
            "CONE": "Data Centers",
            
            # Residential REITs
            "EQR": "Residential",
            "AVB": "Residential",
            "ESS": "Residential",
            "MAA": "Residential",
            "UDR": "Residential",
            "CPT": "Residential",
            
            # Healthcare REITs
            "VTR": "Healthcare",
            "WELL": "Healthcare",
            "HCP": "Healthcare",
            "OHI": "Healthcare",
            "HR": "Healthcare",
            
            # Industrial REITs
            "PLD": "Industrial",
            "DRE": "Industrial",
            "EGP": "Industrial",
            "FR": "Industrial",
            "STAG": "Industrial",
            "TRNO": "Industrial",
            
            # Retail REITs
            "SPG": "Retail",
            "REG": "Retail",
            "FRT": "Retail",
            "KIM": "Retail",
            "BRX": "Retail",
            
            # Office REITs
            "BXP": "Office",
            "VNO": "Office",
            "SLG": "Office",
            "PGRE": "Office",
            "HIW": "Office",
            
            # Mortgage REITs
            "NLY": "Mortgage",
            "AGNC": "Mortgage",
            "STWD": "Mortgage",
            
            # Diversified REITs
            "O": "Triple Net",
            "WPC": "Triple Net",
            "EPRT": "Triple Net",
            "NNN": "Triple Net",
            
            # Storage REITs
            "PSA": "Storage",
            "EXR": "Storage",
            "CUBE": "Storage",
            "LSI": "Storage"
        }
        
        # Initialize UI
        self.init_ui()
        
        # Draw chart
        self.create_chart()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.setStyleSheet("background-color: #F5F5F5;")
        
        # Title
        title_frame = QFrame()
        title_frame.setStyleSheet("background-color: white; border-radius: 8px; padding: 10px;")
        title_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        title_layout = QVBoxLayout(title_frame)
        
        title_label = QLabel("REIT Portfolio Allocation by Sector")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2C3E50;")
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Click on a sector to view detailed holdings")
        subtitle_label.setStyleSheet("font-size: 12px; color: #7F8C8D;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        layout.addWidget(title_frame)
        
        # Chart container
        chart_frame = QFrame()
        chart_frame.setStyleSheet("background-color: white; border-radius: 8px; padding: 15px;")
        chart_layout = QVBoxLayout(chart_frame)
        
        self.chart_canvas = MplCanvas(width=8, height=6, dpi=100)
        chart_layout.addWidget(self.chart_canvas)
        
        layout.addWidget(chart_frame)
        
        # Sector info panel
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Box)
        info_frame.setFrameShadow(QFrame.Sunken)
        info_frame.setStyleSheet("""
            background-color: white; 
            border-radius: 8px; 
            padding: 15px;
            border: 1px solid #E0E0E0;
        """)
        info_layout = QVBoxLayout(info_frame)
        
        info_title = QLabel("Sector Details")
        info_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2C3E50;")
        info_layout.addWidget(info_title)
        
        self.sector_info_label = QLabel("Click on a sector in the chart to see details.")
        self.sector_info_label.setStyleSheet("font-size: 12px; color: #7F8C8D;")
        self.sector_info_label.setWordWrap(True)
        info_layout.addWidget(self.sector_info_label)
        
        layout.addWidget(info_frame)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        close_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def determine_sector_by_name(self, ticker, name):
        """Tenta determinar o setor baseado no nome do REIT"""
        name = name.lower() if name else ""
        
        # Palavras-chave para cada setor
        sector_keywords = {
            "Residential": ["apartment", "residential", "housing", "home", "multifamily"],
            "Office": ["office", "workplace", "corporate"],
            "Retail": ["retail", "mall", "shopping", "store", "outlet"],
            "Industrial": ["industrial", "logistic", "warehouse", "manufacturing"],
            "Healthcare": ["healthcare", "medical", "hospital", "senior", "care", "clinic"],
            "Hotel": ["hotel", "resort", "lodging", "hospitality"],
            "Storage": ["storage", "self storage", "self-storage"],
            "Data Centers": ["data center", "datacenter", "server", "computing", "digital"],
            "Infrastructure": ["infrastructure", "tower", "communication", "telecom", "utility"],
            "Triple Net": ["triple", "net lease", "freestanding", "income"],
            "Mortgage": ["mortgage", "loan", "debt", "finance"]
        }
        
        # Verificar se o nome contém palavras-chave
        for sector, keywords in sector_keywords.items():
            for keyword in keywords:
                if keyword in name:
                    return sector
        
        # Procurar por classificadores específicos
        if "reit" in name:
            for sector in sector_keywords.keys():
                if sector.lower() in name:
                    return sector
        
        return "Other"
    
    def get_reit_sector(self, ticker, position):
        """Determina o setor de um REIT com base no ticker ou nome"""
        # Primeiro, verifique se o ticker está no dicionário de setores predefinido
        if ticker in self.reit_sectors:
            return self.reit_sectors[ticker]
        
        # Se não estiver, tente determinar pelo nome
        return self.determine_sector_by_name(ticker, position.name)
        
    def create_chart(self):
        if not self.portfolio or not self.portfolio.positions:
            self.show_empty_chart()
            return
            
        # Collect data by sector
        sector_values = {}
        
        for ticker, position in self.portfolio.positions.items():
            metrics = position.calculate_metrics()
            if metrics['shares'] <= 0:
                continue
                
            value = position.current_price * metrics['shares']
            sector = self.get_reit_sector(ticker, position)
            
            if sector not in sector_values:
                sector_values[sector] = 0
            sector_values[sector] += value
        
        if not sector_values:
            self.show_empty_chart()
            return
            
        # Prepare data for pie chart
        sectors = []
        values = []
        explode = []
        
        # Sort sectors by value (descending)
        sorted_sectors = sorted(sector_values.items(), key=lambda x: x[1], reverse=True)
        
        # Define colors for sectors (use a colorful palette)
        colors = [
            '#FF9999', '#66B3FF', '#99FF99', '#FFCC99', '#C2C2F0', 
            '#FFB3E6', '#C4E17F', '#F7786B', '#91A6FF', '#84B1ED',
            '#89F7FE', '#66A5AD', '#2E8B57', '#DAA520', '#BA55D3',
            '#2C82C9', '#58C9B9', '#9DE0AD', '#BC70A4', '#BFD641'
        ]
        
        for i, (sector, value) in enumerate(sorted_sectors):
            sectors.append(sector)
            values.append(value)
            # Explode the largest sector slightly
            explode.append(0.02 if sector == sorted_sectors[0][0] else 0)
        
        # Create pie chart
        self.chart_canvas.axes.clear()
        
        # Set background color for elegance
        self.chart_canvas.fig.set_facecolor('#F5F5F5')
        self.chart_canvas.axes.set_facecolor('#F5F5F5')
        
        wedges, texts, autotexts = self.chart_canvas.axes.pie(
            values, 
            labels=None,  # We'll use a legend instead of direct labels
            explode=explode,
            autopct='%1.1f%%',
            shadow=False,  # Remove shadow for cleaner look
            startangle=90,
            textprops={'fontsize': 11, 'color': 'white', 'fontweight': 'bold'},
            wedgeprops={'edgecolor': 'white', 'linewidth': 1.5},
            colors=colors[:len(sectors)]
        )
        
        # Add a white circle in the middle for a donut chart effect
        centre_circle = plt.Circle((0, 0), 0.50, fc='white')
        self.chart_canvas.axes.add_patch(centre_circle)
        
        # Add title in center of donut
        total_value = sum(values)
        self.chart_canvas.axes.text(0, 0, f"${total_value:,.2f}", 
                     horizontalalignment='center',
                     verticalalignment='center',
                     fontsize=20, fontweight='bold')
        
        # Add a detailed legend
        legend_labels = [f"{sectors[i]} (${values[i]:,.2f})" for i in range(len(sectors))]
        self.chart_canvas.axes.legend(wedges, legend_labels, 
                         loc="center left", 
                         bbox_to_anchor=(1, 0, 0.5, 1),
                         fontsize=9)
        
        # Make the plot aspect ratio equal to ensure circular pie
        self.chart_canvas.axes.axis('equal')
        
        # Add a clickable functionality to display information
        self.wedges = wedges
        self.sector_data = {sectors[i]: values[i] for i in range(len(sectors))}
        
        def on_click(event):
            if event.inaxes == self.chart_canvas.axes:
                for i, wedge in enumerate(self.wedges):
                    cont, _ = wedge.contains(event)
                    if cont:
                        sector = sectors[i]
                        value = values[i]
                        percentage = value / total_value * 100
                        self.show_sector_details(sector, value, percentage)
                        # Highlight the wedge
                        for w in self.wedges:
                            w.set_linewidth(1.5)
                        wedge.set_linewidth(3)
                        self.chart_canvas.draw()
                        return
        
        self.chart_canvas.mpl_connect('button_press_event', on_click)
        
        # Draw the chart
        self.chart_canvas.draw()

    def show_sector_details(self, sector, value, percentage):
        """Display details about the clicked sector"""
        # Get REITs in this sector
        reits_in_sector = []
        
        for ticker, position in self.portfolio.positions.items():
            if self.get_reit_sector(ticker, position) == sector:
                metrics = position.calculate_metrics()
                if metrics['shares'] > 0:
                    reit_value = position.current_price * metrics['shares']
                    name = position.name if position.name else ticker
                    annual_income = metrics['annual_income']
                    dividend_yield = position.dividend_yield
                    reits_in_sector.append((
                        ticker, 
                        name,
                        reit_value, 
                        reit_value/value*100,
                        annual_income,
                        dividend_yield
                    ))
        
        # Sort REITs in this sector by value (descending)
        reits_in_sector.sort(key=lambda x: x[2], reverse=True)
        
        # Create details text with HTML formatting for better appearance
        details = f"""
        <h2 style='color: #2C3E50;'>{sector} Sector</h2>
        <p style='font-size: 14px;'>
            <b>Total Value:</b> ${value:,.2f}<br>
            <b>Portfolio Allocation:</b> {percentage:.1f}%<br>
            <b>Number of REITs:</b> {len(reits_in_sector)}
        </p>
        
        <h3 style='color: #2C3E50; margin-top: 15px;'>REITs in this Sector:</h3>
        <table width='100%' style='border-collapse: collapse;'>
            <tr style='background-color: #f2f2f2;'>
                <th align='left' style='padding: 8px; border-bottom: 1px solid #ddd;'>Ticker</th>
                <th align='left' style='padding: 8px; border-bottom: 1px solid #ddd;'>Name</th>
                <th align='right' style='padding: 8px; border-bottom: 1px solid #ddd;'>Value</th>
                <th align='right' style='padding: 8px; border-bottom: 1px solid #ddd;'>% of Sector</th>
                <th align='right' style='padding: 8px; border-bottom: 1px solid #ddd;'>Dividend Yield</th>
                <th align='right' style='padding: 8px; border-bottom: 1px solid #ddd;'>Annual Income</th>
            </tr>
        """
        
        for i, (ticker, name, reit_value, reit_pct, annual_income, dividend_yield) in enumerate(reits_in_sector):
            row_style = "background-color: #f9f9f9;" if i % 2 == 0 else ""
            details += f"""
            <tr style='{row_style}'>
                <td style='padding: 8px; border-bottom: 1px solid #ddd;'><b>{ticker}</b></td>
                <td style='padding: 8px; border-bottom: 1px solid #ddd;'>{name}</td>
                <td align='right' style='padding: 8px; border-bottom: 1px solid #ddd;'>${reit_value:,.2f}</td>
                <td align='right' style='padding: 8px; border-bottom: 1px solid #ddd;'>{reit_pct:.1f}%</td>
                <td align='right' style='padding: 8px; border-bottom: 1px solid #ddd;'>{dividend_yield:.2f}%</td>
                <td align='right' style='padding: 8px; border-bottom: 1px solid #ddd;'>${annual_income:.2f}</td>
            </tr>
            """
        
        details += "</table>"
        
        # Add sector summary
        total_income = sum(item[4] for item in reits_in_sector)
        avg_yield = sum(item[5] for item in reits_in_sector) / len(reits_in_sector) if reits_in_sector else 0
        
        details += f"""
        <p style='font-size: 14px; margin-top: 15px;'>
            <b>Sector Income:</b> ${total_income:.2f} per year<br>
            <b>Average Yield:</b> {avg_yield:.2f}%
        </p>
        """
        
        self.sector_info_label.setText(details)
        
    def show_empty_chart(self):
        """Display a message when there is no data"""
        self.chart_canvas.axes.clear()
        self.chart_canvas.axes.text(0.5, 0.5, "No portfolio data available", 
                      horizontalalignment='center', verticalalignment='center',
                      transform=self.chart_canvas.axes.transAxes, fontsize=14)
        self.chart_canvas.draw()
        
    def closeEvent(self, event):
        """Clean up when closing"""
        self.chart_canvas.fig.clear()
        event.accept()
        
if __name__ == "__main__":
    # Test the dialog standalone
    app = QApplication(sys.argv)
    dialog = SectorAllocationDialog()
    dialog.show()
    sys.exit(app.exec_())