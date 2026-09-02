from agents.base_agent import BaseAgent
from agents.contracts.memory import MemoryContract
from agents.contract_agent import ContractAgent
from app.core.logger import AppLogger


class MemoryAgent(BaseAgent):

    def __init__(
        self,
        memory,
        contract_agent=None,
    ):

        super().__init__(
            "Memory Agent",
            memory
        )

        self.memory = memory
        self.contract_agent = contract_agent or ContractAgent()
        self.logger = AppLogger()

    def save(
        self,
        data
    ):
        contract = self._to_contract("save", data)
        self.logger.info(
            f"Saving memory contract: key={contract.key}, category={contract.category}"
        )

        self.memory.save(
            contract.key,
            contract.value,
            contract.category
        )

        if contract.key == "user_name" and contract.value:
            return f"Tamam, adını {contract.value} olarak hatırlayacağım."

        return "Bilgi hafızaya kaydedildi."

    def get(
        self,
        data
    ):
        contract = self._to_contract("get", data)
        self.logger.info(
            f"Getting memory contract: key={contract.key}"
        )

        try:
            val = self.memory.get(contract.key)
            if contract.key == "user_name":
                if val:
                    return f"Senin adın {val}."
                return "İsim bilgisi kayıtlı değil."

            if val:
                return str(val)

            return "Hatırlanan bilgi bulunamadı."

        except Exception as error:
            self.logger.error(f"Memory get error: {error}")
            return f"Memory error: {error}"

    def _to_contract(self, default_action, data) -> MemoryContract:
        if isinstance(data, MemoryContract):
            return data

        if isinstance(data, dict):
            return self.contract_agent.to_memory_contract(data, default_action=default_action)

        text = str(data or "").strip()
        lower = text.lower()

        if default_action == "save":
            name = self.extract_name(text)
            if name:
                return MemoryContract(
                    action="save",
                    key="user_name",
                    value=name,
                    category="personal"
                )
            return MemoryContract(
                action="save",
                key="last_memory",
                value=text,
                category="general"
            )
        else:
            if any(p in lower for p in ["adım ne", "ismim ne", "ben kimim", "adımı biliyor musun"]):
                return MemoryContract(
                    action="get",
                    key="user_name",
                    category="personal"
                )
            return MemoryContract(
                action="get",
                key="last_memory",
                category="general"
            )

    def extract_name(
        self,
        message
    ):
        text = message.strip()
        patterns = [
            "benim adım",
            "adım",
            "ismim"
        ]
        lower = text.lower()
        for pattern in patterns:
            if pattern in lower:
                index = lower.find(pattern)
                name = text[index + len(pattern):].strip()
                if name:
                    return name.capitalize()
        return None