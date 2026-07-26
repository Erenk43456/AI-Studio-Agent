import json
from pathlib import Path

from memory.chat import Chat



class ChatManager:


    def __init__(self):

        self.chats = {}

        self.current_chat = None

        self.next_id = 1


        self.file = Path(
            "data/chats.json"
        )


        self.file.parent.mkdir(
            exist_ok=True
        )


        self.load()



    def create_chat(
        self,
        title="New Chat"
    ):


        chat = Chat(
            self.next_id,
            title
        )


        self.chats[chat.id] = chat


        self.current_chat = chat


        self.next_id += 1


        self.save()


        return chat





    def get_chat(
        self,
        chat_id
    ):

        return self.chats.get(
            chat_id
        )





    def get_current_chat(self):

        return self.current_chat





    def switch_chat(
        self,
        chat_id
    ):


        chat = self.get_chat(
            chat_id
        )


        if chat:


            self.current_chat = chat


            return chat



        return None





    def rename_chat(
        self,
        chat_id,
        title
    ):


        chat = self.get_chat(
            chat_id
        )


        if chat:


            chat.title = title


            self.save()


            return True



        return False





    def delete_chat(
        self,
        chat_id
    ):


        if chat_id in self.chats:


            del self.chats[chat_id]


            if (
                self.current_chat
                and
                self.current_chat.id == chat_id
            ):

                self.current_chat = None



            self.save()





    def list_chats(self):


        return sorted(

            self.chats.values(),

            key=lambda chat: chat.id

        )





    def save(self):


        data = []


        for chat in self.chats.values():


            data.append(

                chat.info()

            )



        with open(

            self.file,

            "w",

            encoding="utf-8"

        ) as f:


            json.dump(

                data,

                f,

                ensure_ascii=False,

                indent=4

            )





    def load(self):


        if not self.file.exists():

            return



        try:


            with open(

                self.file,

                "r",

                encoding="utf-8"

            ) as f:


                data = json.load(f)



            for item in data:


                chat = Chat(

                    item["id"],

                    item["title"]

                )


                self.chats[chat.id] = chat



                self.next_id = max(

                    self.next_id,

                    chat.id + 1

                )



            # Son yüklenen sohbet aktif olsun

            if self.chats:


                self.current_chat = (

                    self.list_chats()[0]

                )



        except Exception:


            self.chats = {}