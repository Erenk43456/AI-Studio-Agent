class FakeDevelopmentContext:
    """
    Deterministic DevelopmentContext double for tests.

    Two modes:
    - fixed mode: pass `context` to always return that exact dict
      from build(), regardless of the task text.
    - dynamic mode (default): build(task) returns a context shaped
      like the real DevelopmentContext.build() output, with `task`
      filled in from the actual argument. Pass `fallback=True` to
      simulate the repository-analysis-fallback path (adds
      `targets` and flips `repository_analysis_fallback`).

    Pass `error` to make build() raise it, for failure-path tests.
    """

    def __init__(self, context=None, fallback=False, error=None):
        self.context = context
        self.fallback = fallback
        self.error = error
        self.calls = []

    def build(self, task):
        self.calls.append(task)

        if self.error:
            raise self.error

        if self.context is not None:
            return self.context

        result = {
            "task": task,
            "strategy": {
                "type": "development",
                "repository_analysis_fallback": self.fallback,
            },
        }

        if self.fallback:
            result["targets"] = ["app/core/parser.py"]

        return result
