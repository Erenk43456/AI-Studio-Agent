class FakeProjectMemory:
    """
    Deterministic Project Memory double for tests.

    Covers the full ProjectMemory interface exercised across the
    test suite:
    - read access used by DevelopmentContext (get_all_files,
      get_file, get_architecture)
    - read access used by ProjectMemoryTool (get_file, get_all_files,
      get_architecture, search, get_context, load_json)
    - write/sync access used by ProjectMemorySync
      (update_project_info, update_architecture,
      sync_repository_analysis)

    Every read defaults to an empty/falsy value (no hidden non-empty
    defaults) -- DevelopmentContext treats a non-empty architecture
    or file set as a signal that memory is "available", so a fake
    with a surprising default could silently change which code path
    a test exercises. Pass exactly the data your test needs via the
    constructor.

    `search` and `get_context` are the one exception: with no
    override they echo their arguments back (matching what a real,
    minimal implementation would do), since nothing couples their
    output to a side effect the way get_all_files/get_architecture
    do for DevelopmentContext.

    Pass `error` to make every method raise it, for failure-path
    tests (replaces the old, per-file FailingProjectMemory classes).
    """

    def __init__(
        self,
        files=None,
        architecture=None,
        search_result=None,
        context_result=None,
        overview=None,
        project_file="project.json",
        error=None,
    ):
        self.files = files if files is not None else {}
        self.architecture = architecture if architecture is not None else {}
        self.search_result = search_result
        self.context_result = context_result
        self.overview = overview if overview is not None else {}
        self.project_file = project_file
        self.error = error
        self.calls = []

    # ---- read side ----

    def get_all_files(self):
        self.calls.append(("get_all_files",))

        if self.error:
            raise self.error

        return self.files

    def get_file(self, path):
        self.calls.append(("get_file", path))

        if self.error:
            raise self.error

        if isinstance(self.files, dict):
            return self.files.get(path)

        return None

    def get_architecture(self):
        self.calls.append(("get_architecture",))

        if self.error:
            raise self.error

        return self.architecture

    def search(self, query):
        self.calls.append(("search", query))

        if self.error:
            raise self.error

        if self.search_result is not None:
            return self.search_result

        return [{"path": "app/parser.py", "match": query}]

    def get_context(self, query, limit=5):
        self.calls.append(("get_context", query, limit))

        if self.error:
            raise self.error

        if self.context_result is not None:
            return self.context_result

        return {"query": query, "limit": limit}

    def load_json(self, path):
        self.calls.append(("load_json", path))

        if self.error:
            raise self.error

        return self.overview

    # ---- write/sync side ----

    def update_project_info(self, data):
        self.calls.append(("project_info", data))

        if self.error:
            raise self.error

    def update_architecture(self, name, data):
        self.calls.append(("architecture", name, data))

        if self.error:
            raise self.error

    def sync_repository_analysis(self, analysis):
        self.calls.append(("repository_analysis", analysis))

        if self.error:
            raise self.error

        return True
