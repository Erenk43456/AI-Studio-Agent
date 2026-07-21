from memory.memory import Memory


def test_memory_save_and_get(tmp_path):

    memory = Memory()

    memory.save(
        "test",
        "value"
    )

    result = memory.get(
        "test"
    )

    assert result == "value"