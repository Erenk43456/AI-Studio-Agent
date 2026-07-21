from tools.tool_registry import ToolRegistry
from tools.calculator import Calculator
from tools.file_tool import FileTool
from tools.memory_tool import MemoryTool

from agents.tool_agent import ToolAgent
from agents.planner_agent import PlannerAgent
from agents.chat_agent import ChatAgent

from memory.memory import Memory
from memory.conversation import ConversationMemory



def main():

    memory = Memory()

    registry = ToolRegistry()


    calculator = Calculator()
    file_tool = FileTool()
    memory_tool = MemoryTool(
        memory
    )


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


    tool_agent = ToolAgent(
        registry,
        memory
    )


    chat_agent = ChatAgent(
    memory
    )


    planner_agent = PlannerAgent(
        memory
    )


    conversation = ConversationMemory()



    print(
        "Kayıtlı araçlar:"
    )

    print(
        registry.list_tools()
    )


    request = input(
        "\nİstek:\n"
    ).strip()


    if not request:
        return



    history = conversation.get()


    if history:

        print(
            "\nSon konuşma:"
        )

        last = history[-1]

        print(
            last
        )



    plan = planner_agent.create_plan(
        request
    )


    print(
        "\nPlan:"
    )

    print(
        plan
    )


    if plan.get("tool") == "chat":

        result = chat_agent.respond(
            plan.get("message", request)
        )

    else:

        result = tool_agent.execute(
            plan
        )


    print(
        "\nSonuç:"
    )

    print(
        result
    )


    conversation.add(
        request,
        str(result)
    )



if __name__ == "__main__":
    main()