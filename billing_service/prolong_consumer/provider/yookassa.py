from yookassa import Configuration, Payment

from .abc_provider import Provider


class Yookassa(Provider):
    def __init__(self, account_id: int, secret_key: str):
        self.account_id = account_id
        self.secret_key = secret_key

    def prolong_payment(self, payment_id, amount):
        Configuration.account_id = self.account_id
        Configuration.secret_key = self.secret_key

        payment = Payment.create({
            "amount": {
                "value": f"{amount}.00",
                "currency": "RUB"
            },
            "capture": True,
            "payment_method_id": payment_id,
            "description": "Renew order"
        })

        return payment
