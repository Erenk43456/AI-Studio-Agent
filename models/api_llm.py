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

        # GPT-OSS-120B and other large reasoning models
        # may need significantly more than 60 seconds.
        self.timeout = self.config.get(
            "api_timeout",
            180
        )

        self.logger.info(
            f"API LLM initialized: {self.model}"
        )

    # =============================================================
    # Generate
    # =============================================================

    def generate(
        self,
        prompt,
        max_tokens=None,
        temperature=None,
        timeout=None
    ):

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
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

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

            request_timeout = (
                timeout
                if timeout is not None
                else self.timeout
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
                "Sending request to NVIDIA NIM"
            )

            self.logger.info(
                f"URL: {self.url}"
            )

            self.logger.info(
                f"MODEL: {self.model}"
            )

            self.logger.info(
                f"MAX TOKENS: {request_max_tokens}"
            )

            self.logger.info(
                f"TIMEOUT: {request_timeout}"
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

            # =====================================================
            # HTTP error
            # =====================================================

            if response.status_code != 200:

                self.logger.error(
                    response.text
                )

                return {
                    "error": response.text,
                    "status": response.status_code
                }

            # =====================================================
            # Parse response
            # =====================================================

            data = response.json()

            choices = data.get(
                "choices",
                []
            )

            if not choices:

                self.logger.error(
                    "No choices returned by LLM."
                )

                return {
                    "error": "No choices returned",
                    "raw": data
                }

            choice = choices[0]

            message = choice.get(
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

            finish_reason = choice.get(
                "finish_reason"
            )

            reasoning = message.get(
                "reasoning"
            )

            reasoning_content = message.get(
                "reasoning_content"
            )

            # =====================================================
            # Normal response
            # =====================================================

            if isinstance(
                content,
                str
            ) and content.strip():

                return content.strip()

            # =====================================================
            # Missing final content
            # =====================================================

            self.logger.error(
                "LLM returned no content."
            )

            self.logger.error(
                f"Finish reason: {finish_reason}"
            )

            if reasoning or reasoning_content:

                self.logger.error(
                    "Model produced reasoning but no final content."
                )

                if finish_reason == "length":

                    return {
                        "error": (
                            "Model reached max_tokens "
                            "during reasoning before producing "
                            "a final response."
                        ),
                        "finish_reason": finish_reason,
                        "reasoning_present": True
                    }

            return {
                "error": "Empty model response",
                "finish_reason": finish_reason,
                "raw": data
            }

        # =========================================================
        # Timeout
        # =========================================================

        except requests.exceptions.Timeout:

            self.logger.error(
                f"API request timeout after {request_timeout} seconds."
            )

            return {
                "error": "API timeout",
                "timeout": request_timeout,
                "model": self.model
            }

        # =========================================================
        # Request error
        # =========================================================

        except requests.exceptions.RequestException as error:

            self.logger.error(
                f"API request error: {error}"
            )

            return {
                "error": f"API request error: {error}"
            }

        # =========================================================
        # Invalid JSON
        # =========================================================

        except ValueError as error:

            self.logger.error(
                f"Invalid JSON response: {error}"
            )

            return {
                "error": f"Invalid API response: {error}"
            }

        # =========================================================
        # Unknown error
        # =========================================================

        except Exception as error:

            self.logger.error(
                f"API LLM error: {error}"
            )

            return {
                "error": str(error)
            }