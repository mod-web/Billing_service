from abc import ABC, abstractmethod


class AbstractRmq(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def on_response(self):
        pass

    @abstractmethod
    def publish(self):
        pass
