import pytest

from memory.conversation import ConversationMemory


@pytest.mark.unit
def test_conversation_save_propagates_persistence_error(
    tmp_path,
    monkeypatch,
):
    conversation = ConversationMemory(
        file_path=tmp_path / "conversation.json"
    )

    def fail_open(*args, **kwargs):
        raise OSError("disk write failed")

    monkeypatch.setattr(
        "builtins.open",
        fail_open,
    )

    with pytest.raises(
        OSError,
        match="disk write failed",
    ):
        conversation.save()