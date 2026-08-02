from app.core.logger import AppLogger



class Orchestrator:


    def __init__(
        self,
        planner,
        agents
    ):

        self.planner = planner

        self.agents = agents

        self.logger = AppLogger()






    def run(
        self,
        message,
        conversation=None
    ):


        self.logger.info(
            f"Processing request: {message}"
        )



        plan = self.planner.create_plan(
            message
        )



        print("\n===== GENERATED PLAN =====")
        print(plan)
        print("==========================\n")



        if not plan:

            return "Planner failed to create a plan."





        steps = plan.get(
            "steps",
            []
        )


        tool_name = plan.get(
            "tool"
        )






        #
        # Tek işlem
        #

        if not steps:


            if tool_name == "code":


                agent = self.agents.get(
                    "code"
                )


                if not agent:

                    return "Code agent not available."



                result = agent.run(
                    message
                )



                return self.process_tool_result(
                    result,
                    conversation
                )







            if tool_name == "chat":


                agent = self.agents.get(
                    "chat"
                )


                if not agent:

                    return "Chat agent not available."



                if conversation is not None:

                    agent.conversation = conversation



                return agent.chat(
                    message
                )








            agent = self.agents.get(
                "tool"
            )


            if not agent:

                return "Tool agent not available."



            result = agent.execute(
                plan
            )



            return self.process_tool_result(
                result,
                conversation
            )









        #
        # Tek adımlı chat
        #

        if (

            len(steps) == 1

            and steps[0].get("tool") == "chat"

        ):


            agent = self.agents.get(
                "chat"
            )


            if not agent:

                return "Chat agent not available."



            if conversation is not None:

                agent.conversation = conversation



            return agent.chat(
                message
            )









        #
        # Tek adımlı code
        #

        if (

            len(steps) == 1

            and steps[0].get("tool") == "code"

        ):


            agent = self.agents.get(
                "code"
            )


            if not agent:

                return "Code agent not available."



            result = agent.run(

                steps[0].get(

                    "input",

                    message

                )

            )



            return self.process_tool_result(
                result,
                conversation
            )









        #
        # Multi step tool workflow
        #

        agent = self.agents.get(
            "tool"
        )


        if not agent:

            return "Tool agent not available."



        result = agent.execute_steps(
            plan
        )



        return self.process_tool_result(
            result,
            conversation
        )











    def process_tool_result(
        self,
        result,
        conversation=None
    ):



        #
        # Multi step sonuçları
        #

        if isinstance(result, list):


            messages = []


            has_read_content = False



            for item in result:


                if not isinstance(item, dict):

                    continue



                tool_result = item.get(
                    "result",
                    ""
                )



                if not isinstance(tool_result, str):

                    continue






                #
                # Read işlemi
                #

                if item.get("action") == "read":


                    has_read_content = True


                    messages.append(
                        tool_result
                    )





                #
                # Update işlemi
                #

                elif tool_result.startswith(
                    "File updated:"
                ):


                    messages.append(

                        "Dosya başarıyla güncellendi."

                    )





                #
                # Create işlemi
                #

                elif tool_result.startswith(
                    "File created:"
                ):


                    messages.append(

                        "Dosya başarıyla oluşturuldu."

                    )





                #
                # Diğer sonuçlar
                #

                else:


                    messages.append(
                        tool_result
                    )






            if messages:


                #
                # Read + Write birlikteyse
                # sadece işlem sonucunu göster
                #

                if has_read_content and len(messages) > 1:


                    return messages[-1]



                return "\n\n".join(
                    messages
                )



            return "İşlem tamamlandı."









        #
        # String sonuçlar
        #

        if isinstance(result, str):



            if result.startswith(
                "File updated:"
            ):


                return "Dosya başarıyla güncellendi."




            if result.startswith(
                "File created:"
            ):


                return "Dosya başarıyla oluşturuldu."




            if result.startswith(
                "File not found:"
            ):

                return result




            if result.startswith(
                "File error:"
            ):

                return result




            if result.startswith(
                "Filename missing:"
            ):

                return result




            if result.startswith(
                "Tool not found:"
            ):

                return result




            if result.startswith(
                "Tool error:"
            ):

                return result






            #
            # Read sonucu
            #

            if len(result) > 50:

                return result







        #
        # Chat açıklaması gereken durumlar
        #

        chat_agent = self.agents.get(
            "chat"
        )



        if not chat_agent:

            return result





        if conversation is not None:

            chat_agent.conversation = conversation







        prompt = f"""

Bir araç çalıştırıldı ve sonuç döndü.

Bu sonucu kullanıcı için anlaşılır bir cevap haline getir.

Kurallar:

- Ham tool çıktısını tekrar yazma.
- Teknik ama okunabilir açıkla.
- Gereksiz detay verme.
- Kullanıcının istediği amaca göre yorumla.
- Türkçe cevap ver.


Tool sonucu:

{result}


Açıklama:

"""



        return chat_agent.respond(
            prompt
        )