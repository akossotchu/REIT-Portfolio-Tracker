import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.colors import HexColor
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QCheckBox, QDialogButtonBox, 
                            QLabel, QFrame, QGroupBox)
from PyQt5.QtCore import Qt

class ReportSectionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Report Sections")
        self.setMinimumWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        # Criar layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        title_label = QLabel("Select Sections to Include in Report")
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        layout.addWidget(title_label)
        
        # Explicação
        explanation = QLabel(
            "Choose which sections you want to include in your REIT portfolio report. "
            "The Cover Page and Portfolio Summary are always included."
        )
        explanation.setWordWrap(True)
        explanation.setStyleSheet("color: #555;")
        layout.addWidget(explanation)
        
        # Container para checkboxes com estilo
        sections_group = QGroupBox("Report Sections")
        sections_layout = QVBoxLayout(sections_group)
        
        # Checkboxes para cada seção
        self.cover_check = QCheckBox("Cover Page")
        self.cover_check.setChecked(True)
        self.cover_check.setEnabled(False)  # Sempre incluído
        sections_layout.addWidget(self.cover_check)
        
        self.summary_check = QCheckBox("Portfolio Summary")
        self.summary_check.setChecked(True)
        self.summary_check.setEnabled(False)  # Sempre incluído
        sections_layout.addWidget(self.summary_check)
        
        self.holdings_check = QCheckBox("Holdings Table")
        self.holdings_check.setChecked(True)
        sections_layout.addWidget(self.holdings_check)
        
        self.allocation_check = QCheckBox("Portfolio Allocation")
        self.allocation_check.setChecked(True)
        sections_layout.addWidget(self.allocation_check)
        
        self.dividend_check = QCheckBox("Dividend Growth Analysis")
        self.dividend_check.setChecked(True)
        sections_layout.addWidget(self.dividend_check)
        
        self.nav_check = QCheckBox("NAV Analysis")
        self.nav_check.setChecked(True)
        sections_layout.addWidget(self.nav_check)
        
        layout.addWidget(sections_group)
        
        # Botões
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_selected_sections(self):
        """Retorna um dicionário com as seções selecionadas"""
        return {
            'cover': self.cover_check.isChecked(),         # Sempre True
            'summary': self.summary_check.isChecked(),     # Sempre True
            'holdings': self.holdings_check.isChecked(),
            'allocation': self.allocation_check.isChecked(),
            'dividend': self.dividend_check.isChecked(),
            'nav': self.nav_check.isChecked()
        }

class PortfolioReportGenerator:
    def __init__(self, portfolio, app_instance):
        self.portfolio = portfolio
        self.app = app_instance
        self.styles = getSampleStyleSheet()
        
        # Paleta de cores mais consistente
        self.brand_primary = colors.HexColor("#1a5276")       # Azul escuro (principal)
        self.brand_secondary = colors.HexColor("#2980b9")     # Azul médio (secundário)
        self.brand_accent = colors.HexColor("#3498db")        # Azul claro (destaque)
        self.brand_success = colors.HexColor("#27ae60")       # Verde (valores positivos)
        self.brand_warning = colors.HexColor("#f39c12")       # Laranja (alertas)
        self.brand_danger = colors.HexColor("#c0392b")        # Vermelho (valores negativos)
        self.brand_text = colors.HexColor("#2c3e50")          # Texto principal
        self.brand_light_bg = colors.HexColor("#f5f7fa")      # Fundo claro
        
        # Estilo de título aprimorado
        self.title_style = ParagraphStyle(
            "Title",
            parent=self.styles["Heading1"],
            fontSize=22,
            spaceAfter=14,
            textColor=self.brand_primary,
            alignment=1,  # Centro
            fontName="Helvetica-Bold",
            leading=26
        )
        
        # Estilo de cabeçalho 2 com linha inferior
        self.heading2_style = ParagraphStyle(
            "Heading2",
            parent=self.styles["Heading2"],
            fontSize=16,
            spaceAfter=10,
            spaceBefore=12,
            textColor=self.brand_secondary,
            borderWidth=1,
            borderColor=self.brand_accent,
            borderPadding=(0, 0, 2, 0),  # Apenas borda inferior
            leading=20,
            fontName="Helvetica-Bold"
        )
        
        # Estilo de cabeçalho 3 melhorado
        self.heading3_style = ParagraphStyle(
            "Heading3",
            parent=self.styles["Heading3"],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=10,
            textColor=self.brand_secondary,
            leading=16,
            fontName="Helvetica-Bold"
        )
        
        # Estilo de texto normal mais legível
        self.normal_style = ParagraphStyle(
            "Normal",
            parent=self.styles["Normal"],
            fontSize=10,
            spaceAfter=6,
            leading=14,
            textColor=self.brand_text
        )
        
        # Estilo de legenda melhorado
        self.caption_style = ParagraphStyle(
            "Caption",
            parent=self.styles["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#7f8c8d"),
            alignment=1,  # Centro
            fontName="Helvetica-Oblique",
            spaceAfter=8
        )
        
        # Estilo para dados destacados
        self.highlight_style = ParagraphStyle(
            "Highlight",
            parent=self.styles["Normal"],
            fontSize=11,
            textColor=self.brand_primary,
            fontName="Helvetica-Bold"
        )
        
        # Paleta de cores para gráficos - cores mais harmoniosas
        self.color_palette = [
            '#1a5276', '#2980b9', '#3498db', '#85c1e9', '#aed6f1',  # Tons de azul
            '#27ae60', '#58d68d', '#2ecc71',                        # Tons de verde
            '#f39c12', '#f1c40f', '#f8c471',                        # Tons de amarelo/laranja
            '#c0392b', '#e74c3c', '#ec7063',                        # Tons de vermelho
            '#8e44ad', '#9b59b6', '#d2b4de'                         # Tons de roxo
        ]
        
    def generate_report(self, filename, sections=None):
        """
        Gera um relatório de portfólio em formato PDF com as seções selecionadas
        
        Args:
            filename (str): Caminho do arquivo PDF a ser gerado
            sections (dict, optional): Dicionário com as seções a incluir. 
                                      Se None, todas as seções são incluídas.
        """
        # Definir seções padrão caso nenhuma seja fornecida
        if sections is None:
            sections = {
                'cover': True,
                'summary': True,
                'holdings': True,
                'allocation': True,
                'dividend': True,
                'nav': True
            }
        
        # Definir margens mais profissionais
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            leftMargin=20*mm,
            rightMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm,
            title="REIT Portfolio Report",
            author="Portfolio Manager"
        )
        
        # Container para os objetos Flowable
        elements = []
        
        # Adicionar página de capa (sempre incluída)
        if sections.get('cover', True):
            self.generate_cover_page(elements)
        
        # Adicionar cabeçalho (sempre incluído)
        self.add_header(elements)
        
        # Adicionar sumário do portfólio (sempre incluído)
        if sections.get('summary', True):
            self.add_portfolio_summary(elements)
        
        # Adicionar tabela de participações
        if sections.get('holdings', True):
            self.add_holdings_table(elements)
        
        # Adicionar gráfico de alocação
        if sections.get('allocation', True):
            self.add_allocation_chart(elements)
        
        # Adicionar análise de crescimento de dividendos
        if sections.get('dividend', True):
            self.add_dividend_growth_analysis(elements)
        
        # Add sector-based dividend growth analysis
        if sections.get('dividend', True):
            self.add_sector_dividend_growth_analysis(elements)
		
        # Adicionar análise de NAV
        if sections.get('nav', True):
            self.add_nav_analysis(elements)
        
        # Criar o PDF com numeração de página
        doc.build(elements, onFirstPage=self.add_page_number, onLaterPages=self.add_page_number)
        
        return filename
        
    def add_header(self, elements):
        """Cabeçalho aprimorado com logotipo e linha decorativa"""
        # Criar tabela para o cabeçalho com duas colunas
        # (no futuro pode incluir logotipo na esquerda)
        header_data = [[
            '',  # Espaço para logo futuro
            Paragraph("REIT Portfolio Report", self.title_style)
        ]]
        header_table = Table(header_data, colWidths=[80, 400])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ]))
        elements.append(header_table)
        
        # Data de geração com formatação aprimorada
        today = datetime.now()
        date_text = f"<i>Generated on: {today.strftime('%B %d, %Y at %H:%M')}</i>"
        elements.append(Paragraph(date_text, self.caption_style))
        
        # Linha decorativa de estilo duplo (mais fina em cima, mais grossa embaixo)
        elements.append(Spacer(1, 3*mm))
        elements.append(Table([['']], colWidths=[450], rowHeights=[0.5], 
                       style=TableStyle([('LINEABOVE', (0, 0), (0, 0), 0.5, self.brand_accent)])))
        elements.append(Spacer(1, 1*mm))  # Pequeno espaço entre as linhas
        elements.append(Table([['']], colWidths=[450], rowHeights=[0.5], 
                       style=TableStyle([('LINEABOVE', (0, 0), (0, 0), 2, self.brand_primary)])))
        
        # Adicionar um subtítulo que descreve o propósito do relatório
        elements.append(Spacer(1, 5*mm))
        elements.append(Paragraph(
            "This report provides a comprehensive overview of your REIT portfolio, "
            "including performance metrics, holdings, allocation, and dividend growth analysis.",
            self.normal_style
        ))
        elements.append(Spacer(1, 10*mm))
        
    def add_portfolio_summary(self, elements):
        """Resumo do portfólio com layout em colunas e indicadores visuais"""
        elements.append(Paragraph("Portfolio Summary", self.heading2_style))
        
        # Obter métricas do portfólio
        metrics = self.portfolio.calculate_portfolio_metrics()
        
        # Introdução com informações gerais
        active_positions = len([p for p in self.portfolio.positions.values() if p.calculate_metrics()['shares'] > 0])
        intro_text = (
            f"Your portfolio contains <b>{active_positions}</b> different REITs "
            f"with a current total value of <b>${metrics['total_value']:,.2f}</b>."
        )
        elements.append(Paragraph(intro_text, self.normal_style))
        elements.append(Spacer(1, 5*mm))
        
        # Criar tabela de resumo com duas colunas principais
        data = []
        
        # Títulos das seções - usando Paragraph para garantir formatação correta
        data.append([
            Paragraph("<b>Value &amp; Performance</b>", self.highlight_style),
            Paragraph("<b>Income &amp; Yield</b>", self.highlight_style)
        ])
        
        # Linhas de dados - valor e custo
        profit_loss = metrics['total_profit_loss']
        profit_loss_sign = "+" if profit_loss >= 0 else "-"
        
        # Definir cor com base no sinal de lucro/perda
        profit_loss_color = self.brand_success if profit_loss >= 0 else self.brand_danger
        hex_color = profit_loss_color.hexval() if hasattr(profit_loss_color, 'hexval') else profit_loss_color.hex_value
        
        # Remover o símbolo # se estiver presente e então adicionar novamente de forma correta
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
        
        # Calcular percentual de ganho/perda
        pct_change = (profit_loss / metrics['total_cost'] * 100) if metrics['total_cost'] > 0 else 0
        
        # Linhas de valores - usando Paragraph para garantir formatação correta
        data.append([
            Paragraph(f"Total Value: <b>${metrics['total_value']:,.2f}</b>", self.normal_style),
            Paragraph(f"Portfolio Yield: <b>{metrics['portfolio_yield']:.2f}%</b>", self.normal_style)
        ])
        
        data.append([
            Paragraph(f"Total Cost: <b>${metrics['total_cost']:,.2f}</b>", self.normal_style),
            Paragraph(f"Yield on Cost: <b>{metrics['portfolio_yield_on_cost']:.2f}%</b>", self.normal_style)
        ])
        
        # P/L com cor condicional - usando Paragraph completo
        profit_loss_text = (
            f"Profit/Loss: <font color=\"#{hex_color}\"><b>{profit_loss_sign}${abs(profit_loss):,.2f}</b> "
            f"({profit_loss_sign}{abs(pct_change):.2f}%)</font>"
        )
        
        data.append([
            Paragraph(profit_loss_text, self.normal_style),
            Paragraph(f"Annual Income: <b>${metrics['total_annual_income']:,.2f}</b>", self.normal_style)
        ])
        
        # Renda mensal
        monthly_income_usd = metrics['total_annual_income'] / 12
        data.append([
            Paragraph("", self.normal_style),  # Célula vazia formatada corretamente
            Paragraph(f"Monthly Income: <b>${monthly_income_usd:,.2f}</b>", self.normal_style)
        ])
        
        # Se disponível, adicione a conversão para BRL
        try:
            usd_brl_rate = self.app.get_usd_to_brl_rate()
            monthly_income_brl = monthly_income_usd * usd_brl_rate
            after_tax_monthly_income_brl = monthly_income_brl * 0.7  # 30% imposto
            
            data.append([
                Paragraph("", self.normal_style),
                Paragraph(f"Monthly Income (BRL): <b>R$ {monthly_income_brl:,.2f}</b>", self.normal_style)
            ])
            
            data.append([
                Paragraph("", self.normal_style),
                Paragraph(f"After-tax Monthly Income (BRL): <b>R$ {after_tax_monthly_income_brl:,.2f}</b>", self.normal_style)
            ])
        except:
            pass
        
        # Criar e estilizar a tabela
        available_width = 160*mm
        col_widths = [available_width/2.0, available_width/2.0]
        summary_table = Table(data, colWidths=col_widths)
        
        # Estilo base da tabela
        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            
            # Estilo para a linha de título
            ('BACKGROUND', (0, 0), (-1, 0), self.brand_light_bg),
            ('LINEBELOW', (0, 0), (-1, 0), 1, self.brand_primary),
        ]
        
        # Adicionar cor de fundo alternada para cada seção
        for i in range(1, len(data)):
            if i % 2 == 0:
                table_style.append(('BACKGROUND', (0, i), (-1, i), self.brand_light_bg))
        
        summary_table.setStyle(TableStyle(table_style))
        elements.append(summary_table)
        
        # Adicionar nota informativa - usando Paragraph com tags HTML corretas
        elements.append(Spacer(1, 5*mm))
        note_text = (
            "<i>Note: Yield metrics are based on current dividend rates. "
            "Income projections assume no changes in dividends or portfolio composition.</i>"
        )
        elements.append(Paragraph(note_text, self.caption_style))
        elements.append(Spacer(1, 10*mm))
        
    def add_holdings_table(self, elements):
        """Tabela de participações aprimorada com visual mais profissional"""
		
        elements.append(PageBreak())
		
        elements.append(Paragraph("Portfolio Holdings", self.heading2_style))
        
        # Dados do portfólio para cálculo de percentuais
        portfolio_metrics = self.portfolio.calculate_portfolio_metrics()
        total_portfolio_value = portfolio_metrics["total_value"]
        
        # Texto introdutório com mais detalhes
        active_positions = [p for p in self.portfolio.positions.values() if p.calculate_metrics()['shares'] > 0]
        elements.append(Paragraph(
            f"Your portfolio consists of {len(active_positions)} different REITs "
            f"with a total market value of ${total_portfolio_value:,.2f}. "
            f"The table below presents all holdings sorted by position value.",
            self.normal_style
        ))
        elements.append(Spacer(1, 5*mm))
        
        # Cabeçalhos da tabela - com abreviações mais claras
        headers = [
            "Ticker", 
            "Shares", 
            "Price ($)", 
            "Value ($)", 
            "Avg. Cost", 
            "P/L ($)", 
            "Div. Yield", 
            "YOC", 
            "Annual Inc.",
            "% of Port."
        ]
        
        # Dados da tabela
        table_data = [headers]
        
        # Ordenar posições por valor (maior primeiro)
        sorted_positions = sorted(
            [(ticker, position) for ticker, position in self.portfolio.positions.items()],
            key=lambda x: x[1].calculate_metrics()["position_value"],
            reverse=True
        )
        
        # Adicionar linhas para cada posição
        total_annual_income = 0
        for ticker, position in sorted_positions:
            metrics = position.calculate_metrics()
            shares = metrics["shares"]
            
            if shares <= 0:
                continue
                
            position_value = metrics["position_value"]
            percentage = (position_value / total_portfolio_value * 100) if total_portfolio_value > 0 else 0
            
            # Formatação de lucro/perda com sinal + para valores positivos
            profit_loss = metrics['profit_loss']
            profit_loss_str = f"+{profit_loss:.2f}" if profit_loss >= 0 else f"{profit_loss:.2f}"
            
            row = [
                ticker,
                f"{int(shares) if shares.is_integer() else shares:.3f}",
                f"{position.current_price:.2f}",
                f"{position_value:.2f}",
                f"{metrics['average_cost']:.2f}",
                profit_loss_str,
                f"{position.dividend_yield:.2f}%",
                f"{metrics['yield_on_cost']:.2f}%",
                f"{metrics['annual_income']:.2f}",
                f"{percentage:.2f}%"
            ]
            
            total_annual_income += metrics['annual_income']
            table_data.append(row)
            
        # Adicionar linha de total para colunas-chave
        total_row = ["TOTAL", "", "", f"{total_portfolio_value:.2f}", "", "", "", "", f"{total_annual_income:.2f}", "100.00%"]
        table_data.append(total_row)
            
        # Calcular larguras das colunas - melhor distribuição
        available_width = 160*mm
        col_widths = [
            16*mm,      # Ticker
            14*mm,      # Shares
            14*mm,      # Price
            20*mm,      # Position Value
            16*mm,      # Average Cost
            16*mm,      # P/L
            16*mm,      # Dividend Yield
            14*mm,      # YOC
            18*mm,      # Annual Income
            16*mm       # % of Port
        ]
            
        # Criar a tabela
        holdings_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Estilo da tabela - versão aprimorada
        table_style = [
            # Estilo do cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), self.brand_primary),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            
            # Grade e alinhamento
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),      # Alinhar tickers à esquerda
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),    # Alinhar valores à direita
            
            # Estilo para a linha de totais
            ('BACKGROUND', (0, -1), (-1, -1), self.brand_primary),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]
        
        # Cor de fundo alternada para melhor legibilidade
        for i in range(1, len(table_data) - 1):  # Pular cabeçalho e linha de total
            if i % 2 == 0:
                table_style.append(('BACKGROUND', (0, i), (-1, i), self.brand_light_bg))
        
        # Colorir coluna de lucro/perda com base no valor
        pl_col = 5  # Índice da coluna P/L
        for i in range(1, len(table_data) - 1):  # Pular cabeçalho e linha de total
            try:
                pl_value = float(table_data[i][pl_col])
                if pl_value < 0:
                    table_style.append(('TEXTCOLOR', (pl_col, i), (pl_col, i), self.brand_danger))
                    table_style.append(('FONTNAME', (pl_col, i), (pl_col, i), 'Helvetica-Bold'))
                else:
                    table_style.append(('TEXTCOLOR', (pl_col, i), (pl_col, i), self.brand_success))
                    table_style.append(('FONTNAME', (pl_col, i), (pl_col, i), 'Helvetica-Bold'))
            except:
                pass
        
        # Destacar rendimentos de dividendos altos em verde
        div_yield_col = 6  # Índice da coluna de Dividend Yield
        for i in range(1, len(table_data) - 1):  # Pular cabeçalho e total
            try:
                yield_value = float(table_data[i][div_yield_col].strip('%'))
                if yield_value > 8:  # Rendimento muito alto
                    table_style.append(('TEXTCOLOR', (div_yield_col, i), (div_yield_col, i), self.brand_success))
                    table_style.append(('FONTNAME', (div_yield_col, i), (div_yield_col, i), 'Helvetica-Bold'))
                elif yield_value > 6:  # Rendimento alto
                    table_style.append(('TEXTCOLOR', (div_yield_col, i), (div_yield_col, i), self.brand_success))
            except:
                pass
        
        # Destacar YOC alto em verde
        yoc_col = 7  # Índice da coluna YOC
        for i in range(1, len(table_data) - 1):  # Pular cabeçalho e total
            try:
                yoc_value = float(table_data[i][yoc_col].strip('%'))
                if yoc_value > 8:  # YOC muito alto
                    table_style.append(('TEXTCOLOR', (yoc_col, i), (yoc_col, i), self.brand_success))
                    table_style.append(('FONTNAME', (yoc_col, i), (yoc_col, i), 'Helvetica-Bold'))
                elif yoc_value > 6:  # YOC alto
                    table_style.append(('TEXTCOLOR', (yoc_col, i), (yoc_col, i), self.brand_success))
            except:
                pass
                
        # Destacar posições que representam grande percentual do portfólio
        pct_col = 9  # Índice da coluna de percentual
        for i in range(1, len(table_data) - 1):  # Pular cabeçalho e total
            try:
                pct_value = float(table_data[i][pct_col].strip('%'))
                if pct_value > 15:  # Posição principal (>15%)
                    table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor("#fadbd8")))  # Fundo vermelho claro
                    table_style.append(('TEXTCOLOR', (pct_col, i), (pct_col, i), self.brand_danger))
                    table_style.append(('FONTNAME', (pct_col, i), (pct_col, i), 'Helvetica-Bold'))
                elif pct_value > 10:  # Posição significativa (>10%)
                    table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor("#fef9e7")))  # Fundo amarelo claro
                    table_style.append(('TEXTCOLOR', (pct_col, i), (pct_col, i), self.brand_warning))
                    table_style.append(('FONTNAME', (pct_col, i), (pct_col, i), 'Helvetica-Bold'))
            except:
                pass
                
        holdings_table.setStyle(TableStyle(table_style))
        elements.append(holdings_table)
        
        # Adicionar legenda explicativa com ícones visuais
        elements.append(Spacer(1, 5*mm))
        legend_text = (
            "<i><b>Legend:</b> "
            "<font color='#27ae60'>■</font> High yield (>6%) "
            "<font color='#f39c12'>■</font> Significant position (>10%) "
            "<font color='#c0392b'>■</font> Major position (>15%) "
            "<font color='#27ae60'>+</font> Profit "
            "<font color='#c0392b'>-</font> Loss</i>"
        )
        elements.append(Paragraph(legend_text, self.caption_style))
        elements.append(Spacer(1, 10*mm))
        
    def add_allocation_chart(self, elements):
        """Adiciona seção de alocação do portfólio com tabela aprimorada e barras visuais"""
        elements.append(PageBreak())
        elements.append(Paragraph("Portfolio Allocation", self.heading2_style))
        
        # Obter métricas do portfólio para valores
        metrics = self.portfolio.calculate_portfolio_metrics()
        position_values = metrics["position_values"]
        total_value = metrics["total_value"]
        
        # Texto introdutório
        elements.append(Paragraph(
            "This section shows how your portfolio is allocated across different REITs. "
            "The table below includes visual indicators of allocation percentage to help "
            "identify concentration risks.",
            self.normal_style
        ))
        elements.append(Spacer(1, 8*mm))
        
        # Ordenar posições por valor (maior primeiro)
        sorted_positions = sorted(
            [(ticker, value) for ticker, value in position_values.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Criar uma tabela para mostrar a alocação com barras visuais
        table_data = [["Ticker", "Value ($)", "Percentage", "Visual Allocation"]]
        
        # Adicionar linhas para cada posição
        for ticker, value in sorted_positions:
            percentage = (value / total_value * 100) if total_value > 0 else 0
            
            # Criar barra visual de alocação
            bar_width = int(percentage) * 3  # 3mm por cada ponto percentual
            
            # Definir cor com base no percentual
            if percentage > 15:
                bar_color = self.brand_danger
            elif percentage > 10:
                bar_color = self.brand_warning
            elif percentage > 5:
                bar_color = self.brand_accent
            else:
                bar_color = self.brand_primary
                
            # Obter código hexadecimal da cor de forma segura
            hex_color = bar_color.hexval() if hasattr(bar_color, 'hexval') else bar_color.hex_value
            if hex_color.startswith('#'):
                hex_color = hex_color[1:]
                
            # Criar representação visual de barra usando HTML+CSS
            bar_symbols = "■" * int(percentage)
            visual_bar = Paragraph(f'<font color="#{hex_color}">{bar_symbols}</font>', self.normal_style)
            
            table_data.append([
                ticker,
                f"{value:,.2f}",
                f"{percentage:.2f}%",
                visual_bar
            ])
            
        # Adicionar linha de total
        table_data.append([
            "Total",
            f"{total_value:,.2f}",
            "100.00%",
            ""
        ])
        
        # Criar a tabela com larguras de coluna otimizadas
        available_width = 160*mm
        col_widths = [30*mm, 40*mm, 30*mm, 60*mm]
        allocation_table = Table(table_data, colWidths=col_widths)
        
        # Estilo da tabela
        table_style = [
            # Estilo do cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), self.brand_primary),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            
            # Grade e alinhamento
            ('GRID', (0, 0), (2, -1), 0.5, colors.lightgrey),  # Grade apenas nas três primeiras colunas
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),       # Alinhar tickers à esquerda
            ('ALIGN', (1, 1), (2, -1), 'RIGHT'),      # Alinhar valores e percentuais à direita
            ('ALIGN', (3, 0), (3, -1), 'LEFT'),       # Alinhar barras à esquerda
            
            # Estilo para linha de total
            ('BACKGROUND', (0, -1), (2, -1), self.brand_light_bg),
            ('FONTNAME', (0, -1), (2, -1), 'Helvetica-Bold'),
            ('LINEABOVE', (0, -1), (2, -1), 1, self.brand_primary),
        ]
        
        # Cor de fundo alternada para melhor legibilidade
        for i in range(1, len(table_data) - 1):  # Pular cabeçalho e total
            if i % 2 == 0:
                table_style.append(('BACKGROUND', (0, i), (2, i), self.brand_light_bg))
        
        # Colorir a coluna de percentuais com base no valor
        for i in range(1, len(table_data) - 1):  # Pular cabeçalho e total
            try:
                percentage = float(table_data[i][2].replace('%', ''))
                if percentage > 15:  # Posição principal
                    table_style.append(('TEXTCOLOR', (2, i), (2, i), self.brand_danger))
                    table_style.append(('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'))
                elif percentage > 10:  # Posição significativa
                    table_style.append(('TEXTCOLOR', (2, i), (2, i), self.brand_warning))
                    table_style.append(('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'))
                elif percentage > 5:   # Posição moderada
                    table_style.append(('TEXTCOLOR', (2, i), (2, i), self.brand_accent))
            except:
                pass
                
        allocation_table.setStyle(TableStyle(table_style))
        elements.append(allocation_table)
        
        # Adicionar legenda explicativa com formatação corrigida
        elements.append(Spacer(1, 5*mm))
        
        # Obter códigos de cores hexadecimais de forma segura
        danger_hex = self.brand_danger.hexval() if hasattr(self.brand_danger, 'hexval') else self.brand_danger.hex_value
        warning_hex = self.brand_warning.hexval() if hasattr(self.brand_warning, 'hexval') else self.brand_warning.hex_value
        accent_hex = self.brand_accent.hexval() if hasattr(self.brand_accent, 'hexval') else self.brand_accent.hex_value
        primary_hex = self.brand_primary.hexval() if hasattr(self.brand_primary, 'hexval') else self.brand_primary.hex_value
        
        # Remover # se presente
        if danger_hex.startswith('#'): danger_hex = danger_hex[1:]
        if warning_hex.startswith('#'): warning_hex = warning_hex[1:]
        if accent_hex.startswith('#'): accent_hex = accent_hex[1:]
        if primary_hex.startswith('#'): primary_hex = primary_hex[1:]
        
        legend_text = (
            "<i><b>Legend:</b> "
            f'<font color="#{danger_hex}">■</font> Major position (>15%) ' 
            f'<font color="#{warning_hex}">■</font> Significant position (>10%) '
            f'<font color="#{accent_hex}">■</font> Moderate position (>5%) '
            f'<font color="#{primary_hex}">■</font> Standard position (≤5%)</i>'
        )
        
        elements.append(Paragraph(legend_text, self.caption_style))
        
        # Adicionar aviso sobre concentração de portfólio
        elements.append(Spacer(1, 8*mm))
        concentration_warning = ""
        
        # Verificar se há posições acima de 15%
        major_positions = [pos for pos, val in sorted_positions if (val/total_value*100) > 15]
        if major_positions:
            concentration_warning = (
                "<b>Portfolio Concentration Alert:</b> "
                f"Your portfolio has {len(major_positions)} major positions "
                f"({', '.join(major_positions)}) each representing over 15% of total value. "
                "Consider diversification to reduce concentration risk."
            )
        else:
            # Verificar se há posições acima de 10%
            significant_positions = [pos for pos, val in sorted_positions if (val/total_value*100) > 10]
            if significant_positions:
                concentration_warning = (
                    "<b>Note:</b> "
                    f"Your portfolio has {len(significant_positions)} significant positions "
                    f"({', '.join(significant_positions)}) each representing over 10% of total value. "
                    "This is generally considered a reasonable concentration."
                )
            else:
                concentration_warning = (
                    "<b>Diversification Note:</b> "
                    "Your portfolio appears well diversified with no individual position exceeding 10% of total value."
                )
        
        elements.append(Paragraph(concentration_warning, self.normal_style))
        elements.append(Spacer(1, 10*mm))
        
    def add_dividend_growth_analysis(self, elements):
        """Análise de crescimento de dividendos aprimorada com representação visual"""
        elements.append(PageBreak())
        elements.append(Paragraph("Dividend Growth Analysis", self.heading2_style))
        
        # Introdução explicativa
        elements.append(Paragraph(
            "This section analyzes the dividend growth history of your holdings. "
            "CAGR (Compound Annual Growth Rate) values represent the average annual rate "
            "at which dividends have increased over the specified period.",
            self.normal_style
        ))
        elements.append(Spacer(1, 8*mm))
        
        # Adicionar métricas de CAGR do portfólio
        metrics = self.portfolio.calculate_portfolio_metrics()
        elements.append(Paragraph("Portfolio Dividend Growth Summary", self.heading3_style))
        
        # Criar tabela de resumo com representação visual de crescimento
        cagr_data = []
        
        # Cabeçalho
        cagr_data.append(["Timeframe", "CAGR", "Visual Indicator"])
        
        # Dados de CAGR de 3 anos
        cagr_3y = metrics['weighted_dg_3y']
        cagr_3y_color = self._get_growth_color(cagr_3y)
        cagr_3y_visual = self._create_growth_indicator(cagr_3y)
        
        cagr_data.append([
            "3-Year Dividend Growth",
            f"{cagr_3y:.2f}%",
            Paragraph(cagr_3y_visual, self.normal_style)
        ])
        
        # Dados de CAGR de 5 anos
        cagr_5y = metrics['weighted_dg_5y']
        cagr_5y_color = self._get_growth_color(cagr_5y)
        cagr_5y_visual = self._create_growth_indicator(cagr_5y)
        
        cagr_data.append([
            "5-Year Dividend Growth",
            f"{cagr_5y:.2f}%",
            Paragraph(cagr_5y_visual, self.normal_style)
        ])
        
        # Criar e estilizar a tabela de resumo
        available_width = 160*mm
        cagr_summary_table = Table(cagr_data, colWidths=[available_width*0.4, available_width*0.2, available_width*0.4])
        cagr_summary_table.setStyle(TableStyle([
            # Estilo do cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), self.brand_primary),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            
            # Cor de fundo para linhas
            ('BACKGROUND', (0, 1), (-1, 1), self.brand_light_bg),
            
            # Grade e alinhamento
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            
            # Cores personalizadas para valores CAGR
            ('TEXTCOLOR', (1, 1), (1, 1), cagr_3y_color),
            ('TEXTCOLOR', (1, 2), (1, 2), cagr_5y_color),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(cagr_summary_table)
        
        # Adicionar interpretação dos resultados
        elements.append(Spacer(1, 5*mm))
        
        # Análise personalizada com base nos valores de CAGR
        cagr_analysis = self._get_cagr_analysis(cagr_3y, cagr_5y)
        elements.append(Paragraph(cagr_analysis, self.normal_style))
        elements.append(Spacer(1, 10*mm))
        
        # Criar uma tabela para crescimento de dividendos por posição
        elements.append(Paragraph("Dividend Growth by Position", self.heading3_style))
        
        headers = ["Ticker", "Current Yield", "3yr CAGR", "5yr CAGR", "Annual Income", "Growth Rating"]
        
        # Construir dados
        table_data = [headers]
        
        # Ordenar posições por crescimento de dividendos de 5 anos (maior primeiro)
        sorted_positions = sorted(
            [(ticker, position) for ticker, position in self.portfolio.positions.items()
             if position.calculate_metrics()["shares"] > 0],
            key=lambda x: x[1].dividend_growth_5y if x[1].dividend_growth_5y > 0 else -1,
            reverse=True
        )
        
        # Adicionar linhas para cada posição
        for ticker, position in sorted_positions:
            metrics = position.calculate_metrics()
            
            # Pular posições sem ações
            if metrics["shares"] <= 0:
                continue
                
            # Pular posições sem dados de crescimento de dividendos
            if position.dividend_growth_3y == 0 and position.dividend_growth_5y == 0:
                continue
                
            # Calcular classificação de crescimento
            growth_rating = self._calculate_growth_rating(position.dividend_growth_3y, position.dividend_growth_5y)
            
            row = [
                ticker,
                f"{position.dividend_yield:.2f}%",
                f"{position.dividend_growth_3y:.2f}%" if position.dividend_growth_3y > 0 else "N/A",
                f"{position.dividend_growth_5y:.2f}%" if position.dividend_growth_5y > 0 else "N/A",
                f"${metrics['annual_income']:.2f}",
                growth_rating
            ]
            table_data.append(row)
            
        # Se não houver dados, adicionar uma mensagem
        if len(table_data) == 1:
            elements.append(Paragraph("No dividend growth data available for the positions in this portfolio.", 
                                    self.normal_style))
            elements.append(Spacer(1, 5*mm))
            return
            
        # Criar a tabela
        available_width = 160*mm
        col_widths = [
            20*mm,      # Ticker
            25*mm,      # Current Yield
            25*mm,      # 3yr CAGR
            25*mm,      # 5yr CAGR
            30*mm,      # Annual Income
            35*mm,      # Growth Rating
        ]
        positions_cagr_table = Table(table_data, colWidths=col_widths)
        
        # Adicionar estilo à tabela
        table_style = [
            # Estilo do cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), self.brand_primary),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            
            # Grade e alinhamento
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),       # Alinhar coluna de ticker à esquerda
            ('ALIGN', (1, 1), (4, -1), 'CENTER'),     # Alinhar colunas numéricas ao centro
            ('ALIGN', (5, 1), (5, -1), 'CENTER'),     # Alinhar classificação ao centro
        ]
        
        # Cor de fundo alternada
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                table_style.append(('BACKGROUND', (0, i), (-1, i), self.brand_light_bg))
                
        # Colorir os valores de crescimento de dividendos
        for i in range(1, len(table_data)):
            # Colorir CAGR de 3 anos
            if table_data[i][2] != "N/A":
                try:
                    cagr_3yr = float(table_data[i][2].strip("%"))
                    color = self._get_growth_color(cagr_3yr)
                    table_style.append(('TEXTCOLOR', (2, i), (2, i), color))
                    if cagr_3yr > 10:  # Crescimento excepcional
                        table_style.append(('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'))
                except:
                    pass
            
            # Colorir CAGR de 5 anos
            if table_data[i][3] != "N/A":
                try:
                    cagr_5yr = float(table_data[i][3].strip("%"))
                    color = self._get_growth_color(cagr_5yr)
                    table_style.append(('TEXTCOLOR', (3, i), (3, i), color))
                    if cagr_5yr > 10:  # Crescimento excepcional
                        table_style.append(('FONTNAME', (3, i), (3, i), 'Helvetica-Bold'))
                except:
                    pass
                    
            # Colorir classificação de crescimento
            growth_rating = table_data[i][5]
            rating_color = self.brand_text
            if "Excellent" in growth_rating:
                rating_color = self.brand_success
                table_style.append(('FONTNAME', (5, i), (5, i), 'Helvetica-Bold'))
            elif "Good" in growth_rating:
                rating_color = self.brand_success
            elif "Moderate" in growth_rating:
                rating_color = self.brand_accent
            elif "Weak" in growth_rating:
                rating_color = self.brand_warning
            elif "Poor" in growth_rating:
                rating_color = self.brand_danger
            
            table_style.append(('TEXTCOLOR', (5, i), (5, i), rating_color))
                    
        positions_cagr_table.setStyle(TableStyle(table_style))
        
        elements.append(positions_cagr_table)
        elements.append(Spacer(1, 5*mm))
        
        # Adicionar legenda sobre cores - com formatação correta das tags font
        # Obter códigos hexadecimais de forma segura
        success_hex = self.brand_success.hexval() if hasattr(self.brand_success, 'hexval') else self.brand_success.hex_value
        accent_hex = self.brand_accent.hexval() if hasattr(self.brand_accent, 'hexval') else self.brand_accent.hex_value
        warning_hex = self.brand_warning.hexval() if hasattr(self.brand_warning, 'hexval') else self.brand_warning.hex_value
        danger_hex = self.brand_danger.hexval() if hasattr(self.brand_danger, 'hexval') else self.brand_danger.hex_value
        
        # Remover # se presente
        if success_hex.startswith('#'): success_hex = success_hex[1:]
        if accent_hex.startswith('#'): accent_hex = accent_hex[1:]
        if warning_hex.startswith('#'): warning_hex = warning_hex[1:]
        if danger_hex.startswith('#'): danger_hex = danger_hex[1:]
        
        legend_text = (
            "<i><b>Legend:</b> Growth rates >10% (Excellent) are highlighted in "
            f'<font color="#{success_hex}">bold green</font>, '
            f'>5% (Good) in <font color="#{success_hex}">green</font>, '
            f'>2% (Moderate) in <font color="#{accent_hex}">blue</font>, '
            f'>0% (Weak) in <font color="#{warning_hex}">orange</font>, and '
            f'≤0% (Poor) in <font color="#{danger_hex}">red</font>.</i>'
        )
        
        elements.append(Paragraph(legend_text, self.caption_style))
        
    def add_sector_dividend_growth_analysis(self, elements):
        """Adds a sector-based dividend growth analysis table to the report"""
        import requests
        from bs4 import BeautifulSoup
        import pandas as pd
        import yfinance as yf
        
        # Add page break before starting this section
        elements.append(PageBreak())
        
        # Create subheading for the section
        elements.append(Paragraph("Sector-Based Dividend Growth Analysis", self.heading3_style))
        
        # Introduction text
        elements.append(Paragraph(
            "This analysis shows the average dividend growth rates grouped by REIT sectors. "
            "This can help identify which sectors are delivering the strongest dividend growth "
            "and may warrant increased allocation.",
            self.normal_style
        ))
        elements.append(Spacer(1, 8*mm))
        
        # Function to get sector information from alreits.com
        def get_sector_from_alreits(ticker):
            try:
                url = f"https://alreits.com/reits/{ticker}"
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                response = requests.get(url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Look for the sector information in the specified class
                    sector_elements = soup.find_all(class_="MuiTypography-root MuiTypography-body1 LabeledIcon__Label-sc-1l6onqv-2 hHdysU css-99u0rr")
                    
                    # If we found potential sector elements, check each one
                    for element in sector_elements:
                        # The sector typically appears after a label like "Sector:" or similar
                        # We'll take the first valid sector we find
                        if element.text and len(element.text) > 0:
                            return element.text
                
                # If we get here, we couldn't find the sector
                return None
                
            except Exception as e:
                print(f"Error getting sector for {ticker} from alreits.com: {e}")
                return None
        
        # Function to get sector information from yfinance as fallback
        def get_sector_from_yfinance(ticker):
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                sector = info.get('sector', 'Unknown')
                # Some REITs may be classified under "Real Estate" but have a more specific industry
                if sector == "Real Estate" and 'industry' in info:
                    return info.get('industry', 'Unknown')
                return sector
            except Exception as e:
                print(f"Error getting sector for {ticker} from yfinance: {e}")
                return "Unknown"
        
        # Collect position data with sectors
        position_data = []
        
        for ticker, position in self.portfolio.positions.items():
            # Skip positions with no shares
            metrics = position.calculate_metrics()
            if metrics["shares"] <= 0:
                continue
                
            # Skip positions without dividend growth data
            if position.dividend_growth_3y == 0 and position.dividend_growth_5y == 0:
                continue
            
            # Get the sector - try alreits.com first, then fallback to yfinance
            sector = get_sector_from_alreits(ticker)
            if not sector or sector == "Unknown":
                sector = get_sector_from_yfinance(ticker)
            
            # If we still don't have a sector, mark as Unknown
            if not sector:
                sector = "Unknown"
            
            position_data.append({
                "ticker": ticker,
                "sector": sector,
                "dividend_growth_3y": position.dividend_growth_3y,
                "dividend_growth_5y": position.dividend_growth_5y,
                "annual_income": metrics["annual_income"],
                # Calculate position value for weighting
                "position_value": metrics["position_value"]
            })
        
        # If no valid data, show a message and return
        if not position_data:
            elements.append(Paragraph(
                "No dividend growth data available for sector-based analysis.",
                self.normal_style
            ))
            return
        
        # Convert to DataFrame for easier grouping operations
        df = pd.DataFrame(position_data)
        
        # Group by sector and calculate weighted averages
        grouped_data = []
        for sector, group in df.groupby("sector"):
            total_value = group["position_value"].sum()
            
            # Calculate weighted 3-year and 5-year CAGR
            weighted_dg_3y = 0
            weighted_dg_5y = 0
            
            # Only include positions with valid dividend growth data in calculation
            valid_3y = group[group["dividend_growth_3y"] > 0]
            if not valid_3y.empty:
                total_3y_value = valid_3y["position_value"].sum()
                weighted_dg_3y = sum(row["dividend_growth_3y"] * row["position_value"] / total_3y_value 
                                    for _, row in valid_3y.iterrows())
            
            valid_5y = group[group["dividend_growth_5y"] > 0]
            if not valid_5y.empty:
                total_5y_value = valid_5y["position_value"].sum()
                weighted_dg_5y = sum(row["dividend_growth_5y"] * row["position_value"] / total_5y_value 
                                    for _, row in valid_5y.iterrows())
            
            # Calculate total income for the sector
            total_annual_income = group["annual_income"].sum()
            
            # Count REITs in this sector
            reit_count = len(group)
            
            grouped_data.append({
                "sector": sector,
                "reit_count": reit_count,
                "weighted_dg_3y": weighted_dg_3y,
                "weighted_dg_5y": weighted_dg_5y,
                "total_annual_income": total_annual_income,
                "total_value": total_value
            })
        
        # Sort by 5-year growth rate (highest first)
        grouped_data.sort(key=lambda x: x["weighted_dg_5y"], reverse=True)
        
        # Create the table for sector analysis
        headers = ["Sector", "REITs", "3Y CAGR", "5Y CAGR", "Annual Income", "% of Portfolio"]
        
        # Calculate total portfolio value for percentage calculation
        total_portfolio_value = sum(item["total_value"] for item in grouped_data)
        
        # Create table data
        table_data = [headers]
        
        # Add data rows
        for data in grouped_data:
            sector = data["sector"]
            reit_count = data["reit_count"]
            weighted_dg_3y = data["weighted_dg_3y"]
            weighted_dg_5y = data["weighted_dg_5y"]
            total_annual_income = data["total_annual_income"]
            portfolio_percentage = (data["total_value"] / total_portfolio_value * 100) if total_portfolio_value > 0 else 0
            
            row = [
                sector,
                str(reit_count),
                f"{weighted_dg_3y:.2f}%" if weighted_dg_3y > 0 else "N/A",
                f"{weighted_dg_5y:.2f}%" if weighted_dg_5y > 0 else "N/A",
                f"${total_annual_income:.2f}",
                f"{portfolio_percentage:.2f}%"
            ]
            
            table_data.append(row)
        
        # Add a total row
        total_reits = sum(data["reit_count"] for data in grouped_data)
        total_income = sum(data["total_annual_income"] for data in grouped_data)
        
        # Calculate portfolio-wide weighted averages for display in total row
        portfolio_dg_3y = sum(data["weighted_dg_3y"] * data["total_value"] for data in grouped_data 
                             if data["weighted_dg_3y"] > 0) / sum(data["total_value"] for data in grouped_data 
                                                                 if data["weighted_dg_3y"] > 0)
        
        portfolio_dg_5y = sum(data["weighted_dg_5y"] * data["total_value"] for data in grouped_data 
                             if data["weighted_dg_5y"] > 0) / sum(data["total_value"] for data in grouped_data 
                                                                 if data["weighted_dg_5y"] > 0)
        
        total_row = [
            "TOTAL",
            str(total_reits),
            f"{portfolio_dg_3y:.2f}%",
            f"{portfolio_dg_5y:.2f}%",
            f"${total_income:.2f}",
            "100.00%"
        ]
        
        table_data.append(total_row)
        
        # Create the table with appropriate column widths
        available_width = 160*mm
        col_widths = [
            40*mm,      # Sector
            15*mm,      # REITs Count
            25*mm,      # 3Y CAGR
            25*mm,      # 5Y CAGR
            30*mm,      # Annual Income
            25*mm       # % of Portfolio
        ]
        
        sectors_table = Table(table_data, colWidths=col_widths)
        
        # Style the table
        table_style = [
            # Header style
            ('BACKGROUND', (0, 0), (-1, 0), self.brand_primary),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            
            # Grid and alignment
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),      # Align sector names to left
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),    # Align REIT count to center
            ('ALIGN', (2, 1), (5, -1), 'RIGHT'),     # Align numeric columns to right
            
            # Total row style
            ('BACKGROUND', (0, -1), (-1, -1), self.brand_primary),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]
        
        # Add alternating row colors for better readability
        for i in range(1, len(table_data) - 1):  # Skip header and total row
            if i % 2 == 0:
                table_style.append(('BACKGROUND', (0, i), (-1, i), self.brand_light_bg))
        
        # Color code growth rates
        for i in range(1, len(table_data) - 1):  # Skip header and total row
            # 3-year CAGR
            if table_data[i][2] != "N/A":
                try:
                    cagr_3y = float(table_data[i][2].strip("%"))
                    color = self._get_growth_color(cagr_3y)
                    table_style.append(('TEXTCOLOR', (2, i), (2, i), color))
                    if cagr_3y > 8:  # Exceptional growth
                        table_style.append(('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'))
                except:
                    pass
            
            # 5-year CAGR
            if table_data[i][3] != "N/A":
                try:
                    cagr_5y = float(table_data[i][3].strip("%"))
                    color = self._get_growth_color(cagr_5y)
                    table_style.append(('TEXTCOLOR', (3, i), (3, i), color))
                    if cagr_5y > 8:  # Exceptional growth
                        table_style.append(('FONTNAME', (3, i), (3, i), 'Helvetica-Bold'))
                except:
                    pass
        
        sectors_table.setStyle(TableStyle(table_style))
        elements.append(sectors_table)
        
        # Add explanation and insights
        elements.append(Spacer(1, 5*mm))
        
        # Find top and bottom performing sectors
        top_sectors = sorted([data for data in grouped_data if data["weighted_dg_5y"] > 0], 
                            key=lambda x: x["weighted_dg_5y"], reverse=True)
        
        bottom_sectors = sorted([data for data in grouped_data if data["weighted_dg_5y"] > 0], 
                               key=lambda x: x["weighted_dg_5y"])
        
        insights_text = ""
        if top_sectors:
            top_sector = top_sectors[0]["sector"]
            top_growth = top_sectors[0]["weighted_dg_5y"]
            insights_text += (
                f"<b>Top Performing Sector:</b> The {top_sector} sector shows the strongest "
                f"dividend growth at {top_growth:.2f}% over 5 years. "
            )
            
            if len(top_sectors) > 1:
                second_sector = top_sectors[1]["sector"]
                second_growth = top_sectors[1]["weighted_dg_5y"]
                insights_text += (
                    f"This is followed by {second_sector} at {second_growth:.2f}%. "
                )
        
        if bottom_sectors:
            bottom_sector = bottom_sectors[0]["sector"]
            bottom_growth = bottom_sectors[0]["weighted_dg_5y"]
            insights_text += (
                f"<b>Lowest Performing Sector:</b> The {bottom_sector} sector shows the weakest "
                f"dividend growth at {bottom_growth:.2f}% over 5 years. "
            )
        
        if insights_text:
            insights_text += (
                "Consider these sector performance trends when rebalancing your portfolio "
                "or making new investments."
            )
            elements.append(Paragraph(insights_text, self.normal_style))
        
        # Add note about data sourcing
        elements.append(Spacer(1, 5*mm))
        note_text = (
            "<i>Note: Sector classification data is sourced from alreits.com and yfinance. "
            "Weighted averages are calculated based on the position value within each sector.</i>"
        )
        elements.append(Paragraph(note_text, self.caption_style))

    # Métodos auxiliares para análise de crescimento de dividendos
    def _get_growth_color(self, growth_rate):
        """Retorna a cor apropriada com base na taxa de crescimento"""
        if growth_rate > 10:
            return self.brand_success
        elif growth_rate > 5:
            return self.brand_success
        elif growth_rate > 2:
            return self.brand_accent
        elif growth_rate > 0:
            return self.brand_warning
        else:
            return self.brand_danger
    
    def _create_growth_indicator(self, growth_rate):
        """Cria um indicador visual de crescimento"""
        color = self._get_growth_color(growth_rate)
        
        # Obter código hexadecimal da cor de forma segura
        hex_color = color.hexval() if hasattr(color, 'hexval') else color.hex_value
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
        
        if growth_rate > 10:
            indicator = f'<font color="#{hex_color}">★★★★★ Excellent</font>'
        elif growth_rate > 5:
            indicator = f'<font color="#{hex_color}">★★★★☆ Good</font>'
        elif growth_rate > 2:
            indicator = f'<font color="#{hex_color}">★★★☆☆ Moderate</font>'
        elif growth_rate > 0:
            indicator = f'<font color="#{hex_color}">★★☆☆☆ Weak</font>'
        else:
            indicator = f'<font color="#{hex_color}">★☆☆☆☆ Poor</font>'
            
        return indicator
    
    def _calculate_growth_rating(self, growth_3y, growth_5y):
        """Calcula uma classificação de crescimento combinada"""
        # Se ambos os valores estiverem disponíveis, use uma média ponderada
        if growth_3y > 0 and growth_5y > 0:
            # Dar mais peso ao crescimento de 5 anos
            weighted_growth = (growth_3y * 0.4) + (growth_5y * 0.6)
            
            if weighted_growth > 10:
                return "★★★★★ Excellent"
            elif weighted_growth > 5:
                return "★★★★☆ Good"
            elif weighted_growth > 2:
                return "★★★☆☆ Moderate"
            elif weighted_growth > 0:
                return "★★☆☆☆ Weak"
            else:
                return "★☆☆☆☆ Poor"
        
        # Se apenas um valor estiver disponível, use-o
        elif growth_3y > 0:
            if growth_3y > 10:
                return "★★★★☆ Good (3yr)"
            elif growth_3y > 5:
                return "★★★☆☆ Moderate (3yr)"
            elif growth_3y > 0:
                return "★★☆☆☆ Weak (3yr)"
            else:
                return "★☆☆☆☆ Poor (3yr)"
        
        elif growth_5y > 0:
            if growth_5y > 10:
                return "★★★★★ Excellent (5yr)"
            elif growth_5y > 5:
                return "★★★★☆ Good (5yr)"
            elif growth_5y > 0:
                return "★★☆☆☆ Weak (5yr)"
            else:
                return "★☆☆☆☆ Poor (5yr)"
                
        # Se nenhum valor estiver disponível
        else:
            return "N/A"
    
    def _get_cagr_analysis(self, cagr_3y, cagr_5y):
        """Gera uma análise textual dos valores de CAGR"""
        analysis = "<b>Dividend Growth Analysis:</b> "
        
        # Análise baseada em valores reais
        if cagr_5y > 7 and cagr_3y > 7:
            analysis += (
                "Your portfolio shows excellent dividend growth over both 3-year and 5-year periods, "
                "significantly outpacing inflation. This strong growth indicates high-quality holdings "
                "with sustainable dividend policies."
            )
        elif cagr_5y > 5 and cagr_3y > 5:
            analysis += (
                "Your portfolio demonstrates good dividend growth over both measured periods, "
                "comfortably exceeding typical inflation rates. This consistent growth suggests "
                "quality holdings with solid dividend policies."
            )
        elif cagr_5y > 3 and cagr_3y > 3:
            analysis += (
                "Your portfolio shows moderate dividend growth that generally keeps pace with or slightly "
                "exceeds typical inflation. This provides reasonable income growth over time."
            )
        elif cagr_3y > cagr_5y + 2:
            analysis += (
                "Your portfolio shows accelerating dividend growth in recent years, with the 3-year CAGR "
                "significantly higher than the 5-year measure. This positive trend suggests improving "
                "dividend policies among your holdings."
            )
        elif cagr_5y > cagr_3y + 2:
            analysis += (
                "Your portfolio shows decelerating dividend growth, with recent 3-year growth lower than "
                "the 5-year average. This may warrant monitoring to ensure income growth remains adequate."
            )
        elif cagr_3y < 2 and cagr_5y < 2:
            analysis += (
                "Your portfolio exhibits low dividend growth that may not keep pace with inflation over time. "
                "Consider evaluating holdings for opportunities to improve income growth potential."
            )
        else:
            analysis += (
                "Your portfolio shows reasonable dividend growth overall, though individual holdings may vary. "
                "Continue monitoring to ensure income growth meets your long-term objectives."
            )
            
        return analysis
        
    def add_page_number(self, canvas, doc):
        """Adiciona número de página e rodapé aprimorado a cada página"""
        page_num = canvas.getPageNumber()
        
        # Salvar estado do canvas
        canvas.saveState()
        
        # Adicionar um fundo de cabeçalho sutil
        canvas.setFillColor(self.brand_light_bg)
        canvas.rect(0, doc.height + doc.topMargin - 15*mm, 
                   doc.width + doc.leftMargin + doc.rightMargin, 15*mm, 
                   fill=1, stroke=0)
        
        # Adicionar uma linha dupla na parte inferior da página
        # Linha fina em cima
        canvas.setStrokeColor(self.brand_accent)
        canvas.setLineWidth(0.5)
        canvas.line(doc.leftMargin, 0.8 * inch, doc.width + doc.leftMargin, 0.8 * inch)
        
        # Linha mais grossa embaixo
        canvas.setStrokeColor(self.brand_primary)
        canvas.setLineWidth(1.5)
        canvas.line(doc.leftMargin, 0.75 * inch, doc.width + doc.leftMargin, 0.75 * inch)
        
        # Adicionar número de página com estilo aprimorado
        canvas.setFont("Helvetica-Bold", 9)
        canvas.setFillColor(self.brand_primary)
        page_text = f"Page {page_num}"
        canvas.drawRightString(doc.width + doc.leftMargin, 0.5 * inch, page_text)
        
        # Adicionar rodapé com data de geração e nome do aplicativo
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(self.brand_text)
        
        # Data e hora de geração
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        footer_text = f"REIT Portfolio Report - Generated on {current_time}"
        canvas.drawString(doc.leftMargin, 0.5 * inch, footer_text)
        
        # Adicionar nota de confidencialidade
        canvas.setFont("Helvetica-Oblique", 8)
        canvas.setFillColor(colors.HexColor("#7f8c8d"))
        confidential_text = "CONFIDENTIAL - For personal investment planning only"
        
        # Posicionar no centro da página
        text_width = canvas.stringWidth(confidential_text, "Helvetica-Oblique", 8)
        center_position = doc.leftMargin + (doc.width / 2) - (text_width / 2)
        canvas.drawString(center_position, 0.35 * inch, confidential_text)
        
        # Restaurar estado do canvas
        canvas.restoreState()
		
    def generate_cover_page(self, elements):
        """Cria uma página de capa atraente para o relatório com as métricas solicitadas"""
        # Adicionar um espaço para empurrar o conteúdo para baixo
        elements.append(Spacer(1, 50*mm))
        
        # Título principal
        title_style = ParagraphStyle(
            "CoverTitle",
            parent=self.styles["Title"],
            fontSize=28,
            textColor=self.brand_primary,
            alignment=1,  # Centralizado
            fontName="Helvetica-Bold",
            leading=34,
            spaceAfter=10*mm
        )
        elements.append(Paragraph("REIT Portfolio Report", title_style))
        
        # Subtitle
        date_style = ParagraphStyle(
            "CoverDate",
            parent=self.styles["Normal"],
            fontSize=14,
            textColor=self.brand_secondary,
            alignment=1,  # Centralizado
            fontName="Helvetica-Bold",
            leading=16,
            spaceAfter=30*mm
        )
        
        today = datetime.now()
        date_text = f"{today.strftime('%B %d, %Y')}"
        elements.append(Paragraph(date_text, date_style))
        
        # Adicionar um divisor decorativo
        elements.append(Table([['']], colWidths=[100*mm], rowHeights=[1], 
                       style=TableStyle([('LINEABOVE', (0, 0), (0, 0), 2, self.brand_primary),
                                         ('ALIGN', (0, 0), (0, 0), 'CENTER')])))
        elements.append(Spacer(1, 30*mm))
        
        # Informações resumidas
        metrics = self.portfolio.calculate_portfolio_metrics()
        
        # Formatar valores para exibição destacada
        portfolio_value = f"${metrics['total_value']:,.2f}"
        portfolio_income = f"${metrics['total_annual_income']:,.2f}"
        portfolio_yoc = f"{metrics['portfolio_yield_on_cost']:.2f}%"
        
        # Calcular renda mensal após impostos em BRL
        monthly_income_usd = metrics['total_annual_income'] / 12
        usd_brl_rate = 0
        
        try:
            usd_brl_rate = self.app.get_usd_to_brl_rate()
        except:
            # Fallback para taxa padrão se não conseguir obter
            usd_brl_rate = 5.0  # Taxa padrão
        
        monthly_income_brl = monthly_income_usd * usd_brl_rate
        after_tax_monthly_income_brl = monthly_income_brl * 0.7  # 30% imposto
        after_tax_monthly_brl = f"R$ {after_tax_monthly_income_brl:,.2f}"
        
        # Estilos para textos
        summary_style = ParagraphStyle(
            "CoverSummary",
            parent=self.styles["Normal"],
            fontSize=12,
            textColor=self.brand_text,
            alignment=1,  # Centralizado
            leading=14
        )
        
        summary_value_style = ParagraphStyle(
            "CoverSummaryValue",
            parent=self.styles["Normal"],
            fontSize=20,
            textColor=self.brand_primary,
            alignment=1,  # Centralizado
            fontName="Helvetica-Bold",
            leading=24,
            spaceAfter=6*mm
        )
        
        # Criar uma tabela 2x2 para exibir as métricas solicitadas
        metrics_data = [
            [Paragraph("Total Portfolio Value", summary_style),
             Paragraph("Annual Dividend Income", summary_style)],
            [Paragraph(portfolio_value, summary_value_style),
             Paragraph(portfolio_income, summary_value_style)],
            [Paragraph("After-tax Monthly Income (BRL)", summary_style),
             Paragraph("Yield on Cost", summary_style)],
            [Paragraph(after_tax_monthly_brl, summary_value_style),
             Paragraph(portfolio_yoc, summary_value_style)]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[75*mm, 75*mm])
        metrics_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            # Linhas sutis entre as métricas para melhor separação visual
            ('LINEBELOW', (0, 1), (-1, 1), 0.5, self.brand_light_bg),
        ]))
        
        elements.append(metrics_table)
        elements.append(Spacer(1, 30*mm))
        
        # Texto de preparado para
        prepared_style = ParagraphStyle(
            "CoverPrepared",
            parent=self.styles["Normal"],
            fontSize=12,
            textColor=self.brand_text,
            alignment=1,  # Centralizado
            leading=14,
            spaceAfter=6*mm
        )
        
        elements.append(Paragraph("Prepared for:", prepared_style))
        
        # Nome do investidor (simulado)
        investor_style = ParagraphStyle(
            "CoverInvestor",
            parent=self.styles["Normal"],
            fontSize=16,
            textColor=self.brand_text,
            alignment=1,  # Centralizado
            fontName="Helvetica-Bold",
            leading=20,
            spaceAfter=6*mm
        )
        
        elements.append(Paragraph("Personal Investment Portfolio", investor_style))
        
        # Adicionar marca de confidencialidade
        elements.append(Spacer(1, 30*mm))
        confidential_style = ParagraphStyle(
            "Confidential",
            parent=self.styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#7f8c8d"),
            alignment=1,  # Centralizado
            fontName="Helvetica-Oblique",
            leading=12
        )
        
        elements.append(Paragraph("CONFIDENTIAL DOCUMENT", confidential_style))
        elements.append(Paragraph("For personal investment planning purposes only", confidential_style))
		
    def add_nav_analysis(self, elements):
        """Adiciona seção de análise de NAV (Net Asset Value) ao relatório"""
        elements.append(PageBreak())
        elements.append(Paragraph("NAV Analysis", self.heading2_style))
        
        # Verificar se temos dados de NAV para análise
        nav_data = {}
        nav_report_date = ""
        
        # Verificar se a aplicação tem dados de NAV
        if hasattr(self.app, 'nav_data') and self.app.nav_data:
            nav_data = self.app.nav_data
            if hasattr(self.app, 'nav_report_date'):
                nav_report_date = self.app.nav_report_date
        else:
            # Tentar carregar do arquivo diretamente
            try:
                import os
                import json
                portfolio_file = "reit_portfolio.json"
                if os.path.exists(portfolio_file):
                    with open(portfolio_file, 'r') as f:
                        data = json.load(f)
                    if 'nav_data' in data:
                        nav_data = data['nav_data']
                    if 'nav_report_date' in data:
                        nav_report_date = data['nav_report_date']
            except:
                pass
        
        # Se não há dados de NAV, exibir mensagem e retornar
        if not nav_data:
            elements.append(Paragraph(
                "No NAV (Net Asset Value) data is available for this portfolio. "
                "To add NAV data, use the NAV Analysis feature in the main application.",
                self.normal_style
            ))
            return
        
        # Texto introdutório com data do relatório
        intro_text = (
            f"This section analyzes the difference between the current market price of each REIT "
            f"and its Consensus NAV (Net Asset Value) to identify potential value opportunities. "
        )
        
        if nav_report_date:
            intro_text += f"NAV data was last updated on <b>{nav_report_date}</b>."
            
        elements.append(Paragraph(intro_text, self.normal_style))
        elements.append(Spacer(1, 8*mm))
        
        # Adicionar explicação sobre NAV
        elements.append(Paragraph("What is NAV Analysis?", self.heading3_style))
        
        nav_explanation = (
            "NAV (Net Asset Value) represents the intrinsic value of a REIT's assets minus liabilities. "
            "When REITs trade below their NAV (at a discount), they may represent a value opportunity, "
            "as investors are effectively buying the underlying properties at less than their estimated value. "
            "Conversely, REITs trading above their NAV (at a premium) may be overvalued relative to their assets."
        )
        elements.append(Paragraph(nav_explanation, self.normal_style))
        elements.append(Spacer(1, 8*mm))
        
        # Construir a tabela de análise NAV
        elements.append(Paragraph("Premium/Discount to NAV", self.heading3_style))
        
        # Criar cabeçalho da tabela
        headers = ["Ticker", "Market Price ($)", "Consensus NAV ($)", "Premium/Discount", "Status"]
        
        # Dados da tabela
        table_data = [headers]
        
        # Coletar dados com NAV válido
        valid_nav_data = []
        for ticker, position in self.portfolio.positions.items():
            # Pular posições sem ações
            metrics = position.calculate_metrics()
            if metrics['shares'] <= 0:
                continue
                
            # Obter NAV para este ticker
            nav_value = float(nav_data.get(ticker, 0))
            
            # Pular tickers sem NAV
            if nav_value <= 0:
                continue
                
            current_price = position.current_price
            
            # Calcular Premium/Discount
            # Fórmula: ((current_price / nav_value) - 1) * 100
            premium_discount = ((current_price / nav_value) - 1) * 100
            
            # Status baseado no Premium/Discount
            if premium_discount <= -15:
                status = "Deep Discount"
            elif premium_discount <= -5:
                status = "Discount"
            elif premium_discount <= 5:
                status = "Fair Value"
            elif premium_discount <= 15:
                status = "Premium"
            else:
                status = "High Premium"
                
            valid_nav_data.append({
                'ticker': ticker,
                'price': current_price,
                'nav': nav_value,
                'premium_discount': premium_discount,
                'status': status
            })
        
        # Ordenar por Premium/Discount (menor para maior)
        valid_nav_data.sort(key=lambda x: x['premium_discount'])
        
        # Adicionar dados à tabela
        for data in valid_nav_data:
            ticker = data['ticker']
            current_price = data['price']
            nav_value = data['nav']
            premium_discount = data['premium_discount']
            status = data['status']
            
            # Formatar Premium/Discount com sinal
            premium_str = f"{premium_discount:.2f}%"
            if premium_discount > 0:
                premium_str = f"+{premium_str}"
                
            row = [
                ticker,
                f"{current_price:.2f}",
                f"{nav_value:.2f}",
                premium_str,
                status
            ]
            table_data.append(row)
            
        # Se não houver dados válidos
        if len(table_data) == 1:  # Apenas cabeçalho
            elements.append(Paragraph(
                "No valid NAV data found for the positions in this portfolio. "
                "Please update NAV values in the main application.",
                self.normal_style
            ))
            return
            
        # Criar a tabela
        available_width = 160*mm
        col_widths = [
            20*mm,      # Ticker
            30*mm,      # Market Price
            30*mm,      # NAV
            30*mm,      # Premium/Discount
            50*mm,      # Status
        ]
        
        nav_table = Table(table_data, colWidths=col_widths)
        
        # Estilizar a tabela
        table_style = [
            # Estilo do cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), self.brand_primary),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            
            # Grade e alinhamento
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),      # Alinhar tickers à esquerda
            ('ALIGN', (1, 1), (3, -1), 'CENTER'),    # Alinhar valores ao centro
            ('ALIGN', (4, 1), (4, -1), 'CENTER'),    # Alinhar status ao centro
        ]
        
        # Cor de fundo alternada
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                table_style.append(('BACKGROUND', (0, i), (-1, i), self.brand_light_bg))
                
        # Destacar células de acordo com status
        for i in range(1, len(table_data)):
            status = table_data[i][4]
            premium_discount = table_data[i][3]
            
            # Destacar coluna de Premium/Discount com cor
            if "Deep Discount" in status:
                table_style.append(('TEXTCOLOR', (3, i), (3, i), self.brand_success))
                table_style.append(('FONTNAME', (3, i), (3, i), 'Helvetica-Bold'))
                table_style.append(('TEXTCOLOR', (4, i), (4, i), self.brand_success))
                table_style.append(('FONTNAME', (4, i), (4, i), 'Helvetica-Bold'))
            elif "Discount" in status:
                table_style.append(('TEXTCOLOR', (3, i), (3, i), self.brand_success))
                table_style.append(('TEXTCOLOR', (4, i), (4, i), self.brand_success))
            elif "Fair Value" in status:
                table_style.append(('TEXTCOLOR', (3, i), (3, i), self.brand_text))
                table_style.append(('TEXTCOLOR', (4, i), (4, i), self.brand_text))
            elif "Premium" in status:
                table_style.append(('TEXTCOLOR', (3, i), (3, i), self.brand_warning))
                table_style.append(('TEXTCOLOR', (4, i), (4, i), self.brand_warning))
            elif "High Premium" in status:
                table_style.append(('TEXTCOLOR', (3, i), (3, i), self.brand_danger))
                table_style.append(('FONTNAME', (3, i), (3, i), 'Helvetica-Bold'))
                table_style.append(('TEXTCOLOR', (4, i), (4, i), self.brand_danger))
                table_style.append(('FONTNAME', (4, i), (4, i), 'Helvetica-Bold'))
        
        nav_table.setStyle(TableStyle(table_style))
        elements.append(nav_table)
        
        # Adicionar legenda explicativa
        elements.append(Spacer(1, 5*mm))
        
        # Obter códigos hexadecimais de forma segura
        success_hex = self.brand_success.hexval() if hasattr(self.brand_success, 'hexval') else self.brand_success.hex_value
        warning_hex = self.brand_warning.hexval() if hasattr(self.brand_warning, 'hexval') else self.brand_warning.hex_value
        danger_hex = self.brand_danger.hexval() if hasattr(self.brand_danger, 'hexval') else self.brand_danger.hex_value
        text_hex = self.brand_text.hexval() if hasattr(self.brand_text, 'hexval') else self.brand_text.hex_value
        
        # Remover # se presente
        if success_hex.startswith('#'): success_hex = success_hex[1:]
        if warning_hex.startswith('#'): warning_hex = warning_hex[1:]
        if danger_hex.startswith('#'): danger_hex = danger_hex[1:]
        if text_hex.startswith('#'): text_hex = text_hex[1:]
        
        legend_text = (
            "<i><b>Legend:</b> "
            f'<font color="#{success_hex}">Deep Discount</font> (< -15%), '
            f'<font color="#{success_hex}">Discount</font> (-15% to -5%), '
            f'<font color="#{text_hex}">Fair Value</font> (-5% to +5%), '
            f'<font color="#{warning_hex}">Premium</font> (+5% to +15%), '
            f'<font color="#{danger_hex}">High Premium</font> (> +15%)</i>'
        )
        
        elements.append(Paragraph(legend_text, self.caption_style))
        
        # Adicionar análise de oportunidades
        elements.append(Spacer(1, 10*mm))
        elements.append(Paragraph("NAV Analysis Insights", self.heading3_style))
        
        # Encontrar os maiores descontos e prêmios
        deep_discounts = [item for item in valid_nav_data if item['premium_discount'] <= -15]
        discounts = [item for item in valid_nav_data if -15 < item['premium_discount'] <= -5]
        high_premiums = [item for item in valid_nav_data if item['premium_discount'] > 15]
        
        # Gerar texto de análise
        analysis_text = ""
        
        if deep_discounts:
            tickers = ", ".join([item['ticker'] for item in deep_discounts])
            analysis_text += (
                f"<b>Value Opportunities:</b> {len(deep_discounts)} REITs in your portfolio "
                f"({tickers}) are trading at a deep discount to their NAV "
                f"(below -15%), potentially representing significant value opportunities. "
                f"Consider researching these positions for possible increases to your allocation. "
            )
        
        if discounts:
            if analysis_text:
                analysis_text += "<br/><br/>"
            tickers = ", ".join([item['ticker'] for item in discounts])
            analysis_text += (
                f"<b>Moderate Value:</b> {len(discounts)} REITs ({tickers}) are trading at "
                f"a moderate discount to NAV, suggesting they may be reasonably valued relative to their assets. "
            )
        
        if high_premiums:
            if analysis_text:
                analysis_text += "<br/><br/>"
            tickers = ", ".join([item['ticker'] for item in high_premiums])
            analysis_text += (
                f"<b>Potential Overvaluation:</b> {len(high_premiums)} REITs ({tickers}) "
                f"are trading at a significant premium to NAV (above +15%). "
                f"While premium valuations may be justified by growth prospects or quality assets, "
                f"consider monitoring these positions closely as they may be more vulnerable to corrections. "
            )
        
        if not analysis_text:
            analysis_text = (
                "Most of your REITs are trading close to their consensus NAV values, "
                "suggesting fair valuations overall. Continue monitoring NAV trends "
                "to identify future opportunities when discounts increase."
            )
        
        elements.append(Paragraph(analysis_text, self.normal_style))
        
        # Adicionar nota sobre limitações da análise NAV
        elements.append(Spacer(1, 8*mm))
        note_text = (
            "<i>Note: NAV is one of many valuation tools and has limitations. Consensus NAV may vary between "
            "analysts, and premium/discount trends can change based on market conditions, property types, "
            "and individual REIT quality. Use this analysis alongside other metrics for investment decisions.</i>"
        )
        elements.append(Paragraph(note_text, self.caption_style))
