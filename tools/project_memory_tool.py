from app.core.logger import AppLogger



class ProjectMemoryTool:


    name = "project_memory"


    description = (
        "Provides access to persistent project architecture memory."
    )



    def __init__(
        self,
        project_memory
    ):


        self.project_memory = project_memory

        self.logger = AppLogger()





    def execute(
        self,
        plan
    ):


        if not isinstance(plan, dict):

            return {
                "success": False,
                "message": "Invalid project memory request."
            }



        action = plan.get(
            "action",
            "overview"
        )





        if action == "file":


            path = plan.get(
                "path"
            )


            result = self.project_memory.get_file(
                path
            )


            return {

                "success": True,

                "data": result

            }







        if action == "files":


            return {

                "success": True,

                "data":
                self.project_memory.get_all_files()

            }







        if action == "architecture":


            return {

                "success": True,

                "data":
                self.project_memory.get_architecture()

            }

        if action == "search":


            query = plan.get(
                "query",
                ""
            )


            result = self.project_memory.search(
                query
            )


            return {

                "success": True,

                "data": result

            }

        if action == "context":


            query = plan.get(
                "query",
                ""
            )


            limit = plan.get(
                "limit",
                5
            )


            result = self.project_memory.get_context(
                query,
                limit
            )


            return {

                "success": True,

                "data": result

            }


        if action == "overview":


            project = self.project_memory.load_json(
                self.project_memory.project_file
            )


            return {

                "success": True,

                "data": project

            }







        return {

            "success": False,

            "message":
            f"Unknown action: {action}"

        }