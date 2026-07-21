from tools.tool_registry import ToolRegistry
from tools.calculator import Calculator
from tools.file_tool import FileTool
from tools.memory_tool import MemoryTool

from agents.tool_agent import ToolAgent
from agents.planner_agent import PlannerAgent

from memory.memory import Memory
from memory.conversation import ConversationMemory



def main():

    # Ortak hafıza
    memory = Memory()


    # Tool sistemi
    registry = ToolRegistry()


    calculator = Calculator()
    file_tool = FileTool()
    memory_tool = MemoryTool(memory)


    registry.register(
        "calculator",
        calculator
    )

    registry.register(
        "file",
        file_tool
    )

    registry.register(
        "memory",
        memory_tool
    )


    # Agentlar

    tool_agent = ToolAgent(
        registry
    )

    planner_agent = PlannerAgent(
        memory
    )


    conversation = ConversationMemory()



    print("Kayıtlı araçlar:")
    print(
        registry.list_tools()
    )


    request = input(
        "\nİstek:\n"
    ).strip()


    if not request:
        print(
            "Boş istek gönderilemez."
        )
        return



    try:

        history = conversation.get()


        if history:

            print(
                "\nÖnceki konuşmalar:"
            )

            print(history)



        plan = planner_agent.create_plan(
            request
        )


        print(
            "\nPlan:"
        )

        print(plan)



        result = tool_agent.execute(
            plan
        )


        print(
            "\nSonuç:"
        )

        print(result)



        conversation.add(
            request,
            str(result)
        )


    except Exception as error:

        print(
            "\nHata oluştu:"
        )

        print(error)




if __name__ == "__main__":
    main()