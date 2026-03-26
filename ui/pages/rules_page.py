from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QFrame, QCheckBox,
                             QComboBox, QSpinBox, QListWidget, QListWidgetItem,
                             QMessageBox)


class RulesPage(QWidget):
    def __init__(self, bot_core):
        super().__init__()
        self.bot = bot_core
        self._init_ui()
        self._load_config()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("回复规则")
        title.setProperty("class", "title")
        layout.addWidget(title)

        # Basic toggles
        toggle_card = QFrame()
        toggle_card.setProperty("class", "card")
        toggle_layout = QVBoxLayout(toggle_card)
        toggle_layout.addWidget(QLabel("基本开关"))

        self.private_check = QCheckBox("启用私聊自动回复")
        self.group_check = QCheckBox("启用群聊自动回复")
        toggle_layout.addWidget(self.private_check)
        toggle_layout.addWidget(self.group_check)

        row = QHBoxLayout()
        row.addWidget(QLabel("群聊触发方式"))
        self.trigger_combo = QComboBox()
        self.trigger_combo.addItems(["@机器人触发", "关键词触发", "所有消息"])
        row.addWidget(self.trigger_combo, 1)
        toggle_layout.addLayout(row)

        cd_row = QHBoxLayout()
        cd_row.addWidget(QLabel("冷却时间（秒）"))
        self.cooldown_spin = QSpinBox()
        self.cooldown_spin.setRange(0, 300)
        self.cooldown_spin.setValue(3)
        cd_row.addWidget(self.cooldown_spin)
        cd_row.addStretch()
        toggle_layout.addLayout(cd_row)

        layout.addWidget(toggle_card)

        # Keywords
        kw_card = QFrame()
        kw_card.setProperty("class", "card")
        kw_layout = QVBoxLayout(kw_card)
        kw_layout.addWidget(QLabel("触发关键词（关键词模式下使用）"))

        kw_row = QHBoxLayout()
        self.kw_input = QLineEdit()
        self.kw_input.setPlaceholderText("输入关键词后回车添加")
        self.kw_input.returnPressed.connect(self._add_keyword)
        kw_add_btn = QPushButton("添加")
        kw_add_btn.setFixedWidth(80)
        kw_add_btn.clicked.connect(self._add_keyword)
        kw_row.addWidget(self.kw_input, 1)
        kw_row.addWidget(kw_add_btn)
        kw_layout.addLayout(kw_row)

        self.kw_list = QListWidget()
        self.kw_list.setMaximumHeight(120)
        kw_layout.addWidget(self.kw_list)

        kw_del_btn = QPushButton("删除选中")
        kw_del_btn.setProperty("class", "danger")
        kw_del_btn.setFixedWidth(100)
        kw_del_btn.clicked.connect(self._del_keyword)
        kw_layout.addWidget(kw_del_btn)

        layout.addWidget(kw_card)

        # Whitelist / Blacklist
        list_card = QFrame()
        list_card.setProperty("class", "card")
        list_layout = QVBoxLayout(list_card)

        self.whitelist_mode_check = QCheckBox("使用白名单模式（仅允许列表中的用户/群）")
        list_layout.addWidget(self.whitelist_mode_check)

        # Users
        list_layout.addWidget(QLabel("用户黑名单/白名单（QQ号，每行一个）"))
        user_row = QHBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("输入 QQ 号")
        self.user_input.returnPressed.connect(self._add_user)
        user_add_btn = QPushButton("添加")
        user_add_btn.setFixedWidth(80)
        user_add_btn.clicked.connect(self._add_user)
        user_row.addWidget(self.user_input, 1)
        user_row.addWidget(user_add_btn)
        list_layout.addLayout(user_row)

        self.user_list = QListWidget()
        self.user_list.setMaximumHeight(100)
        list_layout.addWidget(self.user_list)

        # Groups
        list_layout.addWidget(QLabel("群号黑名单/白名单"))
        group_row = QHBoxLayout()
        self.group_input = QLineEdit()
        self.group_input.setPlaceholderText("输入群号")
        self.group_input.returnPressed.connect(self._add_group)
        group_add_btn = QPushButton("添加")
        group_add_btn.setFixedWidth(80)
        group_add_btn.clicked.connect(self._add_group)
        group_row.addWidget(self.group_input, 1)
        group_row.addWidget(group_add_btn)
        list_layout.addLayout(group_row)

        self.group_list = QListWidget()
        self.group_list.setMaximumHeight(100)
        list_layout.addWidget(self.group_list)

        del_row = QHBoxLayout()
        user_del = QPushButton("删除选中用户")
        user_del.setProperty("class", "danger")
        user_del.clicked.connect(lambda: self._del_selected(self.user_list))
        group_del = QPushButton("删除选中群")
        group_del.setProperty("class", "danger")
        group_del.clicked.connect(lambda: self._del_selected(self.group_list))
        del_row.addWidget(user_del)
        del_row.addWidget(group_del)
        del_row.addStretch()
        list_layout.addLayout(del_row)

        layout.addWidget(list_card)

        # Save
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save_btn = QPushButton("保存规则")
        save_btn.clicked.connect(self._save_config)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _load_config(self):
        cfg = self.bot.config
        rules = cfg.config.get("rules", {})

        self.private_check.setChecked(rules.get("private_chat_enabled", True))
        self.group_check.setChecked(rules.get("group_chat_enabled", True))

        trigger_map = {"at": 0, "keyword": 1, "all": 2}
        self.trigger_combo.setCurrentIndex(trigger_map.get(rules.get("group_trigger_mode", "at"), 0))

        self.cooldown_spin.setValue(rules.get("cooldown_seconds", 3))
        self.whitelist_mode_check.setChecked(rules.get("use_whitelist_mode", False))

        for kw in rules.get("keywords", []):
            self.kw_list.addItem(str(kw))

        wl_users = rules.get("whitelist_users", [])
        bl_users = rules.get("blacklist_users", [])
        for u in (wl_users if rules.get("use_whitelist_mode") else bl_users):
            self.user_list.addItem(str(u))

        wl_groups = rules.get("whitelist_groups", [])
        bl_groups = rules.get("blacklist_groups", [])
        for g in (wl_groups if rules.get("use_whitelist_mode") else bl_groups):
            self.group_list.addItem(str(g))

    def _save_config(self):
        cfg = self.bot.config
        trigger_map = {0: "at", 1: "keyword", 2: "all"}
        is_whitelist = self.whitelist_mode_check.isChecked()

        users = [self.user_list.item(i).text() for i in range(self.user_list.count())]
        groups = [self.group_list.item(i).text() for i in range(self.group_list.count())]
        keywords = [self.kw_list.item(i).text() for i in range(self.kw_list.count())]

        cfg.set("rules", "private_chat_enabled", self.private_check.isChecked())
        cfg.set("rules", "group_chat_enabled", self.group_check.isChecked())
        cfg.set("rules", "group_trigger_mode", trigger_map.get(self.trigger_combo.currentIndex(), "at"))
        cfg.set("rules", "cooldown_seconds", self.cooldown_spin.value())
        cfg.set("rules", "use_whitelist_mode", is_whitelist)
        cfg.set("rules", "keywords", keywords)

        if is_whitelist:
            cfg.set("rules", "whitelist_users", users)
            cfg.set("rules", "whitelist_groups", groups)
        else:
            cfg.set("rules", "blacklist_users", users)
            cfg.set("rules", "blacklist_groups", groups)

        QMessageBox.information(self, "提示", "回复规则已保存")

    def _add_keyword(self):
        text = self.kw_input.text().strip()
        if text:
            self.kw_list.addItem(text)
            self.kw_input.clear()

    def _del_keyword(self):
        for item in self.kw_list.selectedItems():
            self.kw_list.takeItem(self.kw_list.row(item))

    def _add_user(self):
        text = self.user_input.text().strip()
        if text and text.isdigit():
            self.user_list.addItem(text)
            self.user_input.clear()

    def _add_group(self):
        text = self.group_input.text().strip()
        if text and text.isdigit():
            self.group_list.addItem(text)
            self.group_input.clear()

    def _del_selected(self, list_widget):
        for item in list_widget.selectedItems():
            list_widget.takeItem(list_widget.row(item))
