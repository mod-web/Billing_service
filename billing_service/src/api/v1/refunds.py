from fastapi import APIRouter, Depends
from yookassa import Configuration, Refund


router = APIRouter()


@router.post(
    '/',
    description='Create refund for a order',
    summary='Create refund for a order',
)
async def create_refund(payment_id: str, amount: int):
    Configuration.account_id = 243091
    Configuration.secret_key = 'test_3SWAMPhw_Q1RcbAjaGY_GQpts4CSQ5D6Txv7ivHpwMg'

    refund = Refund.create({
        "amount": {
            "value": f"{amount}.00",
            "currency": "RUB"
        },
        "payment_id": f"{payment_id}"
    })
    for i in refund:
        print(i)

    return "ok"
