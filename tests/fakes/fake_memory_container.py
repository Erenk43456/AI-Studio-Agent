class FakeMemoryContainer:
    """
    Deterministic fake for the MemoryContainer dependency.

    This fake performs no filesystem or network access.
    """

    def __init__(
        self,
        memory=None,
        project_memory=None,
    ):
        self.memory = memory
        self.project_memory = project_memory

        self.calls = []

    @property
    def call_count(self):
        return len(self.calls)

    def reset(self):
        self.calls.clear()