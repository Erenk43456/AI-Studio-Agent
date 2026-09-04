import time

import threading

import requests

from app.core.logger import AppLogger

from contracts.llm_contract import LLMContract


class APILLM(LLMContract):

    def __init__(
        self,
        config,
        agent_name="API"
    ):

        self.config = config

        self.agent_name = agent_name or "unknown"

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

        self.max_retries = getattr(
            config,
            "max_retries",
            3
        )

        self.retry_backoff = getattr(
            config,
            "retry_backoff",
            2
        )

        self.retryable_status_codes = {
            429,
            500,
            502,
            503,
            504
        }

        self.logger.info(
            f"{self.agent_name} API LLM initialized: {self.model}"
        )


    def generate(
        self,
        prompt,
        max_tokens=None,
        temperature=None,
        timeout=None,
        cancel_event=None
    ):

        request_timeout = (
            timeout
            if timeout is not None
            else self.timeout
        )

        try:

            if (
                cancel_event is not None
                and cancel_event.is_set()
            ):

                return {
                    "error": "API request cancelled."
                }

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

            last_error = None

            for attempt in range(
                self.max_retries + 1
            ):

                if (
                    cancel_event is not None
                    and cancel_event.is_set()
                ):

                    return {
                        "error": "API request cancelled."
                    }

                try:

                    self.logger.info(
                        f"[{self.agent_name}] Sending API request: {self.model}"
                        f"(attempt {attempt + 1}/{self.max_retries + 1})"
                    )

                    response = requests.post(

                        self.url,

                        headers=headers,

                        json=payload,

                        timeout=request_timeout
                    )

                    if (
                        cancel_event is not None
                        and cancel_event.is_set()
                    ):

                        return {
                            "error": "API request cancelled."
                        }

                    if (
                        response.status_code
                        in self.retryable_status_codes
                    ):

                        if attempt < self.max_retries:

                            delay = (
                                self.retry_backoff
                                * (2 ** attempt)
                            )

                            self.logger.warning(
                                f"API returned HTTP "
                                f"{response.status_code}. "
                                f"Retrying in {delay}s..."
                            )

                            if (
                                cancel_event is not None
                                and cancel_event.wait(delay)
                            ):

                                return {
                                    "error": "API request cancelled."
                                }

                            continue

                        response.raise_for_status()

                    response.raise_for_status()

                    data = response.json()

                    break

                except requests.exceptions.Timeout as error:

                    last_error = error

                    if attempt < self.max_retries:

                        delay = (
                            self.retry_backoff
                            * (2 ** attempt)
                        )

                        self.logger.warning(
                            f"API request timed out. "
                            f"Retrying in {delay}s..."
                        )

                        if (
                            cancel_event is not None
                            and cancel_event.wait(delay)
                        ):

                            return {
                                "error": "API request cancelled."
                            }

                        continue

                    raise

                except requests.exceptions.ConnectionError as error:

                    last_error = error

                    if attempt < self.max_retries:

                        delay = (
                            self.retry_backoff
                            * (2 ** attempt)
                        )

                        self.logger.warning(
                            f"API connection error. "
                            f"Retrying in {delay}s..."
                        )

                        if (
                            cancel_event is not None
                            and cancel_event.wait(delay)
                        ):

                            return {
                                "error": "API request cancelled."
                            }

                        continue

                    raise

                except requests.exceptions.HTTPError:

                    raise

            else:

                if last_error is not None:

                    raise last_error

                raise RuntimeError(
                    "API request failed after all retries."
                )

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
                f"[{self.agent_name}] API request error: {error}"
            )

            return {
                "error": f"[{self.agent_name}] API request error: {error}"
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

            response = requests.post(
                self.url,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                json={},
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
        self,
        model_name: str
    ) -> bool:

        return model_name in self.get_models()


    def get_current_model(
        self
    ):

        return self.model