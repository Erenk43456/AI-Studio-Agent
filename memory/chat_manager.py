import json
import shutil
import threading

from datetime import datetime
from pathlib import Path

from memory.chat import Chat


class ChatManager:

    def __init__(self):

        self.chats = {}

        self.current_chat = None

        self.next_id = 1

        self._lock = threading.RLock()

        self.file = Path("data/chats.json")

        self.file.parent.mkdir(exist_ok=True)

        self.load()

    def create_chat(self, title="New Chat"):

        with self._lock:

            chat = Chat(self.next_id, title)

            self.chats[chat.id] = chat

            self.current_chat = chat

            self.next_id += 1

            self.save()

            return chat

    def get_chat(self, chat_id):

        with self._lock:

            return self.chats.get(chat_id)

    def get_current_chat(self):

        with self._lock:

            return self.current_chat

    def switch_chat(self, chat_id):

        with self._lock:

            chat = self.get_chat(chat_id)

            if chat:

                self.current_chat = chat

                return chat

            return None

    def rename_chat(self, chat_id, title):

        with self._lock:

            chat = self.get_chat(chat_id)

            if chat:

                chat.title = title

                self.save()

                return True

            return False

    def delete_chat(self, chat_id):

        with self._lock:

            chat = self.chats.get(chat_id)

            if not chat:

                return False

            # Diskteki chat klasörünü sil

            if chat.folder.exists():

                shutil.rmtree(chat.folder)

            # Chat listesinden kaldır

            del self.chats[chat_id]

            # Aktif chat silindiyse

            if self.current_chat and self.current_chat.id == chat_id:

                self.current_chat = None

            self.save()

            return True

    def list_chats(self):

        with self._lock:

            return sorted(self.chats.values(), key=lambda chat: chat.id)

    def save(self):

        with self._lock:

            data = []

            for chat in self.chats.values():

                data.append(chat.info())

            with open(self.file, "w", encoding="utf-8") as f:

                json.dump(data, f, ensure_ascii=False, indent=4)

    def load(self):

        with self._lock:

            if not self.file.exists():

                return

            try:

                with open(
                    self.file,
                    "r",
                    encoding="utf-8"
                ) as f:

                    data = json.load(f)

                loaded_chats = {}
                next_id = self.next_id

                for item in data:

                    chat = Chat(
                        item["id"],
                        item["title"]
                    )

                    created_at = item.get("created_at")

                    if created_at:
                        chat.created_at = datetime.strptime(
                            created_at,
                            "%Y-%m-%d %H:%M:%S"
                        )

                    loaded_chats[chat.id] = chat
                    next_id = max(
                        next_id,
                        chat.id + 1
                    )

                self.chats = loaded_chats
                self.next_id = next_id

                if self.chats:

                    self.current_chat = self.list_chats()[0]

            except Exception as error:

                print(
                    f"Failed to load chats: {error}"
                )