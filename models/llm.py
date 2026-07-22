import requests


class LLM:

    def __init__(
        self,
        model="qwen2.5:3b",
        url="http://localhost:11434/api/generate"
    ):

        self.name = "Qwen2.5 Local LLM"
        self.model = model
        self.url = url



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
                        "temperature": 0.3,
                        "num_predict": 150
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