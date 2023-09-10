from abc import ABC, abstractmethod

from sqlalchemy import text


class AbstractBroker(ABC):
    @abstractmethod
    def publish_to_broker(self, routing_key: str, message: str) -> None:
        pass


class AbstractService(ABC):
    @abstractmethod
    def _execute_stmt(self, stmt: text):
        pass


