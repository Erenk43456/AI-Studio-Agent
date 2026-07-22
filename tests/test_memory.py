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






def test_memory_update():


    memory = Memory()



    memory.save(

        "name",

        "eren"

    )



    memory.update(

        "name",

        "python"

    )



    result = memory.get(

        "name"

    )



    assert result == "python"








def test_memory_delete():


    memory = Memory()



    memory.save(

        "delete_test",

        "data"

    )



    result = memory.delete(

        "delete_test"

    )



    assert result is True



    assert memory.get(

        "delete_test"

    ) is None







def test_memory_clear():


    memory = Memory()



    memory.save(

        "test1",

        "value1"

    )


    memory.save(

        "test2",

        "value2"

    )



    memory.clear()



    assert memory.data == {}