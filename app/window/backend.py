from app.core.container import AIContainer





class Backend:


    @staticmethod
    def setup(window):


        window.container = AIContainer()



        window.memory = (

            window.container.memory

        )


        window.chat_manager = (

            window.container.chat_manager

        )


        window.registry = (

            window.container.registry

        )



        window.planner = (

            window.container.planner

        )


        window.chat_agent = (

            window.container.chat_agent

        )


        window.tool_agent = (

            window.container.tool_agent

        )


        window.orchestrator = (

            window.container.orchestrator

        )




        chats = window.chat_manager.list_chats()



        if chats:


            chat = chats[0]


        else:


            chat = window.chat_manager.create_chat()





        window.current_chat = chat.id


        window.conversation = chat.conversation