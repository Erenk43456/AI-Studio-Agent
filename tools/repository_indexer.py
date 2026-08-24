"""Language-agnostic repository file indexing."""

import hashlib
from pathlib import Path

SKIP_DIRS = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "build",
    "dist",
    "release",
    "exports",
    "logs",
    "data",
    ".pytest_cache",
    ".mypy_cache",
    ".vscode",
    ".idea",
    "node_modules",
    ".aider.tags.cache.v4",
    ".ai_memory",
}

LANGUAGE_BY_EXTENSION = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".rs": "rust",
    ".go": "go",
    ".java": "java",
    ".kt": "kotlin",
    ".rb": "ruby",
    ".php": "php",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".md": "markdown",
}

CONFIGURATION_NAMES = {
    "pyproject.toml",
    "requirements.txt",
    "package.json",
    "cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "pytest.ini",
    "setup.cfg",
}

DOCUMENTATION_NAMES = {"readme", "changelog", "contributing", "license"}


class RepositoryIndexer:
    """Collect deterministic filesystem facts without parsing source syntax."""

    def __init__(self, skip_dirs=None):
        self.skip_dirs = set(skip_dirs or SKIP_DIRS)

    def index(self, root):
        root = Path(root)
        files = {}
        languages = {}
        extensions = {}
        configuration_files = []
        documentation_files = []
        test_files = []
        source_files = []

        scan_errors = []

        for path in self.iter_files(root):
            relative = path.relative_to(root).as_posix()
            try:
                metadata = self.file_metadata(path, relative)
            except (OSError, ValueError) as error:
                scan_errors.append({"path": relative, "error": str(error)})
                continue
            files[relative] = metadata

            language = metadata["language"]
            languages[language] = languages.get(language, 0) + 1
            extension = metadata["extension"] or "[no extension]"
            extensions[extension] = extensions.get(extension, 0) + 1

            category = metadata["category"]
            if category == "configuration":
                configuration_files.append(relative)
            elif category == "documentation":
                documentation_files.append(relative)
            elif category == "test":
                test_files.append(relative)
            elif category == "source":
                source_files.append(relative)

        return {
            "root": str(root.resolve()),
            "files": files,
            "languages": dict(sorted(languages.items())),
            "extensions": dict(sorted(extensions.items())),
            "configuration_files": sorted(configuration_files),
            "documentation_files": sorted(documentation_files),
            "test_files": sorted(test_files),
            "source_files": sorted(source_files),
            "total_files": len(files),
            "total_bytes": sum(item["size_bytes"] for item in files.values()),
            "total_lines": sum(item["line_count"] or 0 for item in files.values()),
            "scan_errors": sorted(scan_errors, key=lambda item: item["path"]),
        }

    def iter_files(self, root):
        root = Path(root)
        if not root.exists() or not root.is_dir():
            return
        try:
            paths = sorted(root.rglob("*"), key=lambda item: item.as_posix())
        except OSError:
            return
        for path in paths:
            if not path.is_file() or any(part in self.skip_dirs for part in path.parts):
                continue
            yield path

    @staticmethod
    def file_metadata(path, relative_path=None):
        path = Path(path)
        data = path.read_bytes()
        relative = (relative_path or path.name).replace("\\", "/")
        stat = path.stat()
        extension = path.suffix.lower()
        language = LANGUAGE_BY_EXTENSION.get(extension, "unknown")
        name = path.name.lower()
        category = "source"
        if name in CONFIGURATION_NAMES:
            category = "configuration"
        elif name.rsplit(".", 1)[0] in DOCUMENTATION_NAMES or name.startswith("readme"):
            category = "documentation"
        elif (
            "/tests/" in f"/{relative.lower()}/"
            or "/test/" in f"/{relative.lower()}/"
            or name.startswith("test_")
            or ".test." in name
            or ".spec." in name
        ):
            category = "test"
        elif language in {"json", "yaml", "toml", "markdown"}:
            category = "metadata"

        try:
            line_count = data.decode("utf-8").splitlines().__len__()
            is_binary = False
        except UnicodeDecodeError:
            line_count = None
            is_binary = True

        return {
            "path": relative,
            "extension": extension,
            "language": language,
            "category": category,
            "size_bytes": len(data),
            "line_count": line_count,
            "mtime_ns": stat.st_mtime_ns,
            "content_hash": "sha256:" + hashlib.sha256(data).hexdigest(),
            "is_binary": is_binary,
        }
