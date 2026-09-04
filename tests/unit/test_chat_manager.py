import pytest
import threading
import concurrent.futures

from unittest.mock import patch
from memory.chat import Chat
from memory.chat_manager import ChatManager


@pytest.mark.unit
def test_chat_manager_load_failure_preserves_existing_chats(
    tmp_path,
):
    manager = ChatManager.__new__(ChatManager)

    manager.chats = {
        1: Chat(1, "Existing Chat")
    }
    manager.current_chat = manager.chats[1]
    manager.next_id = 2
    manager._lock = threading.RLock()
    manager.file = tmp_path / "chats.json"

    manager.file.write_text(
        "{ invalid json",
        encoding="utf-8",
    )

    manager.load()

    assert list(manager.chats) == [1]
    assert manager.get_chat(1).title == "Existing Chat"
    assert manager.get_current_chat().id == 1
    assert manager.next_id == 2

@pytest.mark.unit
def test_chat_manager_create_chat_is_thread_safe(tmp_path):

    manager = ChatManager.__new__(ChatManager)

    manager.chats = {}
    manager.current_chat = None
    manager.next_id = 1
    manager.file = tmp_path / "chats.json"
    manager._lock = threading.RLock()

    manager.save = lambda: None

    def create_chat(chat_id, title):

        chat = Chat.__new__(Chat)
        chat.id = chat_id
        chat.title = title

        return chat

    with patch(
        "memory.chat_manager.Chat",
        side_effect=create_chat
    ):

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=10
        ) as executor:

            chats = list(
                executor.map(
                    lambda _: manager.create_chat(),
                    range(50)
                )
            )

    ids = [
        chat.id
        for chat in chats
    ]

    assert len(ids) == 50
    assert len(set(ids)) == 50
    assert sorted(ids) == list(range(1, 51))
    assert manager.next_id == 51