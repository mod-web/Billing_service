from yookassa import Configuration, Payment

from .abc_provider import Provider


class Yookassa(Provider):
    def __init__(self, account_id: int, secret_key: str):
        self.account_id = account_id
        self.secret_key = secret_key

    def check_payment(self, payment_id):
        Configuration.account_id = self.account_id
        Configuration.secret_key = self.secret_key

        payment = Payment.find_one(payment_id)

        return payment
