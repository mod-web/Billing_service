from yookassa import Configuration, Payment, Refund
from yookassa.domain.response import RefundResponse, PaymentResponse

from .abc_provider import Provider
from config import settings


class Yookassa(Provider):
    account_id = settings.yookassa.account_id
    secret_key = settings.yookassa.secret_key

    def create_payment(self, order_id: str, name_subscribe: str, amount: int) -> Payment:
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

    def refund_payment(self, payment_id: str, return_price: int) -> Payment:
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
