from tools.tool_registry import ToolRegistry
from tools.calculator import Calculator
from tools.file_tool import FileTool
from tools.memory_tool import MemoryTool

from agents.decision_agent import DecisionAgent
from agents.tool_agent import ToolAgent
from agents.planner_agent import PlannerAgent

from memory.conversation import ConversationMemory


registry = ToolRegistry()


calculator = Calculator()
file_tool = FileTool()
memory_tool = MemoryTool()


registry.register("calculator", calculator)
registry.register("file", file_tool)
registry.register("memory", memory_tool)


tool_agent = ToolAgent(registry)
planner_agent = PlannerAgent()
conversation = ConversationMemory()


print("Kayıtlı araçlar:")
print(registry.list_tools())


request = input("\nİstek:\n")


plan = planner_agent.create_plan(request)

history = conversation.get()

if history:
    print("\nÖnceki konuşmalar:")
    print(history)


print("\nPlan:")
print(plan)


result = tool_agent.execute(plan)


print("\nSonuç:")
print(result)

conversation.add(
    request,
    str(result)
)