from PySide6.QtCore import QThread, Signal

from models.llm_provider import LLMProvider
from models.model_registry import ModelRegistry


class ModelStatusWorker(QThread):

    result = Signal(
        str,
        str,
        bool
    )

    finished_all = Signal()

    def __init__(
        self,
        registry,
        parent=None
    ):

        super().__init__(parent)

        self.registry = registry

    def run(self):

        for slot in ModelRegistry.SLOTS:

            config = self.registry.get(
                slot
            )

            if config is None:

                self.result.emit(
                    slot,
                    "Not Configured",
                    False
                )

                continue

            if not config.enabled:

                self.result.emit(
                    slot,
                    "Disabled",
                    False
                )

                continue

            if not config.model:

                self.result.emit(
                    slot,
                    "Not Configured",
                    False
                )

                continue

            try:

                provider = LLMProvider(
                    config
                )

                connected = provider.check_connection()

                if connected:

                    provider_name = (
                        "API"
                        if config.provider == "api"
                        else "Local"
                    )

                    self.result.emit(
                        slot,
                        f"Connected · {provider_name}",
                        True
                    )

                else:

                    self.result.emit(
                        slot,
                        "Connection Failed",
                        False
                    )

            except Exception:

                self.result.emit(
                    slot,
                    "Connection Failed",
                    False
                )

        self.finished_all.emit()