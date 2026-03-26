from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QHeaderView)
from PyQt6.QtCore import Qt


class ChatLogPage(QWidget):
    def __init__(self, bot_core):
        super().__init__()
        self.bot = bot_core
        self._init_ui()
        self.bot.log_message.connect(self.add_log)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        header = QHBoxLayout()
        title = QLabel("消息日志")
        title.setProperty("class", "title")
        header.addWidget(title)
        header.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索消息...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self._filter_logs)
        header.addWidget(self.search_input)

        clear_btn = QPushButton("清空日志")
        clear_btn.setProperty("class", "danger")
        clear_btn.clicked.connect(self._clear_logs)
        header.addWidget(clear_btn)

        layout.addLayout(header)

        # Count label
        self.count_label = QLabel("共 0 条消息")
        self.count_label.setProperty("class", "subtitle")
        layout.addWidget(self.count_label)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["时间", "类型", "来源", "发送者", "内容"])
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 80)
        self.table.setColumnWidth(1, 60)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 100)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        self._all_logs = []

    def add_log(self, log_data):
        self._all_logs.append(log_data)

        search_text = self.search_input.text().strip().lower()
        if search_text:
            content = log_data.get("content", "").lower()
            sender = log_data.get("sender", "").lower()
            if search_text not in content and search_text not in sender:
                self._update_count()
                return

        self._insert_row(log_data)
        self._update_count()

        # Auto-scroll to bottom
        self.table.scrollToBottom()

    def _insert_row(self, log_data):
        row = self.table.rowCount()
        self.table.insertRow(row)

        items = [
            log_data.get("time", ""),
            log_data.get("type", ""),
            log_data.get("source", ""),
            log_data.get("sender", ""),
            log_data.get("content", ""),
        ]

        for col, text in enumerate(items):
            item = QTableWidgetItem(text)
            # Color code by type
            msg_type = log_data.get("type", "")
            if msg_type == "回复":
                item.setForeground(Qt.GlobalColor.cyan)
            elif msg_type == "错误":
                item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row, col, item)

    def _filter_logs(self, text):
        text = text.strip().lower()
        self.table.setRowCount(0)
        for log in self._all_logs:
            if not text:
                self._insert_row(log)
            else:
                content = log.get("content", "").lower()
                sender = log.get("sender", "").lower()
                source = log.get("source", "").lower()
                if text in content or text in sender or text in source:
                    self._insert_row(log)
        self._update_count()

    def _clear_logs(self):
        self._all_logs.clear()
        self.table.setRowCount(0)
        self._update_count()

    def _update_count(self):
        total = len(self._all_logs)
        shown = self.table.rowCount()
        if shown == total:
            self.count_label.setText(f"共 {total} 条消息")
        else:
            self.count_label.setText(f"共 {total} 条消息，显示 {shown} 条")
