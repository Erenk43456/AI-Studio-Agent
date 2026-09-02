from app.core.logger import AppLogger
from agents.contract_agent import ContractAgent
from agents.contracts.memory import MemoryContract


class MemoryOrchestrator:

    def __init__(
        self,
        agents,
        contract_agent=None
    ):
        self.memory_agent = (
            agents.memory
        )
        self.contract_agent = contract_agent or ContractAgent()
        self.logger = AppLogger()

    def run(
        self,
        message,
        decision=None,
        conversation=None
    ):
        self.logger.info(
            f"Memory request: {message}"
        )

        if not decision:
            return (
                "Memory decision missing."
            )

        if hasattr(decision, "action"):
            action = decision.action
            metadata = getattr(decision, "metadata", {}) or {}
        elif isinstance(decision, dict):
            action = decision.get("action")
            metadata = decision.get("metadata", {}) or {}
        else:
            action = None
            metadata = {}

        if action == "save":
            key = metadata.get("key")
            value = metadata.get("value")
            category = metadata.get("category", "general")

            if key and value:
                contract = MemoryContract(
                    action="save",
                    key=key,
                    value=value,
                    category=category
                )
            elif hasattr(self.memory_agent, "_to_contract"):
                contract = self.memory_agent._to_contract("save", message)
            else:
                contract = message

            return self.memory_agent.save(
                contract
            )

        if action == "get":
            key = metadata.get("key")
            if key:
                contract = MemoryContract(
                    action="get",
                    key=key,
                    category=metadata.get("category", "general")
                )
            elif hasattr(self.memory_agent, "_to_contract"):
                contract = self.memory_agent._to_contract("get", message)
            else:
                contract = message

            return self.memory_agent.get(
                contract
            )

        return (
            "Unknown memory action."
        )