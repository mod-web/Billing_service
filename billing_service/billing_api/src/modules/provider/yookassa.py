from yookassa import Configuration, Payment, Refund

from .abc_provider import Provider


class Yookassa(Provider):
    def __init__(self, account_id: int, secret_key: str):
        self.account_id = account_id
        self.secret_key = secret_key

    def create_payment(self, order_id, name_subscribe, amount):
        Configuration.account_id = self.account_id
        Configuration.secret_key = self.secret_key

        payment = Payment.create({
            "amount": {
                "value": f"{amount}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://www.example.com/return_url"
            },
            "capture": True,
            "description": f'Order "{name_subscribe} - {amount} RUB"'
        }, order_id)

        return payment

    def refund_payment(self, payment_id, return_price):
        Configuration.account_id = self.account_id
        Configuration.secret_key = self.secret_key

        payment = Refund.create({
            "amount": {
                "value": f"{return_price}.00",
                "currency": "RUB"
            },
            "payment_id": f"{payment_id}"
        })

        return payment
