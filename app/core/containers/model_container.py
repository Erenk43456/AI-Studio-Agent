from models.llm_provider import LLMProvider
from models.model_registry import ModelRegistry


class ModelContainer:

    def __init__(
        self,
        core
    ):

        self.registry = ModelRegistry()

        self.chat_llm = LLMProvider(
            self.registry.get("chat"),
            agent_name="chat"
        )

        self.code_llm = LLMProvider(
            self.registry.get("code"),
            agent_name="code"
        )

        self.planner_llm = LLMProvider(
            self.registry.get("planner"),
            agent_name="planner"
        )

        self.decision_llm = LLMProvider(
            self.registry.get("decision"),
            agent_name="decision"
        )

    def set_cancel_event(
        self,
        cancel_event
    ):

        for provider in (
            self.chat_llm,
            self.code_llm,
            self.planner_llm,
            self.decision_llm,
        ):

            provider.set_cancel_event(
                cancel_event
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
            config,
            agent_name=slot
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