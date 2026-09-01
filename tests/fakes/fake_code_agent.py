class FakeCodeAgent:
    """
    Deterministic CodeAgent double for tests.

    run(task, development_context=None) returns a fixed `result`
    (or raises `error`), and records every call in `.calls`.

    `development_context` is exposed as a plain attribute too,
    since some callers read it directly instead of passing it
    as a run() argument.
    """

    def __init__(self, result=None, development_context=None, error=None):
        self.result = result if result is not None else {
            "success": True,
            "write_result": {
                "success": True,
                "files_written": ["app/parser.py"],
            },
        }
        self.development_context = development_context
        self.error = error
        self.calls = []

    def run(self, task, development_context=None):
        self.calls.append((task, development_context))

        if self.error:
            raise self.error

        return self.result
