class FakeLLM:
    """
    Deterministic LLM double for tests.

    This class must never perform network access.

    Supports three response modes:
    - a fixed `response` string (default)
    - a queue of `responses` consumed in order (for tests that need
      different output on successive calls)
    - raising `error` on every call (for failure-path tests)
    """

    def __init__(
        self,
        response="Fake response",
        model="fake-model",
        responses=None,
        error=None,
    ):
        self.response = response
        self.responses = list(responses) if responses is not None else None
        self.model = model
        self.error = error
        self.calls = []

    def generate(
        self,
        prompt,
        *args,
        max_tokens=None,
        temperature=None,
        timeout=None,
        **kwargs,
    ):
        self.calls.append(prompt)

        if self.error:
            raise self.error

        if self.responses is not None:
            return self.responses.pop(0)

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
