import json
from pathlib import Path
from datetime import datetime

from app.core.logger import AppLogger



class ProjectMemory:


    def __init__(
        self,
        workspace
    ):


        self.workspace = Path(
            workspace
        )


        self.memory_path = (
            self.workspace
            /
            ".ai_memory"
        )


        self.memory_path.mkdir(
            exist_ok=True
        )


        self.project_file = (
            self.memory_path
            /
            "project.json"
        )


        self.files_file = (
            self.memory_path
            /
            "files.json"
        )


        self.architecture_file = (
            self.memory_path
            /
            "architecture.json"
        )


        self.logger = AppLogger()


        self.initialize()





    def initialize(
        self
    ):


        defaults = {


            self.project_file:
            {

                "name":
                self.workspace.name,

                "created":
                str(datetime.now()),

                "last_scan":
                None

            },


            self.files_file:
            {},



            self.architecture_file:
            {}

        }



        for path, data in defaults.items():


            if not path.exists():


                self.save_json(
                    path,
                    data
                )





        self.logger.info(
            "Project memory initialized."
        )








    def save_json(
        self,
        path,
        data
    ):


        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:


            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )







    def load_json(
        self,
        path
    ):


        if not path.exists():

            return {}


        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:


            return json.load(
                file
            )








    def update_project_info(
        self,
        data
    ):


        project = self.load_json(
            self.project_file
        )


        project.update(
            data
        )


        project["last_scan"] = str(
            datetime.now()
        )


        self.save_json(
            self.project_file,
            project
        )








    def add_file(
        self,
        path,
        info
    ):


        files = self.load_json(
            self.files_file
        )


        files[path] = info


        self.save_json(
            self.files_file,
            files
        )


        self.logger.info(
            f"Project memory updated: {path}"
        )








    def get_file(
        self,
        path
    ):


        files = self.load_json(
            self.files_file
        )


        return files.get(
            path
        )








    def get_all_files(
        self
    ):


        return self.load_json(
            self.files_file
        )








    def update_architecture(
        self,
        name,
        data
    ):


        architecture = self.load_json(
            self.architecture_file
        )


        architecture[name] = data


        self.save_json(
            self.architecture_file,
            architecture
        )








    def get_architecture(
        self
    ):


        return self.load_json(
            self.architecture_file
        )

    def search(
        self,
        query
    ):

        query = query.lower()

        results = {}

        files = self.get_all_files()


        for path, info in files.items():

            content = json.dumps(
                info,
                ensure_ascii=False
            ).lower()


            if query in path.lower() or query in content:

                results[path] = info


        return results

    def get_context(
        self,
        query,
        limit=5
    ):

        results = self.search(
            query
        )


        context = []


        for path, info in list(results.items())[:limit]:


            context.append(
                {
                    "file": path,
                    "info": info
                }
            )


        return context

    def remove_file(
        self,
        path
    ):

        files = self.get_all_files()


        if path in files:

            del files[path]


            self.save_json(
                self.files_file,
                files
            )


            self.logger.info(
                f"Project memory removed: {path}"
            )