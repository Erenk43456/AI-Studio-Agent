import os


class FileTool:

    def create_file(
        self,
        filename,
        content
    ):

        """
        Creates a new file.
        """

        if not filename:
            return "Filename not provided."


        try:

            with open(
                filename,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    content or ""
                )


            return f"{filename} created successfully."


        except OSError as error:

            return f"File creation error: {error}"



    def read_file(
        self,
        filename
    ):

        """
        Reads file content.
        """

        if not filename:
            return "Filename not provided."


        if not os.path.exists(filename):
            return "File not found."


        try:

            with open(
                filename,
                "r",
                encoding="utf-8"
            ) as file:

                return file.read()


        except OSError as error:

            return f"File reading error: {error}"