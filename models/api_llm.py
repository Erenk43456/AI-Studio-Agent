import requests

from app.core.logger import AppLogger



class APILLM:


    def __init__(
        self,
        config
    ):


        self.config = config


        self.logger = AppLogger()



        self.url = self.config.get(

            "api_url",

            ""

        )



        self.model = self.config.get(

            "api_model",

            ""

        )



        self.api_key = self.config.get(

            "api_key",

            ""

        )



        self.temperature = self.config.get(

            "temperature",

            0.3

        )



        self.num_predict = self.config.get(

            "num_predict",

            1200

        )



        self.logger.info(

            f"API LLM initialized: {self.model}"

        )







    def generate(
        self,
        prompt
    ):


        try:


            if not self.url:


                return "LLM_ERROR: API URL missing."



            if not self.model:


                return "LLM_ERROR: API model missing."






            headers = {


                "Content-Type":

                "application/json"

            }



            if self.api_key:


                headers["Authorization"] = (

                    f"Bearer {self.api_key}"

                )






            response = requests.post(


                self.url,


                headers=headers,


                json={


                    "model": self.model,


                    "messages": [


                        {


                            "role": "user",


                            "content": prompt

                        }

                    ],


                    "temperature": self.temperature,


                    "max_tokens": self.num_predict


                },


                timeout=120

            )




            response.raise_for_status()



            data = response.json()



            return data.get(

                "choices",

                [{}]

            )[0].get(

                "message",

                {}

            ).get(

                "content",

                ""

            ).strip()





        except requests.exceptions.Timeout:


            self.logger.error(

                "API request timeout."

            )


            return "LLM_ERROR: API timeout."





        except requests.exceptions.RequestException as error:


            self.logger.error(

                f"API request error: {error}"

            )


            return f"LLM_ERROR: {error}"





        except Exception as error:


            self.logger.error(

                f"API LLM error: {error}"

            )


            return f"LLM_ERROR: {error}"