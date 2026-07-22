import requests

from config.config_manager import ConfigManager



class LLM:


    def __init__(self):


        self.name = "Qwen2.5 Local LLM"



        self.config = ConfigManager()



        self.model = self.config.get(

            "model",

            "qwen2.5:3b"

        )



        self.url = self.config.get(

            "ollama_url",

            "http://localhost:11434/api/generate"

        )



        self.base_url = (

            self.url

            .replace(

                "/api/generate",

                ""

            )

        )



        self.temperature = self.config.get(

            "temperature",

            0.3

        )



        self.num_predict = self.config.get(

            "num_predict",

            150

        )









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



            return data.get(

                "response",

                ""

            ).strip()





        except requests.exceptions.Timeout:


            return "LLM_ERROR: Request timeout."





        except requests.exceptions.ConnectionError:


            return "LLM_ERROR: Connection failed."





        except Exception as error:


            return f"LLM_ERROR: {error}"









    def check_connection(self):


        try:


            response = requests.get(

                self.base_url,

                timeout=5

            )



            return response.status_code == 200





        except:


            return False







    def get_models(self):


        try:


            response = requests.get(


                self.base_url + "/api/tags",


                timeout=5


            )



            response.raise_for_status()



            data = response.json()



            models = []



            for model in data.get(

                "models",

                []

            ):


                models.append(

                    model.get(

                        "name"

                    )

                )



            return models





        except:


            return []









    def get_current_model(self):


        return self.model