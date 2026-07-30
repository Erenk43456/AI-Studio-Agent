from app.core.logger import AppLogger



class MemoryTool:


    def __init__(
        self,
        memory
    ):


        self.memory = memory

        self.logger = AppLogger()





    def execute(
        self,
        plan
    ):


        if not plan:

            return "Empty memory request."



        tool_name = plan.get(
            "tool"
        )


        action = plan.get(
            "action"
        )



        self.logger.info(
            f"Memory request: {tool_name or action}"
        )





        #
        # SAVE
        #

        if (

            tool_name == "memory_save"

            or

            action == "save"

        ):


            return self.save_info(

                plan.get("key"),

                plan.get("value"),

                plan.get(
                    "category",
                    "general"
                )

            )





        #
        # GET
        #

        if (

            tool_name == "memory_get"

            or

            action == "get"

        ):


            return self.get_info(

                plan.get("key")

            )





        return "Invalid memory action."









    def save_info(
        self,
        key,
        value,
        category="general"
    ):


        if not key or value is None:


            return "Memory key or value missing."





        try:


            self.memory.save(

                key,

                value,

                category

            )



            self.logger.info(

                f"Memory saved successfully: {key}"

            )



            return f"Saved: {key}"





        except Exception as error:


            self.logger.error(

                f"Memory save error: {error}"

            )


            return f"Memory save error: {error}"









    def get_info(
        self,
        key
    ):


        if not key:


            return "Memory key missing."





        try:


            self.logger.info(

                f"Searching memory: {key}"

            )



            data = self.memory.get(

                key

            )



            self.logger.info(

                f"Memory result: {data}"

            )





            if data is None:


                return "Information not found."





            return str(data)





        except Exception as error:


            self.logger.error(

                f"Memory get error: {error}"

            )


            return f"Memory get error: {error}"