from tools.code_repair_tool import CodeRepairTool


tool = CodeRepairTool()


result = tool.repair_code(
"""
def test(
    print("hello")
"""
)


print(result)