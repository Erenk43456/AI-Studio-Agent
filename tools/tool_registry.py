class ToolRegistry:

    def __init__(self):
        self.tools = {}



    def register(
        self,
        name,
        tool
    ):

        """
        Yeni tool ekler.
        """

        if name in self.tools:
            raise ValueError(
                f"'{name}' isimli tool zaten kayıtlı."
            )


        self.tools[name] = tool



    def get(
        self,
        name
    ):

        """
        Tool getirir.
        """

        return self.tools.get(name)



    def has(
        self,
        name
    ):

        """
        Tool var mı kontrol eder.
        """

        return name in self.tools



    def list_tools(self):

        """
        Kayıtlı tool isimlerini döndürür.
        """

        return list(
            self.tools.keys()
        )



    def remove(
        self,
        name
    ):

        """
        Tool siler.
        """

        if name in self.tools:
            del self.tools[name]