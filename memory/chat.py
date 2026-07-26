from datetime import datetime
from pathlib import Path

from memory.conversation import ConversationMemory



class Chat:


    def __init__(
        self,
        chat_id,
        title="New Chat"
    ):


        self.id = chat_id


        self.title = title


        self.created_at = datetime.now()



        self.folder = Path(
            f"data/chats/chat_{chat_id}"
        )


        self.folder.mkdir(
            parents=True,
            exist_ok=True
        )



        self.conversation = ConversationMemory(

            self.folder /
            "conversation.json"

        )





    def rename(
        self,
        title
    ):

        title = title.strip()


        if title:

            self.title = title[:30]





    def info(self):

        return {

            "id": self.id,

            "title": self.title,

            "created_at":
                self.created_at.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

        }