from tools.formatter_tool import FormatterTool


formatter = FormatterTool()


result = formatter.format_file(
    "memory/chat_manager.py"
)


print(result)