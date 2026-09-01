class FakeRepositoryAnalyzer:
    """
    Deterministic Repository Analyzer double for tests.

    Pass `error` to make analyze() raise it, for failure-path
    tests (replaces the old, per-file FailingRepositoryAnalyzer
    classes).
    """

    def __init__(self, analysis=None, error=None):
        self.calls = []
        self.error = error
        self.analysis = analysis or {
            "generated_at": "2026-08-20 21:00:00",
            "overview": {
                "python_files": 10,
                "total_lines": 100,
            },
            "modules": {},
            "module_roles": {},
            "definitions": {},
            "tools": [],
            "registry_names": [],
            "wiring_checks": [],
            "issues": [],
        }

    def analyze(self, root):
        self.calls.append(str(root))

        if self.error:
            raise self.error

        return self.analysis

    def execute(self, plan):
        """
        RepositoryAnalyzerTool is used two ways in the real code:
        directly via analyze(root) (DevelopmentContext,
        ProjectMemorySync), and as a registered tool via
        execute(plan) (DevelopmentOrchestrator's "analyze" action).
        Both return the same canned `analysis` value here.
        """
        self.calls.append(plan)

        if self.error:
            raise self.error

        return self.analysis
