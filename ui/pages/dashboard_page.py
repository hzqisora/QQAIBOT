from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QGridLayout)
from PyQt6.QtCore import Qt


class DashboardPage(QWidget):
    def __init__(self, bot_core):
        super().__init__()
        self.bot = bot_core
        self._init_ui()

        self.bot.status_changed.connect(self._update_status)
        self.bot.connection_changed.connect(self._update_connection)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        title = QLabel("仪表盘")
        title.setProperty("class", "title")
        layout.addWidget(title)

        # Status card
        status_card = QFrame()
        status_card.setProperty("class", "card")
        status_layout = QHBoxLayout(status_card)

        left = QVBoxLayout()
        self.status_label = QLabel("已停止")
        self.status_label.setProperty("class", "status_offline")
        self.status_label.setStyleSheet("font-size: 18px;")
        left.addWidget(QLabel("运行状态"))
        left.addWidget(self.status_label)

        right = QHBoxLayout()
        self.start_btn = QPushButton("启动机器人")
        self.start_btn.setProperty("class", "success")
        self.start_btn.setFixedWidth(140)
        self.start_btn.clicked.connect(self._toggle_bot)

        self.stop_btn = QPushButton("停止")
        self.stop_btn.setProperty("class", "danger")
        self.stop_btn.setFixedWidth(100)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_bot)

        right.addWidget(self.start_btn)
        right.addWidget(self.stop_btn)

        status_layout.addLayout(left, 1)
        status_layout.addLayout(right)
        layout.addWidget(status_card)

        # Stats cards
        stats_grid = QGridLayout()
        stats_grid.setSpacing(16)

        self.stat_widgets = {}
        stats = [
            ("today_messages", "今日消息", "0"),
            ("today_tokens", "今日 Token", "0"),
            ("total_messages", "总消息数", "0"),
            ("total_tokens", "总 Token", "0"),
        ]

        for i, (key, label, val) in enumerate(stats):
            card = QFrame()
            card.setProperty("class", "card")
            card_layout = QVBoxLayout(card)

            num = QLabel(val)
            num.setProperty("class", "stat_number")
            num.setAlignment(Qt.AlignmentFlag.AlignCenter)

            desc = QLabel(label)
            desc.setProperty("class", "stat_label")
            desc.setAlignment(Qt.AlignmentFlag.AlignCenter)

            card_layout.addWidget(num)
            card_layout.addWidget(desc)

            self.stat_widgets[key] = num
            stats_grid.addWidget(card, 0, i)

        layout.addLayout(stats_grid)

        # Connection info
        conn_card = QFrame()
        conn_card.setProperty("class", "card")
        conn_layout = QVBoxLayout(conn_card)
        conn_layout.addWidget(QLabel("连接信息"))
        self.conn_info = QLabel("未连接")
        self.conn_info.setProperty("class", "subtitle")
        conn_layout.addWidget(self.conn_info)
        layout.addWidget(conn_card)

        layout.addStretch()

    def _toggle_bot(self):
        if not self.bot.is_running:
            self.bot.start()
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)

    def _stop_bot(self):
        self.bot.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def _update_status(self, status):
        status_map = {
            "running": ("运行中", "status_online"),
            "stopped": ("已停止", "status_offline"),
            "connecting": ("连接中...", "status_offline"),
            "error": ("错误", "status_offline"),
        }
        text, cls = status_map.get(status, ("未知", "status_offline"))
        self.status_label.setText(text)
        self.status_label.setProperty("class", cls)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

        if status == "stopped":
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

    def _update_connection(self, connected):
        if connected:
            url = self.bot.config.get("connection", "ws_url", default="")
            self.conn_info.setText(f"已连接到 {url}")
        else:
            self.conn_info.setText("未连接")

    def refresh_stats(self):
        cfg = self.bot.config
        for key, widget in self.stat_widgets.items():
            val = cfg.get("stats", key, default=0)
            widget.setText(str(val))
