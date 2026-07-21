from memory.memory import Memory


class MemoryTool:

    def __init__(
        self,
        memory=None
    ):

        # Dışarıdan memory verilirse onu kullanır.
        # Yoksa yeni oluşturur.
        self.memory = memory if memory else Memory()



    def remember(self):

        """
        Tüm hafızayı döndürür.
        """

        return self.memory.recall()



    def save_info(
        self,
        key,
        value
    ):

        """
        Bilgi kaydeder.
        """

        if not key:
            return "Anahtar boş olamaz."


        self.memory.save(
            key,
            value
        )


        return f"{key} kaydedildi."



    def get_info(
        self,
        key
    ):

        """
        Bilgi getirir.
        """

        if not key:
            return None


        return self.memory.get(
            key
        )