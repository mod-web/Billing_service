from abc import ABC, abstractmethod


class Provider(ABC):
    """ Interface """

    @property
    def account_id(self):
        raise NotImplementedError

    @property
    def secret_key(self):
        raise NotImplementedError

    @abstractmethod
    def create_payment(self, order_id: str, name_subscribe: str, amount: int):
        pass

    @abstractmethod
    def refund_payment(self, payment_id: str, return_price: int):
        pass
