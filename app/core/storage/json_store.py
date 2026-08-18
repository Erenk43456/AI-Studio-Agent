import json
import os
import tempfile
import threading
from pathlib import Path


class JsonStore:
    def __init__(self, path):
        self.path = Path(path)
        self._lock = threading.RLock()

    def load(self, default=None):
        with self._lock:
            if not self.path.exists():
                return default

            try:
                with self.path.open(
                    "r",
                    encoding="utf-8",
                ) as file:
                    return json.load(file)

            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSON in {self.path}"
                ) from error

    def save(self, data):
        with self._lock:
            self.path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            fd, temp_path = tempfile.mkstemp(
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                dir=self.path.parent,
            )

            try:
                with os.fdopen(
                    fd,
                    "w",
                    encoding="utf-8",
                ) as file:
                    json.dump(
                        data,
                        file,
                        indent=2,
                        ensure_ascii=False,
                    )

                    file.flush()
                    os.fsync(file.fileno())

                os.replace(
                    temp_path,
                    self.path,
                )

            except Exception:
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass

                raise