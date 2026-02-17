import uuid


class ChatManager:
    def __init__(self):
        self.sessions = {}

    def create_chat(self, system_prompt):
        chat_id = str(uuid.uuid4())
        self.sessions[chat_id] = [
            {"role": "system", "content": system_prompt}
        ]
        return chat_id

    def get_messages(self, chat_id):
        return self.sessions.get(chat_id)

    def add_user(self, chat_id, message):
        self.sessions[chat_id].append({
            "role": "user",
            "content": message
        })

    def add_assistant(self, chat_id, message):
        self.sessions[chat_id].append({
            "role": "assistant",
            "content": message
        })
