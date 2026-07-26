from tools.file_tool import FileTool


tool = FileTool()

print(
    tool.write_file(
        "test_file_tool.py",
        """
def hello():
        print("hello")
"""
    )
)