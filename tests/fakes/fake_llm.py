class FakeLLM:
    """
    Deterministic LLM double for tests.

    This class must never perform network access.
    """

    def __init__(
        self,
        response="Fake response",
        model="fake-model",
    ):
        self.response = response
        self.model = model
        self.calls = []

    def generate(self, prompt):
        self.calls.append(prompt)
        return self.response

    def get_current_model(self):
        return self.model

    def get_models(self):
        return [self.model]

    def has_model(self, model):
        return model == self.model

    def check_connection(self):
        return True

    @property
    def call_count(self):
        return len(self.calls)

    def reset(self):
        self.calls.clear()