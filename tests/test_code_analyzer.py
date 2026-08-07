from tools.code_analyzer_tool import CodeAnalyzerTool


tool = CodeAnalyzerTool()


code = """
def hello(
    print("Merhaba")
"""


result = tool.analyze_code(
    code
)


print(result)