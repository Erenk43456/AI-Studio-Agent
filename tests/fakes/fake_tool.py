from tools.base_tool import BaseTool


class FakeTool(BaseTool):
    """
    Minimal deterministic tool implementation.
    """

    def __init__(
        self,
        name="fake_tool",
        result=None,
    ):

        self.name = name
        self.result = result
        self.calls = []

    def execute(self, *args, **kwargs):
        self.calls.append(
            {
                "args": args,
                "kwargs": kwargs,
            }
        )

        return self.result

    @property
    def call_count(self):
        return len(self.calls)