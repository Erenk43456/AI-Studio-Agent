import pytest

from tests.fakes.fake_tool import FakeTool
from contracts.tool_contract import ToolContract


@pytest.mark.contract
def test_tool_satisfies_tool_contract():
    tool = FakeTool(name="contract_tool")
    assert isinstance(tool, ToolContract)


@pytest.mark.contract
def test_tool_has_name():


    tool = FakeTool(
        name="contract_tool"
    )

    assert tool.name == "contract_tool"


@pytest.mark.contract
def test_tool_is_executable():

    tool = FakeTool()

    assert callable(
        tool.execute
    )


@pytest.mark.contract
def test_tool_execute_returns_result():

    tool = FakeTool(
        result="tool result"
    )

    result = tool.execute(
        "input"
    )

    assert result == "tool result"


@pytest.mark.contract
def test_tool_tracks_execution():

    tool = FakeTool(
        result="ok"
    )

    tool.execute(
        "first"
    )

    tool.execute(
        "second"
    )

    assert tool.call_count == 2


@pytest.mark.contract
def test_tool_tracks_arguments():

    tool = FakeTool()

    tool.execute(
        "hello",
        mode="test",
    )

    assert tool.calls[0]["args"] == (
        "hello",
    )

    assert tool.calls[0]["kwargs"] == {
        "mode": "test"
    }


@pytest.mark.contract
def test_tool_supports_empty_result():

    tool = FakeTool(
        result=None
    )

    result = tool.execute(
        "input"
    )

    assert result is None