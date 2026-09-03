from pathlib import Path
from datetime import datetime

from app.core.logger import AppLogger
from app.core.storage.json_store import JsonStore


class Memory:

    def __init__(self, data_dir=None):

        self.logger = AppLogger()

        self.data_dir = Path(
            data_dir or "data"
        )

        self.data_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.file = (
            self.data_dir / "memory.json"
        )

        self.store = JsonStore(
            self.file
        )

        try:

            data = self.store.load(
                default={}
            )

            if isinstance(data, dict):

                self.data = data

            else:

                self.logger.warning(
                    "Memory data is not a dictionary. "
                    "Starting with empty memory."
                )

                self.data = {}

            if self.file.exists():

                self.logger.info(
                    "Memory loaded successfully."
                )

            else:

                self.logger.info(
                    "New memory created."
                )

        except ValueError as error:

            self.logger.error(
                f"Memory JSON error: {error}"
            )

            self.data = {}

    def _timestamp(self):

        return datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    def save(
        self,
        key,
        value,
        category="general"
    ):

        now = self._timestamp()

        self.data[key] = {
            "value": value,
            "category": category,
            "created": now,
            "updated": now
        }

        self._write()

        self.logger.info(
            f"Memory saved: {key}"
        )

    def update(
        self,
        key,
        value
    ):

        if (
            key in self.data
            and isinstance(
                self.data[key],
                dict
            )
        ):

            self.data[key]["value"] = value

            self.data[key]["updated"] = (
                self._timestamp()
            )

            self._write()

            self.logger.info(
                f"Memory updated: {key}"
            )

        else:

            self.save(
                key,
                value
            )

    def get(
        self,
        key
    ):

        item = self.data.get(
            key
        )

        if item is None:

            self.logger.warning(
                f"Memory not found: {key}"
            )

            return None

        if (
            isinstance(
                item,
                dict
            )
            and "value" in item
        ):

            return item["value"]

        return item

    def get_full(
        self,
        key
    ):

        return self.data.get(
            key
        )

    def delete(
        self,
        key
    ):

        if key in self.data:

            del self.data[key]

            self._write()

            self.logger.info(
                f"Memory deleted: {key}"
            )

            return True

        self.logger.warning(
            f"Delete failed, memory not found: {key}"
        )

        return False

    def clear(self):

        self.data = {}

        self._write()

        self.logger.info(
            "All memory cleared."
        )

    def recall(self):

        return self.data

    def _write(self):

        try:

            self.store.save(
                self.data
            )

        except Exception as error:

            self.logger.error(
                f"Memory write error: {error}"
            )

            raise