import threading
from openai import OpenAI
from PyQt6.QtCore import QObject, pyqtSignal


class AIClient(QObject):
    reply_ready = pyqtSignal(str, str, object)  # session_id, reply_text, meta
    error_occurred = pyqtSignal(str, str)  # session_id, error_message

    def __init__(self, config_manager):
        super().__init__()
        self.config = config_manager
        self.client = None
        self.contexts = {}  # session_id -> [messages]
        self._init_client()

    def _init_client(self):
        api_key = self.config.get("ai", "api_key", default="")
        base_url = self.config.get("ai", "base_url", default="https://api.deepseek.com/v1")
        if api_key:
            self.client = OpenAI(api_key=api_key, base_url=base_url)

    def reload_client(self):
        self._init_client()

    def get_context(self, session_id):
        if session_id not in self.contexts:
            self.contexts[session_id] = []
        return self.contexts[session_id]

    def clear_context(self, session_id):
        self.contexts.pop(session_id, None)

    def clear_all_contexts(self):
        self.contexts.clear()

    def _trim_context(self, messages):
        max_rounds = self.config.get("ai", "context_rounds", default=10)
        max_messages = max_rounds * 2
        if len(messages) > max_messages:
            return messages[-max_messages:]
        return messages

    def chat(self, session_id, user_message, meta=None):
        thread = threading.Thread(
            target=self._do_chat,
            args=(session_id, user_message, meta),
            daemon=True
        )
        thread.start()

    def _do_chat(self, session_id, user_message, meta):
        if not self.client:
            self.error_occurred.emit(session_id, "AI 未配置：请先设置 API Key")
            return

        try:
            context = self.get_context(session_id)
            context.append({"role": "user", "content": user_message})
            context_trimmed = self._trim_context(context)

            system_prompt = self.config.get_active_prompt()
            messages = [{"role": "system", "content": system_prompt}] + context_trimmed

            model = self.config.get("ai", "model", default="deepseek-chat")
            temperature = self.config.get("ai", "temperature", default=0.7)
            max_tokens = self.config.get("ai", "max_tokens", default=1024)

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            reply = response.choices[0].message.content.strip()
            context.append({"role": "assistant", "content": reply})

            # Update context back (trimmed)
            self.contexts[session_id] = self._trim_context(context)

            # Track token usage
            usage = response.usage
            if usage:
                total = usage.total_tokens
                self.config.set("stats", "total_tokens",
                                self.config.get("stats", "total_tokens", default=0) + total)

            self.reply_ready.emit(session_id, reply, meta)

        except Exception as e:
            self.error_occurred.emit(session_id, str(e))

    def test_connection(self):
        if not self.client:
            return False, "未配置 API Key"
        try:
            response = self.client.chat.completions.create(
                model=self.config.get("ai", "model", default="deepseek-chat"),
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=64
            )
            return True, f"连接成功 - 模型: {response.model}"
        except Exception as e:
            return False, str(e)
