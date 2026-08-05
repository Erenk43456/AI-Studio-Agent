from models.llm_provider import LLMProvider


class ModelContainer:


    def __init__(
        self,
        core
    ):


        self.chat_llm = LLMProvider(
            core.config,
            "chat_model"
        )


        self.code_llm = LLMProvider(
            core.config,
            "code_model"
        )


        self.planner_llm = LLMProvider(
            core.config,
            "planner_model"
        )


        self.decision_llm = LLMProvider(
            core.config,
            "decision_model"
        )