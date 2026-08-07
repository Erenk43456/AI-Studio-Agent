from app.core.containers.main_container import MainContainer
from app.core.orchestrators.main_orchestrator import MainOrchestrator


class Backend:

    @staticmethod
    def setup(window):


        window.container = MainContainer()



        #
        # Memory
        #

        window.memory = (
            window.container.memory.memory
        )


        window.chat_manager = (
            window.container.memory.chat_manager
        )



        #
        # Tools
        #

        window.registry = (
            window.container.tools.registry
        )



        #
        # Agents
        #

        window.decision_agent = (
            window.container.agents.decision
        )


        window.chat_agent = (
            window.container.chat.chat_agent
        )


        window.code_agent = (
            window.container.agents.code
        )



        #
        # Orchestrators
        #

        window.main_orchestrator = MainOrchestrator(
            window.container
        )


        window.chat_orchestrator = (
            window.container.chat.orchestrator
        )


        window.development_orchestrator = (
            window.container.development.orchestrator
        )



        #
        # Chat
        #

        chats = window.chat_manager.list_chats()



        if chats:

            chat = chats[0]

        else:

            chat = window.chat_manager.create_chat()



        window.current_chat = chat.id


        window.conversation = chat.conversation



        #
        # Conversation bağlantısı
        #

        window.chat_agent.conversation = (
            window.conversation
        )