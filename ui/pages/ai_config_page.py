import threading
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QFrame, QDoubleSpinBox,
                             QSpinBox, QComboBox, QMessageBox)
from PyQt6.QtCore import pyqtSignal, QObject


class _TestWorker(QObject):
    finished = pyqtSignal(bool, str)

    def __init__(self, ai_client):
        super().__init__()
        self.ai = ai_client

    def run(self):
        ok, msg = self.ai.test_connection()
        self.finished.emit(ok, msg)


class AIConfigPage(QWidget):
    def __init__(self, bot_core):
        super().__init__()
        self.bot = bot_core
        self._init_ui()
        self._load_config()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("AI 模型配置")
        title.setProperty("class", "title")
        layout.addWidget(title)

        subtitle = QLabel("配置 DeepSeek 或任何 OpenAI 兼容接口")
        subtitle.setProperty("class", "subtitle")
        layout.addWidget(subtitle)

        # Preset selector
        preset_card = QFrame()
        preset_card.setProperty("class", "card")
        preset_layout = QHBoxLayout(preset_card)
        preset_layout.addWidget(QLabel("快速预设"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "DeepSeek (推荐)",
            "通义千问 Qwen",
            "智谱 GLM",
            "自定义"
        ])
        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        preset_layout.addWidget(self.preset_combo, 1)
        layout.addWidget(preset_card)

        # API settings
        card = QFrame()
        card.setProperty("class", "card")
        card_layout = QVBoxLayout(card)

        card_layout.addWidget(QLabel("API 基础地址"))
        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText("https://api.deepseek.com/v1")
        card_layout.addWidget(self.base_url_input)

        card_layout.addWidget(QLabel("API Key"))
        key_row = QHBoxLayout()
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("输入你的 API Key")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.show_key_btn = QPushButton("显示")
        self.show_key_btn.setProperty("class", "secondary")
        self.show_key_btn.setFixedWidth(60)
        self.show_key_btn.clicked.connect(self._toggle_key_visibility)
        key_row.addWidget(self.api_key_input, 1)
        key_row.addWidget(self.show_key_btn)
        card_layout.addLayout(key_row)

        card_layout.addWidget(QLabel("模型名称"))
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("deepseek-chat")
        card_layout.addWidget(self.model_input)

        layout.addWidget(card)

        # Parameters
        param_card = QFrame()
        param_card.setProperty("class", "card")
        param_layout = QVBoxLayout(param_card)
        param_layout.addWidget(QLabel("模型参数"))

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("温度 (Temperature)"))
        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0.0, 2.0)
        self.temp_spin.setSingleStep(0.1)
        self.temp_spin.setValue(0.7)
        row1.addWidget(self.temp_spin)
        param_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("最大 Token"))
        self.max_token_spin = QSpinBox()
        self.max_token_spin.setRange(64, 8192)
        self.max_token_spin.setSingleStep(128)
        self.max_token_spin.setValue(1024)
        row2.addWidget(self.max_token_spin)
        param_layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("上下文轮数"))
        self.context_spin = QSpinBox()
        self.context_spin.setRange(1, 50)
        self.context_spin.setValue(10)
        row3.addWidget(self.context_spin)
        param_layout.addLayout(row3)

        layout.addWidget(param_card)

        # Buttons
        btn_row = QHBoxLayout()
        test_btn = QPushButton("测试连接")
        test_btn.setProperty("class", "secondary")
        test_btn.clicked.connect(self._test_connection)
        btn_row.addWidget(test_btn)

        btn_row.addStretch()

        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self._save_config)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

        layout.addStretch()

    def _on_preset_changed(self, index):
        presets = {
            0: ("https://api.deepseek.com/v1", "deepseek-chat"),
            1: ("https://dashscope.aliyuncs.com/compatible-mode/v1", "qwen-turbo"),
            2: ("https://open.bigmodel.cn/api/paas/v4", "glm-4-flash"),
        }
        if index in presets:
            url, model = presets[index]
            self.base_url_input.setText(url)
            self.model_input.setText(model)

    def _toggle_key_visibility(self):
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_key_btn.setText("隐藏")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_key_btn.setText("显示")

    def _load_config(self):
        cfg = self.bot.config
        self.base_url_input.setText(cfg.get("ai", "base_url", default="https://api.deepseek.com/v1"))
        self.api_key_input.setText(cfg.get("ai", "api_key", default=""))
        self.model_input.setText(cfg.get("ai", "model", default="deepseek-chat"))
        self.temp_spin.setValue(cfg.get("ai", "temperature", default=0.7))
        self.max_token_spin.setValue(cfg.get("ai", "max_tokens", default=1024))
        self.context_spin.setValue(cfg.get("ai", "context_rounds", default=10))

    def _save_config(self):
        cfg = self.bot.config
        cfg.set("ai", "base_url", self.base_url_input.text().strip())
        cfg.set("ai", "api_key", self.api_key_input.text().strip())
        cfg.set("ai", "model", self.model_input.text().strip())
        cfg.set("ai", "temperature", self.temp_spin.value())
        cfg.set("ai", "max_tokens", self.max_token_spin.value())
        cfg.set("ai", "context_rounds", self.context_spin.value())
        self.bot.ai.reload_client()
        QMessageBox.information(self, "提示", "AI 配置已保存")

    def _test_connection(self):
        self._save_config()

        def _run():
            ok, msg = self.bot.ai.test_connection()
            if ok:
                QMessageBox.information(self, "测试成功", msg)
            else:
                QMessageBox.warning(self, "测试失败", msg)

        t = threading.Thread(target=_run, daemon=True)
        t.start()
