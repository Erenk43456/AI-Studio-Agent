from tools.calculator import Calculator


def test_add():

    calculator = Calculator()

    assert calculator.add(2, 3) == 5



def test_multiply():

    calculator = Calculator()

    assert calculator.multiply(4, 5) == 20