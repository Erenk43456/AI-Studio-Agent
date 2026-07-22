import requests

from config.config_manager import ConfigManager
from app.core.logger import AppLogger




class LLM:


    def __init__(self):


        self.name = "Qwen2.5 Local LLM"



        self.config = ConfigManager()


        self.logger = AppLogger()





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





        self.logger.info(

            f"LLM initialized with model: {self.model}"

        )









    def generate(

        self,

        prompt

    ):


        try:


            self.logger.info(

                f"LLM request started. Model: {self.model}"

            )



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

            ).strip()



            self.logger.info(

                "LLM response completed."

            )



            return result





        except requests.exceptions.Timeout as error:


            self.logger.error(

                f"LLM timeout: {error}"

            )


            return "LLM_ERROR: Request timeout."







        except requests.exceptions.ConnectionError as error:


            self.logger.error(

                f"LLM connection failed: {error}"

            )


            return "LLM_ERROR: Connection failed."







        except Exception as error:


            self.logger.error(

                f"LLM unexpected error: {error}"

            )


            return f"LLM_ERROR: {error}"









    def check_connection(self):


        try:


            response = requests.get(

                self.base_url,

                timeout=5

            )



            if response.status_code == 200:


                self.logger.info(

                    "Ollama connection successful."

                )


                return True




            return False





        except Exception as error:


            self.logger.error(

                f"Ollama connection check failed: {error}"

            )


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





        except Exception as error:


            self.logger.error(

                f"Model list error: {error}"

            )


            return []









    def get_current_model(self):


        return self.model