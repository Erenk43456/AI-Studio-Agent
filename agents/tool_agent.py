from agents.base_agent import BaseAgent
from app.core.logger import AppLogger



class ToolAgent(BaseAgent):


    def __init__(
        self,
        registry,
        memory=None,
        chat_agent=None
    ):

        super().__init__(
            "Tool Agent",
            memory
        )


        self.registry = registry

        self.chat_agent = chat_agent

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


            self.logger.info(

                f"Executing step {index + 1}/{len(steps)}: {tool_name}"

            )





            if context:

                step["context"] = context





            result = self.execute(
                step
            )



            context = str(result)



            results.append({

                "step": index + 1,

                "tool": tool_name,

                "result": result

            })





        return results











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
        # Memory alias desteği
        #

        if tool is None and tool_name in [

            "memory_save",

            "memory_get"

        ]:


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


                result = tool.execute(

                    plan

                )





                #
                # Tool sonucunu doğal cevaba çevir
                #

                if self.chat_agent and tool_name != "chat":


                    user_message = plan.get(

                        "user_message",

                        ""

                    )



                    return self.chat_agent.respond(

                        f"""

Kullanıcı mesajı:

{user_message}



Araç sonucu:

{result}



Bu sonucu kullanarak kullanıcıya doğal,

kısa ve anlaşılır Türkçe cevap ver.

"""

                    )





                return result





            return f"Tool {tool_name} does not support execute()."







        except Exception as error:


            self.logger.error(

                f"Tool execution error: {error}"

            )


            return f"Tool error: {error}"