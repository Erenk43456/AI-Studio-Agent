import pytest

from agents.planner.calculator_parser import parse_calculator


@pytest.mark.unit
def test_calculator_parser_detects_addition():
    result = parse_calculator("12 + 8 kaç eder")

    assert result is not None
    assert result["tool"] == "calculator"
    assert result["operation"] == "add"
    assert result["numbers"] == [12, 8]


@pytest.mark.unit
def test_calculator_parser_detects_subtraction():
    result = parse_calculator("20 - 7")

    assert result is not None
    assert result["tool"] == "calculator"
    assert result["operation"] == "subtract"
    assert result["numbers"] == [20, 7]


@pytest.mark.unit
def test_calculator_parser_detects_multiplication():
    result = parse_calculator("6 * 9")

    assert result is not None
    assert result["tool"] == "calculator"
    assert result["operation"] == "multiply"
    assert result["numbers"] == [6, 9]


@pytest.mark.unit
def test_calculator_parser_detects_division():
    result = parse_calculator("100 / 4")

    assert result is not None
    assert result["tool"] == "calculator"
    assert result["operation"] == "divide"
    assert result["numbers"] == [100, 4]


@pytest.mark.unit
def test_calculator_parser_supports_turkish_addition():
    result = parse_calculator("25 ile 15'i topla")

    assert result is not None
    assert result["tool"] == "calculator"
    assert result["operation"] == "add"
    assert result["numbers"] == [25, 15]


@pytest.mark.unit
def test_calculator_parser_supports_turkish_subtraction():
    result = parse_calculator("50'den 12 çıkar")

    assert result is not None
    assert result["tool"] == "calculator"
    assert result["operation"] == "subtract"
    assert result["numbers"] == [50, 12]


@pytest.mark.unit
def test_calculator_parser_supports_turkish_multiplication():
    result = parse_calculator("7 ile 8'i çarp")

    assert result is not None
    assert result["operation"] == "multiply"
    assert result["numbers"] == [7, 8]


@pytest.mark.unit
def test_calculator_parser_supports_turkish_division():
    result = parse_calculator("80'i 4'e böl")

    assert result is not None
    assert result["operation"] == "divide"
    assert result["numbers"] == [80, 4]


@pytest.mark.unit
def test_calculator_parser_rejects_non_calculation():
    result = parse_calculator(
        "Python'da bir calculator classı oluştur"
    )

    assert result is None


@pytest.mark.unit
def test_calculator_parser_rejects_single_number():
    result = parse_calculator("42")

    assert result is None