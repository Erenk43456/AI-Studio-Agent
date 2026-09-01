import pytest

from tests.fakes.fake_project_memory import FakeProjectMemory
from tools.project_memory_tool import ProjectMemoryTool


@pytest.mark.unit
def test_project_memory_tool_has_expected_metadata():
    memory = FakeProjectMemory()

    tool = ProjectMemoryTool(
        memory
    )

    assert tool.name == "project_memory"

    assert tool.description == (
        "Provides access to persistent "
        "project architecture memory."
    )

    assert tool.project_memory is memory


@pytest.mark.unit
def test_project_memory_tool_rejects_non_dict_plan():
    memory = FakeProjectMemory()

    tool = ProjectMemoryTool(
        memory
    )

    result = tool.execute(
        "get project"
    )

    assert result == {
        "success": False,
        "message": (
            "Invalid project memory request."
        ),
    }

    assert memory.calls == []


@pytest.mark.unit
def test_project_memory_tool_defaults_to_overview():
    memory = FakeProjectMemory(
        overview={"project": "AI-Studio", "version": 1}
    )

    tool = ProjectMemoryTool(
        memory
    )

    result = tool.execute({})

    assert result == {
        "success": True,
        "data": {
            "project": "AI-Studio",
            "version": 1,
        },
    }

    assert memory.calls == [
        (
            "load_json",
            "project.json",
        ),
    ]


@pytest.mark.unit
def test_project_memory_tool_file_action():
    memory = FakeProjectMemory(
        files={
            "app/parser.py": {
                "path": "app/parser.py",
                "summary": "Parser file",
            }
        }
    )

    tool = ProjectMemoryTool(
        memory
    )

    result = tool.execute(
        {
            "action": "file",
            "path": "app/parser.py",
        }
    )

    assert result == {
        "success": True,
        "data": {
            "path": "app/parser.py",
            "summary": "Parser file",
        },
    }

    assert memory.calls == [
        (
            "get_file",
            "app/parser.py",
        ),
    ]


@pytest.mark.unit
def test_project_memory_tool_files_action():
    memory = FakeProjectMemory(
        files=["app/parser.py", "app/main.py"]
    )

    tool = ProjectMemoryTool(
        memory
    )

    result = tool.execute(
        {
            "action": "files",
        }
    )

    assert result == {
        "success": True,
        "data": [
            "app/parser.py",
            "app/main.py",
        ],
    }

    assert memory.calls == [
        (
            "get_all_files",
        ),
    ]


@pytest.mark.unit
def test_project_memory_tool_architecture_action():
    memory = FakeProjectMemory(
        architecture={"style": "layered"}
    )

    tool = ProjectMemoryTool(
        memory
    )

    result = tool.execute(
        {
            "action": "architecture",
        }
    )

    assert result == {
        "success": True,
        "data": {
            "style": "layered",
        },
    }

    assert memory.calls == [
        (
            "get_architecture",
        ),
    ]


@pytest.mark.unit
def test_project_memory_tool_search_action():
    memory = FakeProjectMemory()

    tool = ProjectMemoryTool(
        memory
    )

    result = tool.execute(
        {
            "action": "search",
            "query": "parser",
        }
    )

    assert result == {
        "success": True,
        "data": [
            {
                "path": "app/parser.py",
                "match": "parser",
            }
        ],
    }

    assert memory.calls == [
        (
            "search",
            "parser",
        ),
    ]


@pytest.mark.unit
def test_project_memory_tool_search_defaults_to_empty_query():
    memory = FakeProjectMemory()

    tool = ProjectMemoryTool(
        memory
    )

    result = tool.execute(
        {
            "action": "search",
        }
    )

    assert result == {
        "success": True,
        "data": [
            {
                "path": "app/parser.py",
                "match": "",
            }
        ],
    }

    assert memory.calls == [
        (
            "search",
            "",
        ),
    ]


@pytest.mark.unit
def test_project_memory_tool_context_action():
    memory = FakeProjectMemory()

    tool = ProjectMemoryTool(
        memory
    )

    result = tool.execute(
        {
            "action": "context",
            "query": "authentication",
            "limit": 10,
        }
    )

    assert result == {
        "success": True,
        "data": {
            "query": "authentication",
            "limit": 10,
        },
    }

    assert memory.calls == [
        (
            "get_context",
            "authentication",
            10,
        ),
    ]


@pytest.mark.unit
def test_project_memory_tool_context_defaults_limit_to_five():
    memory = FakeProjectMemory()

    tool = ProjectMemoryTool(
        memory
    )

    result = tool.execute(
        {
            "action": "context",
            "query": "parser",
        }
    )

    assert result == {
        "success": True,
        "data": {
            "query": "parser",
            "limit": 5,
        },
    }

    assert memory.calls == [
        (
            "get_context",
            "parser",
            5,
        ),
    ]


@pytest.mark.unit
def test_project_memory_tool_overview_explicit_action():
    memory = FakeProjectMemory(
        overview={"project": "AI-Studio", "version": 1}
    )

    tool = ProjectMemoryTool(
        memory
    )

    result = tool.execute(
        {
            "action": "overview",
        }
    )

    assert result == {
        "success": True,
        "data": {
            "project": "AI-Studio",
            "version": 1,
        },
    }

    assert memory.calls == [
        (
            "load_json",
            "project.json",
        ),
    ]


@pytest.mark.unit
def test_project_memory_tool_unknown_action():
    memory = FakeProjectMemory()

    tool = ProjectMemoryTool(
        memory
    )

    result = tool.execute(
        {
            "action": "delete",
        }
    )

    assert result == {
        "success": False,
        "message": (
            "Unknown action: delete"
        ),
    }

    assert memory.calls == []

@pytest.mark.unit
def test_project_memory_sync_repository_analysis(
    tmp_path
):

    from memory.project_memory.project_memory import (
        ProjectMemory,
    )

    memory = ProjectMemory(
        tmp_path
    )

    analysis = {
        "generated_at": (
            "2026-08-20 21:00:00"
        ),
        "overview": {
            "python_files": 10,
            "total_lines": 100,
        },
        "module_roles": {
            "agents/chat_agent.py": (
                "Conversational agent"
            ),
        },
        "definitions": {
            "agents/chat_agent.py": [
                "class ChatAgent"
            ],
        },
        "tools": [],
        "registry_names": [],
        "wiring_checks": [],
        "issues": [],
    }

    result = memory.sync_repository_analysis(
        analysis
    )

    assert result is True

    project = memory.load_json(
        memory.project_file
    )

    files = memory.get_all_files()

    architecture = (
        memory.get_architecture()
    )

    assert project[
        "python_files"
    ] == 10

    assert files[
        "agents/chat_agent.py"
    ][
        "definitions"
    ] == [
        "class ChatAgent"
    ]

    assert files[
        "agents/chat_agent.py"
    ][
        "role"
    ] == "Conversational agent"

    assert architecture[
        "repository_analysis"
    ] == analysis