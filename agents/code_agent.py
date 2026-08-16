from agents.base_agent import BaseAgent

from app.core.logger import AppLogger

import json
import re





class CodeAgent(BaseAgent):


    def __init__(
        self,
        llm,
        registry,
        memory=None,
        workspace=None
    ):


        super().__init__(
            "Code Agent",
            memory
        )


        self.llm = llm

        self.registry = registry

        self.workspace = workspace

        self.logger = AppLogger()







    def execute(
        self,
        plan
    ):


        if isinstance(plan, dict):


            task = (

                plan.get("input")

                or

                plan.get("message")

                or

                plan.get("task")

                or

                ""

            )


        else:


            task = str(plan)




        return self.run(task)









    def run(
        self,
        task
    ):


        self.logger.info(

            f"Code task: {task}"

        )



        repository = self._analyze_repository()



        prompt = f"""

You are a senior autonomous software engineer.


You are modifying an existing Python AI agent framework.


Project:

AI-Studio-Agent



Repository analysis:

{repository}



User request:

{task}



Your responsibilities:


1. Understand the existing architecture.

2. Identify exactly which files must change.

3. Explain why those files are affected.

4. Design the implementation.

5. Produce a structured modification plan.



Rules:


- Respect existing architecture.

- Do not invent files.

- Do not rewrite unrelated code.

- Prefer minimal changes.

- Consider dependency injection.

- Consider existing agents, tools and memory systems.

- Think like a production software engineer.



Return JSON only.



Format:


{{
    "summary": "",

    "files": [

        {{
            "path": "",
            "purpose": "",
            "changes": [
                ""
            ]
        }}

    ],


    "implementation": [

        ""

    ],


    "risks": [

        ""

    ]
}}



"""



        response = self.llm.generate(

            prompt

        )


        implementation_plan = json.loads(
            self.clean_json(response)
        )


        writer = self.registry.get(
            "code_writer"
        )


        if writer is None:

            return implementation_plan



        write_result = writer.execute(
            implementation_plan
        )


        success = False

        if isinstance(write_result, dict):
            success = write_result.get("success", False)

        return {
            "success": success,
            "plan": implementation_plan,
            "write_result": write_result
        }



    def _analyze_repository(self):


        tool = self.registry.get(

            "repository_analyzer"

        )



        if tool is None:


            return (

                "Repository analyzer unavailable."

            )




        try:


            result = tool.execute({

                "action": "analyze"

            })


            return str(result)



        except Exception as error:


            self.logger.error(

                f"Repository analysis error: {error}"

            )


            return (

                "Repository analysis failed."

            )









    def clean_json(
        self,
        text
    ):


        if not text:


            return "{}"




        text = text.replace(

            "```json",

            ""

        )



        text = text.replace(

            "```",

            ""

        )



        match = re.search(

            r"\{.*\}",

            text,

            re.DOTALL

        )



        if match:


            return match.group()



        return text