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
            2048
        )


        self.timeout = self.config.get(
            "api_timeout",
            60
        )


        self.logger.info(
            f"API LLM initialized: {self.model}"
        )




    def generate(
        self,
        prompt,
        max_tokens=None,
        temperature=None,
        timeout=None
    ):


        try:


            if not self.url:

                return "LLM_ERROR: API URL missing."



            if not self.model:

                return "LLM_ERROR: API model missing."




            headers = {

                "Authorization": f"Bearer {self.api_key}",

                "Accept": "application/json",

                "Content-Type": "application/json"

            }





            payload = {


                "model": self.model,


                "messages": [

                    {

                        "role":"user",

                        "content":prompt

                    }

                ],



                "temperature": (

                    temperature

                    if temperature is not None

                    else self.temperature

                ),



                "max_tokens": (

                    max_tokens

                    if max_tokens is not None

                    else self.num_predict

                ),



                "top_p":1,


                "stream":False

            }





            request_timeout = (

                timeout

                if timeout is not None

                else self.timeout

            )





            self.logger.info(
                "Sending request to NVIDIA NIM"
            )

            self.logger.info(
                f"URL: {self.url}"
            )

            self.logger.info(
                f"MODEL: {self.model}"
            )





            response = requests.post(

                self.url,

                headers=headers,

                json=payload,

                timeout=request_timeout

            )






            self.logger.info(
                f"STATUS: {response.status_code}"
            )





            if response.status_code != 200:


                self.logger.error(
                    response.text
                )


                return {

                    "error": response.text,

                    "status": response.status_code

                }





            data = response.json()





            choices = data.get(
                "choices",
                []
            )



            if not choices:


                return {

                    "error":
                    "No choices returned",

                    "raw":
                    data

                }




            message = choices[0].get(
                "message",
                {}
            )



            content = message.get(
                "content"
            )




            if not content:


                return {

                    "error":
                    "Empty model response",

                    "raw":
                    data

                }





            return content.strip()






        except requests.exceptions.Timeout:


            self.logger.error(
                "API request timeout."
            )


            return {

                "error":
                "API timeout"

            }





        except Exception as e:


            self.logger.error(
                f"API LLM error: {e}"
            )


            return {

                "error":
                str(e)

            }