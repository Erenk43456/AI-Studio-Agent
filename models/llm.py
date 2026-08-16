import requests

from app.core.logger import AppLogger


class LLM:

    def __init__(
        self,
        config
    ):

        self.config = config

        self.logger = AppLogger()

        self.model = getattr(
            config,
            "model",
            "qwen2.5:3b"
        )

        self.url = getattr(
            config,
            "endpoint",
            "http://localhost:11434"
        )

        self.url = self.url.rstrip("/")

        if self.url.endswith(
            "/api/generate"
        ):
            self.generate_url = self.url
            self.base_url = self.url[
                :-len("/api/generate")
            ]
        else:
            self.base_url = self.url
            self.generate_url = (
                self.base_url +
                "/api/generate"
            )

        self.temperature = getattr(
            config,
            "temperature",
            0.3
        )

        self.num_predict = getattr(
            config,
            "max_tokens",
            2048
        )

        self.request_timeout = getattr(
            config,
            "timeout",
            120
        )

        self.logger.info(
            f"Local LLM initialized: {self.model}"
        )


    def generate(
        self,
        prompt,
        max_tokens=None,
        temperature=None,
        timeout=None
    ):

        try:

            if not self.check_connection():

                return (
                    "LLM_ERROR: "
                    "Local LLM is not reachable."
                )

            response = requests.post(

                self.generate_url,

                json={
                    "model": self.model,

                    "prompt": prompt,

                    "stream": False,

                    "options": {

                        "temperature": (
                            self.temperature
                            if temperature is None
                            else temperature
                        ),

                        "num_predict": (
                            self.num_predict
                            if max_tokens is None
                            else max_tokens
                        )
                    }
                },

                timeout=(
                    self.request_timeout
                    if timeout is None
                    else timeout
                )
            )

            response.raise_for_status()

            data = response.json()

            result = data.get(
                "response",
                ""
            ).strip()

            if not result:

                return (
                    "LLM_ERROR: "
                    "Empty response."
                )

            return result

        except requests.exceptions.Timeout:

            self.logger.error(
                "Local LLM request timeout."
            )

            return (
                "LLM_ERROR: "
                "Request timeout."
            )

        except requests.exceptions.ConnectionError:

            self.logger.error(
                "Local LLM connection failed."
            )

            return (
                "LLM_ERROR: "
                "Connection failed."
            )

        except Exception as error:

            self.logger.error(
                f"Local LLM error: {error}"
            )

            return f"LLM_ERROR: {error}"


    def check_connection(
        self
    ):

        try:

            response = requests.get(
                self.base_url,
                timeout=5
            )

            return response.status_code == 200

        except Exception:

            return False


    def get_models(
        self
    ):

        try:

            response = requests.get(
                self.base_url +
                "/api/tags",
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
                if model.get("name")
            ]

        except Exception as error:

            self.logger.error(
                f"Local model list error: {error}"
            )

            return []


    def has_model(
        self
    ):

        return (
            self.model
            in self.get_models()
        )


    def get_current_model(
        self
    ):

        return self.model