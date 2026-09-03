from app.core.logger import AppLogger


class LLMRouter:

    def __init__(
        self,
        planner_llm,
        chat_llm
    ):

        self.planner_llm = planner_llm

        self.chat_llm = chat_llm

        self.logger = AppLogger()


    def generate(
        self,
        prompt,
        mode="chat",
        max_tokens=None,
        temperature=None,
        timeout=None
    ):

        llm = self.get_for_mode(
            mode
        )

        kwargs = {}

        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        if temperature is not None:
            kwargs["temperature"] = temperature

        if timeout is not None:
            kwargs["timeout"] = timeout

        return llm.generate(
            prompt,
            **kwargs
        )


    def get_for_mode(
        self,
        mode
    ):

        if mode == "planner":

            self.logger.info(
                "Router selected: planner LLM"
            )

            return self.planner_llm


        self.logger.info(
            "Router selected: chat LLM"
        )

        return self.chat_llm


    def get_models(
        self
    ):

        models = []


        if hasattr(
            self.planner_llm,
            "get_models"
        ):

            models.extend(
                self.planner_llm.get_models()
            )


        if hasattr(
            self.chat_llm,
            "get_models"
        ):

            models.extend(
                self.chat_llm.get_models()
            )


        return list(
            set(models)
        )


    def get_current_model(
        self
    ):

        if hasattr(
            self.chat_llm,
            "get_current_model"
        ):

            return self.chat_llm.get_current_model()


        return None


    def has_model(
        self,
        model_name: str
    ) -> bool:

        if not model_name:
            return False

        planner_has_model = getattr(
            self.planner_llm,
            "has_model",
            None
        )

        if callable(planner_has_model) and planner_has_model(model_name):
            return True

        chat_has_model = getattr(
            self.chat_llm,
            "has_model",
            None
        )

        if callable(chat_has_model) and chat_has_model(model_name):
            return True

        return False

    def check_connection(
        self
    ):

        chat_status = False

        planner_status = False


        if hasattr(
            self.chat_llm,
            "check_connection"
        ):

            chat_status = (
                self.chat_llm.check_connection()
            )


        if hasattr(
            self.planner_llm,
            "check_connection"
        ):

            planner_status = (
                self.planner_llm.check_connection()
            )


        return (
            chat_status
            or
            planner_status
        )


    def get_for_task(
        self,
        task,
        mode="auto"
    ):

        if mode == "planner":

            return self.planner_llm


        if mode == "chat":

            return self.chat_llm


        task_lower = task.lower()


        coding_keywords = [

            "kod",
            "code",
            "dosya",
            ".py",
            "hata",
            "bug",
            "düzelt",
            "geliştir",
            "ekle",
            "refactor",
            "implement",
            "agent",
            "framework",
            "proje"

        ]


        for word in coding_keywords:

            if word in task_lower:

                self.logger.info(
                    "Router selected: planner LLM"
                )

                return self.planner_llm


        self.logger.info(
            "Router selected: chat LLM"
        )

        return self.chat_llm