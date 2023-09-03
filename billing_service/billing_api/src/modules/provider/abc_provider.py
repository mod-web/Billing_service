from abc import ABC, abstractmethod


class Provider(ABC):
    """ Interface """

    @abstractmethod
    def create_payment(self):
        pass

    @abstractmethod
    def refund_payment(self):
        pass
