import json
from pathlib import Path

from models.model_config import ModelConfig


class ModelRegistry:

    SLOTS = (
        "chat",
        "code",
        "planner",
        "decision"
    )

    def __init__(
        self,
        config_dir="config"
    ):

        self.config_dir = Path(
            config_dir
        )

        self.defaults_path = (
            self.config_dir /
            "defaults.json"
        )

        self.user_path = (
            self.config_dir /
            "user.json"
        )

        self.models = {}

        self.load()

    # =========================================================
    # LOAD
    # =========================================================

    def load(self):

        defaults = self._read_json(
            self.defaults_path
        )

        user = self._read_json(
            self.user_path
        )

        default_models = defaults.get(
            "models",
            {}
        )

        user_models = user.get(
            "models",
            {}
        )

        self.models.clear()

        for slot in self.SLOTS:

            data = dict(
                default_models.get(
                    slot,
                    {}
                )
            )

            data.update(
                user_models.get(
                    slot,
                    {}
                )
            )

            if not data:
                continue

            self.models[slot] = ModelConfig(
                name=slot,
                provider=data.get(
                    "provider",
                    "local"
                ),
                model=data.get(
                    "model",
                    ""
                ),
                endpoint=data.get(
                    "endpoint",
                    ""
                ),
                api_key=data.get(
                    "api_key",
                    ""
                ),
                temperature=data.get(
                    "temperature",
                    0.3
                ),
                max_tokens=data.get(
                    "max_tokens",
                    2048
                ),
                timeout=data.get(
                    "timeout",
                    120
                ),
                enabled=data.get(
                    "enabled",
                    True
                )
            )

    # =========================================================
    # GET
    # =========================================================

    def get(
        self,
        slot
    ):

        return self.models.get(
            slot
        )

    # =========================================================
    # ALL
    # =========================================================

    def all(self):

        return dict(
            self.models
        )

    # =========================================================
    # UPDATE MODEL
    # =========================================================

    def update(
        self,
        slot,
        **values
    ):

        if slot not in self.SLOTS:

            raise ValueError(
                f"Unknown model slot: {slot}"
            )

        current = self.models.get(
            slot
        )

        if current is None:

            current = ModelConfig(
                name=slot,
                provider="local",
                model="",
                endpoint="",
                api_key="",
                temperature=0.3,
                max_tokens=2048,
                timeout=120,
                enabled=True
            )

        data = current.to_dict()

        data.update(
            values
        )

        data["name"] = slot

        self.models[slot] = ModelConfig(
            name=slot,
            provider=data.get(
                "provider",
                "local"
            ),
            model=data.get(
                "model",
                ""
            ),
            endpoint=data.get(
                "endpoint",
                ""
            ),
            api_key=data.get(
                "api_key",
                ""
            ),
            temperature=data.get(
                "temperature",
                0.3
            ),
            max_tokens=data.get(
                "max_tokens",
                2048
            ),
            timeout=data.get(
                "timeout",
                120
            ),
            enabled=data.get(
                "enabled",
                True
            )
        )

        self.save()

    # =========================================================
    # SAVE
    # =========================================================

    def save(self):

        self.config_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        existing = self._read_json(
            self.user_path
        )

        if not isinstance(
            existing,
            dict
        ):

            existing = {}

        models = existing.get(
            "models",
            {}
        )

        if not isinstance(
            models,
            dict
        ):

            models = {}

        for slot, model in self.models.items():

            models[slot] = model.to_dict()

        existing["models"] = models

        temp_path = self.user_path.with_suffix(
            ".tmp"
        )

        with temp_path.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                existing,
                file,
                indent=4,
                ensure_ascii=False
            )

            file.write("\n")

        temp_path.replace(
            self.user_path
        )

    # =========================================================
    # RESET SLOT
    # =========================================================

    def reset(
        self,
        slot
    ):

        if slot not in self.SLOTS:

            raise ValueError(
                f"Unknown model slot: {slot}"
            )

        defaults = self._read_json(
            self.defaults_path
        )

        default_data = defaults.get(
            "models",
            {}
        ).get(
            slot,
            {}
        )

        if not default_data:

            return False

        self.models[slot] = ModelConfig(
            name=slot,
            provider=default_data.get(
                "provider",
                "local"
            ),
            model=default_data.get(
                "model",
                ""
            ),
            endpoint=default_data.get(
                "endpoint",
                ""
            ),
            api_key=default_data.get(
                "api_key",
                ""
            ),
            temperature=default_data.get(
                "temperature",
                0.3
            ),
            max_tokens=default_data.get(
                "max_tokens",
                2048
            ),
            timeout=default_data.get(
                "timeout",
                120
            ),
            enabled=default_data.get(
                "enabled",
                True
            )
        )

        self.save()

        return True

    # =========================================================
    # JSON READER
    # =========================================================

    @staticmethod
    def _read_json(
        path
    ):

        if not path.is_file():

            return {}

        try:

            with path.open(
                "r",
                encoding="utf-8-sig"
            ) as file:

                data = json.load(
                    file
                )

            return (
                data
                if isinstance(
                    data,
                    dict
                )
                else {}
            )

        except Exception:

            return {}