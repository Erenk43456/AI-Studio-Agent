from memory.memory import Memory


class MemoryTool:
    def __init__(self):
        self.memory = Memory()


    def remember(self):
        return self.memory.recall()


    def save_info(self, key, value):
        self.memory.save(key, value)
        return f"{key} kaydedildi."


    def get_info(self, key):
        return self.memory.get(key)