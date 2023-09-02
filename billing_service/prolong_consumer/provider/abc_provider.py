from abc import ABC, abstractmethod


class Provider(ABC):
    """ Interface """

    @abstractmethod
    def prolong_payment(self):
        pass
