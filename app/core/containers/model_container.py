from models.llm_provider import LLMProvider
from models.model_registry import ModelRegistry


class ModelContainer:

    def __init__(
        self,
        core
    ):

        self.registry = ModelRegistry()

        self.chat_llm = LLMProvider(
            self.registry.get("chat")
        )

        self.code_llm = LLMProvider(
            self.registry.get("code")
        )

        self.planner_llm = LLMProvider(
            self.registry.get("planner")
        )

        self.decision_llm = LLMProvider(
            self.registry.get("decision")
        )

    # =========================================================
    # RELOAD MODEL
    # =========================================================

    def reload_model(
        self,
        slot
    ):

        config = self.registry.get(
            slot
        )

        if config is None:

            raise ValueError(
                f"Model configuration missing: {slot}"
            )

        provider = LLMProvider(
            config
        )

        if slot == "chat":

            self.chat_llm = provider

        elif slot == "code":

            self.code_llm = provider

        elif slot == "planner":

            self.planner_llm = provider

        elif slot == "decision":

            self.decision_llm = provider

        else:

            raise ValueError(
                f"Unknown model slot: {slot}"
            )

        return provider