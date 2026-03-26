import json
import os

DEFAULT_CONFIG = {
    "connection": {
        "ws_url": "ws://127.0.0.1:3001",
        "reconnect_interval": 5,
        "access_token": ""
    },
    "ai": {
        "base_url": "https://api.deepseek.com/v1",
        "api_key": "",
        "model": "deepseek-chat",
        "temperature": 0.7,
        "max_tokens": 1024,
        "context_rounds": 10,
        "system_prompt": "你是一个友好的AI助手，请用简洁自然的中文回复。"
    },
    "rules": {
        "private_chat_enabled": True,
        "group_chat_enabled": True,
        "group_trigger_mode": "at",  # at / keyword / all
        "keywords": [],
        "whitelist_users": [],
        "blacklist_users": [],
        "whitelist_groups": [],
        "blacklist_groups": [],
        "cooldown_seconds": 3,
        "use_whitelist_mode": False
    },
    "prompts": {
        "active": "default",
        "presets": {
            "default": "你是一个友好的AI助手，请用简洁自然的中文回复。",
            "catgirl": "你是一只可爱的猫娘，说话带有喵~的语气，性格活泼。",
            "assistant": "你是一个专业的技术助手，回答准确且有条理。"
        }
    },
    "stats": {
        "total_messages": 0,
        "total_tokens": 0,
        "today_messages": 0,
        "today_tokens": 0,
        "today_date": ""
    }
}


class ConfigManager:
    def __init__(self, config_path=None):
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "config.json")
        self.config_path = config_path
        self.config = {}
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
            self._merge_defaults(self.config, DEFAULT_CONFIG)
        else:
            self.config = json.loads(json.dumps(DEFAULT_CONFIG))
            self.save()

    def _merge_defaults(self, config, defaults):
        for key, value in defaults.items():
            if key not in config:
                config[key] = json.loads(json.dumps(value))
            elif isinstance(value, dict) and isinstance(config[key], dict):
                self._merge_defaults(config[key], value)

    def save(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def get(self, *keys, default=None):
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, *args):
        if len(args) < 2:
            return
        keys = args[:-1]
        value = args[-1]
        target = self.config
        for key in keys[:-1]:
            if key not in target or not isinstance(target[key], dict):
                target[key] = {}
            target = target[key]
        target[keys[-1]] = value
        self.save()

    def get_active_prompt(self):
        active = self.get("prompts", "active", default="default")
        return self.get("prompts", "presets", active,
                        default=DEFAULT_CONFIG["ai"]["system_prompt"])
