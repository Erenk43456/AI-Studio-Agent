import requests


class LLM:

    def __init__(
        self,
        model="qwen2.5:1.5b",
        url="http://localhost:11434/api/generate"
    ):

        self.name = "Qwen2.5 Local"

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
                    "stream": False
                },
                timeout=120
            )


            response.raise_for_status()


            data = response.json()


            return data.get(
                "response",
                ""
            )


        except requests.exceptions.Timeout:

            return "LLM zaman aşımına uğradı."


        except requests.exceptions.ConnectionError:

            return "LLM bağlantısı kurulamadı. Ollama çalışıyor mu kontrol edin."


        except Exception as error:

            return f"LLM hatası: {error}"