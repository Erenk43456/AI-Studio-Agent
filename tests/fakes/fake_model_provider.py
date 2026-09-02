from contracts.llm_contract import LLMContract


class FakeModelProvider(LLMContract):
    """
    Deterministic model provider used by unit and integration tests.
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

    def check_connection(self):
        return True

    def get_current_model(self):
        return self.model

    def get_models(self):
        return [self.model]

    def has_model(self, model):
        return model == self.model