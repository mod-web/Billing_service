from abc import ABC, abstractmethod


class AbstractBroker(ABC):
    @abstractmethod
    def publish_to_broker(self, routing_key: str, message: str) -> None:
        pass


class AbstractService(ABC):
    @abstractmethod
    def execute_stmt(self, stmt: str):
        pass


