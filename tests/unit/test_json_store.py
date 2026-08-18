import json

import pytest

from app.core.storage.json_store import JsonStore


@pytest.mark.unit
def test_load_returns_default_when_file_does_not_exist(
    tmp_path,
):
    store = JsonStore(
        tmp_path / "data.json"
    )

    assert store.load(default={}) == {}


@pytest.mark.unit
def test_save_and_load_round_trip(
    tmp_path,
):
    store = JsonStore(
        tmp_path / "data.json"
    )

    data = {
        "name": "Eren",
        "items": [1, 2, 3],
    }

    store.save(data)

    assert store.load() == data


@pytest.mark.unit
def test_save_creates_parent_directories(
    tmp_path,
):
    store = JsonStore(
        tmp_path / "nested" / "data.json"
    )

    store.save({"ok": True})

    assert store.load() == {
        "ok": True
    }


@pytest.mark.unit
def test_load_raises_controlled_error_for_invalid_json(
    tmp_path,
):
    path = (
        tmp_path / "data.json"
    )

    path.write_text(
        "{invalid json",
        encoding="utf-8",
    )

    store = JsonStore(path)

    with pytest.raises(ValueError):
        store.load()


@pytest.mark.unit
def test_save_is_valid_json(
    tmp_path,
):
    path = (
        tmp_path / "data.json"
    )

    store = JsonStore(path)

    store.save({
        "unicode": "çalışıyor",
    })

    raw = path.read_text(
        encoding="utf-8",
    )

    assert json.loads(raw) == {
        "unicode": "çalışıyor",
    }