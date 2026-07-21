import os


class FileTool:

    def create_file(
        self,
        filename,
        content
    ):

        """
        Yeni dosya oluşturur.
        """

        if not filename:
            return "Dosya adı belirtilmedi."


        try:

            with open(
                filename,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    content or ""
                )


            return f"{filename} oluşturuldu."


        except OSError as error:

            return f"Dosya oluşturma hatası: {error}"



    def read_file(
        self,
        filename
    ):

        """
        Dosya içeriğini okur.
        """

        if not filename:
            return "Dosya adı belirtilmedi."


        if not os.path.exists(filename):
            return "Dosya bulunamadı."


        try:

            with open(
                filename,
                "r",
                encoding="utf-8"
            ) as file:

                return file.read()


        except OSError as error:

            return f"Dosya okuma hatası: {error}"