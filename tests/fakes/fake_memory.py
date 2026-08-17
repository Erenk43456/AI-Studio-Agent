class FakeMemory:
    """
    In-memory deterministic memory implementation for tests.
    """

    def __init__(self):
        self.data = []

    def add(self, item):
        self.data.append(item)

    def get(self):
        return list(self.data)

    def clear(self):
        self.data.clear()

    def __len__(self):
        return len(self.data)