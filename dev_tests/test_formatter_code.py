from tools.formatter_tool import FormatterTool


formatter = FormatterTool()


code = """
def hello():
        print("Merhaba")
"""


result = formatter.format_code(code)


print(result)