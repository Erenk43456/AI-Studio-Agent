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

            self.models[slot] = (
                ModelConfig(
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
            )


    def get(
        self,
        slot
    ):

        return self.models.get(
            slot
        )


    def all(self):

        return dict(
            self.models
        )


    @staticmethod
    def _read_json(
        path
    ):

        if not path.is_file():

            return {}

        try:

            with path.open(
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(
                    file
                )

            return (
                data
                if isinstance(data, dict)
                else {}
            )

        except Exception:

            return {}
