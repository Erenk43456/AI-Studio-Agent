import json
import os


class Memory:

    def __init__(self, file="memory.json"):

        self.file = file
        self.data = {}

        self.load()


    def load(self):

        """
        Hafızayı dosyadan yükler.
        """

        if not os.path.exists(self.file):
            self.data = {}
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

            # Bozuk dosya varsa temiz başla
            self.data = {}



    def save(self, key, value):

        """
        Yeni bilgi kaydeder.
        """

        self.data[key] = value

        self._write()



    def get(self, key):

        """
        Hafızadan bilgi alır.
        """

        return self.data.get(key)



    def recall(self):

        """
        Tüm hafızayı döndürür.
        """

        return self.data



    def clear(self):

        """
        Hafızayı temizler.
        """

        self.data = {}

        self._write()



    def _write(self):

        """
        JSON dosyasına güvenli yazma.
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
                "Memory kayıt hatası:",
                error
            )