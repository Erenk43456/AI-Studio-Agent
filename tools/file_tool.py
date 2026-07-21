class FileTool:
    def create_file(self, filename, content):
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)

        return f"{filename} oluşturuldu."

    def read_file(self, filename):
        with open(filename, "r", encoding="utf-8") as file:
            return file.read()