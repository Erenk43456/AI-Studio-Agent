from agents.base_agent import BaseAgent
from app.core.logger import AppLogger



class CodeAgent(BaseAgent):


    def __init__(
        self,
        llm,
        registry,
        memory=None
    ):

        super().__init__(
            "Code Agent",
            memory
        )


        self.llm = llm

        self.registry = registry

        self.logger = AppLogger()





    def run(
        self,
        task
    ):


        self.logger.info(
            f"Code task: {task}"
        )


        prompt = f"""
You are a senior software engineer.

User request:

{task}


Your responsibilities:

- Analyze the problem.
- Decide which tools are needed.
- Explain the solution.
- Provide clean code when necessary.
- Avoid unnecessary assumptions.
"""


        response = self.llm.generate(
            prompt
        )


        return response