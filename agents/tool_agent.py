from agents.base_agent import BaseAgent

from app.core.logger import AppLogger

import re





class ToolAgent(BaseAgent):


    def __init__(
        self,
        registry,
        memory=None,
        llm=None
    ):

        super().__init__(
            "Tool Agent",
            memory
        )


        self.registry = registry

        self.llm = llm

        self.logger = AppLogger()







    def execute_steps(
        self,
        plan
    ):


        if not plan:

            return "Invalid plan."



        steps = plan.get(
            "steps",
            []
        )



        if not steps:

            return self.execute(
                plan
            )






        results = []

        context = ""






        for index, step in enumerate(steps):


            tool_name = step.get(
                "tool"
            )


            action = step.get(
                "action"
            )



            self.logger.info(

                f"Executing step {index + 1}/{len(steps)}: {tool_name}"

            )







            #
            # Önceki işlem sonucunu aktar
            #

            if context:


                step["context"] = context




                #
                # Write işlemi
                #

                if action == "write":


                    content = step.get(
                        "content"
                    )



                    if not content:


                        if self.should_generate_code(
                            step
                        ):


                            step["content"] = self.generate_code_change(

                                step,

                                context

                            )


                        else:


                            step["content"] = self.prepare_write_content(

                                step.get(
                                    "input",
                                    ""
                                ),

                                context

                            )







            result = self.execute(
                step
            )





            #
            # Context güncelle
            #

            if isinstance(result, str):

                context = result


            else:

                context = str(result)






            results.append({

                "step": index + 1,

                "tool": tool_name,

                "action": action,

                "filename": step.get(
                    "filename"
                ),

                "input": step.get(
                    "input"
                ),

                "result": result

            })







        return results













    def should_generate_code(
        self,
        step
    ):


        text = (

            step.get(
                "input",
                ""

            ).lower()

        )



        keywords = [

            "ekle",

            "oluştur",

            "geliştir",

            "refactor",

            "değiştir",

            "entegre",

            "mimari",

            "sistem",

            "özellik",

            "fonksiyon",

            "class",

            "agent"

        ]



        return any(

            word in text

            for word in keywords

        )












    def generate_code_change(
        self,
        step,
        existing_content
    ):


        if not self.llm:


            return existing_content





        prompt = f"""

You are a senior Python software engineer.

Modify the existing file according to the user request.


Existing file:

{existing_content}



Requested change:

{step.get("input")}



Rules:

- Return ONLY complete file content.
- Do not explain.
- Do not use markdown.
- Preserve existing architecture.
- Do not remove existing features.
- Apply only required changes.
- Keep imports correct.


New file:

"""



        try:


            result = self.llm.generate(

                prompt

            )


            return result



        except Exception as error:


            self.logger.error(

                f"Code generation error: {error}"

            )


            return existing_content











    def prepare_write_content(
        self,
        instruction,
        existing_content
    ):


        if not existing_content:

            return ""



        lower_instruction = instruction.lower()






        #
        # Dosyanın başına yorum ekleme
        #

        if any(word in lower_instruction for word in [

            "en üstüne",

            "başına",

            "top"

        ]):



            if "#" in instruction:


                comment = instruction.split(

                    "#",

                    1

                )[1]




                comment = re.sub(

                    r"\b(ekle|yaz|koy|getir|başına|en üstüne)\b",

                    "",

                    comment,

                    flags=re.IGNORECASE

                )



                comment = comment.strip()



                return (

                    "# "

                    + comment

                    + "\n\n"

                    + existing_content

                )








        #
        # Varsayılan
        #

        return existing_content











    def execute(
        self,
        plan
    ):


        if not plan:

            return "Invalid plan."






        tool_name = plan.get(
            "tool"
        )



        self.logger.info(

            f"Executing tool: {tool_name}"

        )






        if not tool_name:

            return "Tool name missing."







        tool = self.registry.get(

            tool_name

        )







        #
        # Memory alias
        #

        if (

            tool is None

            and tool_name in [

                "memory_save",

                "memory_get"

            ]

        ):


            tool = self.registry.get(

                "memory"

            )







        if tool is None:


            self.logger.warning(

                f"Tool not found: {tool_name}"

            )


            return f"Tool not found: {tool_name}"









        try:


            if hasattr(

                tool,

                "execute"

            ):


                return tool.execute(

                    plan

                )







            return (

                f"Tool {tool_name} "

                "does not support execute method."

            )









        except Exception as error:


            self.logger.error(

                f"Tool execution error: {error}"

            )


            return f"Tool error: {error}"