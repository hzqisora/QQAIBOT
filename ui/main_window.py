import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QStackedWidget, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon

from ui.pages.dashboard_page import DashboardPage
from ui.pages.connection_page import ConnectionPage
from ui.pages.ai_config_page import AIConfigPage
from ui.pages.rules_page import RulesPage
from ui.pages.prompt_page import PromptPage
from ui.pages.chat_log_page import ChatLogPage


class MainWindow(QMainWindow):
    def __init__(self, bot_core):
        super().__init__()
        self.bot = bot_core
        self.setWindowTitle("QQ Bot Manager")
        self.setMinimumSize(1000, 650)
        self.resize(1100, 720)

        self._load_style()
        self._init_ui()

        # Stats refresh timer
        self._timer = QTimer()
        self._timer.timeout.connect(self._refresh_stats)
        self._timer.start(5000)

    def _load_style(self):
        import sys
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        style_path = os.path.join(base_path, "ui", "resources", "style.qss")
        if not os.path.exists(style_path):
            # Fallback for directly running the file without Pyinstaller, some relative setups
            style_path = os.path.join(os.path.dirname(__file__), "resources", "style.qss")

        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left navigation
        nav_widget = QWidget()
        nav_widget.setObjectName("nav_widget")
        nav_widget.setFixedWidth(200)
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)

        # App title
        title_label = QLabel("  QQ Bot Manager")
        title_label.setObjectName("nav_title")
        title_label.setFixedHeight(60)
        title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        nav_layout.addWidget(title_label)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #313244; max-height: 1px;")
        nav_layout.addWidget(sep)

        nav_layout.addSpacing(8)

        # Navigation buttons
        self.nav_buttons = []
        nav_items = [
            ("  \u2302  仪表盘", 0),
            ("  \u2316  连接设置", 1),
            ("  \u2699  AI 配置", 2),
            ("  \u2637  回复规则", 3),
            ("  \u263A  人设管理", 4),
            ("  \u2709  消息日志", 5),
        ]

        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setProperty("class", "nav_btn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, i=index: self._switch_page(i))
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        nav_layout.addStretch()

        # Version
        ver_label = QLabel("  v1.0.0")
        ver_label.setProperty("class", "subtitle")
        ver_label.setStyleSheet("padding: 12px;")
        nav_layout.addWidget(ver_label)

        main_layout.addWidget(nav_widget)

        # Right content area
        self.stack = QStackedWidget()

        self.dashboard_page = DashboardPage(self.bot)
        self.connection_page = ConnectionPage(self.bot)
        self.ai_config_page = AIConfigPage(self.bot)
        self.rules_page = RulesPage(self.bot)
        self.prompt_page = PromptPage(self.bot)
        self.chat_log_page = ChatLogPage(self.bot)

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.connection_page)
        self.stack.addWidget(self.ai_config_page)
        self.stack.addWidget(self.rules_page)
        self.stack.addWidget(self.prompt_page)
        self.stack.addWidget(self.chat_log_page)

        main_layout.addWidget(self.stack, 1)

        # Set default page
        self._switch_page(0)

    def _switch_page(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("active", "true" if i == index else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _refresh_stats(self):
        if self.stack.currentIndex() == 0:
            self.dashboard_page.refresh_stats()

    def closeEvent(self, event):
        self.bot.stop()
        event.accept()
