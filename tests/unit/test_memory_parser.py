import pytest

from agents.planner.memory_parser import parse_memory


@pytest.mark.unit
def test_memory_get_name():
    result = parse_memory("adım ne")

    assert result == {
        "tool": "memory_get",
        "key": "isim",
    }


@pytest.mark.unit
def test_memory_get_identity():
    result = parse_memory("ben kimim")

    assert result == {
        "tool": "memory_get",
        "key": "isim",
    }


@pytest.mark.unit
def test_memory_get_favorite_game():
    result = parse_memory("favori oyunum ne")

    assert result == {
        "tool": "memory_get",
        "key": "favori_oyun",
    }


@pytest.mark.unit
def test_memory_save_name():
    result = parse_memory("Benim adım Eren")

    assert result == {
        "tool": "memory_save",
        "key": "isim",
        "value": "eren",
        "category": "personal",
    }


@pytest.mark.unit
def test_memory_save_favorite_game():
    result = parse_memory("favori oyunum GTA San Andreas")

    assert result == {
        "tool": "memory_save",
        "key": "favori_oyun",
        "value": "gta san andreas",
        "category": "preference",
    }


@pytest.mark.unit
def test_memory_save_learning():
    result = parse_memory("Python öğreniyorum")

    assert result == {
        "tool": "memory_save",
        "key": "öğreniyor",
        "value": "python",
        "category": "interest",
    }


@pytest.mark.unit
def test_memory_save_learning_without_turkish_characters():
    result = parse_memory("Python ogreniyorum")

    assert result == {
        "tool": "memory_save",
        "key": "öğreniyor",
        "value": "python",
        "category": "interest",
    }


@pytest.mark.unit
def test_memory_parser_handles_normal_case_variation():
    result = parse_memory("Benim adım Eren")

    assert result == {
        "tool": "memory_save",
        "key": "isim",
        "value": "eren",
        "category": "personal",
    }


@pytest.mark.unit
def test_memory_parser_strips_whitespace():
    result = parse_memory("   adım ne   ")

    assert result == {
        "tool": "memory_get",
        "key": "isim",
    }


@pytest.mark.unit
def test_memory_parser_rejects_unrelated_request():
    result = parse_memory(
        "Python'da bir fonksiyon oluştur"
    )

    assert result is None