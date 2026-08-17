import pytest

from agents.planner.parser_registry import ParserRegistry


class FakeParser:
    def __init__(self, priority, result=None):
        self.priority = priority
        self.result = result
        self.calls = []

    def parse(self, message):
        self.calls.append(message)
        return self.result


@pytest.mark.unit
def test_registry_orders_parsers_by_priority():
    registry = ParserRegistry()

    parser_high = FakeParser(priority=100)
    parser_low = FakeParser(priority=10)

    registry.register(parser_high)
    registry.register(parser_low)

    assert registry.parsers == [
        parser_low,
        parser_high,
    ]


@pytest.mark.unit
def test_registry_returns_first_successful_parse():
    registry = ParserRegistry()

    first = FakeParser(
        priority=10,
        result=None,
    )

    second = FakeParser(
        priority=20,
        result={
            "tool": "fake_tool",
            "action": "execute",
        },
    )

    third = FakeParser(
        priority=30,
        result={
            "tool": "another_tool",
        },
    )

    registry.register(third)
    registry.register(first)
    registry.register(second)

    result = registry.parse("hello")

    assert result == {
        "tool": "fake_tool",
        "action": "execute",
    }

    assert first.calls == ["hello"]
    assert second.calls == ["hello"]

    # Registry should stop after first successful parser.
    assert third.calls == []


@pytest.mark.unit
def test_registry_returns_none_when_no_parser_matches():
    registry = ParserRegistry()

    parser = FakeParser(
        priority=10,
        result=None,
    )

    registry.register(parser)

    assert registry.parse("hello") is None

    assert parser.calls == ["hello"]


@pytest.mark.unit
def test_registry_preserves_priority_order_after_multiple_registrations():
    registry = ParserRegistry()

    parsers = [
        FakeParser(50),
        FakeParser(5),
        FakeParser(30),
        FakeParser(10),
    ]

    for parser in parsers:
        registry.register(parser)

    assert [
        parser.priority
        for parser in registry.parsers
    ] == [
        5,
        10,
        30,
        50,
    ]