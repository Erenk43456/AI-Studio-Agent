from memory.memory import Memory


class BaseAgent:
    def __init__(self, name):
        self.name = name
        self.memory = Memory()

    def think(self, task):
        self.memory.save(task)
        return f"{self.name} düşünüyor: {task}"

    def remember(self):
        return self.memory.recall()

    def act(self, task):
        self.memory.save(task)
        return f"{self.name} çalışıyor: {task}"