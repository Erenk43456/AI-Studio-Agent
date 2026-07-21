from memory.memory import Memory


class BaseAgent:

    def __init__(self, name, memory=None):
        self.name = name

        # Dışarıdan memory verilirse onu kullanır.
        # Verilmezse kendi memory'sini oluşturur.
        self.memory = memory if memory else Memory()


    def think(self, task):
        """
        Agent düşünme aşaması.
        """

        self.memory.save(
            "last_thought",
            task
        )

        return f"{self.name} düşünüyor: {task}"


    def remember(self):
        """
        Hafızayı getirir.
        """

        return self.memory.recall()


    def act(self, task):
        """
        Agent çalışma aşaması.
        """

        self.memory.save(
            "last_action",
            task
        )

        return f"{self.name} çalışıyor: {task}"