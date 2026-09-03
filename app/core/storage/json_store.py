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

    @staticmethod
    def save_transaction(stores):
        stores = list(stores)

        if not stores:
            return

        staged = []

        try:
            for store, data in stores:
                store.path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                fd, temp_path = tempfile.mkstemp(
                    prefix=f".{store.path.name}.",
                    suffix=".tmp",
                    dir=store.path.parent,
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

                    staged.append(
                        (
                            store,
                            Path(temp_path),
                        )
                    )

                except Exception:
                    try:
                        os.unlink(temp_path)
                    except OSError:
                        pass
                    raise

            backups = []
            committed = []

            try:
                for store, temp_path in staged:
                    backup_path = None

                    if store.path.exists():
                        fd, backup_path = tempfile.mkstemp(
                            prefix=f".{store.path.name}.",
                            suffix=".bak",
                            dir=store.path.parent,
                        )
                        os.close(fd)

                        os.replace(
                            store.path,
                            backup_path,
                        )

                    backups.append(
                        (
                            store,
                            backup_path,
                        )
                    )

                    os.replace(
                        temp_path,
                        store.path,
                    )

                    committed.append(store)

            except Exception:
                for store in reversed(committed):
                    try:
                        if store.path.exists():
                            store.path.unlink()
                    except OSError:
                        pass

                for store, backup_path in reversed(backups):
                    if backup_path is not None:
                        try:
                            os.replace(
                                backup_path,
                                store.path,
                            )
                        except OSError:
                            pass

                raise

            finally:
                for _, temp_path in staged:
                    try:
                        if temp_path.exists():
                            temp_path.unlink()
                    except OSError:
                        pass

                for _, backup_path in backups:
                    if backup_path is not None:
                        try:
                            if Path(backup_path).exists():
                                Path(backup_path).unlink()
                        except OSError:
                            pass

        except Exception:
            for _, temp_path in staged:
                try:
                    if temp_path.exists():
                        temp_path.unlink()
                except OSError:
                    pass

            raise