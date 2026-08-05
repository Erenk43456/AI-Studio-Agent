class DevelopmentContainer:


    def __init__(
        self,
        main
    ):


        self.project_memory = (
            main.memory.project_memory
        )


        self.code_llm = (
            main.models.code_llm
        )


        self.planner_llm = (
            main.models.planner_llm
        )