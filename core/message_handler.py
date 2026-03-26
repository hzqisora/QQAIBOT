import time
from PyQt6.QtCore import QObject, pyqtSignal


class MessageHandler(QObject):
    log_message = pyqtSignal(dict)  # {time, type, source, sender, content, reply}

    def __init__(self, config_manager, ai_client, onebot_client):
        super().__init__()
        self.config = config_manager
        self.ai = ai_client
        self.onebot = onebot_client
        self._cooldowns = {}  # session_id -> last_reply_timestamp
        self.self_id = None

        self.onebot.message_received.connect(self._on_message)
        self.ai.reply_ready.connect(self._on_reply_ready)
        self.ai.error_occurred.connect(self._on_ai_error)

    def _on_message(self, data):
        msg_type = data.get("message_type", "")
        user_id = data.get("user_id", 0)
        group_id = data.get("group_id", 0)
        text = self.onebot.extract_text(data)
        sender_name = data.get("sender", {}).get("nickname", str(user_id))

        if not text:
            return

        # Store self_id from event
        if "self_id" in data:
            self.self_id = data["self_id"]

        # Log incoming message
        self.log_message.emit({
            "time": time.strftime("%H:%M:%S"),
            "type": "群聊" if msg_type == "group" else "私聊",
            "source": str(group_id) if msg_type == "group" else str(user_id),
            "sender": sender_name,
            "content": text,
            "reply": ""
        })

        # Check rules
        if not self._should_reply(data, msg_type, user_id, group_id, text):
            return

        # Check cooldown
        session_id = self._get_session_id(msg_type, user_id, group_id)
        cooldown = self.config.get("rules", "cooldown_seconds", default=3)
        now = time.time()
        if session_id in self._cooldowns:
            if now - self._cooldowns[session_id] < cooldown:
                return
        self._cooldowns[session_id] = now

        # Update stats
        from datetime import date
        today = date.today().isoformat()
        if self.config.get("stats", "today_date") != today:
            self.config.set("stats", "today_date", today)
            self.config.set("stats", "today_messages", 0)
            self.config.set("stats", "today_tokens", 0)

        self.config.set("stats", "total_messages",
                        self.config.get("stats", "total_messages", default=0) + 1)
        self.config.set("stats", "today_messages",
                        self.config.get("stats", "today_messages", default=0) + 1)

        # Call AI
        meta = {
            "msg_type": msg_type,
            "user_id": user_id,
            "group_id": group_id,
            "sender_name": sender_name
        }
        print(f"DEBUG: Calling AI chat with: {text}")
        self.ai.chat(session_id, text, meta=meta)

    def _should_reply(self, data, msg_type, user_id, group_id, text):
        rules = self.config.config.get("rules", {})

        # Private chat
        if msg_type == "private":
            if not rules.get("private_chat_enabled", True):
                return False
            if self._is_blocked(user_id, None, rules):
                return False
            return True

        # Group chat
        if msg_type == "group":
            if not rules.get("group_chat_enabled", True):
                return False
            if self._is_blocked(user_id, group_id, rules):
                return False

            trigger = rules.get("group_trigger_mode", "at")

            if trigger == "at":
                return self.onebot.is_at_bot(data, self.self_id) if self.self_id else False
            elif trigger == "keyword":
                keywords = rules.get("keywords", [])
                return any(kw in text for kw in keywords) if keywords else False
            elif trigger == "all":
                return True

        return False

    def _is_blocked(self, user_id, group_id, rules):
        use_whitelist = rules.get("use_whitelist_mode", False)

        if use_whitelist:
            # Whitelist mode: only allow listed
            wl_users = rules.get("whitelist_users", [])
            wl_groups = rules.get("whitelist_groups", [])
            if group_id:
                return group_id not in wl_groups and str(group_id) not in [str(g) for g in wl_groups]
            else:
                return user_id not in wl_users and str(user_id) not in [str(u) for u in wl_users]
        else:
            # Blacklist mode: block listed
            bl_users = rules.get("blacklist_users", [])
            bl_groups = rules.get("blacklist_groups", [])
            if group_id and (group_id in bl_groups or str(group_id) in [str(g) for g in bl_groups]):
                return True
            if user_id in bl_users or str(user_id) in [str(u) for u in bl_users]:
                return True
            return False

    def _get_session_id(self, msg_type, user_id, group_id):
        if msg_type == "group":
            return f"group_{group_id}_{user_id}"
        return f"private_{user_id}"

    def _on_reply_ready(self, session_id, reply, meta):
        if not meta:
            return
        msg_type = meta.get("msg_type")
        user_id = meta.get("user_id")
        group_id = meta.get("group_id")

        if msg_type == "private":
            self.onebot.send_private_message(user_id, reply)
        elif msg_type == "group":
            self.onebot.send_group_message(group_id, reply, at_user_id=user_id)

        self.log_message.emit({
            "time": time.strftime("%H:%M:%S"),
            "type": "回复",
            "source": str(group_id) if msg_type == "group" else str(user_id),
            "sender": "Bot",
            "content": reply,
            "reply": ""
        })

    def _on_ai_error(self, session_id, error):
        self.log_message.emit({
            "time": time.strftime("%H:%M:%S"),
            "type": "错误",
            "source": session_id,
            "sender": "System",
            "content": error,
            "reply": ""
        })
