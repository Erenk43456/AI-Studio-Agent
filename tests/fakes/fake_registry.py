class FakeRegistry:
    """
    Deterministic Tool Registry double for tests.

    Backed by a plain dict of name -> tool. Tracks every name
    that was looked up via `.calls` so tests can assert on
    which tools were requested.
    """

    def __init__(self, tools=None):
        self.tools = tools or {}
        self.calls = []

    def get(self, name):
        self.calls.append(name)
        return self.tools.get(name)

    def get_tool_descriptions(self):
        descriptions = []

        for name, tool in self.tools.items():
            descriptions.append(
                {
                    "name": name,
                    "description": getattr(
                        tool,
                        "description",
                        "No description provided.",
                    ),
                    "purpose": getattr(
                        tool,
                        "purpose",
                        "Unknown",
                    ),
                    "safe": getattr(
                        tool,
                        "safe",
                        True,
                    ),
                    "modifies_files": getattr(
                        tool,
                        "modifies_files",
                        False,
                    ),
                    "requires_confirmation": getattr(
                        tool,
                        "requires_confirmation",
                        False,
                    ),
                }
            )

        return descriptions

    def register(self, name, tool):
        self.tools[name] = tool