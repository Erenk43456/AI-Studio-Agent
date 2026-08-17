import pytest

from tools.calculator import Calculator


@pytest.fixture
def calculator():
    return Calculator()


@pytest.mark.unit
def test_calculator_add(calculator):
    result = calculator.execute(
        {
            "operation": "add",
            "numbers": [2, 3],
        }
    )

    assert result == 5.0


@pytest.mark.unit
def test_calculator_subtract(calculator):
    result = calculator.execute(
        {
            "operation": "subtract",
            "numbers": [10, 4],
        }
    )

    assert result == 6.0


@pytest.mark.unit
def test_calculator_multiply(calculator):
    result = calculator.execute(
        {
            "operation": "multiply",
            "numbers": [6, 7],
        }
    )

    assert result == 42.0


@pytest.mark.unit
def test_calculator_divide(calculator):
    result = calculator.execute(
        {
            "operation": "divide",
            "numbers": [20, 4],
        }
    )

    assert result == 5.0


@pytest.mark.unit
def test_calculator_divide_by_zero(calculator):
    result = calculator.execute(
        {
            "operation": "divide",
            "numbers": [10, 0],
        }
    )

    assert result == "Cannot divide by zero."


@pytest.mark.unit
def test_calculator_requires_two_numbers(calculator):
    result = calculator.execute(
        {
            "operation": "add",
            "numbers": [5],
        }
    )

    assert result == "Two numbers required."


@pytest.mark.unit
def test_calculator_requires_numbers(calculator):
    result = calculator.execute(
        {
            "operation": "add",
        }
    )

    assert result == "Two numbers required."


@pytest.mark.unit
def test_calculator_unsupported_operation(calculator):
    result = calculator.execute(
        {
            "operation": "modulo",
            "numbers": [10, 3],
        }
    )

    assert result == "Unsupported operation."


@pytest.mark.unit
def test_calculator_converts_numbers_to_float(calculator):
    result = calculator.execute(
        {
            "operation": "add",
            "numbers": ["2", "3.5"],
        }
    )

    assert result == 5.5


@pytest.mark.unit
def test_calculator_handles_invalid_number(calculator):
    result = calculator.execute(
        {
            "operation": "add",
            "numbers": ["invalid", 3],
        }
    )

    assert result.startswith(
        "Calculator error:"
    )

@pytest.mark.unit
def test_calculator_add_method(calculator):
    assert calculator.add(2, 3) == 5


@pytest.mark.unit
def test_calculator_subtract_method(calculator):
    assert calculator.subtract(10, 4) == 6


@pytest.mark.unit
def test_calculator_multiply_method(calculator):
    assert calculator.multiply(6, 7) == 42


@pytest.mark.unit
def test_calculator_divide_method(calculator):
    assert calculator.divide(20, 4) == 5


@pytest.mark.unit
def test_calculator_metadata(calculator):
    assert calculator.name == "calculator"
    assert calculator.description
    assert calculator.purpose
    assert calculator.safe is True
    assert calculator.modifies_files is False
    assert calculator.requires_confirmation is False
    assert calculator.version