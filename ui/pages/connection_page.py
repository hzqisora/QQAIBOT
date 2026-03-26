from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QFrame, QSpinBox)


class ConnectionPage(QWidget):
    def __init__(self, bot_core):
        super().__init__()
        self.bot = bot_core
        self._init_ui()
        self._load_config()

        self.bot.connection_changed.connect(self._update_status)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("连接设置")
        title.setProperty("class", "title")
        layout.addWidget(title)

        subtitle = QLabel("配置 NapCat / OneBot WebSocket 连接参数")
        subtitle.setProperty("class", "subtitle")
        layout.addWidget(subtitle)

        # WebSocket URL
        card = QFrame()
        card.setProperty("class", "card")
        card_layout = QVBoxLayout(card)

        card_layout.addWidget(QLabel("WebSocket 地址"))
        self.ws_url_input = QLineEdit()
        self.ws_url_input.setPlaceholderText("ws://127.0.0.1:3001")
        card_layout.addWidget(self.ws_url_input)

        card_layout.addWidget(QLabel("Access Token（可选）"))
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("留空表示无需鉴权")
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        card_layout.addWidget(self.token_input)

        row = QHBoxLayout()
        row.addWidget(QLabel("重连间隔（秒）"))
        self.reconnect_spin = QSpinBox()
        self.reconnect_spin.setRange(1, 60)
        self.reconnect_spin.setValue(5)
        row.addWidget(self.reconnect_spin)
        row.addStretch()
        card_layout.addLayout(row)

        layout.addWidget(card)

        # Status card
        status_card = QFrame()
        status_card.setProperty("class", "card")
        status_layout = QHBoxLayout(status_card)

        self.status_label = QLabel("未连接")
        self.status_label.setProperty("class", "status_offline")
        status_layout.addWidget(QLabel("连接状态:"))
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        self.connect_btn = QPushButton("连接")
        self.connect_btn.clicked.connect(self._toggle_connection)
        status_layout.addWidget(self.connect_btn)

        layout.addWidget(status_card)

        # Save button
        btn_row = QHBoxLayout()
        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self._save_config)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

        layout.addStretch()

    def _load_config(self):
        cfg = self.bot.config
        self.ws_url_input.setText(cfg.get("connection", "ws_url", default="ws://127.0.0.1:3001"))
        self.token_input.setText(cfg.get("connection", "access_token", default=""))
        self.reconnect_spin.setValue(cfg.get("connection", "reconnect_interval", default=5))

    def _save_config(self):
        cfg = self.bot.config
        cfg.set("connection", "ws_url", self.ws_url_input.text().strip())
        cfg.set("connection", "access_token", self.token_input.text().strip())
        cfg.set("connection", "reconnect_interval", self.reconnect_spin.value())

    def _toggle_connection(self):
        if self.bot.is_running:
            self.bot.stop()
        else:
            self._save_config()
            self.bot.start()

    def _update_status(self, connected):
        if connected:
            self.status_label.setText("已连接")
            self.status_label.setProperty("class", "status_online")
            self.connect_btn.setText("断开")
            self.connect_btn.setProperty("class", "danger")
        else:
            self.status_label.setText("未连接")
            self.status_label.setProperty("class", "status_offline")
            self.connect_btn.setText("连接")
            self.connect_btn.setProperty("class", "")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.connect_btn.style().unpolish(self.connect_btn)
        self.connect_btn.style().polish(self.connect_btn)
