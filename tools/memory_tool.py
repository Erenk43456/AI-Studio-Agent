from memory.memory import Memory



class MemoryTool:


    def __init__(
        self,
        memory=None
    ):

        self.memory = memory or Memory()



    def normalize(
        self,
        value
    ):

        value = value.lower().strip()


        replacements = {

            "hio4": "hoi4",
            "hıo4": "hoi4",
            "hoı4": "hoi4"

        }


        return replacements.get(
            value,
            value
        )



    def remember(self):

        return self.memory.recall()



    def save_info(
        self,
        key,
        value
    ):

        key = key.lower().strip()
        value = self.normalize(value)


        self.memory.save(
            key,
            value
        )


        return f"{key} saved successfully."



    def get_info(
        self,
        key
    ):

        return self.memory.get(
            key
        )