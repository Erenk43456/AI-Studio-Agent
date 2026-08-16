from tools.tool_registry import ToolRegistry
from tools.calculator import Calculator
from tools.file_tool import FileTool
from tools.memory_tool import MemoryTool
from tools.repository_analyzer import RepositoryAnalyzerTool

from agents.tool_agent import ToolAgent
from agents.planner_agent import PlannerAgent
from agents.chat_agent import ChatAgent

from memory.memory import Memory
from memory.conversation import ConversationMemory

from app.core.containers.core_container import CoreContainer
from app.core.containers.model_container import ModelContainer


def main():

    #
    # CORE
    #

    core = CoreContainer()

    #
    # MODELS
    #

    models = ModelContainer(
        core
    )

    #
    # MEMORY
    #

    memory = Memory()

    #
    # TOOLS
    #

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

    registry.register(
        "repository_analyzer",
        RepositoryAnalyzerTool()
    )

    #
    # TOOL AGENT
    #

    tool_agent = ToolAgent(
        registry,
        memory
    )

    #
    # CONVERSATION
    #

    conversation = ConversationMemory()

    #
    # CHAT AGENT
    #

    chat_agent = ChatAgent(
        models.chat_llm,
        memory,
        conversation=conversation
    )

    #
    # PLANNER AGENT
    #

    planner_agent = PlannerAgent(
        models.planner_llm,
        memory
    )

    #
    # DEBUG
    #

    print(
        "Registered tools:"
    )

    print(
        registry.list_tools()
    )

    print(
        "\nModels:"
    )

    print(
        f"Chat: {models.chat_llm.get_current_model()}"
    )

    print(
        f"Code: {models.code_llm.get_current_model()}"
    )

    print(
        f"Planner: {models.planner_llm.get_current_model()}"
    )

    print(
        f"Decision: {models.decision_llm.get_current_model()}"
    )

    #
    # REQUEST
    #

    request = input(
        "\nRequest:\n"
    ).strip()

    if not request:
        return

    #
    # HISTORY
    #

    history = conversation.get()

    if history:

        print(
            "\nPrevious conversation:"
        )

        last = history[-1]

        print(
            last
        )

    #
    # PLANNING
    #

    plan = planner_agent.create_plan(
        request
    )

    print(
        "\nPlan:"
    )

    print(
        plan
    )

    #
    # EXECUTION
    #

    if plan.get("tool") == "chat":

        result = chat_agent.respond(
            plan.get(
                "message",
                request
            )
        )

    elif plan.get("steps"):

        steps = plan["steps"]

        if (
            len(steps) == 1
            and steps[0].get("tool") == "chat"
        ):

            result = chat_agent.respond(
                request
            )

        else:

            result = tool_agent.execute_steps(
                plan
            )

    else:

        result = tool_agent.execute(
            plan
        )

    #
    # RESULT
    #

    print(
        "\nResult:"
    )

    print(
        result
    )

    #
    # SAVE CONVERSATION
    #

    conversation.add(
        request,
        str(result)
    )


if __name__ == "__main__":

    main()