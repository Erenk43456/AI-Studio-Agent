from memory.memory import Memory


def test_memory_save_and_get():

    memory = Memory()

    memory.save(
        "test",
        "value"
    )

    result = memory.get(
        "test"
    )

    assert result == "value"