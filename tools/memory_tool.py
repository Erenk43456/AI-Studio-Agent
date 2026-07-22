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
        value,
        category="general"
    ):


        key = key.lower().strip()


        value = self.normalize(
            value
        )



        self.memory.save(
            key,
            value,
            category
        )



        return (
            f"{key} saved successfully."
        )





    def get_info(
        self,
        key
    ):


        return self.memory.get(
            key
        )





    def get_details(
        self,
        key
    ):


        return self.memory.get_full(
            key
        )





    def delete_info(
        self,
        key
    ):


        result = self.memory.delete(
            key
        )


        if result:

            return (
                f"{key} deleted successfully."
            )


        return (
            f"{key} not found."
        )