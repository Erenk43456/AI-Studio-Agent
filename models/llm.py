import requests
import json
import os


class LLM:

    def __init__(self):

        self.name = "Qwen2.5 Local LLM"

        settings = self.load_settings()

        self.model = settings.get(
            "model",
            "qwen2.5:3b"
        )

        self.url = settings.get(
            "ollama_url",
            "http://localhost:11434/api/generate"
        )

        self.temperature = settings.get(
            "temperature",
            0.3
        )

        self.num_predict = settings.get(
            "num_predict",
            150
        )



    def load_settings(self):

        path = "config/settings.json"


        if os.path.exists(path):

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)


        return {}




    def generate(
        self,
        prompt
    ):

        try:

            response = requests.post(

                self.url,

                json={

                    "model": self.model,

                    "prompt": prompt,

                    "stream": False,

                    "options": {

                        "temperature": self.temperature,

                        "num_predict": self.num_predict

                    }

                },

                timeout=120

            )


            response.raise_for_status()


            data = response.json()


            result = data.get(
                "response",
                ""
            )


            return result.strip()



        except requests.exceptions.Timeout:

            return "LLM_ERROR: Request timeout."



        except requests.exceptions.ConnectionError:

            return "LLM_ERROR: Connection failed."



        except Exception as error:

            return f"LLM_ERROR: {error}"