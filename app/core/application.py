from app.core.containers.core_container import CoreContainer

from app.core.containers.decision_container import DecisionContainer
from app.core.containers.memory_container import MemoryContainer
from app.core.containers.development_container import DevelopmentContainer


from app.core.orchestrators.master_orchestrator import MasterOrchestrator



class Application:


    def __init__(self):


        self.core = CoreContainer()


        self.decision = DecisionContainer(
            self.core
        )


        self.memory = MemoryContainer(
            self.core
        )


        self.development = DevelopmentContainer(
            self.core
        )



        self.master = MasterOrchestrator(

            self.decision.agent,

            {

                "memory":
                self.memory.orchestrator,


                "development":
                self.development.orchestrator

            }

        )