import pytest

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