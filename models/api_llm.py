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


                return (
                    "LLM_ERROR: API URL missing."
                )



            if not self.model:


                return (
                    "LLM_ERROR: API model missing."
                )





            headers = {

                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json"

            }





            if self.api_key:


                headers["Authorization"] = (

                    f"Bearer {self.api_key}"

                )







            payload = {


                "model": self.model,



                "messages": [


                    {


                        "role": "user",


                        "content": prompt


                    }


                ],



                "temperature": (

                    temperature

                    if temperature is not None

                    else 1

                ),



                "max_tokens": (

                    max_tokens

                    if max_tokens is not None

                    else 16384

                ),

                "top_p": 1,
                "stream": False,
                "seed": 0

            }






            request_timeout = (

                timeout

                if timeout is not None

                else self.timeout

            )





            self.logger.info(
                "Sending request to NVIDIA NIM"
            )





            response = requests.post(


                self.url,


                headers=headers,


                json=payload,


                timeout=request_timeout


            )






            if response.status_code != 200:


                self.logger.error(

                    f"NVIDIA API Error STATUS: {response.status_code}"

                )

                self.logger.error(
                    
                    f"NVIDIA API BODY: {response.text}"

                )


                return (

                    f"LLM_ERROR: HTTP {response.status_code}: {response.text}"

                )







            data = response.json()






            result = (

                data

                .get(
                    "choices",
                    [{}]
                )[0]

                .get(
                    "message",
                    {}
                )

                .get(
                    "content",
                    ""
                )

            )





            if not result:


                return (

                    "LLM_ERROR: Empty response."

                )





            return result.strip()






        except requests.exceptions.Timeout:


            self.logger.error(
                "API request timeout."
            )


            return (

                "LLM_ERROR: API timeout."

            )







        except requests.exceptions.RequestException as error:


            self.logger.error(

                f"API request error: {error}"

            )


            return (

                f"LLM_ERROR: {error}"

            )







        except Exception as error:


            self.logger.error(

                f"API LLM error: {error}"

            )


            return (

                f"LLM_ERROR: {error}"

            )