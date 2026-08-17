import pytest

from tools.memory_tool import MemoryTool

from tests.fakes.fake_memory import FakeMemory


@pytest.mark.unit
def test_memory_tool_has_expected_metadata():
    memory = FakeMemory()

    tool = MemoryTool(
        memory
    )

    assert tool.name == "memory"

    assert tool.description == (
        "Provides access to persistent "
        "user memory. "
        "Use action 'get' to retrieve "
        "stored information "
        "and action 'save' to store "
        "new information."
    )

    assert tool.memory is memory


@pytest.mark.unit
def test_memory_tool_rejects_non_dict_plan():
    memory = FakeMemory()

    tool = MemoryTool(
        memory
    )

    result = tool.execute(
        "save my name"
    )

    assert result == {
        "success": False,
        "error": "Invalid memory request.",
    }


@pytest.mark.unit
def test_memory_tool_rejects_unknown_action():
    memory = FakeMemory()

    tool = MemoryTool(
        memory
    )

    result = tool.execute(
        {
            "action": "delete",
            "key": "name",
        }
    )

    assert result == {
        "success": False,
        "error": (
            "Unknown memory action: delete"
        ),
    }


@pytest.mark.unit
def test_memory_tool_save_uses_default_category():
    memory = FakeMemory()

    tool = MemoryTool(
        memory
    )

    result = tool.execute(
        {
            "action": "save",
            "key": "name",
            "value": "Eren",
        }
    )

    assert result == {
        "success": True,
        "action": "save",
        "key": "name",
        "value": "Eren",
        "message": "Saved memory: name",
    }

    assert memory.data["name"] == {
        "value": "Eren",
        "category": "general",
    }


@pytest.mark.unit
def test_memory_tool_save_uses_custom_category():
    memory = FakeMemory()

    tool = MemoryTool(
        memory
    )

    result = tool.execute(
        {
            "action": "save",
            "key": "favorite_language",
            "value": "Rust",
            "category": "preferences",
        }
    )

    assert result == {
        "success": True,
        "action": "save",
        "key": "favorite_language",
        "value": "Rust",
        "message": (
            "Saved memory: favorite_language"
        ),
    }

    assert memory.data["favorite_language"] == {
        "value": "Rust",
        "category": "preferences",
    }


@pytest.mark.unit
@pytest.mark.parametrize(
    "plan",
    [
        {
            "action": "save",
            "value": "Eren",
        },
        {
            "action": "save",
            "key": "",
            "value": "Eren",
        },
        {
            "action": "save",
            "key": "name",
            "value": None,
        },
    ],
)
def test_memory_tool_save_rejects_missing_key_or_value(
    plan,
):
    memory = FakeMemory()

    tool = MemoryTool(
        memory
    )

    result = tool.execute(
        plan
    )

    assert result == {
        "success": False,
        "error": (
            "Memory key or value missing."
        ),
    }


@pytest.mark.unit
def test_memory_tool_get_returns_existing_memory():
    memory = FakeMemory()

    memory.save(
        "name",
        "Eren",
    )

    tool = MemoryTool(
        memory
    )

    result = tool.execute(
        {
            "action": "get",
            "key": "name",
        }
    )

    assert result == {
        "success": True,
        "action": "get",
        "key": "name",
        "value": "Eren",
        "message": "Eren",
    }


@pytest.mark.unit
def test_memory_tool_get_returns_failure_when_memory_not_found():
    memory = FakeMemory()

    tool = MemoryTool(
        memory
    )

    result = tool.execute(
        {
            "action": "get",
            "key": "unknown",
        }
    )

    assert result == {
        "success": False,
        "action": "get",
        "key": "unknown",
        "error": (
            "Information not found."
        ),
    }


@pytest.mark.unit
def test_memory_tool_get_rejects_missing_key():
    memory = FakeMemory()

    tool = MemoryTool(
        memory
    )

    result = tool.execute(
        {
            "action": "get",
        }
    )

    assert result == {
        "success": False,
        "error": "Memory key missing.",
    }


@pytest.mark.unit
def test_memory_tool_save_handles_memory_exception():
    class FailingMemory:
        def save(
            self,
            key,
            value,
            category,
        ):
            raise RuntimeError(
                "storage unavailable"
            )

    tool = MemoryTool(
        FailingMemory()
    )

    result = tool.execute(
        {
            "action": "save",
            "key": "name",
            "value": "Eren",
        }
    )

    assert result == {
        "success": False,
        "action": "save",
        "error": (
            "storage unavailable"
        ),
    }


@pytest.mark.unit
def test_memory_tool_get_handles_memory_exception():
    class FailingMemory:
        def get(self, key):
            raise RuntimeError(
                "storage unavailable"
            )

    tool = MemoryTool(
        FailingMemory()
    )

    result = tool.execute(
        {
            "action": "get",
            "key": "name",
        }
    )

    assert result == {
        "success": False,
        "action": "get",
        "error": (
            "storage unavailable"
        ),
    }