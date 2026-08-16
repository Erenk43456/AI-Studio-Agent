import requests

from app.core.logger import AppLogger


class APILLM:

    def __init__(
        self,
        config
    ):

        self.config = config

        self.logger = AppLogger()

        self.url = getattr(
            config,
            "endpoint",
            ""
        )

        self.model = getattr(
            config,
            "model",
            ""
        )

        self.api_key = getattr(
            config,
            "api_key",
            ""
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

        self.timeout = getattr(
            config,
            "timeout",
            180
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

        request_timeout = (
            timeout
            if timeout is not None
            else self.timeout
        )

        try:

            if not self.url:

                return {
                    "error": "API URL missing."
                }

            if not self.model:

                return {
                    "error": "API model missing."
                }

            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            if self.api_key:

                headers["Authorization"] = (
                    f"Bearer {self.api_key}"
                )

            request_max_tokens = (
                max_tokens
                if max_tokens is not None
                else self.num_predict
            )

            request_temperature = (
                temperature
                if temperature is not None
                else self.temperature
            )

            payload = {

                "model": self.model,

                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                "temperature": request_temperature,

                "max_tokens": request_max_tokens,

                "top_p": 1,

                "stream": False
            }

            self.logger.info(
                f"Sending API request: {self.model}"
            )

            response = requests.post(

                self.url,

                headers=headers,

                json=payload,

                timeout=request_timeout
            )

            response.raise_for_status()

            data = response.json()

            choices = data.get(
                "choices",
                []
            )

            if not choices:

                return {
                    "error": "No choices returned",
                    "raw": data
                }

            message = choices[0].get(
                "message",
                {}
            )

            if not isinstance(
                message,
                dict
            ):

                return {
                    "error": "Invalid message object",
                    "raw": data
                }

            content = message.get(
                "content"
            )

            if isinstance(
                content,
                str
            ) and content.strip():

                return content.strip()

            return {
                "error": "Empty model response",
                "finish_reason": choices[0].get(
                    "finish_reason"
                ),
                "raw": data
            }

        except requests.exceptions.Timeout:

            self.logger.error(
                f"API request timeout after {request_timeout}s."
            )

            return {
                "error": "API timeout",
                "timeout": request_timeout,
                "model": self.model
            }

        except requests.exceptions.RequestException as error:

            self.logger.error(
                f"API request error: {error}"
            )

            return {
                "error": f"API request error: {error}"
            }

        except ValueError as error:

            self.logger.error(
                f"Invalid API response: {error}"
            )

            return {
                "error": f"Invalid API response: {error}"
            }

        except Exception as error:

            self.logger.error(
                f"API LLM error: {error}"
            )

            return {
                "error": str(error)
            }


    def check_connection(
        self
    ):

        try:

            response = requests.get(
                self.url,
                timeout=5
            )

            return response.status_code < 500

        except Exception:

            return False


    def get_models(
        self
    ):

        return [
            self.model
        ] if self.model else []


    def has_model(
        self
    ):

        return bool(
            self.model
        )


    def get_current_model(
        self
    ):

        return self.model