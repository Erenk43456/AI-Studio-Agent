from agents.base_agent import BaseAgent

from app.core.logger import AppLogger




class ImprovementAgent(BaseAgent):


    def __init__(
        self,
        project_memory,
        repository_analyzer,
        memory=None
    ):

        super().__init__(
            "Improvement Agent",
            memory
        )


        self.project_memory = project_memory

        self.repository_analyzer = repository_analyzer

        self.logger = AppLogger()






    def analyze(
        self
    ):


        self.logger.info(
            "Starting self improvement analysis."
        )



        report = {

            "issues": [],

            "suggestions": [],

            "architecture": None

        }




        #
        # Project Memory
        #

        try:


            project_data = self.project_memory.load()


            report["architecture"] = project_data



        except Exception as error:


            self.logger.error(

                f"Project memory read error: {error}"

            )



        #
        # Repository Analysis
        #

        try:


            analysis = self.repository_analyzer.execute(

                {

                    "action": "analyze"

                }

            )



            if isinstance(
                analysis,
                dict
            ):


                report["issues"].extend(

                    analysis.get(
                        "issues",
                        []
                    )

                )



        except Exception as error:


            self.logger.error(

                f"Repository analysis error: {error}"

            )



        #
        # Basic improvement checks
        #

        self.check_architecture(
            report
        )


        self.check_missing_systems(
            report
        )



        self.logger.info(
            "Improvement analysis completed."
        )


        return report







    def check_architecture(
        self,
        report
    ):


        architecture = report.get(
            "architecture"
        )



        if not architecture:


            report["issues"].append(

                "Project architecture memory is empty."

            )


            report["suggestions"].append(

                "Run repository analysis to build project knowledge."

            )









    def check_missing_systems(
        self,
        report
    ):


        suggestions = report["suggestions"]


        issues = report["issues"]



        systems = str(

            report.get(
                "architecture",
                {}

            )

        ).lower()





        if "test" not in systems:


            issues.append(

                "No test automation system detected."

            )


            suggestions.append(

                "Add TestAgent and automated validation."

            )





        if "rollback" not in systems:


            issues.append(

                "No rollback mechanism detected."

            )


            suggestions.append(

                "Add change history and rollback support."

            )








    def run(
        self,
        request
    ):


        return self.analyze()