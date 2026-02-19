import json
import os
import sys

import psycopg as psy
from dotenv import load_dotenv
from PySide6 import QtCore, QtGui, QtWidgets

APP_TITLE = "GLP Installation Sizer"


def make_line_edit(placeholder=""):
    edit = QtWidgets.QLineEdit()
    edit.setPlaceholderText(placeholder)
    return edit


def make_text_area(placeholder=""):
    area = QtWidgets.QTextEdit()
    area.setPlaceholderText(placeholder)
    return area


def make_double_spin(minimum=0.0, maximum=1000000.0, step=0.1, decimals=2, suffix=""):
    spin = QtWidgets.QDoubleSpinBox()
    spin.setMinimum(minimum)
    spin.setMaximum(maximum)
    spin.setSingleStep(step)
    spin.setDecimals(decimals)
    if suffix:
        spin.setSuffix(suffix)
    return spin


def make_int_spin(minimum=0, maximum=1000000, step=1):
    spin = QtWidgets.QSpinBox()
    spin.setMinimum(minimum)
    spin.setMaximum(maximum)
    spin.setSingleStep(step)
    return spin


def section_title(text):
    label = QtWidgets.QLabel(text.upper())
    label.setObjectName("SectionTitle")
    return label


def make_chip(text, tone="amber"):
    chip = QtWidgets.QLabel(text)
    chip.setObjectName("Chip")
    chip.setProperty("tone", tone)
    chip.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    return chip


def make_metric_card(title, value, subtitle, tone="amber"):
    frame = QtWidgets.QFrame()
    frame.setObjectName("MetricCard")
    frame.setProperty("tone", tone)
    layout = QtWidgets.QVBoxLayout(frame)
    layout.setContentsMargins(14, 12, 14, 12)
    layout.setSpacing(6)

    title_label = QtWidgets.QLabel(title)
    title_label.setObjectName("MetricTitle")
    value_label = QtWidgets.QLabel(value)
    value_label.setObjectName("MetricValue")
    subtitle_label = QtWidgets.QLabel(subtitle)
    subtitle_label.setObjectName("MetricSubtitle")

    layout.addWidget(title_label)
    layout.addWidget(value_label)
    layout.addWidget(subtitle_label)
    layout.addStretch()
    return frame


def make_table(headers, rows=0):
    table = QtWidgets.QTableWidget(rows, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
    table.verticalHeader().setVisible(False)
    table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
    table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setAlternatingRowColors(True)
    return table


def add_shadow(widget):
    shadow = QtWidgets.QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(22)
    shadow.setOffset(0, 10)
    shadow.setColor(QtGui.QColor(0, 0, 0, 60))
    widget.setGraphicsEffect(shadow)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1400, 900)
        self.projects = {}
        self.current_project_id = None
        self.criteria_observacao = ""
        self._syncing_criteria = False
        self._db_error_shown = False
        self._build_ui()
        self._apply_styles()
        self._wire_actions()
        self._load_projects()

    def _build_ui(self):
        pages = [
            ("Novo Projeto", self._build_new_project_page()),
            ("Projeto", self._build_project_page()),
            ("Cargas & Equipamentos", self._build_equipment_page()),
            ("Central GLP", self._build_central_page()),
            ("Rede Primaria", self._build_primary_network_page()),
            ("Rede Secundaria", self._build_secondary_network_page()),
            ("Materiais & Pecas", self._build_materials_page()),
            ("Documentos", self._build_memorial_page()),
        ]

        self.stack = QtWidgets.QStackedWidget()
        for _, page in pages:
            self.stack.addWidget(self._wrap_scroll(page))

        root = QtWidgets.QWidget()
        root_layout = QtWidgets.QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar = self._build_sidebar([name for name, _ in pages])

        main_area = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(main_area)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self._build_topbar())
        main_layout.addWidget(self.stack)

        root_layout.addWidget(sidebar)
        root_layout.addWidget(main_area, 1)
        self.setCentralWidget(root)

    def _build_sidebar(self, labels):
        sidebar = QtWidgets.QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(250)

        layout = QtWidgets.QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(12)

        logo = QtWidgets.QLabel("GLP | Sizer")
        logo.setObjectName("Logo")
        layout.addWidget(logo)

        info = QtWidgets.QLabel("Instalacoes prediais\nProjetos e dimensionamento")
        info.setObjectName("SidebarInfo")
        layout.addWidget(info)

        layout.addSpacing(8)

        self.nav_group = QtWidgets.QButtonGroup(self)
        self.nav_group.setExclusive(True)

        for index, label in enumerate(labels):
            button = QtWidgets.QPushButton(label)
            button.setCheckable(True)
            button.setObjectName("NavButton")
            if index == 0:
                button.setChecked(True)
            button.clicked.connect(lambda checked, i=index: self.stack.setCurrentIndex(i))
            self.nav_group.addButton(button)
            layout.addWidget(button)

        layout.addStretch()

        footer = QtWidgets.QLabel("Banco: PostgreSQL\nUltima sync: --")
        footer.setObjectName("SidebarFooter")
        layout.addWidget(footer)
        return sidebar

    def _build_topbar(self):
        topbar = QtWidgets.QFrame()
        topbar.setObjectName("TopBar")
        layout = QtWidgets.QHBoxLayout(topbar)
        layout.setContentsMargins(24, 14, 24, 14)
        layout.setSpacing(16)

        title_block = QtWidgets.QVBoxLayout()
        title = QtWidgets.QLabel("Projetos GLP")
        title.setObjectName("TopTitle")
        subtitle = QtWidgets.QLabel("Crie, dimensione e documente novas instalacoes")
        subtitle.setObjectName("TopSubtitle")
        title_block.addWidget(title)
        title_block.addWidget(subtitle)

        layout.addLayout(title_block)

        project_block = QtWidgets.QVBoxLayout()
        project_label = QtWidgets.QLabel("Projeto ativo")
        project_label.setObjectName("TopHint")
        self.project_combo = QtWidgets.QComboBox()
        self.project_combo.setObjectName("TopCombo")
        self.project_combo.addItems(["Selecionar projeto", "Novo projeto..."])
        project_block.addWidget(project_label)
        project_block.addWidget(self.project_combo)
        layout.addLayout(project_block)
        layout.addStretch()

        self.status_chip = make_chip("Status: Sem projeto", "steel")
        layout.addWidget(self.status_chip)

        primary = QtWidgets.QPushButton("Executar Calculo")
        primary.setObjectName("PrimaryAction")
        self.new_project_button = QtWidgets.QPushButton("Novo Projeto")
        self.new_project_button.setObjectName("SecondaryAction")
        self.save_button = QtWidgets.QPushButton("Salvar")
        self.save_button.setObjectName("GhostAction")

        layout.addWidget(self.save_button)
        layout.addWidget(self.new_project_button)
        layout.addWidget(primary)
        return topbar

    def _wrap_scroll(self, widget):
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        scroll.setWidget(widget)
        return scroll

    def _build_new_project_page(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        chips = QtWidgets.QHBoxLayout()
        chips.addWidget(make_chip("Passo 1: Dados", "amber"))
        chips.addWidget(make_chip("Passo 2: Normas", "orange"))
        chips.addWidget(make_chip("Passo 3: Criterios", "steel"))
        chips.addWidget(make_chip("Passo 4: Salvar", "green"))
        chips.addStretch()
        layout.addLayout(chips)

        hero = QtWidgets.QFrame()
        hero.setObjectName("Card")
        hero_layout = QtWidgets.QHBoxLayout(hero)
        hero_layout.setContentsMargins(18, 18, 18, 18)
        hero_layout.setSpacing(18)

        hero_text = QtWidgets.QVBoxLayout()
        hero_title = QtWidgets.QLabel("Criar novo projeto GLP")
        hero_title.setObjectName("HeroTitle")
        hero_subtitle = QtWidgets.QLabel(
            "Defina o escopo, normas e criterios antes de iniciar os calculos."
        )
        hero_subtitle.setObjectName("HeroSubtitle")
        hero_text.addWidget(hero_title)
        hero_text.addWidget(hero_subtitle)
        hero_text.addStretch()
        hero_layout.addLayout(hero_text, 2)

        hero_actions = QtWidgets.QVBoxLayout()
        hero_actions.addWidget(QtWidgets.QLabel("Modelo base"))
        self.new_project_template_combo = QtWidgets.QComboBox()
        self.new_project_template_combo.addItems(
            ["Residencial", "Comercial", "Industrial", "Personalizado"]
        )
        hero_actions.addWidget(self.new_project_template_combo)
        hero_actions.addSpacing(8)
        hero_actions.addWidget(QtWidgets.QLabel("Criar a partir de"))
        self.new_project_origin_combo = QtWidgets.QComboBox()
        self.new_project_origin_combo.addItems(
            ["Projeto vazio", "Duplicar projeto existente", "Importar memorial"]
        )
        hero_actions.addWidget(self.new_project_origin_combo)
        hero_actions.addStretch()
        hero_layout.addLayout(hero_actions, 1)

        dados_card = QtWidgets.QFrame()
        dados_card.setObjectName("Card")
        dados_layout = QtWidgets.QVBoxLayout(dados_card)
        dados_layout.setContentsMargins(18, 18, 18, 18)
        dados_layout.setSpacing(12)
        dados_layout.addWidget(section_title("Dados do Projeto (projeto)"))

        form = QtWidgets.QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(12)
        self.new_project_name = make_line_edit("Ex.: Condominio Parque Sul")
        self.new_project_description = make_line_edit("Escopo resumido do projeto")
        self.new_project_client = make_line_edit("Empresa ou pessoa")
        self.new_project_cnpj = make_line_edit("00.000.000/0000-00")
        self.new_project_address = make_line_edit("Rua, numero, cidade / UF")
        self.new_project_responsavel = make_line_edit("Eng. Nome")
        self.new_project_crea = make_line_edit("000000-0")
        self.new_project_date = make_line_edit("MM/AAAA")
        self.new_project_revision = make_line_edit("01")

        form.addRow("Nome do projeto", self.new_project_name)
        form.addRow("Descricao", self.new_project_description)
        form.addRow("Cliente / Proprietario", self.new_project_client)
        form.addRow("CNPJ", self.new_project_cnpj)
        form.addRow("Endereco", self.new_project_address)
        form.addRow("Responsavel tecnico", self.new_project_responsavel)
        form.addRow("CREA", self.new_project_crea)
        form.addRow("Data", self.new_project_date)
        form.addRow("Revisao", self.new_project_revision)
        dados_layout.addLayout(form)

        normas_card = QtWidgets.QFrame()
        normas_card.setObjectName("Card")
        normas_layout = QtWidgets.QVBoxLayout(normas_card)
        normas_layout.setContentsMargins(18, 18, 18, 18)
        normas_layout.setSpacing(12)
        normas_layout.addWidget(section_title("Normas e Escopo"))

        normas_grid = QtWidgets.QGridLayout()
        normas_grid.setHorizontalSpacing(16)
        normas_grid.setVerticalSpacing(8)
        self.new_project_normas = {
            "NBR 15526": QtWidgets.QCheckBox("NBR 15526 (Redes internas)"),
            "NBR 13523": QtWidgets.QCheckBox("NBR 13523 (Central GLP)"),
            "NBR 13932": QtWidgets.QCheckBox("NBR 13932 (Instalacoes)"),
            "NBR 15358": QtWidgets.QCheckBox("NBR 15358 (Tubulacoes)"),
            "NBR 8613": QtWidgets.QCheckBox("NBR 8613 (Reguladores)"),
            "NBR 8148": QtWidgets.QCheckBox("NBR 8148 (Cilindros)"),
        }
        normas_grid.addWidget(self.new_project_normas["NBR 15526"], 0, 0)
        normas_grid.addWidget(self.new_project_normas["NBR 13523"], 0, 1)
        normas_grid.addWidget(self.new_project_normas["NBR 13932"], 1, 0)
        normas_grid.addWidget(self.new_project_normas["NBR 15358"], 1, 1)
        normas_grid.addWidget(self.new_project_normas["NBR 8613"], 2, 0)
        normas_grid.addWidget(self.new_project_normas["NBR 8148"], 2, 1)
        normas_layout.addLayout(normas_grid)

        self.new_project_scope = make_text_area(
            "Descreva o escopo, restricoes e observacoes do projeto."
        )
        self.new_project_scope.setMinimumHeight(120)
        normas_layout.addWidget(self.new_project_scope)

        criterios_card = QtWidgets.QFrame()
        criterios_card.setObjectName("Card")
        criterios_layout = QtWidgets.QVBoxLayout(criterios_card)
        criterios_layout.setContentsMargins(18, 18, 18, 18)
        criterios_layout.setSpacing(12)
        criterios_layout.addWidget(section_title("Criterios Base (criterio_projeto)"))

        criterios = QtWidgets.QGridLayout()
        criterios.setHorizontalSpacing(16)
        criterios.setVerticalSpacing(12)
        self.criteria_pressao_operacao = make_double_spin(suffix=" kPa")
        self.criteria_perda_carga_maxima = make_double_spin(suffix=" kPa")
        self.criteria_perda_carga_minima = make_double_spin(suffix=" kPa")
        self.criteria_densidade_relativa = make_double_spin()
        self.criteria_vel_maxima = make_double_spin(suffix=" m/s")
        self.criteria_vel_minima = make_double_spin(suffix=" m/s")
        self.criteria_vel_max_recomendada = make_double_spin(suffix=" m/s")
        self.criteria_vel_min_recomendada = make_double_spin(suffix=" m/s")
        self.criteria_temperatura_projeto = make_double_spin(suffix=" C")

        criterios.addWidget(QtWidgets.QLabel("Pressao operacao"), 0, 0)
        criterios.addWidget(self.criteria_pressao_operacao, 0, 1)
        criterios.addWidget(QtWidgets.QLabel("Perda carga maxima"), 0, 2)
        criterios.addWidget(self.criteria_perda_carga_maxima, 0, 3)
        criterios.addWidget(QtWidgets.QLabel("Perda carga minima"), 1, 0)
        criterios.addWidget(self.criteria_perda_carga_minima, 1, 1)
        criterios.addWidget(QtWidgets.QLabel("Densidade relativa"), 1, 2)
        criterios.addWidget(self.criteria_densidade_relativa, 1, 3)
        criterios.addWidget(QtWidgets.QLabel("Velocidade maxima"), 2, 0)
        criterios.addWidget(self.criteria_vel_maxima, 2, 1)
        criterios.addWidget(QtWidgets.QLabel("Velocidade minima"), 2, 2)
        criterios.addWidget(self.criteria_vel_minima, 2, 3)
        criterios.addWidget(QtWidgets.QLabel("Velocidade max recomendada"), 3, 0)
        criterios.addWidget(self.criteria_vel_max_recomendada, 3, 1)
        criterios.addWidget(QtWidgets.QLabel("Velocidade min recomendada"), 3, 2)
        criterios.addWidget(self.criteria_vel_min_recomendada, 3, 3)
        criterios.addWidget(QtWidgets.QLabel("Temperatura projeto"), 4, 0)
        criterios.addWidget(self.criteria_temperatura_projeto, 4, 1)
        criterios_layout.addLayout(criterios)

        self._bind_criteria_widget("criteria_", "pressao_operacao", self.criteria_pressao_operacao)
        self._bind_criteria_widget("criteria_", "perda_carga_maxima", self.criteria_perda_carga_maxima)
        self._bind_criteria_widget("criteria_", "perda_carga_minima", self.criteria_perda_carga_minima)
        self._bind_criteria_widget("criteria_", "vel_maxima", self.criteria_vel_maxima)
        self._bind_criteria_widget("criteria_", "vel_minima", self.criteria_vel_minima)
        self._bind_criteria_widget(
            "criteria_", "vel_max_recomendada", self.criteria_vel_max_recomendada
        )
        self._bind_criteria_widget(
            "criteria_", "vel_min_recomendada", self.criteria_vel_min_recomendada
        )
        self._bind_criteria_widget("criteria_", "densidade_relativa", self.criteria_densidade_relativa)
        self._bind_criteria_widget(
            "criteria_", "temperatura_projeto", self.criteria_temperatura_projeto
        )

        actions = QtWidgets.QHBoxLayout()
        actions.addStretch()
        actions.addWidget(QtWidgets.QPushButton("Salvar como template"))
        actions.addWidget(QtWidgets.QPushButton("Importar dados"))
        self.create_project_button = QtWidgets.QPushButton("Criar Projeto")
        self.create_project_button.setObjectName("PrimaryAction")
        actions.addWidget(self.create_project_button)

        layout.addWidget(hero)
        layout.addWidget(dados_card)
        layout.addWidget(normas_card)
        layout.addWidget(criterios_card)
        layout.addLayout(actions)
        layout.addStretch()
        return page

    def _build_project_page(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        chips = QtWidgets.QHBoxLayout()
        chips.addWidget(make_chip("Projeto", "amber"))
        chips.addWidget(make_chip("Central GLP", "orange"))
        chips.addWidget(make_chip("Rede Primaria", "steel"))
        chips.addWidget(make_chip("Rede Secundaria", "green"))
        chips.addStretch()
        layout.addLayout(chips)

        ident_card = QtWidgets.QFrame()
        ident_card.setObjectName("Card")
        ident_layout = QtWidgets.QVBoxLayout(ident_card)
        ident_layout.setContentsMargins(18, 18, 18, 18)
        ident_layout.setSpacing(12)
        ident_layout.addWidget(section_title("Identificacao do Projeto"))

        form = QtWidgets.QFormLayout()
        form.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(12)
        self.project_name = make_line_edit("Nome do projeto")
        self.project_client = make_line_edit("Cliente / proprietario")
        self.project_cnpj = make_line_edit("00.000.000/0000-00")
        self.project_address = make_line_edit("Rua, numero, cidade / UF")
        self.project_responsavel = make_line_edit("Eng. Nome")
        self.project_crea = make_line_edit("000000-0")
        self.project_date = make_line_edit("MM/AAAA")
        self.project_revision = make_line_edit("01")

        form.addRow("Nome do projeto", self.project_name)
        form.addRow("Cliente / Proprietario", self.project_client)
        form.addRow("CNPJ", self.project_cnpj)
        form.addRow("Endereco", self.project_address)
        form.addRow("Responsavel Tecnico", self.project_responsavel)
        form.addRow("CREA", self.project_crea)
        form.addRow("Data", self.project_date)
        form.addRow("Revisao", self.project_revision)
        ident_layout.addLayout(form)

        summary_card = QtWidgets.QFrame()
        summary_card.setObjectName("Card")
        summary_layout = QtWidgets.QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(18, 18, 18, 18)
        summary_layout.setSpacing(12)
        summary_layout.addWidget(section_title("Resumo do Projeto"))
        self.project_summary = make_text_area("Resumo do projeto, escopo e normas aplicadas")
        self.project_summary.setMinimumHeight(160)
        summary_layout.addWidget(self.project_summary)

        criteria_card = QtWidgets.QFrame()
        criteria_card.setObjectName("Card")
        criteria_layout = QtWidgets.QVBoxLayout(criteria_card)
        criteria_layout.setContentsMargins(18, 18, 18, 18)
        criteria_layout.setSpacing(12)
        criteria_layout.addWidget(section_title("Criterios do Projeto (criterio_projeto)"))

        criteria_grid = QtWidgets.QGridLayout()
        criteria_grid.setHorizontalSpacing(16)
        criteria_grid.setVerticalSpacing(12)

        self.project_criteria_pressao_operacao = make_double_spin(suffix=" kPa")
        self.project_criteria_perda_carga_maxima = make_double_spin(suffix=" kPa")
        self.project_criteria_perda_carga_minima = make_double_spin(suffix=" kPa")
        self.project_criteria_densidade_relativa = make_double_spin()
        self.project_criteria_vel_maxima = make_double_spin(suffix=" m/s")
        self.project_criteria_vel_minima = make_double_spin(suffix=" m/s")
        self.project_criteria_vel_max_recomendada = make_double_spin(suffix=" m/s")
        self.project_criteria_vel_min_recomendada = make_double_spin(suffix=" m/s")
        self.project_criteria_temperatura_projeto = make_double_spin(suffix=" C")

        criteria_grid.addWidget(QtWidgets.QLabel("Pressao operacao"), 0, 0)
        criteria_grid.addWidget(self.project_criteria_pressao_operacao, 0, 1)
        criteria_grid.addWidget(QtWidgets.QLabel("Perda carga maxima"), 0, 2)
        criteria_grid.addWidget(self.project_criteria_perda_carga_maxima, 0, 3)
        criteria_grid.addWidget(QtWidgets.QLabel("Perda carga minima"), 1, 0)
        criteria_grid.addWidget(self.project_criteria_perda_carga_minima, 1, 1)
        criteria_grid.addWidget(QtWidgets.QLabel("Densidade relativa"), 1, 2)
        criteria_grid.addWidget(self.project_criteria_densidade_relativa, 1, 3)
        criteria_grid.addWidget(QtWidgets.QLabel("Velocidade maxima"), 2, 0)
        criteria_grid.addWidget(self.project_criteria_vel_maxima, 2, 1)
        criteria_grid.addWidget(QtWidgets.QLabel("Velocidade minima"), 2, 2)
        criteria_grid.addWidget(self.project_criteria_vel_minima, 2, 3)
        criteria_grid.addWidget(QtWidgets.QLabel("Velocidade max recomendada"), 3, 0)
        criteria_grid.addWidget(self.project_criteria_vel_max_recomendada, 3, 1)
        criteria_grid.addWidget(QtWidgets.QLabel("Velocidade min recomendada"), 3, 2)
        criteria_grid.addWidget(self.project_criteria_vel_min_recomendada, 3, 3)
        criteria_grid.addWidget(QtWidgets.QLabel("Temperatura projeto"), 4, 0)
        criteria_grid.addWidget(self.project_criteria_temperatura_projeto, 4, 1)
        criteria_layout.addLayout(criteria_grid)

        self._bind_criteria_widget(
            "project_criteria_", "pressao_operacao", self.project_criteria_pressao_operacao
        )
        self._bind_criteria_widget(
            "project_criteria_", "perda_carga_maxima", self.project_criteria_perda_carga_maxima
        )
        self._bind_criteria_widget(
            "project_criteria_", "perda_carga_minima", self.project_criteria_perda_carga_minima
        )
        self._bind_criteria_widget(
            "project_criteria_", "densidade_relativa", self.project_criteria_densidade_relativa
        )
        self._bind_criteria_widget(
            "project_criteria_", "vel_maxima", self.project_criteria_vel_maxima
        )
        self._bind_criteria_widget(
            "project_criteria_", "vel_minima", self.project_criteria_vel_minima
        )
        self._bind_criteria_widget(
            "project_criteria_", "vel_max_recomendada", self.project_criteria_vel_max_recomendada
        )
        self._bind_criteria_widget(
            "project_criteria_", "vel_min_recomendada", self.project_criteria_vel_min_recomendada
        )
        self._bind_criteria_widget(
            "project_criteria_", "temperatura_projeto", self.project_criteria_temperatura_projeto
        )

        docs_card = QtWidgets.QFrame()
        docs_card.setObjectName("Card")
        docs_layout = QtWidgets.QVBoxLayout(docs_card)
        docs_layout.setContentsMargins(18, 18, 18, 18)
        docs_layout.setSpacing(12)
        docs_layout.addWidget(section_title("Documentos do Projeto"))
        docs_table = make_table(["Tipo", "Versao", "Data", "Observacoes"], rows=3)
        docs_layout.addWidget(docs_table)

        layout.addWidget(ident_card)
        layout.addWidget(summary_card)
        layout.addWidget(criteria_card)
        layout.addWidget(docs_card)
        layout.addStretch()
        return page

    def _build_equipment_page(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        metrics = QtWidgets.QHBoxLayout()
        metrics.setSpacing(14)
        metrics.addWidget(make_metric_card("Potencia Computada", "--", "Total de cargas", "amber"))
        metrics.addWidget(make_metric_card("Fator de Simultaneidade", "--", "Criterio do projeto", "steel"))
        metrics.addWidget(make_metric_card("Potencia Adotada", "--", "Base para vazao", "orange"))
        metrics.addWidget(make_metric_card("Vazao GLP", "--", "Projeto", "green"))
        layout.addLayout(metrics)

        equip_card = QtWidgets.QFrame()
        equip_card.setObjectName("Card")
        equip_layout = QtWidgets.QVBoxLayout(equip_card)
        equip_layout.setContentsMargins(18, 18, 18, 18)
        equip_layout.setSpacing(12)
        equip_layout.addWidget(section_title("Equipamentos (equipamento, equipamento_projeto)"))

        equip_toolbar = QtWidgets.QHBoxLayout()
        equip_toolbar.addWidget(make_line_edit("Buscar equipamento"))
        equip_toolbar.addStretch()
        equip_toolbar.addWidget(QtWidgets.QPushButton("Adicionar"))
        equip_toolbar.addWidget(QtWidgets.QPushButton("Editar"))
        equip_toolbar.addWidget(QtWidgets.QPushButton("Remover"))
        equip_layout.addLayout(equip_toolbar)

        equip_table = make_table(
            ["Categoria", "Equipamento", "Potencia", "Unidade", "Qtd", "Potencia Total"], rows=1
        )
        for col in range(6):
            equip_table.setItem(0, col, QtWidgets.QTableWidgetItem("--"))
        equip_layout.addWidget(equip_table)

        layout.addWidget(equip_card)
        layout.addStretch()
        return page

    def _build_central_page(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        metrics = QtWidgets.QHBoxLayout()
        metrics.setSpacing(14)
        metrics.addWidget(make_metric_card("Recipientes Selecionados", "--", "Tipo e taxa", "amber"))
        metrics.addWidget(make_metric_card("Numero de Recipientes", "--", "Em uso + reserva", "orange"))
        metrics.addWidget(make_metric_card("Capacidade Total", "--", "Armazenamento", "steel"))
        metrics.addWidget(make_metric_card("Autonomia Estimada", "--", "Perfil de consumo", "green"))
        layout.addLayout(metrics)

        central_card = QtWidgets.QFrame()
        central_card.setObjectName("Card")
        central_layout = QtWidgets.QVBoxLayout(central_card)
        central_layout.setContentsMargins(18, 18, 18, 18)
        central_layout.setSpacing(12)
        central_layout.addWidget(section_title("Central GLP (central_glp, cilindro_projeto)"))

        form = QtWidgets.QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(12)
        form.addRow("Localizacao", make_line_edit("Area externa, ventilada"))
        form.addRow("Afastamentos", make_line_edit("{\"aberturas\": 3.0, \"divisa\": 1.5}"))
        form.addRow("Observacoes", make_line_edit("Protecao, sinalizacao"))
        ok_box = QtWidgets.QComboBox()
        ok_box.addItems(["OK", "Rever"])
        form.addRow("Conformidade", ok_box)
        central_layout.addLayout(form)

        cilindro_table = make_table(["Tipo", "Capacidade", "Taxa Vaporizacao", "Qtd"], rows=1)
        for col in range(4):
            cilindro_table.setItem(0, col, QtWidgets.QTableWidgetItem("--"))
        central_layout.addWidget(cilindro_table)

        regulador_card = QtWidgets.QFrame()
        regulador_card.setObjectName("Card")
        regulador_layout = QtWidgets.QVBoxLayout(regulador_card)
        regulador_layout.setContentsMargins(18, 18, 18, 18)
        regulador_layout.setSpacing(12)
        regulador_layout.addWidget(section_title("Reguladores (regulador, regulador_projeto)"))
        regulador_table = make_table(["Estagio", "Modelo", "Localizacao", "Qtd"], rows=1)
        for col in range(4):
            regulador_table.setItem(0, col, QtWidgets.QTableWidgetItem("--"))
        regulador_layout.addWidget(regulador_table)

        layout.addWidget(central_card)
        layout.addWidget(regulador_card)
        layout.addStretch()
        return page

    def _build_primary_network_page(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        criteria_card = QtWidgets.QFrame()
        criteria_card.setObjectName("Card")
        criteria_layout = QtWidgets.QVBoxLayout(criteria_card)
        criteria_layout.setContentsMargins(18, 18, 18, 18)
        criteria_layout.setSpacing(12)
        criteria_layout.addWidget(section_title("Criterios de Dimensionamento (criterio_projeto)"))

        hint = QtWidgets.QLabel("Valores sincronizados com os criterios do projeto.")
        hint.setObjectName("HintText")
        criteria_layout.addWidget(hint)

        form = QtWidgets.QGridLayout()
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(12)
        self.primary_criteria_pressao_operacao = make_double_spin(suffix=" kPa")
        self.primary_criteria_perda_carga_maxima = make_double_spin(suffix=" kPa")
        self.primary_criteria_vel_maxima = make_double_spin(suffix=" m/s")
        self.primary_criteria_densidade_relativa = make_double_spin()

        form.addWidget(QtWidgets.QLabel("Pressao operacao"), 0, 0)
        form.addWidget(self.primary_criteria_pressao_operacao, 0, 1)
        form.addWidget(QtWidgets.QLabel("Perda carga maxima"), 0, 2)
        form.addWidget(self.primary_criteria_perda_carga_maxima, 0, 3)
        form.addWidget(QtWidgets.QLabel("Velocidade maxima"), 1, 0)
        form.addWidget(self.primary_criteria_vel_maxima, 1, 1)
        form.addWidget(QtWidgets.QLabel("Densidade relativa"), 1, 2)
        form.addWidget(self.primary_criteria_densidade_relativa, 1, 3)
        criteria_layout.addLayout(form)

        self._bind_criteria_widget(
            "primary_criteria_", "pressao_operacao", self.primary_criteria_pressao_operacao
        )
        self._bind_criteria_widget(
            "primary_criteria_", "perda_carga_maxima", self.primary_criteria_perda_carga_maxima
        )
        self._bind_criteria_widget(
            "primary_criteria_", "vel_maxima", self.primary_criteria_vel_maxima
        )
        self._bind_criteria_widget(
            "primary_criteria_", "densidade_relativa", self.primary_criteria_densidade_relativa
        )

        trechos_card = QtWidgets.QFrame()
        trechos_card.setObjectName("Card")
        trechos_layout = QtWidgets.QVBoxLayout(trechos_card)
        trechos_layout.setContentsMargins(18, 18, 18, 18)
        trechos_layout.setSpacing(12)
        trechos_layout.addWidget(section_title("Trechos da Rede Primaria (trecho, calculo_trecho)"))
        trechos_table = make_table(
            ["Trecho", "Leq (m)", "Q (m3/h)", "Diam", "Pin (kPa)", "Pout (kPa)", "dP", "Vel (m/s)", "OK"],
            rows=1,
        )
        for col in range(9):
            trechos_table.setItem(0, col, QtWidgets.QTableWidgetItem("--"))
        trechos_layout.addWidget(trechos_table)

        layout.addWidget(criteria_card)
        layout.addWidget(trechos_card)
        layout.addStretch()
        return page

    def _build_secondary_network_page(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        criteria_card = QtWidgets.QFrame()
        criteria_card.setObjectName("Card")
        criteria_layout = QtWidgets.QVBoxLayout(criteria_card)
        criteria_layout.setContentsMargins(18, 18, 18, 18)
        criteria_layout.setSpacing(12)
        criteria_layout.addWidget(section_title("Criterios de Dimensionamento"))

        hint = QtWidgets.QLabel("Valores sincronizados com os criterios do projeto.")
        hint.setObjectName("HintText")
        criteria_layout.addWidget(hint)

        form = QtWidgets.QGridLayout()
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(12)
        self.secondary_criteria_pressao_operacao = make_double_spin(suffix=" kPa")
        self.secondary_criteria_perda_carga_maxima = make_double_spin(suffix=" kPa")
        self.secondary_criteria_vel_maxima = make_double_spin(suffix=" m/s")
        self.secondary_vazao_unidade = make_double_spin(suffix=" m3/h")

        form.addWidget(QtWidgets.QLabel("Pressao operacao"), 0, 0)
        form.addWidget(self.secondary_criteria_pressao_operacao, 0, 1)
        form.addWidget(QtWidgets.QLabel("Perda carga maxima"), 0, 2)
        form.addWidget(self.secondary_criteria_perda_carga_maxima, 0, 3)
        form.addWidget(QtWidgets.QLabel("Velocidade maxima"), 1, 0)
        form.addWidget(self.secondary_criteria_vel_maxima, 1, 1)
        form.addWidget(QtWidgets.QLabel("Vazao por unidade"), 1, 2)
        form.addWidget(self.secondary_vazao_unidade, 1, 3)
        criteria_layout.addLayout(form)

        self._bind_criteria_widget(
            "secondary_criteria_", "pressao_operacao", self.secondary_criteria_pressao_operacao
        )
        self._bind_criteria_widget(
            "secondary_criteria_",
            "perda_carga_maxima",
            self.secondary_criteria_perda_carga_maxima,
        )
        self._bind_criteria_widget(
            "secondary_criteria_", "vel_maxima", self.secondary_criteria_vel_maxima
        )

        trechos_card = QtWidgets.QFrame()
        trechos_card.setObjectName("Card")
        trechos_layout = QtWidgets.QVBoxLayout(trechos_card)
        trechos_layout.setContentsMargins(18, 18, 18, 18)
        trechos_layout.setSpacing(12)
        trechos_layout.addWidget(section_title("Trechos da Rede Secundaria"))
        trechos_table = make_table(
            ["Trecho", "Leq (m)", "Q (m3/h)", "Diam", "Pin (kPa)", "Pout (kPa)", "dP", "Vel (m/s)", "OK"],
            rows=1,
        )
        for col in range(9):
            trechos_table.setItem(0, col, QtWidgets.QTableWidgetItem("--"))
        trechos_layout.addWidget(trechos_table)

        layout.addWidget(criteria_card)
        layout.addWidget(trechos_card)
        layout.addStretch()
        return page

    def _build_materials_page(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        upper = QtWidgets.QHBoxLayout()
        upper.setSpacing(16)

        materiais_card = QtWidgets.QFrame()
        materiais_card.setObjectName("Card")
        materiais_layout = QtWidgets.QVBoxLayout(materiais_card)
        materiais_layout.setContentsMargins(18, 18, 18, 18)
        materiais_layout.setSpacing(12)
        materiais_layout.addWidget(section_title("Materiais (material)"))
        materiais_table = make_table(["Nome", "Rugosidade C", "Descricao"], rows=3)
        materiais_layout.addWidget(materiais_table)

        tubos_card = QtWidgets.QFrame()
        tubos_card.setObjectName("Card")
        tubos_layout = QtWidgets.QVBoxLayout(tubos_card)
        tubos_layout.setContentsMargins(18, 18, 18, 18)
        tubos_layout.setSpacing(12)
        tubos_layout.addWidget(section_title("Tubos (tubo)"))
        tubos_table = make_table(["Material", "Diametro Nominal", "Diametro Interno"], rows=3)
        tubos_layout.addWidget(tubos_table)

        upper.addWidget(materiais_card)
        upper.addWidget(tubos_card)

        pecas_card = QtWidgets.QFrame()
        pecas_card.setObjectName("Card")
        pecas_layout = QtWidgets.QVBoxLayout(pecas_card)
        pecas_layout.setContentsMargins(18, 18, 18, 18)
        pecas_layout.setSpacing(12)
        pecas_layout.addWidget(section_title("Pecas e Conexoes (peca)"))
        pecas_table = make_table(["Categoria", "Diametro", "Nome", "Comprimento Eq."], rows=4)
        pecas_layout.addWidget(pecas_table)

        layout.addLayout(upper)
        layout.addWidget(pecas_card)
        layout.addStretch()
        return page

    def _build_memorial_page(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        memorial_card = QtWidgets.QFrame()
        memorial_card.setObjectName("MemorialCard")
        add_shadow(memorial_card)
        memorial_layout = QtWidgets.QHBoxLayout(memorial_card)
        memorial_layout.setContentsMargins(18, 18, 18, 18)
        memorial_layout.setSpacing(16)

        outline = QtWidgets.QListWidget()
        outline.addItems(
            [
                "Memorial de calculo",
                "Plantas e isometricos",
                "ART e responsabilidade",
                "Relatorio de testes",
                "Anexos e catalogos",
            ]
        )
        outline.setFixedWidth(220)

        preview = QtWidgets.QTextEdit()
        preview.setReadOnly(True)
        preview.setPlainText(
            "DOCUMENTOS DO PROJETO\n"
            "\n"
            "Selecione um documento para visualizar o resumo.\n"
            "Aqui voce podera gerar o memorial de calculo, anexos\n"
            "e relatorios de conformidade.\n"
            "\n"
            "Sugestoes:\n"
            "- Memorial de calculo (padrao ABNT)\n"
            "- Checklist de seguranca\n"
            "- ART e registros\n"
        )

        memorial_layout.addWidget(outline)
        memorial_layout.addWidget(preview, 1)

        actions = QtWidgets.QHBoxLayout()
        actions.addStretch()
        actions.addWidget(QtWidgets.QPushButton("Adicionar Documento"))
        actions.addWidget(QtWidgets.QPushButton("Exportar PDF"))
        generate = QtWidgets.QPushButton("Gerar Memorial")
        generate.setObjectName("PrimaryAction")
        actions.addWidget(generate)

        layout.addWidget(memorial_card)
        layout.addLayout(actions)
        layout.addStretch()
        return page

    def _wire_actions(self):
        self.new_project_button.clicked.connect(self._go_new_project)
        self.project_combo.currentIndexChanged.connect(self._on_project_selected)
        self.create_project_button.clicked.connect(self._create_project)
        self.save_button.clicked.connect(self._save_project)

        self._set_default_criteria()
        for key in ("NBR 15526", "NBR 13523", "NBR 8613"):
            if key in self.new_project_normas:
                self.new_project_normas[key].setChecked(True)

    def _bind_criteria_widget(self, prefix, key, widget):
        def handler(value):
            self._on_criteria_changed(prefix, key, value)

        widget.valueChanged.connect(handler)

    def _on_criteria_changed(self, prefix, key, value):
        if self._syncing_criteria:
            return
        self._syncing_criteria = True
        prefixes = [
            "criteria_",
            "project_criteria_",
            "primary_criteria_",
            "secondary_criteria_",
        ]
        for target_prefix in prefixes:
            if target_prefix == prefix:
                continue
            widget = getattr(self, f"{target_prefix}{key}", None)
            if widget is not None:
                widget.setValue(value)
        self._syncing_criteria = False

    def _apply_criteria_values(self, values, prefix):
        self._syncing_criteria = True
        for key, value in values.items():
            widget = getattr(self, f"{prefix}{key}", None)
            if widget is not None:
                widget.setValue(value)
        self._syncing_criteria = False

    def _set_default_criteria(self):
        defaults = {
            "pressao_operacao": 150.0,
            "perda_carga_maxima": 45.0,
            "perda_carga_minima": 0.0,
            "vel_maxima": 20.0,
            "vel_minima": 0.0,
            "vel_max_recomendada": 15.0,
            "vel_min_recomendada": 5.0,
            "densidade_relativa": 1.8,
            "temperatura_projeto": 15.0,
        }
        self._apply_criteria_values(defaults, "criteria_")
        self._apply_criteria_values(defaults, "project_criteria_")
        self._apply_criteria_values(defaults, "primary_criteria_")
        self._apply_criteria_values(defaults, "secondary_criteria_")

    def _read_criteria_values(self, prefix):
        keys = [
            "pressao_operacao",
            "perda_carga_maxima",
            "perda_carga_minima",
            "vel_maxima",
            "vel_minima",
            "vel_max_recomendada",
            "vel_min_recomendada",
            "densidade_relativa",
            "temperatura_projeto",
        ]
        values = {}
        for key in keys:
            widget = getattr(self, f"{prefix}{key}", None)
            if widget is not None:
                values[key] = widget.value()
        return values

    def _go_new_project(self):
        new_index = 0
        self.stack.setCurrentIndex(new_index)
        target_index = self.project_combo.findData("NEW")
        if target_index >= 0:
            self.project_combo.setCurrentIndex(target_index)

    def _set_status(self, text, tone):
        self.status_chip.setText(text)
        self.status_chip.setProperty("tone", tone)
        self.status_chip.style().unpolish(self.status_chip)
        self.status_chip.style().polish(self.status_chip)
        self.status_chip.update()

    def _get_conn_info(self):
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
        load_dotenv(env_path, override=False)

        pool_url = os.getenv("DB_POOL_URL")
        if pool_url:
            return pool_url

        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "")

        missing = [key for key, value in (("DB_NAME", db_name), ("DB_USER", db_user), ("DB_PASSWORD", db_password)) if not value]
        if missing:
            raise RuntimeError(f"Variaveis ausentes no .env: {', '.join(missing)}")

        parts = [f"dbname={db_name}", f"user={db_user}", f"password={db_password}", f"host={db_host}"]
        if db_port:
            parts.append(f"port={db_port}")
        return " ".join(parts)

    def _db_connect(self):
        return psy.connect(self._get_conn_info())

    def _load_projects(self, select_id=None):
        self.projects = {}
        self.project_combo.blockSignals(True)
        self.project_combo.clear()
        self.project_combo.addItem("Selecionar projeto", None)
        self.project_combo.addItem("Novo projeto...", "NEW")

        try:
            with self._db_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id, nome, descricao, created_at FROM projeto ORDER BY created_at DESC"
                    )
                    rows = cur.fetchall()
        except Exception as exc:
            self.project_combo.blockSignals(False)
            self._set_status("Status: Sem conexao", "steel")
            if not self._db_error_shown:
                self._show_error("Erro ao carregar projetos", str(exc))
                self._db_error_shown = True
            return

        for project_id, nome, descricao, created_at in rows:
            self.projects[project_id] = {
                "id": project_id,
                "nome": nome,
                "descricao": descricao,
                "created_at": created_at,
            }
            self.project_combo.addItem(nome, project_id)

        self.project_combo.blockSignals(False)
        if select_id:
            index = self.project_combo.findData(select_id)
            self.project_combo.setCurrentIndex(index if index >= 0 else 0)
        else:
            self.project_combo.setCurrentIndex(0)

    def _on_project_selected(self):
        data = self.project_combo.currentData()
        if data == "NEW":
            self.current_project_id = None
            self.stack.setCurrentIndex(0)
            self._set_status("Status: Novo projeto", "steel")
            return
        if not data:
            self.current_project_id = None
            self._set_status("Status: Sem projeto", "steel")
            return
        self._load_project_details(data)

    def _parse_project_meta(self, descricao):
        if not descricao:
            return {}
        try:
            data = json.loads(descricao)
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {"descricao": descricao}

    def _load_project_details(self, project_id):
        project = self.projects.get(project_id)
        if not project:
            return
        self.current_project_id = project_id

        meta = self._parse_project_meta(project.get("descricao"))
        self.project_name.setText(project.get("nome") or "")
        self.project_client.setText(meta.get("cliente", ""))
        self.project_cnpj.setText(meta.get("cnpj", ""))
        self.project_address.setText(meta.get("endereco", ""))
        self.project_responsavel.setText(meta.get("responsavel", ""))
        self.project_crea.setText(meta.get("crea", ""))
        self.project_date.setText(meta.get("data", ""))
        self.project_revision.setText(meta.get("revisao", ""))
        resumo = meta.get("escopo") or meta.get("descricao") or ""
        self.project_summary.setPlainText(resumo)

        self._load_project_criteria(project_id)
        self._set_status(f"Status: {project.get('nome')}", "green")
        self.stack.setCurrentIndex(1)

    def _load_project_criteria(self, project_id):
        try:
            with self._db_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT
                            pressao_operacao,
                            perda_carga_maxima,
                            perda_carga_minima,
                            vel_maxima,
                            vel_minima,
                            vel_max_recomendada,
                            vel_min_recomendada,
                            densidade_relativa,
                            temperatura_projeto,
                            observacao
                        FROM criterio_projeto
                        WHERE projeto_id = %s
                        """,
                        (project_id,),
                    )
                    row = cur.fetchone()
        except Exception as exc:
            self._show_error("Erro ao carregar criterios", str(exc))
            return

        if not row:
            self.criteria_observacao = ""
            self._set_default_criteria()
            return

        (
            pressao_operacao,
            perda_carga_maxima,
            perda_carga_minima,
            vel_maxima,
            vel_minima,
            vel_max_recomendada,
            vel_min_recomendada,
            densidade_relativa,
            temperatura_projeto,
            observacao,
        ) = row

        self.criteria_observacao = observacao or ""
        values = {
            "pressao_operacao": float(pressao_operacao),
            "perda_carga_maxima": float(perda_carga_maxima),
            "perda_carga_minima": float(perda_carga_minima),
            "vel_maxima": float(vel_maxima),
            "vel_minima": float(vel_minima),
            "vel_max_recomendada": float(vel_max_recomendada),
            "vel_min_recomendada": float(vel_min_recomendada),
            "densidade_relativa": float(densidade_relativa),
            "temperatura_projeto": float(temperatura_projeto),
        }
        self._apply_criteria_values(values, "criteria_")
        self._apply_criteria_values(values, "project_criteria_")
        self._apply_criteria_values(values, "primary_criteria_")
        self._apply_criteria_values(values, "secondary_criteria_")

    def _create_project(self):
        nome = self.new_project_name.text().strip()
        if not nome:
            self._show_error("Dados incompletos", "Informe o nome do projeto.")
            return

        normas = [key for key, box in self.new_project_normas.items() if box.isChecked()]
        meta = {
            "descricao": self.new_project_description.text().strip(),
            "cliente": self.new_project_client.text().strip(),
            "cnpj": self.new_project_cnpj.text().strip(),
            "endereco": self.new_project_address.text().strip(),
            "responsavel": self.new_project_responsavel.text().strip(),
            "crea": self.new_project_crea.text().strip(),
            "data": self.new_project_date.text().strip(),
            "revisao": self.new_project_revision.text().strip(),
            "escopo": self.new_project_scope.toPlainText().strip(),
            "normas": normas,
            "modelo_base": self.new_project_template_combo.currentText(),
            "origem": self.new_project_origin_combo.currentText(),
        }

        criterios = {
            "pressao_operacao": self.criteria_pressao_operacao.value(),
            "perda_carga_maxima": self.criteria_perda_carga_maxima.value(),
            "perda_carga_minima": self.criteria_perda_carga_minima.value(),
            "vel_maxima": self.criteria_vel_maxima.value(),
            "vel_minima": self.criteria_vel_minima.value(),
            "vel_max_recomendada": self.criteria_vel_max_recomendada.value(),
            "vel_min_recomendada": self.criteria_vel_min_recomendada.value(),
            "densidade_relativa": self.criteria_densidade_relativa.value(),
            "temperatura_projeto": self.criteria_temperatura_projeto.value(),
            "observacao": "",
        }

        descricao_json = json.dumps(meta, ensure_ascii=True)

        try:
            with self._db_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO projeto (nome, descricao) VALUES (%s, %s) RETURNING id",
                        (nome, descricao_json),
                    )
                    project_id = cur.fetchone()[0]
                    cur.execute(
                        """
                        INSERT INTO criterio_projeto (
                            projeto_id,
                            pressao_operacao,
                            perda_carga_maxima,
                            perda_carga_minima,
                            vel_maxima,
                            vel_minima,
                            vel_max_recomendada,
                            vel_min_recomendada,
                            densidade_relativa,
                            temperatura_projeto,
                            observacao
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (projeto_id) DO UPDATE SET
                            pressao_operacao = EXCLUDED.pressao_operacao,
                            perda_carga_maxima = EXCLUDED.perda_carga_maxima,
                            perda_carga_minima = EXCLUDED.perda_carga_minima,
                            vel_maxima = EXCLUDED.vel_maxima,
                            vel_minima = EXCLUDED.vel_minima,
                            vel_max_recomendada = EXCLUDED.vel_max_recomendada,
                            vel_min_recomendada = EXCLUDED.vel_min_recomendada,
                            densidade_relativa = EXCLUDED.densidade_relativa,
                            temperatura_projeto = EXCLUDED.temperatura_projeto,
                            observacao = EXCLUDED.observacao
                        """,
                        (
                            project_id,
                            criterios["pressao_operacao"],
                            criterios["perda_carga_maxima"],
                            criterios["perda_carga_minima"],
                            criterios["vel_maxima"],
                            criterios["vel_minima"],
                            criterios["vel_max_recomendada"],
                            criterios["vel_min_recomendada"],
                            criterios["densidade_relativa"],
                            criterios["temperatura_projeto"],
                            criterios["observacao"],
                        ),
                    )
                conn.commit()
        except Exception as exc:
            self._show_error("Erro ao criar projeto", str(exc))
            return

        self.current_project_id = project_id
        self._load_projects(select_id=project_id)
        self._set_status(f"Status: {nome}", "green")
        self.stack.setCurrentIndex(1)

    def _save_project(self):
        if not self.current_project_id:
            self._show_error("Sem projeto", "Selecione um projeto para salvar.")
            return

        nome = self.project_name.text().strip()
        if not nome:
            self._show_error("Dados incompletos", "O nome do projeto nao pode ficar vazio.")
            return

        project = self.projects.get(self.current_project_id, {})
        meta = self._parse_project_meta(project.get("descricao"))
        meta.update(
            {
                "cliente": self.project_client.text().strip(),
                "cnpj": self.project_cnpj.text().strip(),
                "endereco": self.project_address.text().strip(),
                "responsavel": self.project_responsavel.text().strip(),
                "crea": self.project_crea.text().strip(),
                "data": self.project_date.text().strip(),
                "revisao": self.project_revision.text().strip(),
                "escopo": self.project_summary.toPlainText().strip(),
            }
        )

        descricao_json = json.dumps(meta, ensure_ascii=True)

        criterios = self._read_criteria_values("project_criteria_")
        if not criterios:
            criterios = self._read_criteria_values("criteria_")
        defaults = {
            "pressao_operacao": 150.0,
            "perda_carga_maxima": 45.0,
            "perda_carga_minima": 0.0,
            "vel_maxima": 20.0,
            "vel_minima": 0.0,
            "vel_max_recomendada": 15.0,
            "vel_min_recomendada": 5.0,
            "densidade_relativa": 1.8,
            "temperatura_projeto": 15.0,
        }
        defaults.update(criterios)
        criterios = defaults

        try:
            with self._db_connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE projeto SET nome = %s, descricao = %s WHERE id = %s",
                        (nome, descricao_json, self.current_project_id),
                    )
                    if criterios:
                        cur.execute(
                            """
                            INSERT INTO criterio_projeto (
                                projeto_id,
                                pressao_operacao,
                                perda_carga_maxima,
                                perda_carga_minima,
                                vel_maxima,
                                vel_minima,
                                vel_max_recomendada,
                                vel_min_recomendada,
                                densidade_relativa,
                                temperatura_projeto,
                                observacao
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (projeto_id) DO UPDATE SET
                                pressao_operacao = EXCLUDED.pressao_operacao,
                                perda_carga_maxima = EXCLUDED.perda_carga_maxima,
                                perda_carga_minima = EXCLUDED.perda_carga_minima,
                                vel_maxima = EXCLUDED.vel_maxima,
                                vel_minima = EXCLUDED.vel_minima,
                                vel_max_recomendada = EXCLUDED.vel_max_recomendada,
                                vel_min_recomendada = EXCLUDED.vel_min_recomendada,
                                densidade_relativa = EXCLUDED.densidade_relativa,
                                temperatura_projeto = EXCLUDED.temperatura_projeto,
                                observacao = EXCLUDED.observacao
                            """,
                            (
                                self.current_project_id,
                                criterios["pressao_operacao"],
                                criterios["perda_carga_maxima"],
                                criterios["perda_carga_minima"],
                                criterios["vel_maxima"],
                                criterios["vel_minima"],
                                criterios["vel_max_recomendada"],
                                criterios["vel_min_recomendada"],
                                criterios["densidade_relativa"],
                                criterios["temperatura_projeto"],
                                self.criteria_observacao,
                            ),
                        )
                conn.commit()
        except Exception as exc:
            self._show_error("Erro ao salvar", str(exc))
            return

        self._load_projects(select_id=self.current_project_id)
        self._set_status(f"Status: {nome}", "green")

    def _show_error(self, title, message):
        QtWidgets.QMessageBox.critical(self, title, message)

    def _apply_styles(self):
        font = QtGui.QFont("Bahnschrift", 10)
        self.setFont(font)

        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #101A24;
            }
            QWidget {
                color: #1B252F;
            }
            #Sidebar {
                background-color: #0E1B26;
            }
            #Logo {
                color: #F2A900;
                font-size: 20px;
                font-weight: 700;
                letter-spacing: 1px;
            }
            #SidebarInfo {
                color: #9FB0BE;
                font-size: 11px;
            }
            #SidebarFooter {
                color: #7C8A95;
                font-size: 10px;
            }
            #NavButton {
                color: #C7D3DB;
                background: transparent;
                border: none;
                padding: 10px 12px;
                text-align: left;
                border-radius: 8px;
            }
            #NavButton:hover {
                background-color: #1B2A36;
            }
            #NavButton:checked {
                background-color: #F2A900;
                color: #1B1B1B;
                font-weight: 600;
            }
            #TopBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1A2633, stop:1 #233545);
                border-bottom: 1px solid #2E4355;
            }
            #TopTitle {
                color: #F7F4EC;
                font-size: 18px;
                font-weight: 700;
            }
            #TopSubtitle {
                color: #C7D3DB;
                font-size: 11px;
            }
            #TopHint {
                color: #C7D3DB;
                font-size: 10px;
            }
            #TopCombo {
                background-color: #F7F4EC;
                border: 1px solid #3A4C5D;
                border-radius: 6px;
                padding: 4px 8px;
                min-width: 180px;
            }
            #HeroTitle {
                color: #1B252F;
                font-size: 18px;
                font-weight: 700;
            }
            #HeroSubtitle {
                color: #6A7680;
                font-size: 11px;
            }
            #HintText {
                color: #6A7680;
                font-size: 10px;
            }
            #PrimaryAction {
                background-color: #F2A900;
                color: #1B1B1B;
                border: none;
                padding: 8px 14px;
                border-radius: 8px;
                font-weight: 600;
            }
            #PrimaryAction:hover {
                background-color: #F5B81C;
            }
            #SecondaryAction {
                background-color: #F2681F;
                color: #1B1B1B;
                border: none;
                padding: 8px 14px;
                border-radius: 8px;
                font-weight: 600;
            }
            #SecondaryAction:hover {
                background-color: #F47A35;
            }
            #GhostAction {
                background-color: transparent;
                color: #F7F4EC;
                border: 1px solid #3A4C5D;
                padding: 8px 14px;
                border-radius: 8px;
            }
            #GhostAction:hover {
                border-color: #F2A900;
                color: #F2A900;
            }
            #SectionTitle {
                color: #2E3B46;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1px;
            }
            #Card {
                background-color: #F7F4EC;
                border: 1px solid #DDD4C8;
                border-radius: 12px;
            }
            #MemorialCard {
                background-color: #F7F4EC;
                border: 1px solid #DDD4C8;
                border-radius: 14px;
            }
            #MetricCard {
                background-color: #FFFFFF;
                border: 1px solid #E2D9CD;
                border-radius: 12px;
            }
            #MetricCard[tone="amber"] {
                border-left: 4px solid #F2A900;
            }
            #MetricCard[tone="orange"] {
                border-left: 4px solid #F2681F;
            }
            #MetricCard[tone="steel"] {
                border-left: 4px solid #3D6B7B;
            }
            #MetricCard[tone="green"] {
                border-left: 4px solid #2F7D5B;
            }
            #MetricTitle {
                color: #6A7680;
                font-size: 10px;
                font-weight: 600;
            }
            #MetricValue {
                color: #1B252F;
                font-size: 18px;
                font-weight: 700;
            }
            #MetricSubtitle {
                color: #8B97A1;
                font-size: 10px;
            }
            #Chip {
                border-radius: 10px;
                padding: 4px 10px;
                font-size: 10px;
                font-weight: 600;
            }
            #Chip[tone="amber"] {
                background-color: #F2A900;
                color: #1B1B1B;
            }
            #Chip[tone="orange"] {
                background-color: #F2681F;
                color: #1B1B1B;
            }
            #Chip[tone="steel"] {
                background-color: #3D6B7B;
                color: #F7F4EC;
            }
            #Chip[tone="green"] {
                background-color: #2F7D5B;
                color: #F7F4EC;
            }
            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #D8D2C9;
                border-radius: 8px;
                padding: 6px 8px;
            }
            QTextEdit {
                min-height: 120px;
            }
            QTableWidget {
                background-color: #FFFFFF;
                gridline-color: #E6DED3;
                border: 1px solid #D8D2C9;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #EFE8DD;
                color: #394550;
                border: none;
                padding: 6px;
                font-size: 10px;
                font-weight: 600;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QListWidget {
                background-color: #FFFFFF;
                border: 1px solid #D8D2C9;
                border-radius: 8px;
                padding: 6px;
            }
            QScrollArea {
                background-color: #EAE4D8;
            }
            """
        )


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
