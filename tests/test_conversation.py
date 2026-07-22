from memory.conversation import ConversationMemory



def test_add_conversation(tmp_path):

    memory = ConversationMemory()


    memory.add(
        "Merhaba",
        "Selam"
    )


    data = memory.get()


    assert len(data) > 0


    assert data[-1]["user"] == "Merhaba"


    assert data[-1]["assistant"] == "Selam"