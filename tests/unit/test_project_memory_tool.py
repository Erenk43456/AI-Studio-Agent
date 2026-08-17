import pytest

from tools.project_memory_tool import ProjectMemoryTool


class FakeProjectMemory:
    def __init__(self):
        self.calls = []
        self.project_file = "project.json"

    def get_file(self, path):
        self.calls.append(
            ("get_file", path)
        )
        return {
            "path": path,
            "summary": "Parser file",
        }

    def get_all_files(self):
        self.calls.append(
            ("get_all_files",)
        )
        return [
            "app/parser.py",
            "app/main.py",
        ]

    def get_architecture(self):
        self.calls.append(
            ("get_architecture",)
        )
        return {
            "style": "layered",
        }

    def search(self, query):
        self.calls.append(
            ("search", query)
        )
        return [
            {
                "path": "app/parser.py",
                "match": query,
            }
        ]

    def get_context(self, query, limit):
        self.calls.append(
            ("get_context", query, limit)
        )
        return {
            "query": query,
            "limit": limit,
        }

    def load_json(self, path):
        self.calls.append(
            ("load_json", path)
        )
        return {
            "project": "AI-Studio",
            "version": 1,
        }


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
    memory = FakeProjectMemory()

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
    memory = FakeProjectMemory()

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
    memory = FakeProjectMemory()

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
    memory = FakeProjectMemory()

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
    memory = FakeProjectMemory()

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