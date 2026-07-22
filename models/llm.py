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


        self.base_url = self.url.replace(

            "/api/generate",

            ""

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

            f"LLM initialized: {self.model}"

        )









    def generate(

        self,

        prompt

    ):


        try:


            if not self.check_connection():


                return "LLM_ERROR: Ollama is not running."





            self.logger.info(

                "Generating response."

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



            if not result:


                self.logger.warning(

                    "LLM returned empty response."

                )


                return "LLM_ERROR: Empty response."





            self.logger.info(

                "LLM response completed."

            )



            return result







        except requests.exceptions.Timeout:


            self.logger.error(

                "LLM request timeout."

            )


            return "LLM_ERROR: Request timeout."






        except requests.exceptions.ConnectionError:


            self.logger.error(

                "Ollama connection failed."

            )


            return "LLM_ERROR: Connection failed."






        except Exception as error:


            self.logger.error(

                f"LLM error: {error}"

            )


            return f"LLM_ERROR: {error}"









    def check_connection(self):


        try:


            response = requests.get(

                self.base_url,

                timeout=5

            )



            return response.status_code == 200





        except Exception:


            return False










    def get_models(self):


        try:


            response = requests.get(

                self.base_url + "/api/tags",

                timeout=5

            )


            response.raise_for_status()



            data = response.json()



            return [

                model.get("name")

                for model in data.get(

                    "models",

                    []

                )

            ]





        except Exception as error:


            self.logger.error(

                f"Model list error: {error}"

            )


            return []









    def has_model(self):


        models = self.get_models()


        return self.model in models










    def get_current_model(self):


        return self.model