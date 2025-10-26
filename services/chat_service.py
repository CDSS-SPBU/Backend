import uuid
import time
from typing import Dict, List


class ChatSession:
    def __init__(self):
        self.messages: List[Dict] = []

    def add_message(self, role: str, content: str):
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })

    def get_messages(self):
        return self.messages.copy()


class ChatSessionManager:
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = ChatSession()
        return session_id

    def get_history(self, session_id: str) -> List[Dict]:
        return self.sessions[session_id].get_messages() if session_id in self.sessions else []

    def add_message(self, session_id: str, role: str, content: str):
        if session_id in self.sessions:
            self.sessions[session_id].add_message(role, content)

    def remove_session(self, session_id: str):
        self.sessions.pop(session_id, None)
