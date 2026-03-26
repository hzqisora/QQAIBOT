from PyQt6.QtCore import QObject, pyqtSignal
from core.config_manager import ConfigManager
from core.ai_client import AIClient
from core.onebot_client import OneBotClient
from core.message_handler import MessageHandler


class BotCore(QObject):
    status_changed = pyqtSignal(str)  # "running" / "stopped" / "connecting" / "error"
    connection_changed = pyqtSignal(bool)  # connected or not
    log_message = pyqtSignal(dict)

    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config = config_manager
        self.ai = AIClient(config_manager)
        self.onebot = OneBotClient(config_manager)
        self.handler = MessageHandler(config_manager, self.ai, self.onebot)

        self._running = False

        # Wire signals
        self.onebot.connected.connect(self._on_connected)
        self.onebot.disconnected.connect(self._on_disconnected)
        self.onebot.error_occurred.connect(self._on_error)
        self.handler.log_message.connect(self.log_message.emit)

    @property
    def is_running(self):
        return self._running

    def start(self):
        if self._running:
            return
        self._running = True
        self.ai.reload_client()
        self.status_changed.emit("connecting")
        self.onebot.connect()

    def stop(self):
        if not self._running:
            return
        self._running = False
        self.onebot.disconnect()
        self.status_changed.emit("stopped")
        self.connection_changed.emit(False)

    def _on_connected(self):
        self.status_changed.emit("running")
        self.connection_changed.emit(True)

    def _on_disconnected(self):
        if self._running:
            self.status_changed.emit("connecting")
        self.connection_changed.emit(False)

    def _on_error(self, error_msg):
        self.log_message.emit({
            "time": __import__("time").strftime("%H:%M:%S"),
            "type": "错误",
            "source": "System",
            "sender": "System",
            "content": error_msg,
            "reply": ""
        })
