import json
import time
import threading
import websocket
from PyQt6.QtCore import QObject, pyqtSignal


class OneBotClient(QObject):
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    message_received = pyqtSignal(dict)  # raw event dict
    error_occurred = pyqtSignal(str)

    def __init__(self, config_manager):
        super().__init__()
        self.config = config_manager
        self.ws = None
        self._running = False
        self._thread = None
        self._echo_counter = 0
        self._reconnect_interval = self.config.get(
            "connection", "reconnect_interval", default=5)

    @property
    def _is_connected_state(self):
        return getattr(self, '_ws_connected_flag', False)

    def connect(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def disconnect(self):
        self._running = False
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass

    def _run(self):
        while self._running:
            try:
                url = self.config.get("connection", "ws_url",
                                      default="ws://127.0.0.1:3001")
                token = self.config.get("connection", "access_token", default="")

                header = {}
                if token:
                    header["Authorization"] = f"Bearer {token}"

                self.ws = websocket.WebSocketApp(
                    url,
                    header=header,
                    on_open=self._on_open,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close
                )
                self.ws.run_forever(ping_interval=30, ping_timeout=10)
            except Exception as e:
                self.error_occurred.emit(f"WebSocket 异常: {e}")

            if self._running:
                time.sleep(self._reconnect_interval)

    def _on_open(self, ws):
        self._ws_connected_flag = True
        self.connected.emit()

    def _on_message(self, ws, message):
        try:
            data = json.loads(message)
            if data.get("post_type") == "message":
                self.message_received.emit(data)
        except json.JSONDecodeError:
            pass

    def _on_error(self, ws, error):
        self.error_occurred.emit(str(error))

    def _on_close(self, ws, close_status_code, close_msg):
        self._ws_connected_flag = False
        self.disconnected.emit()

    def send_private_message(self, user_id, message):
        self._send_api("send_msg", {
            "message_type": "private",
            "user_id": user_id,
            "message": message
        })

    def send_group_message(self, group_id, message, at_user_id=None):
        msg = ""
        if at_user_id:
            msg = f"[CQ:at,qq={at_user_id}] "
        msg += message
        self._send_api("send_msg", {
            "message_type": "group",
            "group_id": group_id,
            "message": msg
        })

    def _send_api(self, action, params):
        if not self._is_connected_state:
            return
        self._echo_counter += 1
        payload = {
            "action": action,
            "params": params,
            "echo": str(self._echo_counter)
        }
        try:
            self.ws.send(json.dumps(payload))
        except Exception as e:
            self.error_occurred.emit(f"发送失败: {e}")

    @staticmethod
    def extract_text(message_data):
        """Extract plain text from OneBot message."""
        raw_message = message_data.get("raw_message", "")
        if raw_message:
            # Remove CQ codes for display, keep text
            import re
            text = re.sub(r'\[CQ:[^\]]+\]', '', raw_message).strip()
            return text

        # Fallback: parse message array
        message = message_data.get("message", [])
        if isinstance(message, str):
            return message
        parts = []
        for seg in message:
            if isinstance(seg, dict) and seg.get("type") == "text":
                parts.append(seg.get("data", {}).get("text", ""))
        return "".join(parts).strip()

    @staticmethod
    def is_at_bot(message_data, self_id):
        """Check if the message mentions the bot."""
        message = message_data.get("message", [])
        if isinstance(message, list):
            for seg in message:
                if (isinstance(seg, dict) and seg.get("type") == "at"
                        and str(seg.get("data", {}).get("qq")) == str(self_id)):
                    return True
        raw = message_data.get("raw_message", "")
        return f"[CQ:at,qq={self_id}]" in raw
