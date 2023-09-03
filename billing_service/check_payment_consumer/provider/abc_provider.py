from abc import ABC, abstractmethod


class Provider(ABC):
    """ Interface """

    @abstractmethod
    def check_payment(self):
        pass
