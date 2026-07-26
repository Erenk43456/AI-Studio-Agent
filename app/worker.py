from PySide6.QtCore import QThread, Signal



class AIWorker(QThread):

    finished = Signal(str)



    def __init__(
        self,
        planner,
        tool_agent,
        chat_agent,
        conversation,
        message
    ):

        super().__init__()


        self.planner = planner

        self.tool_agent = tool_agent

        self.chat_agent = chat_agent

        self.conversation = conversation

        self.message = message





    def run(self):


        try:


            plan = self.planner.create_plan(
                self.message
            )


            print("\n===== GENERATED PLAN =====")
            print(plan)
            print("==========================\n")



            steps = plan.get(
                "steps",
                []
            )



            # Multi-step plan yoksa eski sistemi destekle

            if not steps:


                if plan.get("tool") == "chat":


                    result = self.chat_agent.chat(
                        self.message
                    )


                else:


                    result = self.tool_agent.execute(
                        plan
                    )



            else:



                # Tek adımlı chat ise ChatAgent kullan

                if (
                    len(steps) == 1
                    and steps[0].get("tool") == "chat"
                ):


                    result = self.chat_agent.chat(

                        self.message

                    )



                else:


                    result = self.tool_agent.execute_steps(

                        plan

                    )





            self.conversation.add(

                self.message,

                str(result)

            )



            self.finished.emit(

                str(result)

            )




        except Exception as error:


            self.finished.emit(

                f"AI Error: {error}"

            )







    def stop(self):


        if self.isRunning():


            self.quit()

            self.wait()