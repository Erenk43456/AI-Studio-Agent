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