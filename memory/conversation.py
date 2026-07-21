import json
import os


class ConversationMemory:

    def __init__(
        self,
        file="conversation.json",
        limit=10
    ):

        self.file = file
        self.limit = limit
        self.data = []

        self.load()



    def load(self):

        """
        Önceki konuşmaları yükler.
        """

        if not os.path.exists(self.file):
            self.data = []
            return


        try:

            with open(
                self.file,
                "r",
                encoding="utf-8"
            ) as f:

                self.data = json.load(f)


        except (
            json.JSONDecodeError,
            OSError
        ):

            self.data = []



    def add(
        self,
        user,
        assistant
    ):

        """
        Yeni konuşma ekler.
        """

        self.data.append(
            {
                "user": user,
                "assistant": assistant
            }
        )


        # Son N konuşmayı tut
        self.data = self.data[-self.limit:]


        self.save()



    def save(self):

        """
        Konuşmaları diske yazar.
        """

        try:

            with open(
                self.file,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    self.data,
                    f,
                    ensure_ascii=False,
                    indent=4
                )


        except OSError as error:

            print(
                "Conversation kayıt hatası:",
                error
            )



    def get(self):

        """
        Konuşma geçmişini döndürür.
        """

        return self.data



    def clear(self):

        """
        Geçmişi temizler.
        """

        self.data = []

        self.save()