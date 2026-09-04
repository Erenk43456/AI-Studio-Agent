import pytest

from tools.tool_registry import ToolRegistry


class FakeRegistryTool:
    """
    Tool double for ToolRegistry tests specifically: carries
    metadata class attributes (so registry auto-extraction can
    be exercised) and echoes its input back from execute(),
    which is a different concern than the shared call-tracking
    FakeTool in tests/fakes/ -- kept local intentionally.
    """

    description = "Fake tool description"
    purpose = "Testing"
    safe = True
    modifies_files = False
    requires_confirmation = False
    version = "2.0"

    def execute(self, data):
        return {
            "success": True,
            "data": data,
        }


@pytest.mark.unit
def test_registry_starts_empty():
    registry = ToolRegistry()

    assert registry.tools == {}
    assert registry.metadata == {}
    assert registry.list_tools() == []


@pytest.mark.unit
def test_register_adds_tool():
    registry = ToolRegistry()
    tool = FakeRegistryTool()

    registry.register(
        "fake",
        tool,
    )

    assert registry.get("fake") is tool
    assert registry.exists("fake") is True
    assert registry.list_tools() == ["fake"]


@pytest.mark.unit
def test_get_returns_none_for_unknown_tool():
    registry = ToolRegistry()

    assert registry.get("unknown") is None


@pytest.mark.unit
def test_exists_returns_false_for_unknown_tool():
    registry = ToolRegistry()

    assert registry.exists("unknown") is False


@pytest.mark.unit
def test_register_creates_default_metadata_from_tool():
    registry = ToolRegistry()
    tool = FakeRegistryTool()

    registry.register(
        "fake",
        tool,
    )

    assert registry.get_metadata("fake") == {
        "description": "Fake tool description",
        "purpose": "Testing",
        "safe": True,
        "modifies_files": False,
        "requires_confirmation": False,
        "version": "2.0",
    }


@pytest.mark.unit
def test_register_accepts_custom_metadata():
    registry = ToolRegistry()
    tool = FakeRegistryTool()

    registry.register(
        "fake",
        tool,
        metadata={
            "description": "Custom description",
            "safe": False,
            "requires_confirmation": True,
        },
    )

    metadata = registry.get_metadata("fake")

    assert metadata == {
        "description": "Custom description",
        "purpose": "Testing",
        "safe": False,
        "modifies_files": False,
        "requires_confirmation": True,
        "version": "2.0",
    }


@pytest.mark.unit
def test_get_metadata_returns_empty_dict_for_unknown_tool():
    registry = ToolRegistry()

    assert registry.get_metadata("unknown") == {}


@pytest.mark.unit
def test_unregister_existing_tool():
    registry = ToolRegistry()
    tool = FakeRegistryTool()

    registry.register(
        "fake",
        tool,
    )

    result = registry.unregister("fake")

    assert result is True
    assert registry.get("fake") is None
    assert registry.get_metadata("fake") == {}
    assert registry.exists("fake") is False
    assert registry.list_tools() == []


@pytest.mark.unit
def test_unregister_unknown_tool_returns_false():
    registry = ToolRegistry()

    result = registry.unregister("unknown")

    assert result is False

@pytest.mark.unit
def test_can_execute_returns_true_for_executable_tool():
    registry = ToolRegistry()
    tool = FakeRegistryTool()

    registry.register(
        "fake",
        tool,
    )

    assert registry.can_execute("fake") is True


@pytest.mark.unit
def test_can_execute_returns_false_for_unknown_tool():
    registry = ToolRegistry()

    assert registry.can_execute("unknown") is False


@pytest.mark.unit
def test_can_execute_returns_false_for_tool_without_execute():
    registry = ToolRegistry()

    class NonExecutableTool:
        pass

    registry.register(
        "broken",
        NonExecutableTool(),
    )

    assert registry.can_execute("broken") is False


@pytest.mark.unit
def test_execute_returns_tool_not_found_error():
    registry = ToolRegistry()

    result = registry.execute(
        "unknown",
        {"value": 42},
    )

    assert result == {
        "success": False,
        "error": "Tool not found: unknown",
    }


@pytest.mark.unit
def test_execute_returns_error_when_tool_has_no_execute():
    registry = ToolRegistry()

    class NonExecutableTool:
        pass

    assert registry.register(
        "broken",
        NonExecutableTool(),
    ) is False

    assert registry.exists("broken") is False
    assert registry.can_execute("broken") is False


@pytest.mark.unit
def test_execute_calls_tool_and_wraps_result():
    registry = ToolRegistry()
    tool = FakeRegistryTool()

    registry.register(
        "fake",
        tool,
    )

    data = {
        "value": 42,
    }

    result = registry.execute(
        "fake",
        data,
    )

    assert result == {
        "success": True,
        "tool": "fake",
        "result": {
            "success": True,
            "data": data,
        },
    }


@pytest.mark.unit
def test_execute_passes_exact_data_to_tool():
    registry = ToolRegistry()
    tool = FakeRegistryTool()

    registry.register(
        "fake",
        tool,
    )

    data = {
        "action": "calculate",
        "input": "2 + 2",
    }

    registry.execute(
        "fake",
        data,
    )

    # FakeTool'in execute() sonucundan bağımsız olarak
    # gerçek input'un geçirildiğini doğruluyoruz.
    assert tool.execute(data) == {
        "success": True,
        "data": data,
    }


@pytest.mark.unit
def test_execute_handles_tool_exception():
    registry = ToolRegistry()

    class FailingTool:
        def execute(self, data):
            raise RuntimeError(
                "execution failed"
            )

    registry.register(
        "failing",
        FailingTool(),
    )

    result = registry.execute(
        "failing",
        {"value": 42},
    )

    assert result == {
        "success": False,
        "tool": "failing",
        "error": "execution failed",
    }


@pytest.mark.unit
def test_get_tool_descriptions_returns_registered_tools():
    registry = ToolRegistry()

    first = FakeRegistryTool()
    second = FakeRegistryTool()

    registry.register(
        "first",
        first,
    )

    registry.register(
        "second",
        second,
    )

    descriptions = registry.get_tool_descriptions()

    assert descriptions == [
        {
            "name": "first",
            "description": "Fake tool description",
            "purpose": "Testing",
            "safe": True,
            "modifies_files": False,
            "requires_confirmation": False,
        },
        {
            "name": "second",
            "description": "Fake tool description",
            "purpose": "Testing",
            "safe": True,
            "modifies_files": False,
            "requires_confirmation": False,
        },
    ]


@pytest.mark.unit
def test_get_tool_descriptions_uses_metadata_defaults():
    registry = ToolRegistry()

    class MinimalTool:
        def execute(self, data):
            return data

    registry.register(
        "minimal",
        MinimalTool(),
    )

    descriptions = registry.get_tool_descriptions()

    assert descriptions == [
        {
            "name": "minimal",
            "description": "No description provided.",
            "purpose": "Unknown",
            "safe": True,
            "modifies_files": False,
            "requires_confirmation": False,
        }
    ]


@pytest.mark.unit
def test_inspect_tool_returns_tool_information():
    registry = ToolRegistry()
    tool = FakeRegistryTool()

    registry.register(
        "fake",
        tool,
    )

    inspection = registry.inspect_tool(
        "fake"
    )

    assert inspection["name"] == "fake"
    assert inspection["class"] == "FakeRegistryTool"
    assert inspection["has_execute"] is True

    assert "execute" in inspection["methods"]


@pytest.mark.unit
def test_inspect_tool_returns_none_for_unknown_tool():
    registry = ToolRegistry()

    assert registry.inspect_tool(
        "unknown"
    ) is None

@pytest.mark.unit
def test_execute_preserves_tool_failure_status():
    registry = ToolRegistry()

    class FailingResultTool:
        def execute(self, data):
            return {
                "success": False,
                "error": "operation failed",
            }

    registry.register(
        "failing_result",
        FailingResultTool(),
    )

    result = registry.execute(
        "failing_result",
        {"value": 42},
    )

    assert result["success"] is False
    assert result["tool"] == "failing_result"
    assert result["result"] == {
        "success": False,
        "error": "operation failed",
    }

def test_register_stores_tool_metadata():
    class FakeTool:
        description = "Test tool"
        purpose = "Testing"
        safe = False
        modifies_files = True
        requires_confirmation = True
        version = "2.0"

        def execute(self, data):
            return {"success": True}

    registry = ToolRegistry()

    assert registry.register(
        "test_tool",
        FakeTool(),
        metadata={"extra": "value"},
    ) is True

    assert registry.get_metadata("test_tool") == {
        "description": "Test tool",
        "purpose": "Testing",
        "safe": False,
        "modifies_files": True,
        "requires_confirmation": True,
        "version": "2.0",
        "extra": "value",
    }