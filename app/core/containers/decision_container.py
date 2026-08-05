from agents.decision_agent import DecisionAgent


class DecisionContainer:


    def __init__(self, main):


        self.agent = DecisionAgent(

            main.models.decision_llm,

            main.memory.memory,

            main.tools.registry

        )