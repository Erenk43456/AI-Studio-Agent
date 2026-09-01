class FakeMemory:
    """
    Deterministic in-memory implementation of the Memory contract.

    This fake never performs filesystem or network access.
    """

    def __init__(self):
        self.data = {}
        self.calls = []

    def save(
        self,
        key,
        value,
        category="general",
    ):
        self.calls.append(
            (key, value, category)
        )

        self.data[key] = {
            "value": value,
            "category": category,
        }

    def update(
        self,
        key,
        value,
    ):
        if key in self.data:
            self.data[key]["value"] = value
        else:
            self.save(
                key,
                value,
            )

    def get(
        self,
        key,
    ):
        item = self.data.get(
            key
        )

        if item is None:
            return None

        if isinstance(
            item,
            dict,
        ) and "value" in item:

            return item["value"]

        return item

    def get_full(
        self,
        key,
    ):
        return self.data.get(
            key
        )

    def delete(
        self,
        key,
    ):
        if key in self.data:
            del self.data[key]
            return True

        return False

    def clear(self):
        self.data = {}

    def recall(self):
        return self.data