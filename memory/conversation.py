import json
import os


class ConversationMemory:

    def __init__(self):
        self.file = "conversation.json"

        if os.path.exists(self.file):
            with open(self.file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = []


    def add(self, user, assistant):

        self.data.append({
            "user": user,
            "assistant": assistant
        })

        self.data = self.data[-10:]

        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(
                self.data,
                f,
                ensure_ascii=False,
                indent=4
            )


    def get(self):
        return self.data