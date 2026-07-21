import requests


class LLM:

    def __init__(self):
        self.name = "Qwen2.5 Local"


    def generate(self, prompt):

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:1.5b",
                "prompt": prompt,
                "stream": False
            }
        )

        data = response.json()

        return data["response"]