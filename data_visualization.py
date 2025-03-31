import sys
from datetime import datetime, timedelta, date as datetime_date
import numpy as np
import yfinance as yf
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QComboBox,
                           QLabel, QPushButton, QTabWidget, QWidget, 
                           QApplication, QDateEdit, QGroupBox, QMessageBox)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QPalette, QColor

class MplCanvas(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)
        
class PortfolioAnalyticsDialog(QDialog):
    def __init__(self, parent=None, portfolio=None):
        super().__init__(parent)
        self.setWindowTitle("Portfolio Analytics")
        self.setMinimumSize(900, 600)
        self.portfolio = portfolio
        
        # Initialize UI
        self.init_ui()
        
        # Use QTimer to delay data loading slightly, allowing UI to render first
        QTimer.singleShot(100, self.load_data)
        
    def load_data(self):
        """Carrega os dados para análise após a interface ser inicializada"""
        try:
            # Mostrar mensagem de carregamento
            for canvas in [self.performance_canvas, self.income_canvas, self.allocation_canvas]:
                canvas.axes.clear()
                canvas.axes.text(0.5, 0.5, 'Carregando dados...', 
                           horizontalalignment='center', verticalalignment='center',
                           transform=canvas.axes.transAxes)
                canvas.draw()
                
            # Generate sample data for visualization
            self.generate_sample_data()
            
            # Update visualizations
            self.update_charts()
        except Exception as e:
            print(f"Erro ao carregar dados: {str(e)}")
            QMessageBox.warning(self, "Erro", f"Falha ao carregar dados: {str(e)}")
            for canvas in [self.performance_canvas, self.income_canvas, self.allocation_canvas]:
                canvas.axes.clear()
                canvas.axes.text(0.5, 0.5, f'Erro ao carregar dados: {str(e)}', 
                           horizontalalignment='center', verticalalignment='center',
                           transform=canvas.axes.transAxes)
                canvas.draw()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("View:"))
        self.view_combo = QComboBox()
        self.view_combo.addItems([
            "All REITs", 
            "Yield Comparison", 
            "Annual Income", 
            "Value Over Time"
        ])
        self.view_combo.currentTextChanged.connect(self.update_charts)
        filter_layout.addWidget(self.view_combo)
        
        filter_layout.addWidget(QLabel("Time Period:"))
        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "1 Month", 
            "3 Months", 
            "6 Months", 
            "1 Year",
            "3 Years",
            "5 Years",
            "All Time"
        ])
        self.period_combo.setCurrentText("1 Year")
        self.period_combo.currentTextChanged.connect(self.update_charts)
        filter_layout.addWidget(self.period_combo)
        
        filter_layout.addWidget(QLabel("Date Range:"))
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addYears(-1))
        self.start_date.dateChanged.connect(self.update_charts)
        filter_layout.addWidget(self.start_date)
        
        filter_layout.addWidget(QLabel("to"))
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.dateChanged.connect(self.update_charts)
        filter_layout.addWidget(self.end_date)
        
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Tabs for different visualizations
        self.tabs = QTabWidget()
        
        # Performance tab
        performance_tab = QWidget()
        performance_layout = QVBoxLayout()
        
        self.performance_canvas = MplCanvas(width=8, height=4, dpi=100)
        performance_layout.addWidget(self.performance_canvas)
        
        performance_tab.setLayout(performance_layout)
        self.tabs.addTab(performance_tab, "Performance")
        
        # Income tab
        income_tab = QWidget()
        income_layout = QVBoxLayout()
        
        self.income_canvas = MplCanvas(width=8, height=4, dpi=100)
        income_layout.addWidget(self.income_canvas)
        
        income_tab.setLayout(income_layout)
        self.tabs.addTab(income_tab, "Income")
        
        # Sector Allocation tab
        allocation_tab = QWidget()
        allocation_layout = QVBoxLayout()
        
        self.allocation_canvas = MplCanvas(width=8, height=4, dpi=100)
        allocation_layout.addWidget(self.allocation_canvas)
        
        allocation_tab.setLayout(allocation_layout)
        self.tabs.addTab(allocation_tab, "Allocation")
        
        layout.addWidget(self.tabs)
        
        # Bottom controls
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def generate_sample_data(self):
        """Gera dados históricos para o portfólio"""
        if not self.portfolio or not self.portfolio.positions:
            QMessageBox.warning(self, "Sem Dados", "Nenhuma posição encontrada no portfólio!")
            return
            
        self.historical_data = {}
        
        # Define o intervalo de datas (últimos 3 anos)
        end_date = datetime.now().date()  # Usar date em vez de datetime
        start_date = end_date - timedelta(days=3*365)
        
        # Configurar barra de status ou indicador de progresso
        print("Gerando dados históricos para visualização...")
        print(f"Período: {start_date} a {end_date}")
        
        for ticker, position in self.portfolio.positions.items():
            metrics = position.calculate_metrics()
            current_shares = metrics['shares']
            current_price = position.current_price
            current_yield = position.dividend_yield
            
            # Pule posições sem ações
            if current_shares <= 0:
                continue
                
            print(f"Processando dados históricos para {ticker}...")
            
            try:
                # Tente obter dados históricos reais do Yahoo Finance
                stock = yf.Ticker(ticker)
                hist = stock.history(start=start_date, end=end_date)
                
                if not hist.empty:
                    # Usar dados reais se disponíveis
                    price_history = []
                    value_history = []
                    income_history = []
                    
                    # Simular histórico de dividendos
                    try:
                        dividends = stock.dividends
                    except:
                        # Se não conseguir obter os dividendos, cria um DataFrame vazio
                        import pandas as pd
                        dividends = pd.Series(dtype=float)
                    
                    for date_index, row in hist.iterrows():
                        # Use o mesmo tipo de data para tudo - date em vez de datetime
                        date_point = date_index.date()  # Converter datetime para date
                        price = row['Close']
                        
                        # Simular número de ações (simplificado - assume ações constantes)
                        # Em um caso real, você calcularia isso com base nas transações reais
                        shares = current_shares
                        
                        # Calcular valor
                        value = shares * price
                        
                        # Calcular renda (dividendos)
                        income = 0.0
                        if not dividends.empty:
                            # Converter os índices de dividendos para date
                            div_dates = [d.date() for d in dividends.index]
                            if date_point in div_dates:
                                div_idx = div_dates.index(date_point)
                                income = dividends.iloc[div_idx] * shares
                        
                        price_history.append((date_point, price))
                        value_history.append((date_point, value))
                        income_history.append((date_point, income))
                    
                    # Adicionar dados ao dicionário
                    if price_history and value_history and income_history:
                        self.historical_data[ticker] = {
                            'price_history': price_history,
                            'value_history': value_history,
                            'income_history': income_history
                        }
                        print(f"Dados históricos obtidos com sucesso para {ticker} ({len(price_history)} pontos)")
                        continue  # Pule a geração de dados aleatórios
                    else:
                        print(f"Dados históricos vazios para {ticker}, gerando dados simulados")
                else:
                    print(f"Sem dados históricos para {ticker}, gerando dados simulados")
            except Exception as e:
                print(f"Erro ao obter dados históricos para {ticker}: {str(e)}")
                import traceback
                traceback.print_exc()
                # Continua para geração de dados simulados abaixo
            
            # Fallback: gerar dados simulados se não conseguir dados reais
            try:
                price_history = []
                value_history = []
                income_history = []
                
                # Simular o intervalo de datas
                date_range = []
                current_date = start_date
                while current_date <= end_date:
                    date_range.append(current_date)
                    current_date += timedelta(days=1)
                
                for date_point in date_range:
                    # Simular volatilidade de preço
                    days_ago = (end_date - date_point).days
                    # Preços tendem a subir ao longo do tempo com alguma volatilidade
                    price_factor = 1 - (days_ago / (3*365)) * 0.15  # 15% mais baixo há 3 anos
                    noise = np.random.normal(0, 0.02)  # 2% de volatilidade diária
                    price = current_price * price_factor * (1 + noise)
                    
                    # Simular ações possuídas (simplificado - assume ações constantes)
                    shares = current_shares
                    
                    # Calcular valor
                    value = shares * price
                    
                    # Calcular renda (simplificado - assume rendimento constante)
                    # Pagamentos de dividendos mensais
                    if date_point.day == 15:  # Pagamento de dividendos no dia 15 de cada mês
                        monthly_yield = current_yield / 12
                        income = value * (monthly_yield / 100)
                    else:
                        income = 0
                    
                    price_history.append((date_point, price))
                    value_history.append((date_point, value))
                    income_history.append((date_point, income))
                
                self.historical_data[ticker] = {
                    'price_history': price_history,
                    'value_history': value_history,
                    'income_history': income_history
                }
                print(f"Dados históricos simulados gerados para {ticker} ({len(price_history)} pontos)")
            except Exception as e:
                print(f"Erro ao gerar dados simulados para {ticker}: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Calcular totais do portfólio
        try:
            print("Calculando totais do portfólio...")
            self.calculate_portfolio_totals(start_date, end_date)
            print("Visualização de dados pronta.")
        except Exception as e:
            print(f"Erro ao calcular totais do portfólio: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Erro", f"Falha ao calcular dados do portfólio: {str(e)}")
            
        # Verificar se conseguimos dados para pelo menos um ticker
        if not self.historical_data:
            QMessageBox.warning(self, "Sem Dados", "Não foi possível obter ou gerar dados históricos.")
            return

    def calculate_portfolio_totals(self, start_date, end_date):
        """Calcula os totais do portfólio para cada data no intervalo histórico"""
        if not self.historical_data:
            print("Sem dados históricos para calcular totais do portfólio")
            return
            
        # Criar lista de todas as datas únicas nos dados históricos
        all_dates = set()
        for ticker in self.historical_data:
            try:
                dates = [date_point for date_point, _ in self.historical_data[ticker]['value_history']]
                all_dates.update(dates)
            except Exception as e:
                print(f"Erro ao extrair datas para {ticker}: {str(e)}")
                continue
        
        if not all_dates:
            print("Não foi possível encontrar datas válidas nos dados históricos")
            return
            
        # Standardize date types (convert all dates to datetime)
        standardized_dates = []
        for date_point in all_dates:
            if isinstance(date_point, datetime_date) and not isinstance(date_point, datetime):
                standardized_dates.append(datetime.combine(date_point, datetime.min.time()))
            else:
                standardized_dates.append(date_point)
                
        all_dates = sorted(standardized_dates)
        print(f"Calculando totais do portfólio para {len(all_dates)} datas únicas")
        
        # Calcular totais do portfólio para cada data
        portfolio_value_history = []
        portfolio_income_history = []
        
        for date_point in all_dates:
            total_value = 0.0
            total_income = 0.0
            
            for ticker in self.historical_data:
                try:
                    # Encontrar o valor para esta data ou datas equivalentes
                    value_history = self.historical_data[ticker]['value_history']
                    
                    # Procurar correspondência de data exata ou por dia
                    value_entries = []
                    for hist_date, value in value_history:
                        # Converter ambas as datas para o mesmo tipo se necessário
                        if isinstance(hist_date, datetime_date) and not isinstance(hist_date, datetime):
                            hist_date = datetime.combine(hist_date, datetime.min.time())
                        if isinstance(date_point, datetime_date) and not isinstance(date_point, datetime):
                            date_dt = datetime.combine(date_point, datetime.min.time())
                        else:
                            date_dt = date_point
                            
                        # Verificar se é a mesma data (ignorando hora/minuto/segundo)
                        if (hist_date.year == date_dt.year and 
                            hist_date.month == date_dt.month and 
                            hist_date.day == date_dt.day):
                            value_entries.append(value)
                    
                    value_on_date = value_entries[0] if value_entries else 0.0
                    total_value += value_on_date
                    
                    # Repetir para o histórico de renda
                    income_history = self.historical_data[ticker]['income_history']
                    income_entries = []
                    for hist_date, income in income_history:
                        # Converter ambas as datas para o mesmo tipo se necessário
                        if isinstance(hist_date, datetime_date) and not isinstance(hist_date, datetime):
                            hist_date = datetime.combine(hist_date, datetime.min.time())
                        if isinstance(date_point, datetime_date) and not isinstance(date_point, datetime):
                            date_dt = datetime.combine(date_point, datetime.min.time())
                        else:
                            date_dt = date_point
                            
                        # Verificar se é a mesma data (ignorando hora/minuto/segundo)
                        if (hist_date.year == date_dt.year and 
                            hist_date.month == date_dt.month and 
                            hist_date.day == date_dt.day):
                            income_entries.append(income)
                    
                    income_on_date = income_entries[0] if income_entries else 0.0
                    total_income += income_on_date
                    
                except Exception as e:
                    print(f"Erro ao calcular valor para {ticker} na data {date_point}: {str(e)}")
                    continue
            
            portfolio_value_history.append((date_point, total_value))
            portfolio_income_history.append((date_point, total_income))
        
        self.historical_data['PORTFOLIO'] = {
            'value_history': portfolio_value_history,
            'income_history': portfolio_income_history
        }
        
        print(f"Totais do portfólio calculados: {len(portfolio_value_history)} pontos de valor, {len(portfolio_income_history)} pontos de renda")
        
    def update_charts(self):
        """Atualiza todos os gráficos com base nas seleções atuais"""
        try:
            # Get filter values
            view = self.view_combo.currentText()
            period = self.period_combo.currentText()
            
            # Set time period based on selection
            end_date = self.end_date.date().toPyDate()  # Isso retorna um objeto date
            
            if period == "1 Month":
                start_date = end_date - timedelta(days=30)
            elif period == "3 Months":
                start_date = end_date - timedelta(days=90)
            elif period == "6 Months":
                start_date = end_date - timedelta(days=180)
            elif period == "1 Year":
                start_date = end_date - timedelta(days=365)
            elif period == "3 Years":
                start_date = end_date - timedelta(days=3*365)
            elif period == "5 Years":
                start_date = end_date - timedelta(days=5*365)
            else:  # All Time
                start_date = datetime_date(2010, 1, 1)  # Arbitrary start date as date object
            
            # Update start date widget
            self.start_date.setDate(QDate(start_date.year, start_date.month, start_date.day))
            
            # O tipo de start_date e end_date aqui deve ser date, não datetime
            print(f"Intervalo de datas: {start_date} a {end_date}")
            print(f"Tipos: {type(start_date)}, {type(end_date)}")
            
            # Update the charts
            self.update_performance_chart(start_date, end_date, view)
            self.update_income_chart(start_date, end_date, view)
            self.update_allocation_chart()
        except Exception as e:
            print(f"Erro ao atualizar gráficos: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def update_performance_chart(self, start_date, end_date, view):
        """Atualiza o gráfico de desempenho do portfólio"""
        if not hasattr(self, 'historical_data') or not self.historical_data:
            self.performance_canvas.axes.clear()
            self.performance_canvas.axes.text(0.5, 0.5, 'Dados históricos não disponíveis', 
                       horizontalalignment='center', verticalalignment='center', 
                       transform=self.performance_canvas.axes.transAxes)
            self.performance_canvas.draw()
            return
            
        ax = self.performance_canvas.axes
        ax.clear()
        
        # Converter start_date e end_date para datetime se forem date
        if isinstance(start_date, type(datetime_date(2020, 1, 1))) and not isinstance(start_date, datetime):
            start_date = datetime.combine(start_date, datetime.min.time())
        if isinstance(end_date, type(datetime_date(2020, 1, 1))) and not isinstance(end_date, datetime):
            end_date = datetime.combine(end_date, datetime.max.time())
        
        if view == "All REITs" or view == "Value Over Time":
            try:
                # Verificar se temos dados para PORTFOLIO
                if 'PORTFOLIO' not in self.historical_data:
                    ax.text(0.5, 0.5, 'Dados do portfólio não disponíveis', 
                           horizontalalignment='center', verticalalignment='center', 
                           transform=ax.transAxes)
                    self.performance_canvas.draw()
                    return
                
                # Filtrar dados do portfólio para o intervalo de datas selecionado
                portfolio_data = []
                for date_point, value in self.historical_data['PORTFOLIO']['value_history']:
                    # Converter date para datetime se for date
                    if isinstance(date_point, type(datetime_date(2020, 1, 1))) and not isinstance(date_point, datetime):
                        date_point = datetime.combine(date_point, datetime.min.time())
                    
                    if start_date <= date_point <= end_date:
                        portfolio_data.append((date_point, value))
                
                if not portfolio_data:
                    ax.text(0.5, 0.5, 'Sem dados disponíveis para o período selecionado', 
                           horizontalalignment='center', verticalalignment='center', 
                           transform=ax.transAxes)
                    self.performance_canvas.draw()
                    return
                
                # Ordenar por data
                portfolio_data.sort(key=lambda x: x[0])
                
                dates = [date_point for date_point, _ in portfolio_data]
                values = [value for _, value in portfolio_data]
                
                if dates and values:
                    # Verificar se há valores não zero
                    if all(value == 0 for value in values):
                        ax.text(0.5, 0.5, 'Todos os valores são zero no período selecionado', 
                               horizontalalignment='center', verticalalignment='center', 
                               transform=ax.transAxes)
                        self.performance_canvas.draw()
                        return
                    
                    # Plotar o valor do portfólio ao longo do tempo
                    ax.plot(dates, values, 'b-', linewidth=2, label='Portfolio Value')
                    
                    # Formatar o gráfico
                    ax.set_title('Portfolio Value Over Time', fontsize=14)
                    ax.set_xlabel('Date', fontsize=12)
                    ax.set_ylabel('Value ($)', fontsize=12)
                    ax.grid(True, linestyle='--', alpha=0.7)
                    
                    # Formatar datas no eixo x
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
                    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
                    plt = self.performance_canvas.fig
                    plt.autofmt_xdate()
                    
                    # Adicionar linha de tendência
                    if len(dates) > 1:
                        try:
                            import numpy as np
                            from scipy import stats
                            
                            # Converter datas para números para regressão linear
                            x = mdates.date2num(dates)
                            y = values
                            
                            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                            
                            # Plotar linha de tendência
                            x_line = np.array([min(x), max(x)])
                            y_line = intercept + slope * x_line
                            
                            # Converter x_line de volta para datas
                            x_line_dates = mdates.num2date(x_line)
                            
                            ax.plot(x_line_dates, y_line, 'r--', linewidth=1, label='Trend Line')
                            
                            # Adicionar R² para mostrar a qualidade do ajuste
                            ax.text(0.02, 0.95, f"R² = {r_value**2:.3f}", transform=ax.transAxes,
                                   fontsize=9, verticalalignment='top',
                                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
                            
                            ax.legend()
                        except Exception as e:
                            print(f"Erro ao calcular linha de tendência: {str(e)}")
                else:
                    ax.text(0.5, 0.5, 'No data available for selected period', 
                           horizontalalignment='center', verticalalignment='center', 
                           transform=ax.transAxes)
            except Exception as e:
                print(f"Erro ao atualizar gráfico de desempenho: {str(e)}")
                import traceback
                traceback.print_exc()
                ax.text(0.5, 0.5, f'Erro ao gerar gráfico: {str(e)}', 
                       horizontalalignment='center', verticalalignment='center', 
                       transform=ax.transAxes)
            
        elif view == "Yield Comparison":
            try:
                # Comparar rendimentos entre REITs
                tickers = [ticker for ticker in self.historical_data.keys() if ticker != 'PORTFOLIO']
                
                if not tickers:
                    ax.text(0.5, 0.5, 'Sem dados de REITs disponíveis', 
                           horizontalalignment='center', verticalalignment='center', 
                           transform=ax.transAxes)
                    self.performance_canvas.draw()
                    return
                
                yields = []
                for ticker in tickers:
                    if ticker in self.portfolio.positions:
                        yields.append(self.portfolio.positions[ticker].dividend_yield)
                    else:
                        yields.append(0)  # Fallback se o ticker não estiver nos dados
                
                # Ordenar por rendimento (do maior para o menor)
                ticker_yield_pairs = sorted(zip(tickers, yields), key=lambda x: x[1], reverse=True)
                tickers = [t for t, _ in ticker_yield_pairs]
                yields = [y for _, y in ticker_yield_pairs]
                
                if tickers and yields:
                    bars = ax.bar(tickers, yields, color='skyblue')
                    
                    # Adicionar rótulos de valor acima das barras
                    for i, v in enumerate(yields):
                        ax.text(i, v + 0.1, f"{v:.2f}%", ha='center')
                    
                    # Formatar o gráfico
                    ax.set_title('Dividend Yield Comparison', fontsize=14)
                    ax.set_xlabel('REIT', fontsize=12)
                    ax.set_ylabel('Dividend Yield (%)', fontsize=12)
                    ax.grid(True, linestyle='--', alpha=0.7, axis='y')
                    
                    # Rotacionar rótulos do eixo x para melhor legibilidade
                    plt = self.performance_canvas.fig
                    plt.autofmt_xdate(rotation=45)
                else:
                    ax.text(0.5, 0.5, 'No yield data available', 
                           horizontalalignment='center', verticalalignment='center', 
                           transform=ax.transAxes)
            except Exception as e:
                print(f"Erro ao atualizar gráfico de comparação de yields: {str(e)}")
                import traceback
                traceback.print_exc()
                ax.text(0.5, 0.5, f'Erro ao gerar gráfico: {str(e)}', 
                       horizontalalignment='center', verticalalignment='center', 
                       transform=ax.transAxes)
        
        self.performance_canvas.draw()
    
    def update_income_chart(self, start_date, end_date, view):
        """Atualiza o gráfico de receita de dividendos"""
        if not hasattr(self, 'historical_data') or not self.historical_data:
            self.income_canvas.axes.clear()
            self.income_canvas.axes.text(0.5, 0.5, 'Dados históricos não disponíveis', 
                       horizontalalignment='center', verticalalignment='center', 
                       transform=self.income_canvas.axes.transAxes)
            self.income_canvas.draw()
            return
            
        ax = self.income_canvas.axes
        ax.clear()
        
        # Converter start_date e end_date para datetime se forem date
        if isinstance(start_date, type(datetime_date(2020, 1, 1))) and not isinstance(start_date, datetime):
            start_date = datetime.combine(start_date, datetime.min.time())
        if isinstance(end_date, type(datetime_date(2020, 1, 1))) and not isinstance(end_date, datetime):
            end_date = datetime.combine(end_date, datetime.max.time())
        
        if view == "All REITs" or view == "Annual Income":
            try:
                # Verificar se temos dados para PORTFOLIO
                if 'PORTFOLIO' not in self.historical_data:
                    ax.text(0.5, 0.5, 'Dados do portfólio não disponíveis', 
                           horizontalalignment='center', verticalalignment='center', 
                           transform=ax.transAxes)
                    self.income_canvas.draw()
                    return
					
                # Filtrar dados de renda para o intervalo de datas selecionado
                portfolio_data = []
                for date, income in self.historical_data['PORTFOLIO']['income_history']:
                    # Converter date para datetime se for date
                    if isinstance(date, type(datetime_date(2020, 1, 1))) and not isinstance(date, datetime):
                        date = datetime.combine(date, datetime.min.time())
                    
                    if start_date <= date <= end_date:
                        portfolio_data.append((date, income))
                
                # Agregar renda mensal
                monthly_income = {}
                
                for date, income in portfolio_data:
                    if income > 0:  # Apenas incluir datas com dividendos
                        month_key = (date.year, date.month)
                        if month_key not in monthly_income:
                            monthly_income[month_key] = 0
                        monthly_income[month_key] += income
                
                if monthly_income:
                    # Ordenar por data
                    month_keys = sorted(monthly_income.keys())
                    months = [datetime(year, month, 15) for year, month in month_keys]  # Usar dia 15 para representar o mês
                    incomes = [monthly_income[key] for key in month_keys]
                    
                    # Criar gráfico de barras para renda mensal
                    bars = ax.bar(months, incomes, width=20, color='green')
                    
                    # Adicionar rótulos de valor acima das barras
                    for i, (month, income) in enumerate(zip(months, incomes)):
                        ax.text(month, income + max(incomes) * 0.02, f"${income:.2f}", 
                               ha='center', va='bottom', fontsize=8, rotation=45)
                    
                    # Calcular e mostrar receita anual total
                    annual_income = sum(incomes)
                    monthly_avg = annual_income / len(incomes) if incomes else 0
                    period_text = f"{len(months)} months"
                    
                    # Adicionar texto informativo
                    ax.text(0.02, 0.95, f"Total Income: ${annual_income:.2f}\nMonthly Avg: ${monthly_avg:.2f}\nPeriod: {period_text}", 
                           transform=ax.transAxes, verticalalignment='top',
                           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
                    
                    # Formatar o gráfico
                    ax.set_title('Monthly Dividend Income', fontsize=14)
                    ax.set_xlabel('Month', fontsize=12)
                    ax.set_ylabel('Income ($)', fontsize=12)
                    ax.grid(True, linestyle='--', alpha=0.7, axis='y')
                    
                    # Formatar datas no eixo x
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
                    if len(months) > 12:
                        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
                    else:
                        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
                    plt = self.income_canvas.fig
                    plt.autofmt_xdate(rotation=45)
                else:
                    ax.text(0.5, 0.5, 'No dividend income data for selected period', 
                           horizontalalignment='center', verticalalignment='center', 
                           transform=ax.transAxes)
            except Exception as e:
                print(f"Erro ao atualizar gráfico de receita: {str(e)}")
                ax.text(0.5, 0.5, f'Erro ao gerar gráfico: {str(e)}', 
                       horizontalalignment='center', verticalalignment='center', 
                       transform=ax.transAxes)
            
        elif view == "Yield Comparison":
            try:
                # Comparar receita anual entre REITs
                tickers = [ticker for ticker in self.historical_data.keys() if ticker != 'PORTFOLIO']
                annual_incomes = []
                
                for ticker in tickers:
                    if ticker in self.portfolio.positions:
                        position = self.portfolio.positions[ticker]
                        metrics = position.calculate_metrics()
                        annual_incomes.append(metrics['annual_income'])
                    else:
                        annual_incomes.append(0)  # Fallback
                
                # Ordenar por receita (do maior para o menor)
                ticker_income_pairs = sorted(zip(tickers, annual_incomes), key=lambda x: x[1], reverse=True)
                tickers = [t for t, _ in ticker_income_pairs]
                annual_incomes = [i for _, i in ticker_income_pairs]
                
                if tickers and annual_incomes:
                    bars = ax.bar(tickers, annual_incomes, color='lightgreen')
                    
                    # Adicionar rótulos de valor acima das barras
                    for i, v in enumerate(annual_incomes):
                        ax.text(i, v + max(annual_incomes) * 0.02, f"${v:.2f}", ha='center')
                    
                    # Formatar o gráfico
                    ax.set_title('Annual Income by REIT', fontsize=14)
                    ax.set_xlabel('REIT', fontsize=12)
                    ax.set_ylabel('Annual Income ($)', fontsize=12)
                    ax.grid(True, linestyle='--', alpha=0.7, axis='y')
                    
                    # Rotacionar rótulos do eixo x para melhor legibilidade
                    plt = self.income_canvas.fig
                    plt.autofmt_xdate(rotation=45)
                else:
                    ax.text(0.5, 0.5, 'No income data available', 
                           horizontalalignment='center', verticalalignment='center', 
                           transform=ax.transAxes)
            except Exception as e:
                print(f"Erro ao atualizar gráfico de comparação de rendimentos: {str(e)}")
                ax.text(0.5, 0.5, f'Erro ao gerar gráfico: {str(e)}', 
                       horizontalalignment='center', verticalalignment='center', 
                       transform=ax.transAxes)
            
        self.income_canvas.draw()
    
    def update_allocation_chart(self):
        if not self.portfolio or not self.portfolio.positions:
            return
            
        ax = self.allocation_canvas.axes
        ax.clear()
        
        # Calcular alocação por custo total
        tickers = []
        costs = []
        names = []
        
        for ticker, position in self.portfolio.positions.items():
            metrics = position.calculate_metrics()
            if metrics['shares'] > 0:
                tickers.append(ticker)
                costs.append(metrics['total_cost'])
                
                # Usar nome completo ou ticker
                name = position.name if position.name else ticker
                names.append(f"{name} ({ticker})")
        
        # Criar um gráfico de pizza
        if costs:
            # Ordenar por custo (maior para menor)
            sorted_data = sorted(zip(names, costs, tickers), key=lambda x: x[1], reverse=True)
            names = [d[0] for d in sorted_data]
            costs = [d[1] for d in sorted_data]
            tickers = [d[2] for d in sorted_data]
            
            # Calcular porcentagens
            total_cost = sum(costs)
            percentages = [cost/total_cost*100 for cost in costs]
            
            # Criar rótulos com ticker, valor e porcentagem
            labels = [f"{name}: ${cost:.2f} ({pct:.1f}%)" for name, cost, pct in zip(names, costs, percentages)]
            
            # Criar o gráfico de pizza com cores atraentes
            colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0','#ffb3e6','#c4e17f','#f7786b',
                     '#8ac6d1','#b6cfb6','#f1e1c2','#a7bed3','#c6d8af','#f5d5cb','#e1ccec','#ffda7a']
            
            # Garantir que temos cores suficientes
            if len(costs) > len(colors):
                from matplotlib.cm import get_cmap
                colors = get_cmap('tab20').colors
            
            # Criar o gráfico de pizza
            wedges, _, autotexts = ax.pie(costs, 
                          autopct='%1.1f%%', 
                          startangle=90,
                          colors=colors[:len(costs)],
                          textprops={'fontsize': 9})
            
            # Colocar rótulos fora do gráfico para melhor legibilidade
            ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            
            # Ajustar cor do texto para contraste com fatias
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title('Portfolio Allocation by Cost', fontsize=14)
            ax.axis('equal')  # Proporção igual garante que o gráfico de pizza seja desenhado como um círculo
            
            # Adicionar informações resumidas
            total_text = f"Total Portfolio Cost: ${total_cost:.2f}"
            ax.text(0.5, -0.1, total_text, ha='center', fontsize=12, transform=ax.transAxes)
        else:
            ax.text(0.5, 0.5, 'No positions available', 
                   horizontalalignment='center', verticalalignment='center', 
                   transform=ax.transAxes)
        
        self.allocation_canvas.draw()
        
    def closeEvent(self, event):
        # Properly close matplotlib figures to avoid memory leaks
        self.performance_canvas.fig.clear()
        self.income_canvas.fig.clear()
        self.allocation_canvas.fig.clear()
        event.accept()

if __name__ == "__main__":
    # Test the dialog
    app = QApplication(sys.argv)
    dialog = PortfolioAnalyticsDialog()
    dialog.show()
    sys.exit(app.exec_())