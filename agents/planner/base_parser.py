from abc import ABC, abstractmethod


class BaseParser(ABC):

    name = ""

    priority = 100

    enabled = True


    @abstractmethod
    def parse(
        self,
        message
    ):
        pass