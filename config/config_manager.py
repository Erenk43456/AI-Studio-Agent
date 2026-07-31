import json
import os
from pathlib import Path

from dotenv import load_dotenv



class ConfigManager:


    def __init__(self):

        # Load environment variables from .env
        load_dotenv()


        self.file = Path(
            "config/settings.json"
        )


        self.file.parent.mkdir(
            exist_ok=True
        )


        self.data = self.load()


        self.load_environment()



    def load(self):


        if not self.file.exists():

            return {}



        try:


            with open(

                self.file,

                "r",

                encoding="utf-8"

            ) as f:


                return json.load(f)



        except json.JSONDecodeError:


            return {}





    def load_environment(self):


        """
        Environment variables override config file values.
        Sensitive data should stay in .env.
        """


        env_mapping = {


            "NVIDIA_API_KEY": "api_key",


            "NVIDIA_API_URL": "api_url",


            "NVIDIA_MODEL": "model",


            "LLM_PROVIDER": "llm_provider"


        }



        for env_key, config_key in env_mapping.items():


            value = os.getenv(env_key)


            if value:


                self.data[config_key] = value







    def get(

        self,

        key,

        default=None

    ):


        return self.data.get(

            key,

            default

        )







    def set(

        self,

        key,

        value

    ):


        self.data[key] = value


        self.save()







    def update(

        self,

        values

    ):


        self.data.update(

            values

        )


        self.save()







    def save(self):


        with open(

            self.file,

            "w",

            encoding="utf-8"

        ) as f:


            json.dump(

                self.data,

                f,

                indent=4,

                ensure_ascii=False

            )







    def all(self):


        return self.data