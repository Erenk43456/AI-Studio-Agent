from app.core.logger import AppLogger


class MemoryTool:

    name = "memory"

    description = (
        "Provides access to persistent user memory. "
        "Use action 'get' to retrieve stored information "
        "and action 'save' to store new information."
    )

    def __init__(self, memory):

        self.memory = memory
        self.logger = AppLogger()

    def execute(self, plan):

        if not isinstance(plan, dict):

            return {
                "success": False,
                "error": "Invalid memory request."
            }

        action = plan.get("action")

        self.logger.info(
            f"Memory request: {action}"
        )

        # SAVE
        if action == "save":

            return self.save_info(
                plan.get("key"),
                plan.get("value"),
                plan.get(
                    "category",
                    "general"
                )
            )

        # GET
        if action == "get":

            return self.get_info(
                plan.get("key")
            )

        return {
            "success": False,
            "error": f"Unknown memory action: {action}"
        }

    def save_info(
        self,
        key,
        value,
        category="general"
    ):

        if not key or value is None:

            return {
                "success": False,
                "error": "Memory key or value missing."
            }

        try:

            self.memory.save(
                key,
                value,
                category
            )

            self.logger.info(
                f"Memory saved successfully: {key}"
            )

            return {
                "success": True,
                "action": "save",
                "key": key,
                "value": value,
                "message": f"Saved memory: {key}"
            }

        except Exception as error:

            self.logger.error(
                f"Memory save error: {error}"
            )

            return {
                "success": False,
                "action": "save",
                "error": str(error)
            }

    def get_info(
        self,
        key
    ):

        if not key:

            return {
                "success": False,
                "error": "Memory key missing."
            }

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

                return {
                    "success": False,
                    "action": "get",
                    "key": key,
                    "error": "Information not found."
                }

            return {
                "success": True,
                "action": "get",
                "key": key,
                "value": data,
                "message": str(data)
            }

        except Exception as error:

            self.logger.error(
                f"Memory get error: {error}"
            )

            return {
                "success": False,
                "action": "get",
                "error": str(error)
            }