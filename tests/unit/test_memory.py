import json

import pytest

from memory.memory import Memory


@pytest.mark.unit
def test_memory_starts_empty(tmp_path):
    memory = Memory(data_dir=tmp_path)

    assert memory.recall() == {}


@pytest.mark.unit
def test_memory_save_and_get(tmp_path):
    memory = Memory(data_dir=tmp_path)

    memory.save(
        "name",
        "Eren",
    )

    assert memory.get("name") == "Eren"


@pytest.mark.unit
def test_memory_get_full(tmp_path):
    memory = Memory(data_dir=tmp_path)

    memory.save(
        "name",
        "Eren",
        category="user",
    )

    result = memory.get_full("name")

    assert result["value"] == "Eren"
    assert result["category"] == "user"
    assert "created" in result
    assert "updated" in result


@pytest.mark.unit
def test_memory_update(tmp_path):
    memory = Memory(data_dir=tmp_path)

    memory.save(
        "name",
        "Eren",
    )

    memory.update(
        "name",
        "Atlas",
    )

    assert memory.get("name") == "Atlas"


@pytest.mark.unit
def test_memory_delete(tmp_path):
    memory = Memory(data_dir=tmp_path)

    memory.save(
        "name",
        "Eren",
    )

    assert memory.delete("name") is True
    assert memory.get("name") is None


@pytest.mark.unit
def test_memory_clear(tmp_path):
    memory = Memory(data_dir=tmp_path)

    memory.save(
        "name",
        "Eren",
    )

    memory.save(
        "project",
        "AI-Studio",
    )

    memory.clear()

    assert memory.recall() == {}


@pytest.mark.unit
def test_memory_persists_to_disk(tmp_path):
    memory = Memory(data_dir=tmp_path)

    memory.save(
        "name",
        "Eren",
    )

    memory_file = tmp_path / "memory.json"

    assert memory_file.exists()

    with open(
        memory_file,
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    assert data["name"]["value"] == "Eren"


@pytest.mark.unit
def test_memory_loads_existing_data(tmp_path):
    memory = Memory(data_dir=tmp_path)

    memory.save(
        "name",
        "Eren",
    )

    reloaded = Memory(data_dir=tmp_path)

    assert reloaded.get("name") == "Eren"

@pytest.mark.unit
def test_memory_save_propagates_persistence_error(
    tmp_path,
    monkeypatch,
):
    memory = Memory(data_dir=tmp_path)

    def fail_save(data):
        raise OSError("disk write failed")

    monkeypatch.setattr(
        memory.store,
        "save",
        fail_save,
    )

    with pytest.raises(
        OSError,
        match="disk write failed",
    ):
        memory.save(
            "name",
            "Eren",
        )