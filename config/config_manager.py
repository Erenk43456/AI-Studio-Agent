import json
from pathlib import Path


class ConfigManager:

    def __init__(self):

        self.file = Path(
            "config/user.json"
        )

        self.file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.data = self.load()

    # =========================================================
    # LOAD
    # =========================================================

    def load(self):

        if not self.file.exists():

            return {}

        try:

            with self.file.open(
                "r",
                encoding="utf-8-sig"
            ) as file:

                data = json.load(
                    file
                )

            return (
                data
                if isinstance(data, dict)
                else {}
            )

        except (
            json.JSONDecodeError,
            OSError
        ):

            return {}

    # =========================================================
    # GET
    # =========================================================

    def get(
        self,
        key,
        default=None
    ):

        return self.data.get(
            key,
            default
        )

    # =========================================================
    # SET
    # =========================================================

    def set(
        self,
        key,
        value
    ):

        self.data[key] = value

        self.save()

    # =========================================================
    # UPDATE
    # =========================================================

    def update(
        self,
        values
    ):

        self.data.update(
            values
        )

        self.save()

    # =========================================================
    # SAVE
    # =========================================================

    def save(self):

        self.file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        temp_path = self.file.with_suffix(
            ".tmp"
        )

        with temp_path.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.data,
                file,
                indent=4,
                ensure_ascii=False
            )

            file.write("\n")

        temp_path.replace(
            self.file
        )

    # =========================================================
    # ALL
    # =========================================================

    def all(self):

        return dict(
            self.data
        )