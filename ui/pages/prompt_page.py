from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QListWidget, QTextEdit,
                             QLineEdit, QMessageBox, QInputDialog)


class PromptPage(QWidget):
    def __init__(self, bot_core):
        super().__init__()
        self.bot = bot_core
        self._init_ui()
        self._load_presets()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Left: preset list
        left = QVBoxLayout()
        left_title = QLabel("人设预设")
        left_title.setProperty("class", "title")
        left.addWidget(left_title)

        self.preset_list = QListWidget()
        self.preset_list.currentRowChanged.connect(self._on_preset_selected)
        left.addWidget(self.preset_list)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("新建")
        add_btn.setProperty("class", "success")
        add_btn.clicked.connect(self._add_preset)
        del_btn = QPushButton("删除")
        del_btn.setProperty("class", "danger")
        del_btn.clicked.connect(self._del_preset)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(del_btn)
        left.addLayout(btn_row)

        self.activate_btn = QPushButton("设为当前使用")
        self.activate_btn.clicked.connect(self._activate_preset)
        left.addWidget(self.activate_btn)

        self.active_label = QLabel("当前使用: -")
        self.active_label.setProperty("class", "subtitle")
        left.addWidget(self.active_label)

        left_widget = QWidget()
        left_widget.setLayout(left)
        left_widget.setFixedWidth(220)
        layout.addWidget(left_widget)

        # Right: editor
        right = QVBoxLayout()
        right_title = QLabel("编辑人设提示词")
        right_title.setProperty("class", "title")
        right.addWidget(right_title)

        hint = QLabel("在下方编辑 System Prompt，AI 会按照此人设来回复消息")
        hint.setProperty("class", "subtitle")
        hint.setWordWrap(True)
        right.addWidget(hint)

        self.editor = QTextEdit()
        self.editor.setPlaceholderText("请输入人设提示词...\n\n例如：你是一个友好的AI助手，请用简洁自然的中文回复。")
        right.addWidget(self.editor)

        save_btn = QPushButton("保存修改")
        save_btn.clicked.connect(self._save_current)
        right.addWidget(save_btn)

        right_widget = QWidget()
        right_widget.setLayout(right)
        layout.addWidget(right_widget, 1)

    def _load_presets(self):
        self.preset_list.clear()
        presets = self.bot.config.get("prompts", "presets", default={})
        active = self.bot.config.get("prompts", "active", default="default")
        self.active_label.setText(f"当前使用: {active}")

        for name in presets:
            self.preset_list.addItem(name)

        # Select active
        for i in range(self.preset_list.count()):
            if self.preset_list.item(i).text() == active:
                self.preset_list.setCurrentRow(i)
                break

    def _on_preset_selected(self, row):
        if row < 0:
            return
        name = self.preset_list.item(row).text()
        content = self.bot.config.get("prompts", "presets", name, default="")
        self.editor.setPlainText(content)

    def _save_current(self):
        row = self.preset_list.currentRow()
        if row < 0:
            return
        name = self.preset_list.item(row).text()
        content = self.editor.toPlainText()
        self.bot.config.set("prompts", "presets", name, content)
        QMessageBox.information(self, "提示", f"预设 '{name}' 已保存")

    def _add_preset(self):
        name, ok = QInputDialog.getText(self, "新建预设", "预设名称:")
        if ok and name.strip():
            name = name.strip()
            self.bot.config.set("prompts", "presets", name, "")
            self._load_presets()
            # Select new
            for i in range(self.preset_list.count()):
                if self.preset_list.item(i).text() == name:
                    self.preset_list.setCurrentRow(i)
                    break

    def _del_preset(self):
        row = self.preset_list.currentRow()
        if row < 0:
            return
        name = self.preset_list.item(row).text()
        if name == "default":
            QMessageBox.warning(self, "提示", "默认预设不能删除")
            return

        presets = self.bot.config.get("prompts", "presets", default={})
        presets.pop(name, None)
        self.bot.config.set("prompts", "presets", presets)

        if self.bot.config.get("prompts", "active") == name:
            self.bot.config.set("prompts", "active", "default")

        self._load_presets()

    def _activate_preset(self):
        row = self.preset_list.currentRow()
        if row < 0:
            return
        name = self.preset_list.item(row).text()
        self.bot.config.set("prompts", "active", name)
        self.active_label.setText(f"当前使用: {name}")
        QMessageBox.information(self, "提示", f"已切换到预设: {name}")
